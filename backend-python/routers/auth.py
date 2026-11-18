"""
Learnora authentication and user management.

Account architecture
--------------------
Individual learners are stored in public.users with the normal learner role.
Legacy cohort-assigned rows remain readable through a compatibility role mapping;
new organisation/cohort provisioning is guarded by the exclusive email policy.

Platform administrators are stored in public.admins:
    - super_admin
    - staff_admin

Authentication is JWT based, but the JWT is never treated as the final
authority for account state. The database is checked on every authenticated
request.

Learner access states
---------------------
pending
    Email/account has not been verified yet.

trialing
    User has an active server-side free trial.

active
    User has an active paid membership.

free
    Verified individual learner access while FREE_ACCESS_MODE is enabled.

expired
    Trial or paid membership has expired. The reversible free-launch mode may
    grant individual learner access without rewriting this billing history.

Email verification
------------------
Registration creates a pending account and sends a verification email.

The 7-day trial does NOT begin at registration.

The 7-day trial begins only after successful email verification.

Password reset
--------------
Forgot-password requests generate short-lived, single-use reset tokens.

The API intentionally returns a generic response so attackers cannot use
the endpoint to discover whether an email address belongs to a Learnora
account.

Email delivery
--------------
Transactional email is sent through the Gmail API over HTTPS. The backend
uses a Google OAuth refresh token with the narrowly scoped gmail.send
permission. No SMTP connection, app password, Resend account, or custom
sending domain is required.

Gmail API environment variables:

    GMAIL_OAUTH_CLIENT_ID=<Google OAuth client ID>
    GMAIL_OAUTH_CLIENT_SECRET=<Google OAuth client secret>
    GMAIL_OAUTH_REFRESH_TOKEN=<offline OAuth refresh token>
    GMAIL_USER_EMAIL=sender@gmail.com
    GMAIL_FROM_EMAIL=sender@gmail.com
    GMAIL_FROM_NAME=Learnora Me
"""

import hashlib
import ipaddress
import logging
import hmac
import os
import re
import secrets
import base64
import time
from html import escape

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from typing import Optional

import bcrypt
import httpx

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from supabase import Client, create_client

from services.free_access import free_access_mode_enabled, is_individual_learner


router = APIRouter()
log = logging.getLogger("auth")
bearer = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# ENVIRONMENT
# ---------------------------------------------------------------------------

APP_ENV = os.getenv(
    "APP_ENV",
    "production",
).strip().lower()

SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    "",
).strip()

SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    or os.getenv("SUPABASE_SECRET_KEY", "").strip()
)

if not SUPABASE_URL or not SUPABASE_KEY:
    if APP_ENV != "development":
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set."
        )

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)


# ---------------------------------------------------------------------------
# APPLICATION URLS
# ---------------------------------------------------------------------------

FRONTEND_URL = (
    os.getenv(
        "FRONTEND_URL",
        "https://learnora-me-v02.vercel.app",
    )
    .strip()
    .rstrip("/")
)

AUTH_COOKIE_NAME = "phx_token"
TEAM_COOKIE_NAME = "learnora_team_token"


def _cookie_auth_origins() -> set[str]:
    """Return the explicit frontend origins allowed to establish cookie sessions."""
    origins = {
        "https://learnora-me-v02.vercel.app",
        "https://teamslearnora.vercel.app",
        "https://thepheonixanalytics.com",
        "https://www.thepheonixanalytics.com",
    }
    for configured in (FRONTEND_URL, os.getenv("INTERNAL_FRONTEND_URL", "").strip()):
        value = configured.strip().rstrip("/")
        if value.startswith("https://") or (APP_ENV != "production" and value.startswith("http://")):
            origins.add(value)
    if APP_ENV != "production":
        origins.update({"http://localhost:3000", "http://localhost:3001"})
    return origins


def deliver_auth_token(request: Request, response: Response | None, token: str, payload: dict, *, cookie_name: str = AUTH_COOKIE_NAME) -> dict:
    """Set an HttpOnly cookie for trusted browsers; retain bearer responses for non-browser clients."""
    origin = (request.headers.get("origin") or "").strip().rstrip("/")
    if not origin:
        return payload
    if origin not in _cookie_auth_origins():
        raise HTTPException(status_code=403, detail="This origin is not allowed to establish a session.")
    if response is None:
        response = Response()
    response.set_cookie(key=cookie_name, value=token, max_age=TOKEN_TTL, httponly=True, secure=APP_ENV == "production", samesite="lax", path="/")
    safe_payload = dict(payload)
    safe_payload.pop("token", None)
    safe_payload.pop("access_token", None)
    safe_payload.pop("refresh_token", None)
    return safe_payload


def clear_auth_cookie(response: Response, cookie_name: str = AUTH_COOKIE_NAME) -> None:
    response.set_cookie(key=cookie_name, value="", max_age=0, expires=0, httponly=True, secure=APP_ENV == "production", samesite="lax", path="/")


def _request_auth_token(request: Request | None, creds: Optional[HTTPAuthorizationCredentials], cookie_name: str = AUTH_COOKIE_NAME) -> Optional[str]:
    cookie_token = request.cookies.get(cookie_name) if request else None
    return cookie_token or (creds.credentials if creds else None)


EMAIL_VERIFICATION_PATH = (
    os.getenv(
        "EMAIL_VERIFICATION_PATH",
        "/verify-email",
    )
    .strip()
)

PASSWORD_RESET_PATH = (
    os.getenv(
        "PASSWORD_RESET_PATH",
        "/reset-password",
    )
    .strip()
)


# ---------------------------------------------------------------------------
# EMAIL CONFIGURATION is defined below the auth helpers.


EMAIL_VERIFICATION_TTL_MINUTES = int(
    os.getenv(
        "EMAIL_VERIFICATION_TTL_MINUTES",
        "60",
    )
)

PASSWORD_RESET_TTL_MINUTES = int(
    os.getenv(
        "PASSWORD_RESET_TTL_MINUTES",
        "30",
    )
)

TRIAL_DAYS = int(
    os.getenv(
        "TRIAL_DAYS",
        "7",
    )
)


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

ALGORITHM = "HS256"

TOKEN_TTL = int(
    os.getenv(
        "TOKEN_TTL_SECONDS",
        "86400",
    )
)

JWT_SECRET = (
    os.getenv(
        "JWT_SECRET",
        "",
    )
    .strip()
)

if len(JWT_SECRET) < 32:

    if APP_ENV != "development":

        raise RuntimeError(
            "JWT_SECRET must be set to a random string of 32+ characters."
        )

    JWT_SECRET = secrets.token_hex(32)


# ---------------------------------------------------------------------------
# ROLES
# ---------------------------------------------------------------------------

LEGACY_ASSIGNED_LEARNER_ROLE = "witstart"

LEARNER_ROLES = {
    "normal",
    LEGACY_ASSIGNED_LEARNER_ROLE,
    "organisation_prospect",
}

ADMIN_ROLES = {
    "super_admin",
    "staff_admin",
}

ACTIVE_STATUSES = {
    "trialing",
    "active",
}


# ---------------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------------

EMAIL_RE = re.compile(
    r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
)


def _escape_ilike_literal(value: str) -> str:
    """Escape user-supplied email characters that are wildcards in LIKE filters.

    Supabase/PostgREST ilike filters interpret pattern metacharacters. Email
    lookups must be case-insensitive but must never let a login identifier
    match a different account through %, _, or the PostgREST * wildcard.
    """
    return (
        value.replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("*", "\\*")
    )


def norm_email(
    email: str,
) -> str:

    normalized = (
        email or ""
    ).lower().strip()

    if (
        not EMAIL_RE.match(normalized)
        or len(normalized) > 254
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid email format",
        )

    return normalized


def check_password_rules(password: str):
    if len(password) < 12:
        raise HTTPException(status_code=400, detail="Password must be at least 12 characters long.")
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password is too long (72 bytes maximum for this password hashing scheme).")

    common_passwords = {
        "password123!", "password1234", "qwerty123456", "123456789012",
        "letmein123456", "welcome12345", "admin1234567", "iloveyou1234",
        "learnora1234", "changeme1234",
    }
    if password.casefold() in common_passwords:
        raise HTTPException(status_code=400, detail="Choose a less common password.")

    # Have I Been Pwned k-anonymity range lookup: only the first five SHA-1
    # characters leave this service; the full password/hash is never sent.
    digest = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = digest[:5], digest[5:]
    try:
        response = httpx.get(
            f"https://api.pwnedpasswords.com/range/{prefix}",
            headers={"Add-Padding": "true", "User-Agent": "Learnora-Password-Check"},
            timeout=httpx.Timeout(3.0, connect=2.0),
        )
        response.raise_for_status()
        compromised = any(
            line.partition(":")[0].strip().upper() == suffix
            and int(line.partition(":")[2].strip() or "0") > 0
            for line in response.text.splitlines()
        )
    except (httpx.HTTPError, ValueError):
        log.exception("Compromised-password check unavailable")
        raise HTTPException(status_code=503, detail="Password security checks are temporarily unavailable. Please try again.") from None
    if compromised:
        raise HTTPException(status_code=400, detail="This password has appeared in known data breaches. Choose a different password.")


# ---------------------------------------------------------------------------
# PASSWORDS
# ---------------------------------------------------------------------------

def hash_password(
    password: str,
) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password exceeds bcrypt's 72-byte input limit")
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(12),
    ).decode("utf-8")


def verify_password(
    password: str,
    stored: str,
) -> tuple[bool, bool]:

    """
    Returns:

        (password_is_valid, needs_rehash)

    bcrypt:
        valid, False

    Legacy SHA256:
        valid, True
    """

    if not stored or len(password.encode("utf-8")) > 72:
        return False, False

    if stored.startswith("$2"):

        try:

            return (
                bcrypt.checkpw(
                    password.encode("utf-8"),
                    stored.encode("utf-8"),
                ),
                False,
            )

        except (
            ValueError,
            TypeError,
        ):

            return False, False

    try:

        hashed_password = hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()

        ok = hmac.compare_digest(
            hashed_password,
            stored,
        )

        return ok, ok

    except Exception:

        return False, False


# ---------------------------------------------------------------------------
# TOKEN HELPERS
# ---------------------------------------------------------------------------

def _generate_raw_token() -> str:

    """
    Generates a cryptographically secure random token.

    The raw token is sent to the user by email.

    Only a SHA-256 hash is stored in the database.
    """

    return secrets.token_urlsafe(48)


def _hash_token(
    token: str,
) -> str:

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


# ---------------------------------------------------------------------------
# LOGIN RATE LIMITING
# ---------------------------------------------------------------------------

# Five failed attempts within five minutes trigger a five-minute lockout.
# Separate account and IP buckets prevent IP rotation and password spraying.
_FAILS: dict[str, deque] = defaultdict(deque)

MAX_FAILS = 5
WINDOW = 300
IP_MAX_FAILS = 20

# Match the expensive password-verification path for unknown email addresses.
# The dummy secret is generated per process and is never associated with an account.
DUMMY_LOGIN_PASSWORD_HASH = hash_password(secrets.token_urlsafe(32))


def _persistent_rate_limits_enabled() -> bool:
    return APP_ENV == "production" or os.getenv("AUTH_RATE_LIMIT_BACKEND", "").strip().lower() == "postgres"


def _rate_limit_digest(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def _rate_limit_rpc(name: str, key: str, max_attempts: int = MAX_FAILS, window_seconds: int = WINDOW):
    return supabase.rpc(name, {
        "p_bucket_key": _rate_limit_digest(key),
        "p_max_attempts": max_attempts,
        "p_window_seconds": window_seconds,
    }).execute()


def _limited(key: str, max_attempts: int = MAX_FAILS, window_seconds: int = WINDOW) -> bool:
    if _persistent_rate_limits_enabled():
        try:
            response = _rate_limit_rpc("check_auth_rate_limit", key, max_attempts, window_seconds)
            data = getattr(response, "data", False)
            if isinstance(data, bool):
                return data
            if isinstance(data, list) and data:
                row = data[0]
                if isinstance(row, dict):
                    return bool(row.get("check_auth_rate_limit", row.get("limited", False)))
            if isinstance(data, dict):
                return bool(data.get("check_auth_rate_limit", data.get("limited", False)))
            return True
        except Exception as exc:
            print(f"Persistent auth rate-limit check failed: {type(exc).__name__}")
            return True
    queue = _FAILS[key]
    cutoff = time.time() - window_seconds
    while queue and queue[0] < cutoff:
        queue.popleft()
    if not queue:
        _FAILS.pop(key, None)
        return False
    return len(queue) >= max_attempts


def _record_failure(key: str, max_attempts: int = MAX_FAILS, window_seconds: int = WINDOW):
    if _persistent_rate_limits_enabled():
        try:
            _rate_limit_rpc("record_auth_rate_failure", key, max_attempts, window_seconds)
            return
        except Exception as exc:
            print(f"Persistent auth rate-limit record failed: {type(exc).__name__}")
            raise RuntimeError("Persistent authentication rate limiting is unavailable.") from exc
    _FAILS[key].append(time.time())


def _login_rate_keys(email: str, request: Request) -> tuple[str, str, str]:
    client_ip = _get_client_ip(request) or "unknown"
    return (
        f"login-account:{email}",
        f"login-account-ip:{email}:{client_ip}",
        f"login-ip:{client_ip}",
    )


def _login_is_limited(keys: tuple[str, str, str]) -> bool:
    account_key, account_ip_key, ip_key = keys
    return (
        _limited(account_key)
        or _limited(account_ip_key)
        or _limited(ip_key, max_attempts=IP_MAX_FAILS)
    )


def _record_login_failure(keys: tuple[str, str, str]) -> None:
    account_key, account_ip_key, ip_key = keys
    _record_failure(account_key)
    _record_failure(account_ip_key)
    _record_failure(ip_key, max_attempts=IP_MAX_FAILS)


def _clear_login_failures(keys: tuple[str, str, str]) -> None:
    account_key, account_ip_key, _ip_key = keys
    _clear_failures(account_key)
    _clear_failures(account_ip_key)


def _clear_failures(key: str):
    if _persistent_rate_limits_enabled():
        try:
            supabase.rpc("clear_auth_rate_limit", {
                "p_bucket_key": _rate_limit_digest(key),
            }).execute()
        except Exception as exc:
            print(f"Persistent auth rate-limit clear failed: {type(exc).__name__}")
        return
    _FAILS.pop(key, None)


# ---------------------------------------------------------------------------
# DATE HELPERS
# ---------------------------------------------------------------------------

def _parse_datetime(
    value,
) -> Optional[datetime]:

    """
    Converts a Supabase/PostgreSQL timestamp into an aware datetime.
    """

    if not value:
        return None

    if isinstance(
        value,
        datetime,
    ):

        dt = value

    else:

        try:

            text = str(
                value
            ).strip()

            if text.endswith("Z"):

                text = (
                    text[:-1]
                    + "+00:00"
                )

            dt = datetime.fromisoformat(
                text
            )

        except (
            ValueError,
            TypeError,
        ):

            return None

    if dt.tzinfo is None:

        dt = dt.replace(
            tzinfo=timezone.utc
        )

    return dt.astimezone(
        timezone.utc
    )


def _iso(
    value,
) -> Optional[str]:

    dt = _parse_datetime(
        value
    )

    if not dt:
        return None

    return dt.isoformat()


# ---------------------------------------------------------------------------
# EMAIL CONFIGURATION — GMAIL API (HTTPS)
# ---------------------------------------------------------------------------

GMAIL_OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_API_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"

GMAIL_OAUTH_CLIENT_ID = os.getenv("GMAIL_OAUTH_CLIENT_ID", "").strip()
GMAIL_OAUTH_CLIENT_SECRET = os.getenv("GMAIL_OAUTH_CLIENT_SECRET", "").strip()
GMAIL_OAUTH_REFRESH_TOKEN = os.getenv("GMAIL_OAUTH_REFRESH_TOKEN", "").strip()
GMAIL_USER_EMAIL = os.getenv("GMAIL_USER_EMAIL", "").strip()
GMAIL_FROM_EMAIL = os.getenv("GMAIL_FROM_EMAIL", "").strip() or GMAIL_USER_EMAIL
GMAIL_FROM_NAME = os.getenv("GMAIL_FROM_NAME", "Learnora Me").strip()


def _gmail_api_configured() -> bool:
    return bool(
        GMAIL_OAUTH_CLIENT_ID
        and GMAIL_OAUTH_CLIENT_SECRET
        and GMAIL_OAUTH_REFRESH_TOKEN
        and GMAIL_USER_EMAIL
        and GMAIL_FROM_EMAIL
    )


def _email_configured() -> bool:
    return _gmail_api_configured()


def _send_email(
    *,
    recipient: str,
    subject: str,
    text_body: str,
    html_body: str,
):
    """Send one MIME email through Gmail API using a server-side OAuth refresh token."""

    if not _email_configured():
        if APP_ENV == "development":
            print("EMAIL DEV MODE")
            print(f"To: {recipient}")
            print(f"Subject: {subject}")
            print(text_body)
            return
        raise RuntimeError("Gmail API email service is not configured.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = (
        f"{GMAIL_FROM_NAME} <{GMAIL_FROM_EMAIL}>"
        if GMAIL_FROM_NAME
        else GMAIL_FROM_EMAIL
    )
    message["To"] = recipient
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")

    try:
        with httpx.Client(timeout=httpx.Timeout(25.0, connect=10.0)) as client:
            token_response = client.post(
                GMAIL_OAUTH_TOKEN_URL,
                data={
                    "client_id": GMAIL_OAUTH_CLIENT_ID,
                    "client_secret": GMAIL_OAUTH_CLIENT_SECRET,
                    "refresh_token": GMAIL_OAUTH_REFRESH_TOKEN,
                    "grant_type": "refresh_token",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if not token_response.is_success:
                print(f"Gmail OAuth token refresh failed: HTTP {token_response.status_code}")
                raise RuntimeError("Unable to authorise Gmail API email delivery.")

            token_data = token_response.json()
            access_token = (
                token_data.get("access_token")
                if isinstance(token_data, dict)
                else None
            )
            if not isinstance(access_token, str) or not access_token:
                print("Gmail OAuth token refresh returned no access token.")
                raise RuntimeError("Unable to authorise Gmail API email delivery.")

            send_response = client.post(
                GMAIL_API_SEND_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json={"raw": raw_message},
            )
            if not send_response.is_success:
                # Do not automatically retry: the provider may have accepted a
                # request even when the response was lost, and retries can duplicate mail.
                print(f"Gmail API message send failed: HTTP {send_response.status_code}")
                raise RuntimeError("Unable to send email.")
    except httpx.RequestError as exc:
        print(f"Gmail API request failed: {type(exc).__name__}")
        raise RuntimeError("Unable to connect to Gmail API.") from exc
    except (ValueError, TypeError) as exc:
        print(f"Gmail API response could not be parsed: {type(exc).__name__}")
        raise RuntimeError("Unable to process Gmail API response.") from exc


# ---------------------------------------------------------------------------
# VERIFICATION EMAIL
# ---------------------------------------------------------------------------

def _build_verification_url(
    token: str,
) -> str:

    return (
        f"{FRONTEND_URL}"
        f"{EMAIL_VERIFICATION_PATH}"
        f"#token={token}"
    )


def _send_verification_email(
    *,
    email: str,
    name: Optional[str],
    token: str,
):

    verification_url = (
        _build_verification_url(
            token
        )
    )

    display_name = (
        name
        or "there"
    )

    subject = (
        "Verify your Learnora Me account"
    )

    text_body = f"""
Hi {display_name},

Welcome to Learnora Me.

Please verify your email address by opening the link below:

{verification_url}

This verification link expires in {EMAIL_VERIFICATION_TTL_MINUTES} minutes.

{ 'You can use Learnora for free after verification; no payment method or trial expiry is required.' if free_access_mode_enabled() else 'Once your email is verified, your 7-day free trial will begin.' }

If you did not create a Learnora Me account, you can ignore this email.

Learnora Me
""".strip()

    html_body = f"""
<!doctype html>
<html>
<body style="margin:0;background:#f8fafc;font-family:Arial,sans-serif;color:#111827;">
  <div style="max-width:600px;margin:40px auto;padding:32px;background:#ffffff;border-radius:20px;border:1px solid #e5e7eb;">

    <h1 style="margin:0 0 16px;color:#111827;">
      Welcome to Learnora Me
    </h1>

    <p style="line-height:1.7;">
      Hi {display_name},
    </p>

    <p style="line-height:1.7;">
      Please verify your email address to activate your Learnora Me account.
    </p>

    <p style="margin:28px 0;">
      <a
        href="{verification_url}"
        style="display:inline-block;background:#111827;color:#ffffff;text-decoration:none;padding:14px 22px;border-radius:10px;font-weight:bold;"
      >
        Verify Email Address
      </a>
    </p>

    <p style="font-size:13px;color:#64748b;line-height:1.6;">
      This link expires in {EMAIL_VERIFICATION_TTL_MINUTES} minutes.
      { 'Free Learnora access begins after successful verification. No payment method or trial expiry is required.' if free_access_mode_enabled() else 'Your 7-day free trial begins after successful verification.' }
    </p>

    <p style="font-size:13px;color:#94a3b8;line-height:1.6;">
      If you did not create a Learnora Me account, you can safely ignore this email.
    </p>

  </div>
</body>
</html>
""".strip()

    _send_email(
        recipient=email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )


# ---------------------------------------------------------------------------
# PASSWORD RESET EMAIL
# ---------------------------------------------------------------------------

def _build_password_reset_url(
    token: str,
) -> str:

    return (
        f"{FRONTEND_URL}"
        f"{PASSWORD_RESET_PATH}"
        f"#token={token}"
    )


def _send_password_reset_email(
    *,
    email: str,
    name: Optional[str],
    token: str,
):

    reset_url = (
        _build_password_reset_url(
            token
        )
    )

    display_name = (
        name
        or "there"
    )

    subject = (
        "Reset your Learnora Me password"
    )

    text_body = f"""
Hi {display_name},

We received a request to reset your Learnora Me password.

Use the link below to choose a new password:

{reset_url}

This password reset link expires in {PASSWORD_RESET_TTL_MINUTES} minutes.

If you did not request a password reset, you can safely ignore this email.

Learnora Me
""".strip()

    html_body = f"""
<!doctype html>
<html>
<body style="margin:0;background:#f8fafc;font-family:Arial,sans-serif;color:#111827;">
  <div style="max-width:600px;margin:40px auto;padding:32px;background:#ffffff;border-radius:20px;border:1px solid #e5e7eb;">

    <h1 style="margin:0 0 16px;color:#111827;">
      Reset your password
    </h1>

    <p style="line-height:1.7;">
      Hi {display_name},
    </p>

    <p style="line-height:1.7;">
      We received a request to reset your Learnora Me password.
    </p>

    <p style="margin:28px 0;">
      <a
        href="{reset_url}"
        style="display:inline-block;background:#111827;color:#ffffff;text-decoration:none;padding:14px 22px;border-radius:10px;font-weight:bold;"
      >
        Reset Password
      </a>
    </p>

    <p style="font-size:13px;color:#64748b;line-height:1.6;">
      This link expires in {PASSWORD_RESET_TTL_MINUTES} minutes.
    </p>

    <p style="font-size:13px;color:#94a3b8;line-height:1.6;">
      If you did not request this, you can safely ignore this email.
    </p>

  </div>
</body>
</html>
""".strip()

    _send_email(
        recipient=email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

def make_token(
    email: str,
    role: str,
    account_type: str,
) -> str:

    # Keep sub-second precision so a password change invalidates every
    # previously issued token, including one created in the same second.
    now = time.time()

    return jwt.encode(
        {
            "sub": email,
            "email": email,
            "role": role,
            "account_type": account_type,
            "iat": now,
            "exp": (
                now
                + TOKEN_TTL
            ),
        },
        JWT_SECRET,
        algorithm=ALGORITHM,
    )




def _assert_session_not_before_password_change(payload: dict, account: dict) -> None:
    changed_at = account.get("password_changed_at")
    issued_at = payload.get("iat")
    if not changed_at:
        return  # The session-revocation migration has not been applied yet.
    if issued_at is None:
        raise HTTPException(status_code=401, detail="Session could not be validated. Please sign in again.")
    try:
        changed_ts = datetime.fromisoformat(str(changed_at).replace("Z", "+00:00")).timestamp()
        if float(issued_at) < changed_ts:
            raise HTTPException(status_code=401, detail="Session expired after a password change. Please sign in again.")
    except (TypeError, ValueError, OverflowError):
        raise HTTPException(status_code=401, detail="Session could not be validated. Please sign in again.")


def _legacy_password_login_allowed(stored_hash: str) -> bool:
    if stored_hash.startswith("$2"):
        return True
    raw_deadline = os.getenv("LEGACY_SHA256_LOGIN_DEADLINE", "2027-01-01T00:00:00Z").strip()
    try:
        deadline = datetime.fromisoformat(raw_deadline.replace("Z", "+00:00"))
    except ValueError:
        log.error("LEGACY_SHA256_LOGIN_DEADLINE is invalid")
        return False
    return datetime.now(timezone.utc) < deadline

# ---------------------------------------------------------------------------
# ACCOUNT PERMISSIONS
# ---------------------------------------------------------------------------

def allowed_for(
    role: str,
    account_type: str,
) -> dict:

    if account_type == "admin":

        if role == "super_admin":

            return {
                "courses": 85,
                "tracks": ["all"],
                "is_admin": True,
                "admin_role": role,
                "redirect_view": (
                    "/dashboard/admin/super_admin"
                ),
                "permissions": [
                    "manage_all_learners",
                    "manage_admins",
                    "grant_free_month",
                    "view_activity",
                    "view_traffic",
                    "view_security_logs",
                ],
            }

        if role == "staff_admin":

            return {
                "courses": 85,
                "tracks": ["Learnora"],
                "is_admin": True,
                "admin_role": role,
                "redirect_view": (
                    "/dashboard/admin/staff_admin"
                ),
                "permissions": [
                    "manage_normal_learners",
                    "view_learnora_activity",
                ],
            }

    if role == LEGACY_ASSIGNED_LEARNER_ROLE:
        return {
            "courses": 12,
            "tracks": ["assigned"],
            "is_admin": False,
            "redirect_view": "/dashboard",
        }

    return {
        "courses": 85,
        "tracks": ["all"],
        "is_admin": False,
        "redirect_view": (
            "/dashboard/general"
        ),
    }


# ---------------------------------------------------------------------------
# CURRENT USER
# ---------------------------------------------------------------------------

class CurrentUser(BaseModel):

    id: Optional[str] = None
    name: Optional[str] = None
    email: str
    role: str
    sub_status: str
    account_type: str
    is_paid: bool = False
    marketing_email_opt_in: bool = False
    marketing_in_app_opt_in: bool = False

    expires_at: Optional[str] = None
    trial_ends_at: Optional[str] = None

    access_state: str = "expired"
    course_access: bool = False
    organisation_id: Optional[str] = None
    organisation_role: Optional[str] = None
    cohort_id: Optional[str] = None
    track_id: Optional[str] = None
    username: Optional[str] = None


# ---------------------------------------------------------------------------
# AUDIT LOGGING
# ---------------------------------------------------------------------------

def _get_client_ip(
    request: Optional[Request],
) -> Optional[str]:
    """Use Vercel's edge-normalised client IP, never a client-supplied XFF entry.

    Vercel supplies X-Real-IP at the edge. X-Forwarded-For may contain a
    client-provided prefix, so taking its leftmost value permits rate-limit
    bucket spoofing when an intermediary appends rather than overwrites it.
    """
    if not request:
        return None

    candidates = []
    # Only trust X-Real-IP when running behind Vercel's managed edge, which
    # normalises this header. In local/other deployments, clients can supply
    # arbitrary X-Real-IP headers, so use the ASGI peer address instead.
    if os.getenv("VERCEL", "").strip() == "1":
        candidates.append(request.headers.get("x-real-ip"))
    if request.client:
        candidates.append(request.client.host)

    for candidate in candidates:
        if not candidate:
            continue
        try:
            return str(ipaddress.ip_address(candidate.strip()))
        except ValueError:
            continue
    return None


def log_audit_event(
    *,
    action: str,
    email: Optional[str] = None,
    account_type: Optional[str] = None,
    role: Optional[str] = None,
    request: Optional[Request] = None,
    metadata: Optional[dict] = None,
):

    try:

        row = {
            "action": action,
            "email": email,
            "account_type": account_type,
            "role": role,
            "ip": _get_client_ip(
                request
            ),
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        if metadata is not None:
            row["metadata"] = metadata

        supabase.table(
            "audit_logs"
        ).insert(row).execute()

    except Exception as exc:

        print(
            f"Audit logging failed: {exc}"
        )


def log_security_event(
    *,
    action: str,
    email: Optional[str] = None,
    request: Optional[Request] = None,
    metadata: Optional[dict] = None,
):
    """
    Record a security event in public.security_logs.

    The security_logs table contains:
        id
        event_type
        ip_address
        details
        created_at
        action
        email
        ip
        metadata

    Security logging must never interrupt the authentication flow.
    """

    try:
        client_ip = _get_client_ip(request)

        row = {
            "event_type": action,
            "ip_address": client_ip,
            "action": action,
            "email": email,
            "ip": client_ip,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        if metadata is not None:
            row["metadata"] = metadata

        supabase.table(
            "security_logs"
        ).insert(row).execute()

    except Exception as exc:
        print(
            f"Security logging failed: {exc}"
        )

# ---------------------------------------------------------------------------
# FIND ACCOUNT
# ---------------------------------------------------------------------------

def _execute_supabase_read_with_retry(query, operation: str):
    """Retry a read once/twice when the pooled HTTP connection is dropped.

    The production traces show intermittent httpx RemoteProtocolError failures
    while PostgREST is serving authentication lookups. These are transport
    failures, not query errors, so retrying the idempotent SELECT is safe.
    """
    for attempt in range(3):
        try:
            return query.execute()
        except httpx.TransportError as exc:
            if attempt == 2:
                print(f"{operation} failed after transient connection retries: {type(exc).__name__}")
                raise HTTPException(
                    status_code=503,
                    detail=f"{operation} is temporarily unavailable. Please try again.",
                ) from None
            time.sleep(0.15 * (attempt + 1))



def _find_admin(
    email: str,
):

    query = (
        supabase
        .table("admins")
        .select(
            "id, email, name, password_hash, role, "
            "is_active, last_login_at, password_changed_at"
        )
        .ilike(
            "email",
            _escape_ilike_literal(email),
        )
        .limit(2)
    )
    response = _execute_supabase_read_with_retry(query, "Admin identity lookup")

    rows = response.data or []
    if len(rows) > 1:
        log_security_event(
            action="duplicate_admin_email_identity",
            email=email,
            metadata={"account_table": "admins", "matched_rows": len(rows)},
        )
        raise HTTPException(
            status_code=409,
            detail="This email has multiple administrator records. Contact Learnora support before signing in.",
        )

    return rows[0] if rows else None


def _find_user(
    email: str,
):

    query = (
        supabase
        .table("users")
        .select(
            "id, name, email, password_hash, role, "
            "sub_status, is_paid, subscription_tier, "
            "expires_at, trial_ends_at, email_verified_at, "
            "account_status, account_deactivation_until, marketing_email_opt_in, "
            "marketing_in_app_opt_in, password_changed_at"
        )
        .ilike(
            "email",
            _escape_ilike_literal(email),
        )
        .limit(2)
    )
    response = _execute_supabase_read_with_retry(query, "Learner identity lookup")

    rows = response.data or []
    if len(rows) > 1:
        log_security_event(
            action="duplicate_individual_email_identity",
            email=email,
            metadata={"account_table": "users", "matched_rows": len(rows)},
        )
        raise HTTPException(
            status_code=409,
            detail="This email has multiple learner account records. Contact Learnora support before continuing.",
        )

    return rows[0] if rows else None


# ---------------------------------------------------------------------------
def _find_cohort_accounts_by_email(email: str) -> list[dict]:
    """Find every reserved organisation/cohort identity for a canonical email.

    Cohort accounts are still stored separately for compatibility. This guard
    prevents the public individual registration/login path from treating an
    existing organisation identity as an available individual email.
    """
    try:
        query = (
            supabase.table("cohort_accounts")
            .select("id,cohort_id,organisation_id,status")
            .ilike("email", _escape_ilike_literal(email))
            .limit(10)
        )
        response = _execute_supabase_read_with_retry(query, "Reserved account lookup")
    except Exception as exc:
        print(f"Reserved account lookup failed: {type(exc).__name__}")
        raise HTTPException(
            status_code=503,
            detail="Account availability could not be verified. Please try again.",
        ) from None
    return response.data or []


# LEARNER ENTITLEMENT
# ---------------------------------------------------------------------------

def _resolve_learner_access(
    user: dict,
    organisation_id: str | None = None,
) -> dict:

    now = datetime.now(
        timezone.utc
    )

    # Free launch is a server-side access policy, not a rewrite of billing
    # history. Do not mutate paid/trial rows while the mode is enabled.
    if (
        free_access_mode_enabled()
        and is_individual_learner(user.get("role"), "learner", organisation_id)
        and user.get("email_verified_at")
        and str(user.get("sub_status") or "").lower()
        in {"trialing", "active", "expired", "cancelled", "free"}
    ):
        return {
            "sub_status": user.get("sub_status") or "expired",
            "is_paid": False,
            "access_state": "free",
            "course_access": True,
            "trial_ends_at": user.get("trial_ends_at"),
            "expires_at": user.get("expires_at"),
        }

    sub_status = (
        user.get("sub_status")
        or "pending"
    )

    is_paid = bool(
        user.get("is_paid")
    )

    trial_ends = _parse_datetime(
        user.get(
            "trial_ends_at"
        )
    )

    expires_at = _parse_datetime(
        user.get(
            "expires_at"
        )
    )

    # ---------------------------------------------------------------
    # PAID MEMBERSHIP
    # ---------------------------------------------------------------

    if is_paid:

        if (
            expires_at
            and expires_at <= now
        ):

            try:

                supabase.table(
                    "users"
                ).update(
                    {
                        "is_paid": False,
                        "subscription_tier": "free",
                        "sub_status": "expired",
                    }
                ).eq(
                    "id",
                    user["id"],
                ).execute()

            except Exception as exc:

                print(
                    "Failed to expire "
                    f"paid membership: {exc}"
                )

            return {
                "sub_status": "expired",
                "is_paid": False,
                "access_state": "expired",
                "course_access": False,
                "trial_ends_at": _iso(
                    trial_ends
                ),
                "expires_at": _iso(
                    expires_at
                ),
            }

        return {
            "sub_status": "active",
            "is_paid": True,
            "access_state": "pro",
            "course_access": True,
            "trial_ends_at": _iso(
                trial_ends
            ),
            "expires_at": _iso(
                expires_at
            ),
        }

    # ---------------------------------------------------------------
    # FREE TRIAL
    # ---------------------------------------------------------------

    if sub_status == "trialing":

        if (
            trial_ends
            and trial_ends > now
        ):

            return {
                "sub_status": "trialing",
                "is_paid": False,
                "access_state": "trial",
                "course_access": True,
                "trial_ends_at": _iso(
                    trial_ends
                ),
                "expires_at": _iso(
                    expires_at
                ),
            }

        try:

            supabase.table(
                "users"
            ).update(
                {
                    "is_paid": False,
                    "subscription_tier": "free",
                    "sub_status": "expired",
                }
            ).eq(
                "id",
                user["id"],
            ).execute()

        except Exception as exc:

            print(
                f"Failed to expire trial: {exc}"
            )

        return {
            "sub_status": "expired",
            "is_paid": False,
            "access_state": "expired",
            "course_access": False,
            "trial_ends_at": _iso(
                trial_ends
            ),
            "expires_at": _iso(
                expires_at
            ),
        }

    # ---------------------------------------------------------------
    # PENDING / EXPIRED / FREE
    # ---------------------------------------------------------------

    return {
        "sub_status": sub_status,
        "is_paid": False,
        "access_state": (
            "pending"
            if sub_status == "pending"
            else "expired"
        ),
        "course_access": False,
        "trial_ends_at": _iso(
            trial_ends
        ),
        "expires_at": _iso(
            expires_at
        ),
    }


# ---------------------------------------------------------------------------
# AUTH DEPENDENCY
# ---------------------------------------------------------------------------

def get_optional_current_user(
    creds: Optional[
        HTTPAuthorizationCredentials
    ] = Depends(bearer),
    request: Request = None,
) -> Optional[CurrentUser]:
    """Resolve a session when one is present, while allowing anonymous discovery."""
    if not _request_auth_token(request, creds):
        return None
    try:
        return get_current_user(creds, request)
    except HTTPException as exc:
        # Public catalogue pages remain browseable after a stale/expired
        # browser session. Valid managed sessions are still explicitly denied
        # by the public discovery guard; account conflicts and service errors
        # are not silently downgraded to anonymous access.
        if exc.status_code == 401:
            return None
        raise


def get_current_user(
    creds: Optional[
        HTTPAuthorizationCredentials
    ] = Depends(bearer),
    request: Request = None,
) -> CurrentUser:

    token_value = _request_auth_token(request, creds)
    if not token_value:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    try:

        payload = jwt.decode(
            token_value,
            JWT_SECRET,
            algorithms=[ALGORITHM],
        )

    except InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    # Existing cohort accounts remain a separate compatibility source until the
    # identity migration is implemented. The email guards below ensure a
    # cohort credential cannot coexist with an individual/admin identity or
    # another cohort credential for the same canonical email.
    if payload.get("account_type") == "cohort":
        cohort_account_id = str(payload.get("cohort_account_id") or payload.get("sub") or "")
        if not cohort_account_id:
            raise HTTPException(status_code=401, detail="Invalid cohort token")
        account_result = (
            supabase.table("cohort_accounts")
            .select("id,cohort_id,organisation_id,email,username,first_name,last_name,status")
            .eq("id", cohort_account_id)
            .limit(1)
            .execute()
        )
        if not account_result.data or account_result.data[0].get("status") != "active":
            raise HTTPException(status_code=403, detail="Cohort account is inactive")
        cohort_account = account_result.data[0]
        cohort_email = norm_email(str(cohort_account.get("email") or ""))
        email_accounts = _find_cohort_accounts_by_email(cohort_email)
        if (
            len(email_accounts) != 1
            or str(email_accounts[0].get("id")) != cohort_account_id
            or _find_user(cohort_email)
            or _find_admin(cohort_email)
        ):
            log_security_event(
                action="conflicting_email_account_contexts",
                email=cohort_email,
                metadata={
                    "account_type": "cohort",
                    "cohort_account_id": cohort_account_id,
                    "cohort_account_count": len(email_accounts),
                },
            )
            raise HTTPException(
                status_code=409,
                detail="This email has conflicting account records. Contact Learnora support before continuing.",
            )
        membership_result = (
            supabase.table("cohort_members")
            .select("id,track_id,status")
            .eq("cohort_id", cohort_account["cohort_id"])
            .eq("cohort_account_id", cohort_account_id)
            .eq("status", "active")
            .limit(1)
            .execute()
        )
        if not membership_result.data:
            raise HTTPException(status_code=403, detail="Cohort membership is inactive")
        cohort_result = (
            supabase.table("cohorts")
            .select("status")
            .eq("id", cohort_account["cohort_id"])
            .limit(1)
            .execute()
        )
        if not cohort_result.data or cohort_result.data[0].get("status") not in {"draft", "upcoming", "active"}:
            raise HTTPException(status_code=403, detail="Cohort is closed")
        cohort_status = cohort_result.data[0]["status"]
        member = membership_result.data[0]
        return CurrentUser(
            id=cohort_account_id,
            name=f"{cohort_account.get('first_name', '')} {cohort_account.get('last_name', '')}".strip(),
            email=cohort_account["email"],
            role="cohort_learner",
            sub_status="active",
            account_type="cohort",
            is_paid=False,
            access_state="cohort",
            course_access=cohort_status == "active",
            organisation_id=str(cohort_account["organisation_id"]),
            cohort_id=str(cohort_account["cohort_id"]),
            track_id=str(member["track_id"]) if member.get("track_id") else None,
            username=cohort_account.get("username"),
        )

    email = (
        payload.get("email")
        or payload.get("sub")
        or ""
    ).lower().strip()

    if not email:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    token_role = payload.get(
        "role"
    )

    token_account_type = payload.get(
        "account_type"
    )

    cohort_accounts = _find_cohort_accounts_by_email(email)
    admin = _find_admin(email)
    user = _find_user(email)
    if (admin and user) or (cohort_accounts and (admin or user)):
        log_security_event(
            action="conflicting_email_account_contexts",
            email=email,
            metadata={
                "has_admin": bool(admin),
                "has_individual_user": bool(user),
                "cohort_account_count": len(cohort_accounts),
            },
        )
        raise HTTPException(
            status_code=409,
            detail="This email has conflicting account records. Contact Learnora support before continuing.",
        )

    # ---------------------------------------------------------------
    # ADMIN ACCOUNT
    # ---------------------------------------------------------------

    if admin:
        _assert_session_not_before_password_change(payload, admin)

        if not admin.get(
            "is_active",
            False,
        ):

            raise HTTPException(
                status_code=403,
                detail=(
                    "Administrator account is disabled"
                ),
            )

        role = admin.get(
            "role"
        )

        if role not in ADMIN_ROLES:

            raise HTTPException(
                status_code=403,
                detail=(
                    "Invalid administrator role"
                ),
            )

        if (
            token_role
            and token_role != role
        ):

            raise HTTPException(
                status_code=401,
                detail=(
                    "Invalid authentication token"
                ),
            )

        if (
            token_account_type
            and token_account_type != "admin"
        ):

            raise HTTPException(
                status_code=401,
                detail=(
                    "Invalid authentication token"
                ),
            )

        return CurrentUser(
            id=(
                str(admin["id"])
                if admin.get("id") is not None
                else None
            ),
            name=(
                str(
                    admin.get("name")
                ).strip()
                if admin.get("name")
                else None
            ),
            email=(
                admin.get("email")
                or email
            ).lower().strip(),
            role=role,
            sub_status="active",
            account_type="admin",
            is_paid=True,
            access_state="admin",
            course_access=True,
        )

    # ---------------------------------------------------------------
    # LEARNER ACCOUNT
    # ---------------------------------------------------------------

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User account not found",
        )
    _assert_session_not_before_password_change(payload, user)

    if user.get("account_status") == "deactivation_pending":
        raise HTTPException(
            status_code=403,
            detail="This account is deactivated and scheduled for deletion. Reactivate it using the link sent to your email.",
        )

    role = (
        user.get("role")
        or "normal"
    )

    if role not in LEARNER_ROLES:

        raise HTTPException(
            status_code=403,
            detail=(
                "Invalid learner role"
            ),
        )

    if (
        token_role
        and token_role != role
    ):

        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid authentication token"
            ),
        )

    if (
        token_account_type
        and token_account_type != "learner"
    ):

        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid authentication token"
            ),
        )

    # ---------------------------------------------------------------
    # EMAIL VERIFICATION CHECK
    # ---------------------------------------------------------------

    if (
        user.get("sub_status")
        == "pending"
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Please verify your email address "
                "before accessing Learnora."
            ),
        )

    organisation_id, organisation_role = (
        _active_organisation_context(str(user["id"]), fail_closed=role in {"normal", LEGACY_ASSIGNED_LEARNER_ROLE})
        if role != "organisation_prospect"
        else (None, None)
    )
    entitlement = _resolve_learner_access(user, organisation_id)
    if role == "organisation_prospect":
        entitlement = {
            **entitlement,
            "is_paid": False,
            "access_state": "prospect",
            "course_access": False,
        }

    return CurrentUser(
        id=(
            str(user["id"])
            if user.get("id") is not None
            else None
        ),
        name=(
            str(
                user.get("name")
            ).strip()
            if user.get("name")
            else None
        ),
        email=(
            user.get("email")
            or email
        ).lower().strip(),
        role=role,
        sub_status=(
            entitlement["sub_status"]
        ),
        account_type="learner",
        is_paid=(
            entitlement["is_paid"]
        ),
        marketing_email_opt_in=bool(user.get("marketing_email_opt_in")),
        marketing_in_app_opt_in=bool(user.get("marketing_in_app_opt_in")),
        expires_at=(
            entitlement["expires_at"]
        ),
        trial_ends_at=(
            entitlement["trial_ends_at"]
        ),
        access_state=(
            entitlement["access_state"]
        ),
        course_access=(
            entitlement["course_access"]
        ),
        organisation_id=organisation_id,
        organisation_role=organisation_role,
    )




def _active_organisation_context(user_id: str, fail_closed: bool = False) -> tuple[str | None, str | None]:
    """Resolve the single retained organisation boundary for an account.

    Membership records reserve an account context even when a cohort has ended
    or a membership is suspended. Suspension removes learning access; it does
    not silently convert an organisation account into an individual account.
    """
    try:
        memberships_query = (
            supabase.table("organisation_members")
            .select("organisation_id,role")
            .eq("user_id", user_id)
            .order("joined_at", desc=True)
        )
        memberships = _execute_supabase_read_with_retry(
            memberships_query, "Organisation membership lookup"
        ).data or []

        contexts: list[tuple[str, str]] = []
        for membership in memberships:
            organisation_id = str(membership.get("organisation_id") or "")
            if organisation_id:
                contexts.append((organisation_id, str(membership.get("role") or "")))

        # Legacy organisation learners may be represented only by a
        # public.users + cohort_members relationship. Any retained cohort
        # membership continues to reserve the organisation account context;
        # cohort status controls learning access, not identity ownership.
        cohort_memberships_query = (
            supabase.table("cohort_members")
            .select("cohort_id")
            .eq("user_id", user_id)
            .limit(1000)
        )
        cohort_memberships = _execute_supabase_read_with_retry(
            cohort_memberships_query, "Cohort identity lookup"
        ).data or []
        cohort_ids = list({
            str(row["cohort_id"])
            for row in cohort_memberships
            if row.get("cohort_id")
        })
        if cohort_ids:
            cohorts_query = (
                supabase.table("cohorts")
                .select("id,organisation_id")
                .in_("id", cohort_ids)
            )
            cohorts = _execute_supabase_read_with_retry(
                cohorts_query, "Cohort organisation lookup"
            ).data or []
            resolved_cohort_ids = set()
            for cohort in cohorts:
                organisation_id = str(cohort.get("organisation_id") or "")
                cohort_id = str(cohort.get("id") or "")
                if organisation_id:
                    contexts.append((organisation_id, "learner"))
                    resolved_cohort_ids.add(cohort_id)
            unresolved_cohort_ids = set(cohort_ids) - resolved_cohort_ids
            if unresolved_cohort_ids:
                log_security_event(
                    action="unresolved_cohort_identity_context",
                    metadata={
                        "user_id": user_id,
                        "unresolved_cohort_count": len(unresolved_cohort_ids),
                    },
                )
                if fail_closed:
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            "This account has an unresolved organisation-managed cohort record. "
                            "Contact Learnora support before continuing."
                        ),
                    )
                return None, None

        organisation_ids = {item[0] for item in contexts}
        if len(organisation_ids) > 1:
            log_security_event(
                action="multiple_active_organisation_contexts",
                metadata={
                    "user_id": user_id,
                    "organisation_count": len(organisation_ids),
                },
            )
            if fail_closed:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "This account is linked to more than one organisation. "
                        "Contact Learnora support to resolve the account before continuing."
                    ),
                )
            return None, None

        if not organisation_ids:
            return None, None

        role_groups = {
            "learner" if role in {"learner", "member"}
            else "admin" if role in {"owner", "admin"}
            else role
            for _, role in contexts
            if role
        }
        if len(role_groups) > 1:
            log_security_event(
                action="multiple_active_organisation_roles",
                metadata={
                    "user_id": user_id,
                    "organisation_id": next(iter(organisation_ids)),
                    "role_groups": sorted(role_groups),
                },
            )
            if fail_closed:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "This account has conflicting organisation roles. "
                        "Contact Learnora support to resolve the account before continuing."
                    ),
                )
            return None, None

        organisation_id = next(iter(organisation_ids))
        membership_role = next(
            (role for oid, role in contexts if oid == organisation_id and role),
            None,
        )
        return organisation_id, membership_role or "learner"

    except HTTPException:
        raise
    except Exception as exc:
        if fail_closed:
            print(f"Organisation identity resolution failed: {type(exc).__name__}")
            raise HTTPException(
                status_code=503,
                detail="Your organisation access could not be verified. Please try again.",
            ) from None
        return None, None


# AUTHORIZATION DEPENDENCIES
# ---------------------------------------------------------------------------

def require_active(
    user: CurrentUser = Depends(
        get_current_user
    ),
) -> CurrentUser:

    if not user.course_access:

        raise HTTPException(
            status_code=402,
            detail=(
                "An active trial or paid "
                "membership is required"
            ),
        )

    return user


def require_admin(
    user: CurrentUser = Depends(
        get_current_user
    ),
) -> CurrentUser:

    if (
        user.account_type
        != "admin"
    ):

        raise HTTPException(
            status_code=403,
            detail="Administrators only",
        )

    if user.role not in ADMIN_ROLES:

        raise HTTPException(
            status_code=403,
            detail="Administrators only",
        )

    return user


def require_super_admin(
    user: CurrentUser = Depends(
        get_current_user
    ),
) -> CurrentUser:

    if (
        user.account_type != "admin"
        or user.role != "super_admin"
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Super administrator "
                "access required"
            ),
        )

    return user


def require_learnora_admin(
    user: CurrentUser = Depends(
        get_current_user
    ),
) -> CurrentUser:

    if (
        user.account_type
        != "admin"
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Administrator access "
                "required"
            ),
        )

    if user.role not in {
        "super_admin",
        "staff_admin",
    }:

        raise HTTPException(
            status_code=403,
            detail=(
                "Learnora administrator "
                "access required"
            ),
        )

    return user


# REQUEST MODELS
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    marketing_email_opt_in: bool = False


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: str


# ---------------------------------------------------------------------------
# LOGIN
# ---------------------------------------------------------------------------

@router.post("/login")
def login(
    payload: LoginRequest,
    request: Request,
    response: Response = None,
):

    email = norm_email(
        payload.email
    )

    rate_keys = _login_rate_keys(email, request)

    if _login_is_limited(rate_keys):

        log_security_event(
            action="login_rate_limited",
            email=email,
            request=request,
        )

        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Try again in five minutes.",
            headers={"Retry-After": str(WINDOW)},
        )

    # Resolve every legacy identity source before choosing an authentication
    # path. Never fall through from a failed account class to another one.
    cohort_accounts = _find_cohort_accounts_by_email(email)
    admin = _find_admin(email)
    user = _find_user(email)

    if (admin and user) or (cohort_accounts and (admin or user)):
        log_security_event(
            action="conflicting_email_account_contexts",
            email=email,
            request=request,
            metadata={
                "has_admin": bool(admin),
                "has_individual_user": bool(user),
                "cohort_account_count": len(cohort_accounts),
            },
        )
        verify_password(payload.password, DUMMY_LOGIN_PASSWORD_HASH)
        _record_login_failure(rate_keys)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if cohort_accounts and not admin and not user:
        # Organisation/cohort identities must not authenticate through the
        # public individual learner endpoint.
        verify_password(payload.password, DUMMY_LOGIN_PASSWORD_HASH)
        _record_login_failure(rate_keys)
        log_security_event(
            action="reserved_organisation_email_login_attempt",
            email=email,
            request=request,
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    # ---------------------------------------------------------------
    # ADMIN
    # ---------------------------------------------------------------

    if admin:
        valid, needs_rehash = verify_password(
            payload.password,
            admin.get("password_hash") or DUMMY_LOGIN_PASSWORD_HASH,
        )

        if not valid:

            _record_login_failure(rate_keys)

            log_security_event(
                action="failed_admin_login",
                email=email,
                request=request,
            )

            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        if not _legacy_password_login_allowed(str(admin.get("password_hash") or "")):
            raise HTTPException(403, "Your password needs to be reset before you can sign in. Use Forgot password to set a new password.")

        if not admin.get("is_active", False):

            _record_login_failure(rate_keys)

            log_security_event(
                action="disabled_admin_login_attempt",
                email=email,
                request=request,
            )

            raise HTTPException(
                status_code=403,
                detail="This administrator account is disabled.",
            )

        _clear_login_failures(rate_keys)

        role = admin["role"]

        if needs_rehash:

            try:

                supabase.table(
                    "admins"
                ).update(
                    {
                        "password_hash": hash_password(
                            payload.password
                        )
                    }
                ).eq(
                    "id",
                    admin["id"],
                ).execute()

            except Exception as exc:

                print(
                    "Admin password rehash "
                    f"failed: {exc}"
                )

        now = datetime.now(
            timezone.utc
        ).isoformat()

        try:

            supabase.table(
                "admins"
            ).update(
                {
                    "last_login_at": now,
                }
            ).eq(
                "id",
                admin["id"],
            ).execute()

        except Exception as exc:

            print(
                "Failed to update admin "
                f"last_login_at: {exc}"
            )

        token = make_token(
            email=email,
            role=role,
            account_type="admin",
        )

        log_audit_event(
            action="admin_login",
            email=email,
            account_type="admin",
            role=role,
            request=request,
        )

        return deliver_auth_token(request, response, token, {
            "status": "success",
            "token": token,
            "access_token": token,
            "email": email,
            "name": admin.get("name"),
            "role": role,
            "account_type": "admin",
            "sub_status": "active",
            "is_paid": True,
            "access_state": "admin",
            "course_access": True,
            "allowed": allowed_for(
                role,
                "admin",
            ),
        })

    # ---------------------------------------------------------------
    # LEARNER
    # ---------------------------------------------------------------

    if not user:

        # Match the bcrypt verification path for known accounts.
        verify_password(
            payload.password,
            DUMMY_LOGIN_PASSWORD_HASH,
        )

        _record_login_failure(rate_keys)

        log_security_event(
            action=(
                "failed_login_unknown_email"
            ),
            email=email,
            request=request,
        )

        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid email or password"
            ),
        )

    stored_password_hash = str(user.get("password_hash") or "")
    valid, needs_rehash = verify_password(payload.password, stored_password_hash)

    if not valid:

        _record_login_failure(rate_keys)

        log_security_event(
            action="failed_learner_login",
            email=email,
            request=request,
        )

        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid email or password"
            ),
        )

    if not _legacy_password_login_allowed(stored_password_hash):
        raise HTTPException(403, "Your password needs to be reset before you can sign in. Use Forgot password to set a new password.")

    if user.get("account_status") == "deactivation_pending":
        recovery_until = _parse_datetime(user.get("account_deactivation_until"))
        if recovery_until and recovery_until > datetime.now(timezone.utc):
            _clear_login_failures(rate_keys)
            raise HTTPException(
                status_code=403,
                detail="ACCOUNT_DEACTIVATED: This Learnora account is deactivated but can still be reactivated within its 30-day recovery period. Continue to the account reactivation page.",
            )
        _clear_login_failures(rate_keys)
        raise HTTPException(
            status_code=403,
            detail="This account's 30-day recovery period has ended and it is awaiting permanent closure.",
        )

    _clear_login_failures(rate_keys)

    role = (
        user.get("role")
        or "normal"
    )

    if role not in LEARNER_ROLES:

        raise HTTPException(
            status_code=403,
            detail=(
                "Invalid learner "
                "account role"
            ),
        )

    # ---------------------------------------------------------------
    # EMAIL VERIFICATION CHECK
    # ---------------------------------------------------------------

    if (
        user.get("sub_status")
        == "pending"
    ):

        log_security_event(
            action=(
                "login_unverified_account"
            ),
            email=email,
            request=request,
        )

        raise HTTPException(
            status_code=403,
            detail=(
                "Please verify your email address "
                "before logging in."
            ),
        )

    if needs_rehash:

        try:

            supabase.table(
                "users"
            ).update(
                {
                    "password_hash": hash_password(
                        payload.password
                    )
                }
            ).eq(
                "id",
                user["id"],
            ).execute()

        except Exception as exc:

            print(
                "Learner password rehash "
                f"failed: {exc}"
            )

    organisation_id, organisation_role = (
        _active_organisation_context(
            str(user["id"]),
            fail_closed=role in {"normal", LEGACY_ASSIGNED_LEARNER_ROLE},
        )
        if role != "organisation_prospect"
        else (None, None)
    )
    entitlement = _resolve_learner_access(user, organisation_id)
    if role == "organisation_prospect":
        entitlement = {
            **entitlement,
            "is_paid": False,
            "access_state": "prospect",
            "course_access": False,
        }

    token = make_token(
        email=email,
        role=role,
        account_type="learner",
    )

    log_audit_event(
        action="learner_login",
        email=email,
        account_type="learner",
        role=role,
        request=request,
    )

    return deliver_auth_token(request, response, token, {
        "status": "success",
        "token": token,
        "access_token": token,
        "email": email,
        "name": user.get("name"),
        "role": role,
        "account_type": "learner",
        "sub_status": (
            entitlement["sub_status"]
        ),
        "is_paid": (
            entitlement["is_paid"]
        ),
        "access_state": (
            entitlement["access_state"]
        ),
        "course_access": (
            entitlement["course_access"]
        ),
        "trial_ends_at": (
            entitlement["trial_ends_at"]
        ),
        "expires_at": (
            entitlement["expires_at"]
        ),
        "organisation_id": organisation_id,
        "organisation_role": organisation_role,
        "allowed": allowed_for(
            role,
            "learner",
        ),
    })


# ---------------------------------------------------------------------------


@router.post("/logout")
def logout(response: Response):
    clear_auth_cookie(response, AUTH_COOKIE_NAME)
    return {"success": True}


# REGISTER
# ---------------------------------------------------------------------------

@router.post(
    "/register",
    status_code=201,
)
def register(
    payload: RegisterRequest,
    request: Request,
):

    email = norm_email(
        payload.email
    )

    check_password_rules(
        payload.password
    )

    name = (
        (payload.name or "")
        .strip()[:100]
        or None
    )
    now = datetime.now(timezone.utc)

    # Keep registration responses indistinguishable for existing individual,
    # administrator and organisation-managed identities. Account recovery and
    # sign-in provide the appropriate next step without exposing email presence.
    generic_registration_response = {
        "status": "accepted",
        "message": (
            "If this email can be used for a Learnora account, verification "
            "instructions will be sent. If you already have an account, sign in "
            "or use password recovery."
        ),
    }

    existing_admin = _find_admin(email)
    reserved_cohort_accounts = _find_cohort_accounts_by_email(email)
    existing_user = _find_user(email)
    if existing_admin or reserved_cohort_accounts or existing_user:
        log_security_event(
            action="registration_for_existing_identity",
            email=email,
            request=request,
            metadata={
                "has_admin": bool(existing_admin),
                "has_individual_user": bool(existing_user),
                "cohort_account_count": len(reserved_cohort_accounts),
            },
        )
        return generic_registration_response

    # ---------------------------------------------------------------
    # CREATE PENDING ACCOUNT
    # ---------------------------------------------------------------

    row = {
        "email": email,
        "name": name,
        "password_hash": hash_password(
            payload.password
        ),
        "password_changed_at": now.isoformat(),
        "role": "normal",
        "sub_status": "pending",
        "is_paid": False,
        "subscription_tier": "free",
        "created_at": now.isoformat(),
        "email_verified_at": None,
        "marketing_email_opt_in": bool(payload.marketing_email_opt_in),
        "marketing_in_app_opt_in": False,
        "marketing_consent_at": now.isoformat() if payload.marketing_email_opt_in else None,
        "marketing_consent_source": "signup_form" if payload.marketing_email_opt_in else None,
        "marketing_unsubscribed_at": None,
    }

    try:

        response = (
            supabase
            .table("users")
            .insert(row)
            .execute()
        )

    except Exception as exc:

        print(
            f"Registration failed: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to create account"
            ),
        )

    if not response.data:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to create account"
            ),
        )

    created_user = response.data[0]

    # ---------------------------------------------------------------
    # CREATE VERIFICATION TOKEN
    # ---------------------------------------------------------------

    raw_token = (
        _generate_raw_token()
    )

    token_hash = _hash_token(
        raw_token
    )

    expires_at = (
        now
        + timedelta(
            minutes=EMAIL_VERIFICATION_TTL_MINUTES
        )
    )

    try:

        supabase.table(
            "email_verification_tokens"
        ).insert(
            {
                "user_id": created_user["id"],
                "email": email,
                "token_hash": token_hash,
                "expires_at": (
                    expires_at.isoformat()
                ),
                "used_at": None,
                "created_at": now.isoformat(),
            }
        ).execute()

    except Exception as exc:

        print(
            "Failed to create "
            f"verification token: {exc}"
        )

        try:

            supabase.table(
                "users"
            ).delete().eq(
                "id",
                created_user["id"],
            ).execute()

        except Exception as cleanup_exc:

            print(
                "Registration cleanup failed: "
                f"{cleanup_exc}"
            )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to initialise "
                "email verification."
            ),
        )

    # ---------------------------------------------------------------
    # SEND VERIFICATION EMAIL
    # ---------------------------------------------------------------

    try:

        _send_verification_email(
            email=email,
            name=name,
            token=raw_token,
        )

    except Exception as exc:
        log.exception(
            "Verification email delivery failed for a newly created account (%s)",
            type(exc).__name__,
        )
        log_security_event(
            action="verification_email_failed",
            email=email,
            request=request,
        )
        # Return the same generic registration response. The learner can use
        # the resend-verification page; the API does not disclose account state.


    log_audit_event(
        action="learner_registered",
        email=email,
        account_type="learner",
        role="normal",
        request=request,
        metadata={"marketing_email_opt_in": bool(payload.marketing_email_opt_in)},
    )

    return generic_registration_response


# ---------------------------------------------------------------------------
# VERIFY EMAIL
# ---------------------------------------------------------------------------

@router.post("/verify-email")
def verify_email(
    payload: VerifyEmailRequest,
    request: Request,
):

    raw_token = (
        payload.token or ""
    ).strip()

    if not raw_token:

        raise HTTPException(
            status_code=400,
            detail=(
                "Verification token is required."
            ),
        )

    token_hash = _hash_token(
        raw_token
    )

    now = datetime.now(
        timezone.utc
    )

    try:

        response = (
            supabase
            .table(
                "email_verification_tokens"
            )
            .select(
                "id, user_id, email, token_hash, "
                "expires_at, used_at"
            )
            .eq(
                "token_hash",
                token_hash,
            )
            .limit(1)
            .execute()
        )

    except Exception as exc:

        print(
            f"Verification lookup failed: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to verify email right now."
            ),
        )

    rows = response.data or []

    if not rows:

        raise HTTPException(
            status_code=400,
            detail=(
                "This verification link is invalid "
                "or has expired."
            ),
        )

    token_record = rows[0]

    if token_record.get(
        "used_at"
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "This verification link "
                "has already been used."
            ),
        )

    token_expires = _parse_datetime(
        token_record.get(
            "expires_at"
        )
    )

    if (
        not token_expires
        or token_expires <= now
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "This verification link has expired. "
                "Please request a new one."
            ),
        )

    # ---------------------------------------------------------------
    # FIND USER
    # ---------------------------------------------------------------

    try:

        user_response = (
            supabase
            .table("users")
            .select(
                "id, email, name, role, "
                "sub_status, is_paid, "
                "trial_ends_at, expires_at, "
                "email_verified_at"
            )
            .eq(
                "id",
                token_record["user_id"],
            )
            .limit(1)
            .execute()
        )

    except Exception as exc:

        print(
            f"Verification user lookup failed: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to verify email right now."
            ),
        )

    users = (
        user_response.data
        or []
    )

    if not users:

        raise HTTPException(
            status_code=404,
            detail="User account not found.",
        )

    user = users[0]

    # ---------------------------------------------------------------
    # ALREADY VERIFIED
    # ---------------------------------------------------------------

    if user.get(
        "sub_status"
    ) != "pending":

        try:

            supabase.table(
                "email_verification_tokens"
            ).update(
                {
                    "used_at": now.isoformat(),
                }
            ).eq(
                "id",
                token_record["id"],
            ).execute()

        except Exception as exc:

            print(
                "Failed to mark old "
                f"verification token used: {exc}"
            )

        return {
            "status": "success",
            "message": (
                "Your email has already been verified. "
                "You can log in."
            ),
            "email": user.get(
                "email"
            ),
        }

    # ---------------------------------------------------------------
    # VERIFY IDENTITY WITHOUT GRANTING A LEARNER TRIAL TO PROSPECTS
    # ---------------------------------------------------------------

    is_prospect = user.get("role") == "organisation_prospect"
    free_launch_learner = (
        free_access_mode_enabled()
        and is_individual_learner(user.get("role"), "learner")
    )
    trial_ends_at = (
        None
        if is_prospect or free_launch_learner
        else now + timedelta(days=TRIAL_DAYS)
    )
    verification_update = {
        "sub_status": "expired" if is_prospect or free_launch_learner else "trialing",
        "is_paid": False,
        "subscription_tier": "free",
        "trial_ends_at": trial_ends_at.isoformat() if trial_ends_at else None,
        "email_verified_at": now.isoformat(),
    }

    try:

        update_response = (
            supabase
            .table("users")
            .update(
                verification_update
            )
            .eq(
                "id",
                user["id"],
            )
            .eq(
                "sub_status",
                "pending",
            )
            .execute()
        )

    except Exception as exc:

        print(
            f"Account activation failed: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to activate your account."
            ),
        )

    if not update_response.data:

        raise HTTPException(
            status_code=409,
            detail=(
                "The account could not be activated. "
                "Please try again."
            ),
        )

    # ---------------------------------------------------------------
    # CONSUME TOKEN
    # ---------------------------------------------------------------

    try:

        supabase.table(
            "email_verification_tokens"
        ).update(
            {
                "used_at": now.isoformat(),
            }
        ).eq(
            "id",
            token_record["id"],
        ).execute()

    except Exception as exc:

        print(
            "Failed to mark verification "
            f"token used: {exc}"
        )

    # ---------------------------------------------------------------
    # INVALIDATE OTHER VERIFICATION TOKENS
    # ---------------------------------------------------------------

    try:

        supabase.table(
            "email_verification_tokens"
        ).update(
            {
                "used_at": now.isoformat(),
            }
        ).eq(
            "user_id",
            user["id"],
        ).is_(
            "used_at",
            "null",
        ).execute()

    except Exception as exc:

        print(
            "Failed to invalidate old "
            f"verification tokens: {exc}"
        )

    # ---------------------------------------------------------------
    # CREATE SESSION TOKEN
    # ---------------------------------------------------------------

    role = (
        user.get("role")
        or "normal"
    )

    email = (
        user.get("email")
        or token_record.get("email")
        or ""
    ).lower().strip()

    token = make_token(
        email=email,
        role=role,
        account_type="learner",
    )

    log_audit_event(
        action="email_verified",
        email=email,
        account_type="learner",
        role=role,
        request=request,
        metadata={
            "free_access_mode": free_launch_learner,
            "trial_days": None if free_launch_learner or is_prospect else TRIAL_DAYS,
            "trial_ends_at": trial_ends_at.isoformat() if trial_ends_at else None,
        },
    )

    return {
        "status": "success",
        "message": (
            "Email verified successfully. You can now use Learnora for free."
            if free_launch_learner
            else "Email verified successfully. "
            f"Your {TRIAL_DAYS}-day free trial has started."
        ),
        "token": token,
        "access_token": token,
        "email": email,
        "name": user.get("name"),
        "role": role,
        "account_type": "learner",
        "sub_status": "expired" if free_launch_learner else "trialing",
        "is_paid": False,
        "access_state": "free" if free_launch_learner else "trial",
        "trial_ends_at": trial_ends_at.isoformat() if trial_ends_at else None,
        "course_access": True,
        "allowed": allowed_for(
            role,
            "learner",
        ),
        "redirect_view": (
            "/dashboard/general"
        ),
    }


# ---------------------------------------------------------------------------
# RESEND VERIFICATION EMAIL
# ---------------------------------------------------------------------------

@router.post(
    "/resend-verification"
)
def resend_verification(
    payload: ResendVerificationRequest,
    request: Request,
):

    email = norm_email(
        payload.email
    )

    generic_response = {
        "status": "success",
        "message": (
            "If an unverified account exists for this email, "
            "a verification email has been sent."
        ),
    }

    cohort_accounts = _find_cohort_accounts_by_email(email)
    admin = _find_admin(email)
    user = _find_user(email)

    if (admin and user) or (cohort_accounts and (admin or user)):
        log_security_event(
            action="conflicting_email_account_contexts",
            email=email,
            request=request,
            metadata={
                "has_admin": bool(admin),
                "has_individual_user": bool(user),
                "cohort_account_count": len(cohort_accounts),
                "endpoint": "resend_verification",
            },
        )
        return generic_response

    # Managed cohort and administrator accounts do not use the individual
    # email-verification flow. Do not send a token to an ambiguous identity.
    if cohort_accounts or admin or not user:
        return generic_response

    if user.get("sub_status") != "pending":
        return generic_response

    now = datetime.now(
        timezone.utc
    )

    # ---------------------------------------------------------------
    # INVALIDATE PREVIOUS TOKENS
    # ---------------------------------------------------------------

    try:

        supabase.table(
            "email_verification_tokens"
        ).update(
            {
                "used_at": now.isoformat(),
            }
        ).eq(
            "user_id",
            user["id"],
        ).is_(
            "used_at",
            "null",
        ).execute()

    except Exception as exc:

        print(
            "Failed to invalidate old "
            f"verification tokens: {exc}"
        )

    # ---------------------------------------------------------------
    # CREATE NEW TOKEN
    # ---------------------------------------------------------------

    raw_token = (
        _generate_raw_token()
    )

    token_hash = _hash_token(
        raw_token
    )

    expires_at = (
        now
        + timedelta(
            minutes=EMAIL_VERIFICATION_TTL_MINUTES
        )
    )

    try:

        supabase.table(
            "email_verification_tokens"
        ).insert(
            {
                "user_id": user["id"],
                "email": email,
                "token_hash": token_hash,
                "expires_at": (
                    expires_at.isoformat()
                ),
                "used_at": None,
                "created_at": (
                    now.isoformat()
                ),
            }
        ).execute()

    except Exception as exc:

        print(
            "Failed to create "
            f"resend token: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to resend verification email."
            ),
        )

    try:

        _send_verification_email(
            email=email,
            name=user.get("name"),
            token=raw_token,
        )

    except Exception as exc:

        print(
            "Resend verification email failed: "
            f"{exc}"
        )

        log_security_event(
            action=(
                "resend_verification_email_failed"
            ),
            email=email,
            request=request,
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Unable to send the verification email "
                "right now. Please try again later."
            ),
        )

    log_security_event(
        action="verification_email_resent",
        email=email,
        request=request,
    )

    return generic_response


# ---------------------------------------------------------------------------
# FORGOT PASSWORD
# ---------------------------------------------------------------------------

@router.post(
    "/forgot-password"
)
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
):

    email = norm_email(
        payload.email
    )

    generic_response = {
        "status": "success",
        "message": (
            "If an account exists for this email, "
            "a password reset email has been sent."
        ),
    }

    cohort_accounts = _find_cohort_accounts_by_email(email)
    admin = _find_admin(email)
    user = _find_user(email)

    if (admin and user) or (cohort_accounts and (admin or user)):
        log_security_event(
            action="conflicting_email_account_contexts",
            email=email,
            request=request,
            metadata={
                "has_admin": bool(admin),
                "has_individual_user": bool(user),
                "cohort_account_count": len(cohort_accounts),
                "endpoint": "forgot_password",
            },
        )
        return generic_response

    # Cohort credentials use their managed-account recovery path. Never reset
    # an administrator or individual password for an email reserved by a cohort.
    if cohort_accounts or (not admin and not user):
        return generic_response

    if admin:
        if not admin.get("is_active", False):
            return generic_response
        account_id = admin["id"]
        account_type = "admin"
        account_name = admin.get("name")
    else:
        account_id = user["id"]
        account_type = "learner"
        account_name = user.get("name")

    now = datetime.now(
        timezone.utc
    )

    # ---------------------------------------------------------------
    # INVALIDATE PREVIOUS RESET TOKENS
    # ---------------------------------------------------------------

    try:

        supabase.table(
            "password_reset_tokens"
        ).update(
            {
                "used_at": now.isoformat(),
            }
        ).eq(
            "account_id",
            account_id,
        ).is_(
            "used_at",
            "null",
        ).execute()

    except Exception as exc:

        print(
            "Failed to invalidate previous "
            f"reset tokens: {exc}"
        )

    # ---------------------------------------------------------------
    # CREATE RESET TOKEN
    # ---------------------------------------------------------------

    raw_token = (
        _generate_raw_token()
    )

    token_hash = _hash_token(
        raw_token
    )

    expires_at = (
        now
        + timedelta(
            minutes=PASSWORD_RESET_TTL_MINUTES
        )
    )

    try:

        supabase.table(
            "password_reset_tokens"
        ).insert(
            {
                "account_id": account_id,
                "email": email,
                "account_type": account_type,
                "token_hash": token_hash,
                "expires_at": (
                    expires_at.isoformat()
                ),
                "used_at": None,
                "created_at": (
                    now.isoformat()
                ),
            }
        ).execute()

    except Exception as exc:

        print(
            "Failed to create password "
            f"reset token: {exc}"
        )

        return generic_response

    # ---------------------------------------------------------------
    # SEND RESET EMAIL
    # ---------------------------------------------------------------

    try:

        _send_password_reset_email(
            email=email,
            name=account_name,
            token=raw_token,
        )

    except Exception as exc:

        print(
            "Password reset email failed: "
            f"{exc}"
        )

        log_security_event(
            action=(
                "password_reset_email_failed"
            ),
            email=email,
            request=request,
        )

        return generic_response

    log_security_event(
        action="password_reset_requested",
        email=email,
        request=request,
        metadata={
            "account_type": account_type,
        },
    )

    return generic_response


# ---------------------------------------------------------------------------
# RESET PASSWORD
# ---------------------------------------------------------------------------

@router.post(
    "/reset-password"
)
def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
):

    raw_token = (
        payload.token or ""
    ).strip()

    if not raw_token:

        raise HTTPException(
            status_code=400,
            detail=(
                "Password reset token is required."
            ),
        )

    check_password_rules(
        payload.new_password
    )

    if (
        payload.new_password
        != payload.confirm_password
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "New passwords do not match."
            ),
        )

    token_hash = _hash_token(
        raw_token
    )

    now = datetime.now(
        timezone.utc
    )

    try:

        response = (
            supabase
            .table(
                "password_reset_tokens"
            )
            .select(
                "id, account_id, email, account_type, "
                "token_hash, expires_at, used_at"
            )
            .eq(
                "token_hash",
                token_hash,
            )
            .limit(1)
            .execute()
        )

    except Exception as exc:

        print(
            f"Password reset lookup failed: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to reset password right now."
            ),
        )

    rows = response.data or []

    if not rows:

        raise HTTPException(
            status_code=400,
            detail=(
                "This password reset link is invalid "
                "or has expired."
            ),
        )

    token_record = rows[0]

    if token_record.get(
        "used_at"
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "This password reset link "
                "has already been used."
            ),
        )

    token_expires = _parse_datetime(
        token_record.get(
            "expires_at"
        )
    )

    if (
        not token_expires
        or token_expires <= now
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "This password reset link has expired. "
                "Please request a new one."
            ),
        )

    account_id = token_record[
        "account_id"
    ]

    account_type = token_record[
        "account_type"
    ]

    if account_type not in {
        "admin",
        "learner",
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid password reset request."
            ),
        )

    email = norm_email(token_record.get("email") or "")
    cohort_accounts = _find_cohort_accounts_by_email(email)
    admin = _find_admin(email)
    user = _find_user(email)
    if account_type == "admin":
        identity_matches_token = (
            bool(admin)
            and str(admin.get("id")) == str(account_id)
            and not user
            and not cohort_accounts
        )
    else:
        identity_matches_token = (
            bool(user)
            and str(user.get("id")) == str(account_id)
            and not admin
            and not cohort_accounts
        )
    if not identity_matches_token:
        raise HTTPException(
            status_code=409,
            detail="This account identity has changed or is ambiguous. Request a new password reset link.",
        )

    table = "admins" if account_type == "admin" else "users"

    # Claim the token before changing the password. The conditional update
    # ensures two simultaneous submissions cannot both consume one token.
    try:
        claimed = (
            supabase.table("password_reset_tokens")
            .update({"used_at": now.isoformat()})
            .eq("id", token_record["id"])
            .is_("used_at", "null")
            .gt("expires_at", now.isoformat())
            .execute()
        ).data or []
    except Exception as exc:
        print(f"Password reset token claim failed: {type(exc).__name__}")
        raise HTTPException(503, "Unable to reset the password right now. Please request a new link.") from None
    if not claimed:
        raise HTTPException(409, "This password reset link has already been used or has expired.")

    new_hash = hash_password(
        payload.new_password
    )

    try:

        response = (
            supabase
            .table(table)
            .update(
                {
                    "password_hash": new_hash,
                    "password_changed_at": now.isoformat(),
                }
            )
            .eq(
                "id",
                account_id,
            )
            .execute()
        )

    except Exception as exc:

        print(
            f"Password reset update failed: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to reset password."
            ),
        )

    if not response.data:

        raise HTTPException(
            status_code=404,
            detail=(
                "Account could not be found."
            ),
        )

    # ---------------------------------------------------------------
    # INVALIDATE OTHER RESET TOKENS
    # ---------------------------------------------------------------

    try:

        supabase.table(
            "password_reset_tokens"
        ).update(
            {
                "used_at": now.isoformat(),
            }
        ).eq(
            "account_id",
            account_id,
        ).is_(
            "used_at",
            "null",
        ).execute()

    except Exception as exc:

        print(
            "Failed to invalidate other "
            f"reset tokens: {exc}"
        )

    log_security_event(
        action="password_reset_completed",
        request=request,
        metadata={
            "account_type": account_type,
            "account_id": str(
                account_id
            ),
        },
    )

    log_audit_event(
        action="password_reset_completed",
        account_type=account_type,
        request=request,
        metadata={
            "account_id": str(
                account_id
            ),
        },
    )
    if account_type == "learner":
        try:
            from services.notification_service import notify_security_event
            notify_security_event(
                user_id=str(account_id),
                event_key=f"security:password-reset:{datetime.now(timezone.utc).isoformat()}",
                title="Your Learnora password was reset",
                body="The password for your Learnora account was successfully reset.",
            )
        except Exception:
            logging.getLogger(__name__).exception("Password-reset security notification failed")

    return {
        "status": "success",
        "message": (
            "Password reset successfully. "
            "You can now log in with your new password."
        ),
    }


# ---------------------------------------------------------------------------
# CURRENT ACCOUNT
# ---------------------------------------------------------------------------

@router.get("/me")
def me(
    user: CurrentUser = Depends(
        get_current_user
    ),
):
    memberships = []
    if user.account_type != "admin":
        try:
            memberships = (
                supabase.table("organisation_members")
                .select("organisation_id,role,status")
                .eq("user_id", user.id)
                .eq("status", "active")
                .execute()
            ).data or []
        except Exception as exc:
            print("Current-user organisation membership lookup failed:", type(exc).__name__)
            raise HTTPException(
                status_code=503,
                detail="Your organisation access could not be verified. Please try again.",
            ) from None

    organisation_ids = list({str(row["organisation_id"]) for row in memberships if row.get("organisation_id")})
    if organisation_ids:
        try:
            organisation_rows = (
                supabase.table("organisations")
                .select("id,name,slug,is_active")
                .in_("id", organisation_ids)
                .execute()
            ).data or []
            organisation_map = {str(row["id"]): row for row in organisation_rows if row.get("is_active")}
            memberships = [
                {**row, "organisation_name": organisation_map[str(row["organisation_id"])].get("name"),
                 "organisation_slug": organisation_map[str(row["organisation_id"])].get("slug")}
                for row in memberships if str(row.get("organisation_id")) in organisation_map
            ]
        except Exception as exc:
            print("Current-user organisation details lookup failed:", exc)

    # A single default organisation is safe to infer. If the user belongs to
    # multiple organisations, return the memberships but do not silently pick one.
    single_membership = memberships[0] if len(memberships) == 1 else None
    cohort_id = user.cohort_id
    if not cohort_id and user.account_type != "cohort" and user.id:
        try:
            cohort_memberships = (
                supabase.table("cohort_members")
                .select("cohort_id")
                .eq("user_id", str(user.id))
                .eq("status", "active")
                .limit(1)
                .execute()
            ).data or []
            cohort_id = str(cohort_memberships[0]["cohort_id"]) if cohort_memberships else None
        except Exception as exc:
            print("Current-user cohort membership lookup failed:", exc)
            raise HTTPException(503, "Your cohort membership could not be verified. Please retry.") from None
    return {
        "status": "success",
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "sub_status": user.sub_status,
        "account_type": user.account_type,
        "is_paid": user.is_paid,
        "access_state": user.access_state,
        "course_access": user.course_access,
        "trial_ends_at": user.trial_ends_at,
        "expires_at": user.expires_at,
        "organisation_id": single_membership.get("organisation_id") if single_membership else (user.organisation_id if not memberships else None),
        "organisation_role": single_membership.get("role") if single_membership else (user.organisation_role if not memberships else None),
        "cohort_id": cohort_id,
        "organisation_memberships": memberships,
        "allowed": allowed_for(
            user.role,
            user.account_type,
        ),
    }


# ---------------------------------------------------------------------------
# CHANGE PASSWORD
# ---------------------------------------------------------------------------

@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    user: CurrentUser = Depends(
        get_current_user
    ),
):

    check_password_rules(
        payload.new_password
    )

    if (
        payload.new_password
        != payload.confirm_password
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "New passwords do not match"
            ),
        )

    if (
        payload.current_password
        == payload.new_password
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "New password must be different "
                "from the current password"
            ),
        )

    # ---------------------------------------------------------------
    # FIND DATABASE ACCOUNT
    # ---------------------------------------------------------------

    if (
        user.account_type
        == "admin"
    ):

        account = _find_admin(
            user.email
        )

        if not account:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Administrator account "
                    "not found"
                ),
            )

        table = "admins"

    else:

        account = _find_user(
            user.email
        )

        if not account:

            raise HTTPException(
                status_code=404,
                detail=(
                    "User account not found"
                ),
            )

        table = "users"

    # ---------------------------------------------------------------
    # VERIFY CURRENT PASSWORD
    # ---------------------------------------------------------------

    valid, _ = verify_password(
        payload.current_password,
        account.get(
            "password_hash",
            "",
        ),
    )

    if not valid:

        log_security_event(
            action="failed_password_change",
            email=user.email,
            request=request,
        )

        raise HTTPException(
            status_code=401,
            detail=(
                "Current password is incorrect"
            ),
        )

    # ---------------------------------------------------------------
    # UPDATE PASSWORD
    # ---------------------------------------------------------------

    new_hash = hash_password(
        payload.new_password
    )

    try:

        response = (
            supabase
            .table(table)
            .update(
                {
                    "password_hash": new_hash,
                    "password_changed_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            .eq(
                "id",
                account["id"],
            )
            .execute()
        )

    except Exception as exc:

        print(
            f"Password update failed: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to change password"
            ),
        )

    if not response.data:

        raise HTTPException(
            status_code=500,
            detail=(
                "Password was not changed"
            ),
        )

    log_audit_event(
        action="password_changed",
        email=user.email,
        account_type=user.account_type,
        role=user.role,
        request=request,
    )

    log_security_event(
        action="password_changed",
        email=user.email,
        request=request,
    )
    if user.account_type == "learner" and user.id:
        try:
            from services.notification_service import notify_security_event
            notify_security_event(
                user_id=str(user.id),
                event_key=f"security:password-change:{datetime.now(timezone.utc).isoformat()}",
                title="Your Learnora password was changed",
                body="The password for your Learnora account was successfully changed.",
            )
        except Exception:
            logging.getLogger(__name__).exception("Password-change security notification failed")

    return {
        "status": "success",
        "message": (
            "Password changed successfully"
        ),
    }