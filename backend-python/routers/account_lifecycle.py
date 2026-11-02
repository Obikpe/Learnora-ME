from datetime import datetime, timedelta, timezone
from html import escape

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from routers import auth, billing

router = APIRouter(prefix="/api/account-lifecycle", tags=["account lifecycle"])

DELETION_TOKEN_TTL_MINUTES = 60


class ConfirmDeletionRequest(BaseModel):
    token: str = Field(min_length=20, max_length=512)


def _require_individual_learner(user: auth.CurrentUser) -> None:
    if user.account_type != "learner" or user.role != "normal" or not user.id:
        raise HTTPException(
            status_code=403,
            detail="Account deletion is available for individual learner accounts. Contact Learnora support for assistance.",
        )


@router.post("/request-deletion")
def request_account_deletion(
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
        })
        .eq("id", user.id)
        .in_("account_status", ["active", "deletion_pending"])
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
        "Your account will not be deleted unless you open this link. "
        "Any active recurring Learnora subscription will be cancelled before deletion is completed. "
        "A limited account record and associated learning history will be retained for legitimate record-keeping.\n\n"
        "If you did not request this, ignore this email and your account will remain available.\n\n"
        "Learnora ME"
    )
    html_body = f"""<!doctype html>
<html><body style="margin:0;background:#f5f7fb;font-family:Arial,sans-serif;color:#172033">
<div style="max-width:600px;margin:40px auto;padding:32px;background:#fff;border:1px solid #e5e7eb;border-radius:18px">
<h1 style="margin:0 0 16px">Confirm account deletion</h1>
<p>Hi {safe_display_name},</p>
<p>We received a request to delete your Learnora account. This action will sign you out and remove access to your account.</p>
<p style="margin:28px 0"><a href="{confirmation_url}" style="display:inline-block;padding:14px 22px;border-radius:10px;background:#172033;color:#fff;text-decoration:none;font-weight:bold">Confirm account deletion</a></p>
<p style="font-size:13px;line-height:1.6;color:#64748b">This secure link expires in 60 minutes. Your account will not be deleted unless you confirm. Active recurring Learnora subscriptions will be cancelled before deletion is completed.</p>
<p style="font-size:13px;line-height:1.6;color:#64748b">A limited account record and associated learning history will be retained for legitimate record-keeping.</p>
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
    )
    return {
        "success": True,
        "message": "We sent a confirmation link to your email address. Your account will remain active until you confirm.",
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
        .select("id,email,name,role,sub_status,is_paid,account_status,account_deletion_expires_at")
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

    auth.log_audit_event(
        action="learner_account_deleted",
        email=account["email"],
        account_type="learner",
        role=account.get("role") or "normal",
        request=request,
        metadata={"user_id": learner.id, "history_retained": True},
    )
    auth.clear_auth_cookie(response)
    return {
        "success": True,
        "message": "Your Learnora account has been deleted.",
    }
