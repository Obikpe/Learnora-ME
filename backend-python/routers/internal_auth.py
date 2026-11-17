"""Internal Learnora staff authentication.

Staff sessions use a domain-separated signing key and explicit issuer/audience
claims. Login shares the persistent account/IP throttles used by learner auth.
"""
import hashlib
import hmac
import logging
import os
import time
from datetime import datetime, timezone
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel, Field

from . import auth
from .auth import (
    ALGORITHM,
    TEAM_COOKIE_NAME,
    _request_auth_token,
    clear_auth_cookie,
    deliver_auth_token,
    hash_password,
    norm_email,
    supabase,
    verify_password,
)

log = logging.getLogger("internal_auth")
router = APIRouter(prefix="/api/internal/auth", tags=["Internal Auth"])
bearer = HTTPBearer(auto_error=False)

# Derive a distinct signing key from the configured root secret. This avoids
# requiring another production secret while preventing learner JWTs from being
# accepted as staff tokens (and vice versa).
INTERNAL_JWT_SECRET = hmac.new(
    auth.JWT_SECRET.encode("utf-8"),
    b"learnora-internal-staff-jwt-v1",
    hashlib.sha256,
).digest()
INTERNAL_TOKEN_ISSUER = "learnora-internal"
INTERNAL_TOKEN_AUDIENCE = "learnora-staff"


class InternalLoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=1, max_length=256)


class InternalStaffContext(BaseModel):
    staff_id: str
    user_id: str
    email: str
    name: Optional[str] = None
    job_title: Optional[str] = None
    status: str
    roles: list[str] = Field(default_factory=list)
    department_ids: list[str] = Field(default_factory=list)
    team_ids: list[str] = Field(default_factory=list)


def _staff_by_email(email: str):
    users = (
        supabase.table("users")
        .select("id,email,name,password_hash,role,password_changed_at,account_status")
        .eq("email", email)
        .limit(1)
        .execute()
    )
    if not users.data:
        return None
    user = users.data[0]
    staff_rows = (
        supabase.table("learnora_staff_accounts")
        .select("id,user_id,job_title,status,employee_code")
        .eq("user_id", user["id"])
        .limit(1)
        .execute()
    )
    return {"user": user, "staff": staff_rows[0]} if staff_rows.data else None


def _load_staff_context(email: str) -> InternalStaffContext:
    found = _staff_by_email(email)
    if not found:
        raise HTTPException(403, "Internal staff access is not enabled for this account.")
    user, staff = found["user"], found["staff"]
    if user.get("account_status") == "deactivation_pending":
        raise HTTPException(403, "This account is deactivated.")
    if staff["status"] != "active":
        raise HTTPException(403, "This staff account is not active.")

    assignments = (
        supabase.table("learnora_staff_role_assignments")
        .select("role_id")
        .eq("staff_id", staff["id"])
        .eq("status", "active")
        .execute()
    )
    role_ids = [row["role_id"] for row in (assignments.data or [])]
    roles = []
    if role_ids:
        role_rows = (
            supabase.table("learnora_staff_roles")
            .select("slug")
            .in_("id", role_ids)
            .eq("status", "active")
            .execute()
        )
        roles = [row["slug"] for row in (role_rows.data or [])]

    memberships = (
        supabase.table("learnora_staff_team_members")
        .select("team_id")
        .eq("staff_id", staff["id"])
        .eq("status", "active")
        .execute()
    )
    team_ids = [row["team_id"] for row in (memberships.data or [])]
    department_ids = []
    if team_ids:
        team_rows = (
            supabase.table("learnora_staff_teams")
            .select("department_id")
            .in_("id", team_ids)
            .execute()
        )
        department_ids = sorted({
            row["department_id"]
            for row in (team_rows.data or [])
            if row.get("department_id")
        })

    return InternalStaffContext(
        staff_id=str(staff["id"]),
        user_id=str(user["id"]),
        email=str(user["email"]).lower(),
        name=user.get("name"),
        job_title=staff.get("job_title"),
        status=staff["status"],
        roles=roles,
        department_ids=department_ids,
        team_ids=team_ids,
    )


def _record_failed_login(email: str, request: Request, rate_keys: tuple[str, str, str]) -> None:
    try:
        auth._record_login_failure(rate_keys)
    except Exception:
        log.exception("Persistent staff login throttling failed")
        raise HTTPException(
            status_code=503,
            detail="Authentication protection is temporarily unavailable. Please retry.",
        ) from None
    auth.log_security_event(
        action="failed_internal_staff_login",
        email=email,
        request=request,
    )


def get_current_staff(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
):
    token_value = _request_auth_token(request, creds, TEAM_COOKIE_NAME)
    if not token_value:
        raise HTTPException(401, "Not authenticated")
    if len(auth.JWT_SECRET) < 32:
        raise HTTPException(500, "Internal authentication is not configured")
    try:
        payload = jwt.decode(
            token_value,
            INTERNAL_JWT_SECRET,
            algorithms=[ALGORITHM],
            issuer=INTERNAL_TOKEN_ISSUER,
            audience=INTERNAL_TOKEN_AUDIENCE,
        )
    except InvalidTokenError:
        raise HTTPException(401, "Invalid or expired internal token") from None

    if payload.get("context") != "internal" or payload.get("account_type") != "staff":
        raise HTTPException(403, "Internal staff token required")
    email = (payload.get("email") or payload.get("sub") or "").lower().strip()
    if not email:
        raise HTTPException(401, "Invalid internal token")

    found = _staff_by_email(email)
    if not found:
        raise HTTPException(401, "Staff identity is no longer active")
    if found["staff"].get("status") != "active":
        raise HTTPException(401, "Staff identity is no longer active")
    if found["user"].get("account_status") == "deactivation_pending":
        raise HTTPException(401, "Staff identity is no longer active")
    auth._assert_session_not_before_password_change(payload, found["user"])
    return _load_staff_context(email)


def require_internal_permission(permission: str):
    def dependency(staff: InternalStaffContext = Depends(get_current_staff)):
        assignments = (
            supabase.table("learnora_staff_role_assignments")
            .select("role_id")
            .eq("staff_id", staff.staff_id)
            .eq("status", "active")
            .execute()
        )
        role_ids = [row["role_id"] for row in (assignments.data or [])]
        if not role_ids:
            raise HTTPException(status_code=403, detail=f"Permission required: {permission}")
        matches = (
            supabase.table("learnora_staff_role_permissions")
            .select("role_id,learnora_permissions!inner(permission_key)")
            .in_("role_id", role_ids)
            .eq("learnora_permissions.permission_key", permission)
            .execute()
        )
        if matches.data:
            return staff
        raise HTTPException(status_code=403, detail=f"Permission required: {permission}")
    return dependency


@router.post("/login")
def internal_login(
    payload: InternalLoginRequest,
    request: Request,
    response: Response = None,
):
    email = norm_email(payload.email)
    rate_keys = auth._login_rate_keys(email, request)

    if auth._login_is_limited(rate_keys):
        auth.log_security_event(
            action="internal_login_rate_limited",
            email=email,
            request=request,
        )
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Try again in five minutes.",
            headers={"Retry-After": str(auth.WINDOW)},
        )

    try:
        found = _staff_by_email(email)
    except Exception:
        log.exception("Staff identity lookup failed")
        raise HTTPException(503, "Staff sign-in is temporarily unavailable.") from None

    # One-time compatibility path for a legacy active super-admin account.
    # The old password is verified, then a fresh bcrypt hash is stored in the
    # new staff identity. Existing learner identities are never overwritten.
    if not found:
        try:
            legacy_rows = (
                supabase.table("admins")
                .select("id,email,name,password_hash,role,is_active")
                .eq("email", email)
                .limit(1)
                .execute()
            ).data or []
        except Exception:
            log.exception("Legacy administrator lookup failed")
            raise HTTPException(503, "Staff sign-in is temporarily unavailable.") from None

        legacy = legacy_rows[0] if legacy_rows else None
        if not legacy or legacy.get("role") != "super_admin" or not legacy.get("is_active"):
            verify_password(payload.password, auth.DUMMY_LOGIN_PASSWORD_HASH)
            _record_failed_login(email, request, rate_keys)
            raise HTTPException(401, "Invalid email or password")

        legacy_hash = str(legacy.get("password_hash") or "")
        if not auth._legacy_password_login_allowed(legacy_hash):
            verify_password(payload.password, auth.DUMMY_LOGIN_PASSWORD_HASH)
            raise HTTPException(
                403,
                "Your password needs to be reset before you can sign in. Use Forgot password.",
            )
        valid, _needs_rehash = verify_password(payload.password, legacy_hash)
        if not valid:
            _record_failed_login(email, request, rate_keys)
            raise HTTPException(401, "Invalid email or password")

        try:
            existing_user = (
                supabase.table("users")
                .select("id")
                .eq("email", email)
                .limit(1)
                .execute()
            ).data or []
            if existing_user:
                raise HTTPException(
                    409,
                    "This email already has a learner identity. Contact support to reconcile staff access.",
                )

            role_rows = (
                supabase.table("learnora_staff_roles")
                .select("id")
                .eq("slug", "super_admin")
                .eq("status", "active")
                .limit(1)
                .execute()
            ).data or []
            if not role_rows:
                raise RuntimeError("The super-admin staff role is not configured.")

            created_user_id = None
            created_staff_id = None
            try:
                now = datetime.now(timezone.utc).isoformat()
                user_rows = (
                    supabase.table("users")
                    .insert({
                        "email": email,
                        "name": legacy.get("name"),
                        "password_hash": hash_password(payload.password),
                        "role": "staff",
                        "is_paid": False,
                        "sub_status": "active",
                        "email_verified": True,
                        "password_changed_at": now,
                    })
                    .execute()
                ).data or []
                if not user_rows:
                    raise RuntimeError("Staff user identity was not created.")
                created_user_id = user_rows[0]["id"]

                staff_rows = (
                    supabase.table("learnora_staff_accounts")
                    .insert({
                        "user_id": created_user_id,
                        "status": "active",
                        "joined_at": now,
                    })
                    .execute()
                ).data or []
                if not staff_rows:
                    raise RuntimeError("Staff account was not created.")
                created_staff_id = staff_rows[0]["id"]

                supabase.table("learnora_staff_role_assignments").insert({
                    "staff_id": created_staff_id,
                    "role_id": role_rows[0]["id"],
                    "status": "active",
                }).execute()
            except Exception:
                log.exception("Legacy super-admin migration failed")
                if created_staff_id:
                    try:
                        supabase.table("learnora_staff_accounts").delete().eq("id", created_staff_id).execute()
                    except Exception:
                        log.exception("Could not clean up partial staff account migration")
                if created_user_id:
                    try:
                        supabase.table("users").delete().eq("id", created_user_id).execute()
                    except Exception:
                        log.exception("Could not clean up partial staff user migration")
                raise

            found = _staff_by_email(email)
        except HTTPException:
            raise
        except Exception:
            log.exception("Legacy super-admin migration could not complete")
            raise HTTPException(503, "Staff sign-in is temporarily unavailable.") from None

    if not found:
        verify_password(payload.password, auth.DUMMY_LOGIN_PASSWORD_HASH)
        _record_failed_login(email, request, rate_keys)
        raise HTTPException(401, "Invalid email or password")

    user, staff = found["user"], found["staff"]
    if user.get("account_status") == "deactivation_pending":
        raise HTTPException(403, "This staff account is deactivated.")
    if staff.get("status") not in {"active", "pending_activation"}:
        raise HTTPException(403, "This staff account is not available for login.")

    stored_hash = str(user.get("password_hash") or "")
    if not auth._legacy_password_login_allowed(stored_hash):
        verify_password(payload.password, auth.DUMMY_LOGIN_PASSWORD_HASH)
        raise HTTPException(
            403,
            "Your password needs to be reset before you can sign in. Use Forgot password.",
        )

    valid, needs_rehash = verify_password(payload.password, stored_hash)
    if not valid:
        _record_failed_login(email, request, rate_keys)
        raise HTTPException(401, "Invalid email or password")

    if needs_rehash:
        supabase.table("users").update({
            "password_hash": hash_password(payload.password)
        }).eq("id", user["id"]).execute()

    if staff["status"] == "pending_activation":
        supabase.table("learnora_staff_accounts").update({
            "status": "active",
            "joined_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", staff["id"]).execute()

    auth._clear_login_failures(rate_keys)
    now = time.time()
    token = jwt.encode(
        {
            "sub": email,
            "email": email,
            "role": "staff",
            "account_type": "staff",
            "context": "internal",
            "iss": INTERNAL_TOKEN_ISSUER,
            "aud": INTERNAL_TOKEN_AUDIENCE,
            "iat": now,
            "exp": now + int(os.getenv("TOKEN_TTL_SECONDS", "86400")),
        },
        INTERNAL_JWT_SECRET,
        algorithm=ALGORITHM,
    )
    context = _load_staff_context(email)
    auth.log_audit_event(
        action="internal_staff_login",
        email=email,
        account_type="staff",
        role="staff",
        request=request,
        metadata={"staff_id": context.staff_id},
    )
    return deliver_auth_token(
        request,
        response,
        token,
        {"status": "success", "token": token, "staff": context.model_dump()},
        cookie_name=TEAM_COOKIE_NAME,
    )


@router.post("/logout")
def internal_logout(response: Response):
    clear_auth_cookie(response, TEAM_COOKIE_NAME)
    return {"success": True}


@router.get("/me")
def internal_me(staff: InternalStaffContext = Depends(get_current_staff)):
    return {"status": "success", "staff": staff.model_dump()}
