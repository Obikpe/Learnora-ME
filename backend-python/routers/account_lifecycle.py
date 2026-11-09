from datetime import datetime, timedelta, timezone
from html import escape
import hmac
import os

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from pydantic import BaseModel, Field
from typing import Literal

from routers import auth, billing

router = APIRouter(prefix="/api/account-lifecycle", tags=["account lifecycle"])

DELETION_TOKEN_TTL_MINUTES = 60
REACTIVATION_TOKEN_TTL_HOURS = 24
ACCOUNT_RECOVERY_DAYS = 30


class RequestDeletionRequest(BaseModel):
    reason: Literal[
        "not_using",
        "found_alternative",
        "missing_content",
        "technical_issues",
        "cost",
        "privacy",
        "other",
    ]
    reason_details: str | None = Field(default=None, max_length=1000)


class ConfirmDeletionRequest(BaseModel):
    token: str = Field(min_length=20, max_length=512)


class MarketingPreferencesRequest(BaseModel):
    enabled: bool


class MarketingUnsubscribeRequest(BaseModel):
    token: str = Field(min_length=20, max_length=4096)


def _require_individual_learner(user: auth.CurrentUser) -> None:
    if user.account_type != "learner" or user.role != "normal" or not user.id:
        raise HTTPException(
            status_code=403,
            detail="Account deletion is available for individual learner accounts. Contact Learnora support for assistance.",
        )

    try:
        active_organisation_memberships = (
            auth.supabase.table("organisation_members")
            .select("id")
            .eq("user_id", user.id)
            .eq("status", "active")
            .limit(1)
            .execute()
        ).data or []
        active_cohort_memberships = (
            auth.supabase.table("cohort_members")
            .select("id")
            .eq("user_id", user.id)
            .eq("status", "active")
            .limit(1)
            .execute()
        ).data or []
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Organisation access could not be verified. Please try again before requesting account deletion.",
        ) from None

    if (
        user.organisation_id
        or user.organisation_role
        or active_organisation_memberships
        or active_cohort_memberships
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "This account is managed by an organisation or cohort. "
                "The organisation must release the account before it can be deleted "
                "and used to create an independent Learnora account."
            ),
        )


@router.post("/request-deletion")
def request_account_deletion(
    payload: RequestDeletionRequest,
    request: Request,
    user: auth.CurrentUser = Depends(auth.get_current_user),
):
    _require_individual_learner(user)

    owner_memberships = (
        auth.supabase.table("organisation_members")
        .select("id")
        .eq("user_id", user.id)
        .eq("role", "owner")
        .eq("status", "active")
        .limit(1)
        .execute()
    ).data or []
    if owner_memberships:
        raise HTTPException(
            status_code=409,
            detail="Transfer organisation ownership before deleting this account. Contact support if you need help.",
        )

    raw_token = auth._generate_raw_token()
    token_hash = auth._hash_token(raw_token)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=DELETION_TOKEN_TTL_MINUTES)

    existing_request = (
        auth.supabase.table("users")
        .select("account_status,account_deletion_expires_at")
        .eq("id", user.id)
        .limit(1)
        .execute()
    ).data or []
    if existing_request and existing_request[0].get("account_status") == "deletion_pending":
        current_expiry = auth._parse_datetime(existing_request[0].get("account_deletion_expires_at"))
        if current_expiry and current_expiry > now:
            raise HTTPException(status_code=409, detail="A confirmation email is already on its way. Check your inbox or wait for the link to expire before requesting another.")

    saved = (
        auth.supabase.table("users")
        .update({
            "account_status": "deletion_pending",
            "account_deletion_token_hash": token_hash,
            "account_deletion_expires_at": expires_at.isoformat(),
            "account_deletion_requested_at": now.isoformat(),
            "deletion_reason": payload.reason,
            "deletion_reason_details": (payload.reason_details or "").strip() or None,
        })
        .eq("id", user.id)
        .in_("account_status", ["active", "deletion_pending"])
        .select("id")
        .execute()
    ).data or []
    if not saved:
        raise HTTPException(status_code=409, detail="A deletion request is already pending or this account is unavailable.")

    confirmation_url = f"{auth.FRONTEND_URL}/confirm-account-deletion#token={raw_token}"
    display_name = user.name or "there"
    safe_display_name = escape(display_name)
    text_body = (
        f"Hi {display_name},\n\n"
        "We received a request to delete your Learnora account. "
        "To confirm, open the secure link below within 60 minutes:\n\n"
        f"{confirmation_url}\n\n"
        "Your account will not be deactivated unless you open this link. "
        "After confirmation, your account will be deactivated for 30 days. You can reactivate it during that period. "
        "After 30 days, the live sign-in profile will be permanently closed. Limited records may be retained under Learnora's privacy and retention policy. "
        "Any active recurring Learnora subscription will be cancelled when deactivation is confirmed.\n\n"
        "If you did not request this, ignore this email and your account will remain available.\n\n"
        "Learnora ME"
    )
    html_body = f"""<!doctype html>
<html><body style="margin:0;background:#f5f7fb;font-family:Arial,sans-serif;color:#172033">
<div style="max-width:600px;margin:40px auto;padding:32px;background:#fff;border:1px solid #e5e7eb;border-radius:18px">
<h1 style="margin:0 0 16px">Confirm account deletion</h1>
<p>Hi {safe_display_name},</p>
<p>We received a request to delete your Learnora account. If you confirm, your account will be deactivated for 30 days. You can reactivate it during that period. After 30 days, it will be permanently deleted.</p>
<p style="margin:28px 0"><a href="{confirmation_url}" style="display:inline-block;padding:14px 22px;border-radius:10px;background:#172033;color:#fff;text-decoration:none;font-weight:bold">Confirm account deletion</a></p>
<p style="font-size:13px;line-height:1.6;color:#64748b">This secure link expires in 60 minutes. If you confirm, your account will be deactivated for 30 days. You can reactivate it during that period. After 30 days, it will be permanently deleted. Active recurring Learnora subscriptions will be cancelled when deactivation is confirmed.</p>
<p style="font-size:13px;line-height:1.6;color:#64748b">Limited account, learning, security or audit records may be retained under Learnora's privacy and retention policy.</p>
<p style="font-size:13px;color:#64748b">If you did not request this, ignore this email. Your account will remain available.</p>
</div></body></html>"""
    try:
        auth._send_email(
            recipient=user.email,
            subject="Confirm deletion of your Learnora account",
            text_body=text_body,
            html_body=html_body,
        )
    except Exception:
        auth.supabase.table("users").update({
            "account_status": "active",
            "account_deletion_token_hash": None,
            "account_deletion_expires_at": None,
            "account_deletion_requested_at": None,
            "deletion_reason": None,
            "deletion_reason_details": None,
        }).eq("id", user.id).eq("account_deletion_token_hash", token_hash).execute()
        raise HTTPException(
            status_code=503,
            detail="We could not send the confirmation email. Your account has not been deleted. Please try again.",
        ) from None

    auth.log_audit_event(
        action="learner_account_deletion_requested",
        email=user.email,
        account_type="learner",
        role=user.role,
        request=request,
        metadata={
            "deletion_reason": payload.reason,
            "confirmation_expires_at": expires_at.isoformat(),
        },
    )
    return {
        "success": True,
        "message": "We sent a confirmation link to your email address. Your account remains active until you confirm.",
        "expires_in_minutes": DELETION_TOKEN_TTL_MINUTES,
    }


@router.post("/confirm-deletion")
def confirm_account_deletion(
    payload: ConfirmDeletionRequest,
    request: Request,
    response: Response,
):
    raw_token = payload.token.strip()
    token_hash = auth._hash_token(raw_token)
    now = datetime.now(timezone.utc)

    rows = (
        auth.supabase.table("users")
        .select("id,email,name,role,sub_status,is_paid,account_status,account_deletion_expires_at,deletion_reason")
        .eq("account_deletion_token_hash", token_hash)
        .eq("account_status", "deletion_pending")
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        raise HTTPException(status_code=400, detail="This confirmation link is invalid or has already been used.")

    account = rows[0]
    expires_at = auth._parse_datetime(account.get("account_deletion_expires_at"))
    if not expires_at or expires_at <= now:
        raise HTTPException(status_code=400, detail="This confirmation link has expired. Request a new one from Settings.")

    learner = auth.CurrentUser(
        id=str(account["id"]),
        name=account.get("name"),
        email=account["email"],
        role=account.get("role") or "normal",
        sub_status=account.get("sub_status") or "active",
        account_type="learner",
        is_paid=bool(account.get("is_paid")),
    )

    # Re-check the retained identity boundary at confirmation time. A managed
    # membership added after the email was sent must not be deleted implicitly.
    organisation_id, organisation_role = auth._active_organisation_context(
        str(account["id"]),
        fail_closed=True,
    )
    if organisation_id or organisation_role:
        raise HTTPException(
            status_code=409,
            detail=(
                "This account is now linked to an organisation or cohort. "
                "The organisation must release the account before deletion can continue."
            ),
        )

    active_subscriptions = (
        billing.supabase.table("learnora_subscriptions")
        .select("id")
        .eq("user_id", learner.id)
        .in_("status", ["active", "past_due", "paused"])
        .limit(20)
        .execute()
    ).data or []
    if active_subscriptions:
        try:
            billing.cancel_learner_subscription(learner)
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=502,
                detail="We could not confirm cancellation of your recurring subscription. Your account has not been deleted; please contact support.",
            ) from None

    result = auth.supabase.rpc(
        "complete_learner_account_deletion",
        {"p_token_hash": token_hash, "p_deleted_at": now.isoformat()},
    ).execute()
    completed = result.data
    if isinstance(completed, list) and completed:
        completed = completed[0]
    if not completed:
        raise HTTPException(
            status_code=409,
            detail="We could not complete account deletion. Please contact Learnora support.",
        )

    deactivation_until = now + timedelta(days=ACCOUNT_RECOVERY_DAYS)
    auth.log_audit_event(
        action="learner_account_deactivated",
        email=account["email"],
        account_type="learner",
        role=account.get("role") or "normal",
        request=request,
        metadata={
            "user_id": learner.id,
            "deactivation_until": deactivation_until.isoformat(),
            "recovery_days": ACCOUNT_RECOVERY_DAYS,
            "deletion_reason": account.get("deletion_reason"),
        },
    )
    auth.clear_auth_cookie(response)
    return {
        "success": True,
        "message": "Your Learnora account is now deactivated. You can reactivate it within 30 days; after that, it will be permanently deleted.",
        "deactivation_until": deactivation_until.isoformat(),
    }


class ReactivateAccountRequest(BaseModel):
    token: str = Field(min_length=20, max_length=512)


@router.post("/reactivate")
def reactivate_account(payload: ReactivateAccountRequest, request: Request):
    raw_token = payload.token.strip()
    token_hash = auth._hash_token(raw_token)
    now = datetime.now(timezone.utc)
    updated = (
        auth.supabase.table("users")
        .update({
            "account_status": "active",
            "account_deactivation_until": None,
            "account_reactivation_token_hash": None,
            "account_reactivation_expires_at": None,
            "account_deletion_requested_at": None,
            "deletion_reason": None,
            "deletion_reason_details": None,
        })
        .eq("account_reactivation_token_hash", token_hash)
        .eq("account_status", "deactivation_pending")
        .gt("account_deactivation_until", now.isoformat())
        .gt("account_reactivation_expires_at", now.isoformat())
        .select("id,email,role")
        .execute()
    ).data or []
    if not updated:
        raise HTTPException(status_code=400, detail="This activation link is invalid, expired, or the recovery period has ended.")

    account = updated[0]
    auth.log_audit_event(
        action="learner_account_reactivated",
        email=account.get("email"),
        account_type="learner",
        role=account.get("role") or "normal",
        request=request,
        metadata={"user_id": account.get("id")},
    )
    return {"success": True, "message": "Your Learnora account has been reactivated. You can now sign in."}


@router.get("/finalize-expired")
def finalize_expired_account_deletions(authorization: str | None = Header(default=None)):
    enabled = os.getenv("ACCOUNT_DELETION_FINALIZER_ENABLED", "false").strip().lower() in {"1", "true", "yes"}
    if not enabled:
        return {"success": True, "enabled": False, "finalised": 0}
    expected = os.getenv("CRON_SECRET", "").strip()
    if not expected:
        raise HTTPException(status_code=503, detail="Account finalisation is not configured.")
    if not hmac.compare_digest(authorization or "", f"Bearer {expected}"):
        raise HTTPException(status_code=401, detail="Unauthorised.")
    now = datetime.now(timezone.utc)
    try:
        result = auth.supabase.rpc(
            "finalize_expired_learner_account_deletions",
            {"p_now": now.isoformat()},
        ).execute()
    except Exception as exc:
        print(f"Expired learner account finalisation failed: {type(exc).__name__}")
        raise HTTPException(status_code=503, detail="Account finalisation is temporarily unavailable.") from None
    count = result.data
    if isinstance(count, list) and count:
        count = next(iter(count[0].values()), 0) if isinstance(count[0], dict) else count[0]
    if isinstance(count, dict):
        count = next(iter(count.values()), 0)
    return {"success": True, "finalised": int(count or 0), "checked_at": now.isoformat()}


def create_marketing_unsubscribe_url(user_id: str) -> str:
    """Create an opaque, single-use unsubscribe URL for one marketing email."""
    eligible = (
        auth.supabase.table("users")
        .select("id")
        .eq("id", str(user_id))
        .eq("account_status", "active")
        .eq("email_verified", True)
        .eq("marketing_email_opt_in", True)
        .limit(1)
        .execute()
    ).data or []
    if not eligible:
        raise ValueError("Learner is not eligible for marketing email delivery.")

    raw_token = auth._generate_raw_token()
    auth.supabase.table("learner_marketing_unsubscribe_tokens").insert({
        "user_id": str(user_id),
        "token_hash": auth._hash_token(raw_token),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()
    return f"{auth.FRONTEND_URL}/unsubscribe#token={raw_token}"


@router.patch("/marketing-preferences")
def update_marketing_preferences(
    payload: MarketingPreferencesRequest,
    request: Request,
    user: auth.CurrentUser = Depends(auth.get_current_user),
):
    if user.account_type != "learner" or user.role != "normal" or not user.id:
        raise HTTPException(status_code=403, detail="Marketing preferences are available for individual learner accounts.")
    now = datetime.now(timezone.utc).isoformat()
    updates = {
        "marketing_email_opt_in": payload.enabled,
        "marketing_in_app_opt_in": payload.enabled,
    }
    if payload.enabled:
        updates.update({
            "marketing_consent_at": now,
            "marketing_consent_source": "account_settings",
            "marketing_unsubscribed_at": None,
        })
    else:
        # Keep the last consent evidence for audit; record withdrawal separately.
        updates["marketing_unsubscribed_at"] = now
    result = (
        auth.supabase.table("users")
        .update(updates)
        .eq("id", user.id)
        .eq("account_status", "active")
        .select("id")
        .execute()
    ).data or []
    if not result:
        raise HTTPException(status_code=409, detail="Marketing preferences could not be updated for this account.")
    if not payload.enabled:
        auth.supabase.table("learner_marketing_unsubscribe_tokens").update({
            "consumed_at": now,
        }).eq("user_id", user.id).is_("consumed_at", "null").execute()
    auth.log_audit_event(
        action="learner_marketing_consent_updated",
        email=user.email,
        account_type="learner",
        role=user.role,
        request=request,
        metadata={"marketing_email_opt_in": payload.enabled, "source": "account_settings"},
    )
    return {"success": True, "marketing_email_opt_in": payload.enabled}


@router.post("/marketing-unsubscribe")
def unsubscribe_from_marketing(
    payload: MarketingUnsubscribeRequest,
    request: Request,
):
    token_hash = auth._hash_token(payload.token.strip())
    token_rows = (
        auth.supabase.table("learner_marketing_unsubscribe_tokens")
        .select("id,user_id")
        .eq("token_hash", token_hash)
        .is_("consumed_at", "null")
        .limit(1)
        .execute()
    ).data or []
    if not token_rows:
        # Idempotent response: never disclose whether an address/account exists.
        return {"success": True, "message": "This email address has been unsubscribed from Learnora marketing emails."}

    token_record = token_rows[0]
    user_id = str(token_record["user_id"])
    now = datetime.now(timezone.utc).isoformat()
    result = (
        auth.supabase.table("users")
        .update({
            "marketing_email_opt_in": False,
            "marketing_in_app_opt_in": False,
            "marketing_unsubscribed_at": now,
        })
        .eq("id", user_id)
        .select("id,email,role")
        .execute()
    ).data or []

    # Consume every outstanding link for this learner. A future opt-in can
    # create new tokens without allowing old campaign links to become active.
    auth.supabase.table("learner_marketing_unsubscribe_tokens").update({
        "consumed_at": now,
    }).eq("user_id", user_id).is_("consumed_at", "null").execute()

    if result:
        account = result[0]
        auth.log_audit_event(
            action="learner_marketing_unsubscribed",
            email=account.get("email"),
            account_type="learner",
            role=account.get("role") or "normal",
            request=request,
            metadata={"source": "email_unsubscribe_link"},
        )
    return {"success": True, "message": "This email address has been unsubscribed from Learnora marketing emails."}

