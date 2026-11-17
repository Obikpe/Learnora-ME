"""Verified payment-provider webhooks.

Recurring Paystack events are mapped to an existing Learnora learner identity.
A provider subscription is never allowed to activate an account by email alone.
"""
import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException, Request

from routers.auth import LEGACY_ASSIGNED_LEARNER_ROLE, supabase

router = APIRouter()
log = logging.getLogger("paystack_webhooks")
PAYSTACK_BASE = "https://api.paystack.co"
LEARNER_ROLES = {"normal", LEGACY_ASSIGNED_LEARNER_ROLE}


def _subscription_details(data: dict) -> dict:
    """Paystack sends subscription details nested on invoice/charge events."""
    nested = data.get("subscription")
    return nested if isinstance(nested, dict) else data


def _subscription_code(data: dict) -> str:
    details = _subscription_details(data)
    return str(details.get("subscription_code") or data.get("subscription_code") or "").strip()


async def _disable_orphaned_subscription(code: str, email_token: str) -> None:
    """Stop provider billing when its event has no eligible Learnora account."""
    secret = (os.getenv("PAYSTACK_SECRET_KEY") or "").strip().strip('"').strip("'")
    if not secret or not code or not email_token:
        log.error("Cannot automatically stop orphaned Paystack subscription: required provider credentials are missing")
        raise HTTPException(503, "Orphaned subscription cancellation requires provider reconciliation.")
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{PAYSTACK_BASE}/subscription/disable",
                headers={"Authorization": f"Bearer {secret}", "Content-Type": "application/json"},
                json={"code": code, "token": email_token},
            )
            response.raise_for_status()
            result = response.json()
    except (httpx.HTTPError, ValueError):
        log.exception("Failed to disable orphaned Paystack subscription")
        raise HTTPException(503, "Could not stop an orphaned Paystack subscription yet; retry webhook delivery.")
    if not isinstance(result, dict) or not result.get("status"):
        log.error("Paystack did not confirm cancellation of an orphaned subscription")
        raise HTTPException(503, "Paystack did not confirm cancellation of the orphaned subscription.")


def _linked_subscription(code: str) -> dict | None:
    if not code:
        return None
    result = (
        supabase.table("learnora_subscriptions")
        .select("id,user_id,status,provider_subscription_code,provider_email_token,current_period_end")
        .eq("provider_subscription_code", code)
        .limit(1)
        .execute()
    )
    rows = result.data or []
    return rows[0] if rows else None


@router.post("/paystack")
async def paystack_webhook(request: Request):
    raw = await request.body()
    secret = (os.getenv("PAYSTACK_SECRET_KEY") or "").strip().strip('"').strip("'")
    expected = hmac.new(secret.encode(), raw, hashlib.sha512).hexdigest()
    signature = request.headers.get("x-paystack-signature", "")
    if not secret or not hmac.compare_digest(signature.encode("utf-8"), expected.encode("ascii")):
        raise HTTPException(401, "Invalid signature")

    try:
        event = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(400, "Invalid JSON payload")

    if not isinstance(event, dict):
        raise HTTPException(400, "Invalid event payload")

    event_type = str(event.get("event") or "")
    data = event.get("data") or {}
    if not isinstance(data, dict):
        raise HTTPException(400, "Invalid event data")

    customer = data.get("customer") or {}
    if not isinstance(customer, dict):
        customer = {}
    email = str(customer.get("email") or "").lower().strip()
    customer_code = str(customer.get("customer_code") or "").strip()
    details = _subscription_details(data)
    code = _subscription_code(data)
    email_token = str(details.get("email_token") or data.get("email_token") or "").strip()
    now = datetime.now(timezone.utc).isoformat()

    # A subscription creation event is the source of the Paystack subscription
    # code and email token required to actually stop future automatic charges.
    if event_type == "subscription.create":
        if not code or not email_token or not email:
            log.error("Paystack subscription.create omitted required account/subscription identifiers")
            raise HTTPException(503, "Subscription event is missing required identifiers; provider reconciliation is needed.")
        try:
            user_result = (
                supabase.table("users")
                .select("id,email,role,email_verified_at,sub_status")
                .eq("email", email)
                .limit(1)
                .execute()
            )
            users = user_result.data or []
        except Exception:
            log.exception("Could not look up Learnora account for subscription event")
            raise HTTPException(503, "Could not reconcile the subscription event yet.")

        eligible = bool(
            users
            and users[0].get("role") in LEARNER_ROLES
            and users[0].get("email_verified_at")
        )
        if not eligible:
            # Deleting the Learnora row does not cancel a provider-side agreement.
            # Actively disable the orphan rather than acknowledging it and leaving
            # recurring charges running.
            await _disable_orphaned_subscription(code, email_token)
            return {"received": True, "orphaned_subscription_disabled": True}

        user = users[0]
        plan = data.get("plan") if isinstance(data.get("plan"), dict) else {}
        next_payment = details.get("next_payment_date") or data.get("next_payment_date")
        try:
            existing_by_code = (
                supabase.table("learnora_subscriptions")
                .select("id,user_id,status")
                .eq("provider_subscription_code", code)
                .limit(1)
                .execute()
                .data or []
            )
            if existing_by_code and str(existing_by_code[0].get("user_id")) != str(user["id"]):
                await _disable_orphaned_subscription(code, email_token)
                return {"received": True, "orphaned_subscription_disabled": True}
            if existing_by_code and existing_by_code[0].get("status") in {"cancelled", "expired"}:
                # A delayed/retried create event must not resurrect local access.
                # Also disable the provider-side agreement: a terminal local row
                # alone cannot guarantee that Paystack has stopped renewal.
                await _disable_orphaned_subscription(code, email_token)
                return {
                    "received": True,
                    "terminal_subscription_unchanged": True,
                    "provider_renewal_disabled": True,
                }
            existing = existing_by_code
            if not existing:
                active_rows = (
                    supabase.table("learnora_subscriptions")
                    .select(
                        "id,user_id,status,provider,provider_subscription_code,"
                        "provider_email_token"
                    )
                    .eq("user_id", user["id"])
                    .in_("status", ["active", "past_due", "paused"])
                    .order("created_at", desc=True)
                    .limit(20)
                    .execute()
                    .data or []
                )
                # A repeated checkout can create a second provider subscription.
                # Never overwrite a different active provider agreement: doing so
                # would lose the only local code/token that can stop its renewal.
                # Keep a legacy Paystack row without a code eligible for linking,
                # because older verification flows created that row before the
                # subscription.create webhook supplied the recurring identifiers.
                conflicting = any(
                    (
                        row.get("provider_subscription_code")
                        and str(row.get("provider_subscription_code")) != code
                    )
                    or (
                        row.get("provider")
                        and row.get("provider") != "paystack"
                    )
                    for row in active_rows
                )
                if conflicting:
                    await _disable_orphaned_subscription(code, email_token)
                    return {
                        "received": True,
                        "duplicate_subscription_disabled": True,
                    }
                existing = active_rows[:1]
            subscription_fields = {
                "provider": "paystack",
                "provider_customer_id": customer_code or None,
                "provider_subscription_code": code,
                "provider_email_token": email_token,
                "status": "active",
                "updated_at": now,
            }
            if next_payment:
                subscription_fields["current_period_end"] = next_payment
            if plan.get("plan_code"):
                subscription_fields["plan_code"] = plan["plan_code"]
            if plan.get("interval"):
                subscription_fields["billing_interval"] = "yearly" if plan["interval"] == "annually" else plan["interval"]
            if data.get("currency") or plan.get("currency"):
                subscription_fields["currency"] = str(data.get("currency") or plan.get("currency")).upper()
            if data.get("amount") is not None or plan.get("amount") is not None:
                subscription_fields["amount_minor"] = int(data.get("amount") or plan.get("amount") or 0)

            if existing:
                supabase.table("learnora_subscriptions").update(subscription_fields).eq("id", existing[0]["id"]).eq("user_id", user["id"]).execute()
            else:
                supabase.table("learnora_subscriptions").insert({
                    **subscription_fields,
                    "user_id": user["id"],
                    "starts_at": now,
                    "current_period_start": now,
                }).execute()
            # Only a currently existing, verified learner row is updated.
            user_fields = {"sub_status": "active", "is_paid": True, "subscription_tier": "paid"}
            if next_payment:
                user_fields["expires_at"] = next_payment
            supabase.table("users").update(user_fields).eq("id", user["id"]).execute()
        except Exception:
            log.exception("Failed to persist Learnora subscription event")
            raise HTTPException(503, "Subscription event could not be saved yet.")
        return {"received": True}

    if event_type in {"subscription.not_renew", "subscription.disable", "invoice.create", "invoice.payment_failed", "invoice.update", "charge.success"}:
        try:
            linked = _linked_subscription(code)
        except Exception:
            log.exception("Failed mapping Paystack event to Learnora subscription")
            raise HTTPException(503, "Subscription event could not be reconciled yet.")

        if not linked and event_type == "invoice.create" and customer_code:
            # Older records may predate saving the Paystack subscription code.
            # Reconcile a single unambiguous active record by its provider
            # customer code before treating the invoice as orphaned.
            try:
                legacy_rows = (
                    supabase.table("learnora_subscriptions")
                    .select("id,user_id,status,provider_subscription_code,provider_email_token,current_period_end")
                    .eq("provider_customer_id", customer_code)
                    .in_("status", ["active", "past_due", "paused"])
                    .order("created_at", desc=True)
                    .limit(2)
                    .execute()
                    .data or []
                )
                if len(legacy_rows) == 1:
                    candidate = legacy_rows[0]
                    updates = {
                        "provider": "paystack",
                        "provider_subscription_code": code,
                        "provider_email_token": email_token,
                        "updated_at": now,
                    }
                    next_payment = details.get("next_payment_date") or data.get("next_payment_date")
                    if next_payment:
                        updates["current_period_end"] = next_payment
                    supabase.table("learnora_subscriptions").update(updates).eq("id", candidate["id"]).eq("user_id", candidate["user_id"]).execute()
                    linked = {**candidate, "provider_subscription_code": code, "provider_email_token": email_token}
            except Exception:
                log.exception("Could not reconcile legacy Paystack subscription")
                raise HTTPException(503, "Could not reconcile the recurring invoice yet.")

        if not linked:
            # A recurring invoice without a local Learnora subscription is not
            # authorised to charge an account. Stop it before the debit where
            # the invoice event provides the provider's cancellation token.
            if event_type == "invoice.create":
                await _disable_orphaned_subscription(code, email_token)
                return {"received": True, "orphaned_subscription_disabled": True}
            # Never grant or change access based on a matching email alone.
            return {"received": True, "unlinked": True}

        user_id = linked["user_id"]

        # A terminal local subscription must never be reactivated by a delayed
        # provider event. invoice.create arrives before the scheduled debit, so
        # actively disable provider renewal and preserve the terminal state.
        if linked.get("status") in {"cancelled", "expired"} and event_type in {
            "invoice.create", "invoice.payment_failed", "invoice.update", "charge.success"
        }:
            if event_type == "invoice.create":
                disable_code = code or str(linked.get("provider_subscription_code") or "")
                disable_token = email_token or str(linked.get("provider_email_token") or "")
                await _disable_orphaned_subscription(disable_code, disable_token)
                return {
                    "received": True,
                    "terminal_subscription_unchanged": True,
                    "provider_renewal_disabled": True,
                }
            log.warning(
                "Ignoring %s for terminal subscription %s; local access remains terminal",
                event_type,
                linked.get("id"),
            )
            return {"received": True, "terminal_subscription_unchanged": True}

        # A deleted, unverified, or non-learner account must not continue
        # generating recurring invoices. invoice.create arrives before the
        # scheduled debit, so disable at this point rather than waiting for
        # charge.success or an account-deletion cleanup job.
        if event_type in {"invoice.create", "invoice.payment_failed", "invoice.update", "charge.success"}:
            try:
                owner_result = (
                    supabase.table("users")
                    .select("id,role,email_verified_at")
                    .eq("id", user_id)
                    .limit(1)
                    .execute()
                )
                owners = owner_result.data or []
            except Exception:
                log.exception("Could not verify account ownership for recurring Paystack event")
                raise HTTPException(503, "Could not verify subscription owner yet.")
            owner_ok = bool(
                owners
                and owners[0].get("role") in LEARNER_ROLES
                and owners[0].get("email_verified_at")
            )
            if not owner_ok:
                disable_code = code or str(linked.get("provider_subscription_code") or "")
                disable_token = email_token or str(linked.get("provider_email_token") or "")
                await _disable_orphaned_subscription(disable_code, disable_token)
                try:
                    supabase.table("learnora_subscriptions").update({
                        "status": "cancelled",
                        "cancelled_at": now,
                        "updated_at": now,
                    }).eq("id", linked["id"]).execute()
                except Exception:
                    log.exception("Provider cancellation succeeded but local orphan status update failed")
                    raise HTTPException(503, "Provider cancellation succeeded; local status reconciliation will be retried.")
                return {"received": True, "orphaned_subscription_disabled": True}

        try:
            if event_type == "subscription.not_renew":
                supabase.table("learnora_subscriptions").update({
                    "status": "cancelled",
                    "cancelled_at": now,
                    "updated_at": now,
                }).eq("id", linked["id"]).execute()
                # Keep current access through the already-paid period.
            elif event_type == "subscription.disable":
                supabase.table("learnora_subscriptions").update({
                    "status": "cancelled",
                    "cancelled_at": now,
                    "updated_at": now,
                }).eq("id", linked["id"]).execute()
                supabase.table("users").update({
                    "sub_status": "expired",
                    "is_paid": False,
                    "subscription_tier": "free",
                }).eq("id", user_id).execute()
            elif event_type == "invoice.payment_failed":
                supabase.table("learnora_subscriptions").update({
                    "status": "past_due",
                    "updated_at": now,
                }).eq("id", linked["id"]).execute()
                supabase.table("users").update({
                    "sub_status": "past_due",
                    "is_paid": False,
                }).eq("id", user_id).execute()
            elif event_type in {"invoice.update", "charge.success"}:
                invoice_status = str(data.get("status") or "").lower()
                successful = event_type == "charge.success" or (invoice_status in {"success", "paid"} and data.get("paid") in (True, 1, "1"))
                if successful:
                    next_payment = details.get("next_payment_date") or data.get("next_payment_date")
                    fields = {"status": "active", "updated_at": now}
                    user_fields = {"sub_status": "active", "is_paid": True, "subscription_tier": "paid"}
                    if next_payment:
                        fields["current_period_end"] = next_payment
                        user_fields["expires_at"] = next_payment
                    supabase.table("learnora_subscriptions").update(fields).eq("id", linked["id"]).execute()
                    supabase.table("users").update(user_fields).eq("id", user_id).execute()
        except Exception:
            log.exception("Failed applying Paystack subscription status event")
            raise HTTPException(503, "Subscription status could not be updated yet.")

    # One-off initial charges are handled by the signed-in verify-payment route.
    # Do not let charge.success reactivate arbitrary accounts by email.
    return {"received": True}
