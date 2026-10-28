"""Paystack webhook regression tests for deleted learner accounts and orphaned renewals."""
import hashlib
import hmac
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from starlette.requests import Request
from routers import webhooks


class Query:
    def __init__(self, db, table):
        self.db = db
        self.table_name = table
        self.filters = {}
        self.in_filters = {}
        self.limit_count = None
        self.operation = "select"
        self.payload = None

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, key, value):
        self.filters[key] = str(value)
        return self

    def in_(self, key, values):
        self.in_filters[key] = {str(value) for value in values}
        return self

    def order(self, *_args, **_kwargs):
        return self

    def limit(self, count):
        self.limit_count = count
        return self

    def update(self, payload):
        self.operation = "update"
        self.payload = payload
        return self

    def execute(self):
        rows = self.db.rows.get(self.table_name, [])
        matches = [row for row in rows if all(str(row.get(key)) == value for key, value in self.filters.items())]
        matches = [row for row in matches if all(str(row.get(key)) in values for key, values in self.in_filters.items())]
        if self.limit_count is not None:
            matches = matches[:self.limit_count]
        if self.operation == "update":
            for row in matches:
                row.update(self.payload or {})
            self.db.updates.append((self.table_name, dict(self.payload or {}), dict(self.filters)))
        return SimpleNamespace(data=matches)


class FakeSupabase:
    def __init__(self, rows=None):
        self.rows = rows or {}
        self.updates = []

    def table(self, name):
        return Query(self, name)


def signed_request(event):
    raw = json.dumps(event, separators=(",", ":")).encode("utf-8")
    secret = "webhook-test-secret"
    signature = hmac.new(secret.encode("utf-8"), raw, hashlib.sha512).hexdigest()
    async def receive():
        return {"type": "http.request", "body": raw, "more_body": False}
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "https",
        "path": "/paystack",
        "raw_path": b"/paystack",
        "query_string": b"",
        "headers": [(b"x-paystack-signature", signature.encode("ascii"))],
        "server": ("test", 443),
        "client": ("127.0.0.1", 12345),
    }
    return Request(scope, receive)


def invoice_event(code="SUB_orphan", token="email-token", email="deleted@example.com"):
    return {
        "event": "invoice.create",
        "data": {
            "customer": {"email": email, "customer_code": "CUS_test"},
            "subscription": {
                "subscription_code": code,
                "email_token": token,
            },
        },
    }


class PaystackOrphanCancellationTests(unittest.IsolatedAsyncioTestCase):
    async def test_unlinked_invoice_is_disabled_before_webhook_acknowledgement(self):
        db = FakeSupabase()
        disable = AsyncMock()
        with patch.dict(os.environ, {"PAYSTACK_SECRET_KEY": "webhook-test-secret"}), \
             patch.object(webhooks, "supabase", db), \
             patch.object(webhooks, "_linked_subscription", return_value=None), \
             patch.object(webhooks, "_disable_orphaned_subscription", disable):
            result = await webhooks.paystack_webhook(signed_request(invoice_event()))

        self.assertEqual(result, {"received": True, "orphaned_subscription_disabled": True})
        disable.assert_awaited_once_with("SUB_orphan", "email-token")
        self.assertEqual(db.updates, [])

    async def test_deleted_subscription_owner_triggers_provider_disable_and_local_cancel(self):
        db = FakeSupabase({
            "users": [],
            "learnora_subscriptions": [{
                "id": "subscription-row-1",
                "user_id": "deleted-user-1",
                "status": "active",
                "provider_subscription_code": "SUB_orphan",
                "provider_email_token": "email-token",
            }],
        })
        linked = {
            "id": "subscription-row-1",
            "user_id": "deleted-user-1",
            "status": "active",
            "provider_subscription_code": "SUB_orphan",
            "provider_email_token": "email-token",
            "current_period_end": None,
        }
        disable = AsyncMock()
        with patch.dict(os.environ, {"PAYSTACK_SECRET_KEY": "webhook-test-secret"}), \
             patch.object(webhooks, "supabase", db), \
             patch.object(webhooks, "_linked_subscription", return_value=linked), \
             patch.object(webhooks, "_disable_orphaned_subscription", disable):
            result = await webhooks.paystack_webhook(signed_request(invoice_event()))

        self.assertEqual(result, {"received": True, "orphaned_subscription_disabled": True})
        disable.assert_awaited_once_with("SUB_orphan", "email-token")
        self.assertEqual(db.rows["learnora_subscriptions"][0]["status"], "cancelled")
        self.assertEqual(db.rows["learnora_subscriptions"][0]["cancelled_at"] is not None, True)


    async def test_duplicate_subscription_create_does_not_replace_existing_provider_agreement(self):
        db = FakeSupabase({
            "users": [{
                "id": "learner-1",
                "email": "learner@example.com",
                "role": "normal",
                "email_verified_at": "2026-01-01T00:00:00Z",
                "sub_status": "active",
            }],
            "learnora_subscriptions": [{
                "id": "subscription-row-existing",
                "user_id": "learner-1",
                "status": "active",
                "provider": "paystack",
                "provider_subscription_code": "SUB_existing",
                "provider_email_token": "existing-token",
            }],
        })
        event = {
            "event": "subscription.create",
            "data": {
                "customer": {
                    "email": "learner@example.com",
                    "customer_code": "CUS_test",
                },
                "subscription_code": "SUB_duplicate",
                "email_token": "duplicate-token",
                "plan": {
                    "plan_code": "PLN_monthly",
                    "interval": "monthly",
                    "amount": 1200000,
                    "currency": "NGN",
                },
            },
        }
        disable = AsyncMock()
        with (
            patch.dict(os.environ, {"PAYSTACK_SECRET_KEY": "webhook-test-secret"}),
            patch.object(webhooks, "supabase", db),
            patch.object(webhooks, "_disable_orphaned_subscription", disable),
        ):
            result = await webhooks.paystack_webhook(signed_request(event))

        self.assertEqual(result, {"received": True, "duplicate_subscription_disabled": True})
        disable.assert_awaited_once_with("SUB_duplicate", "duplicate-token")
        self.assertEqual(
            db.rows["learnora_subscriptions"][0]["provider_subscription_code"],
            "SUB_existing",
        )
        self.assertEqual(db.updates, [])

    async def test_cancelled_subscription_invoice_is_disabled_without_reactivation(self):
        db = FakeSupabase({
            "learnora_subscriptions": [{
                "id": "subscription-row-2",
                "user_id": "learner-2",
                "status": "cancelled",
                "provider_subscription_code": "SUB_cancelled",
                "provider_email_token": "cancel-token",
            }],
        })
        linked = {
            "id": "subscription-row-2",
            "user_id": "learner-2",
            "status": "cancelled",
            "provider_subscription_code": "SUB_cancelled",
            "provider_email_token": "cancel-token",
            "current_period_end": "2026-11-28T00:00:00Z",
        }
        disable = AsyncMock()
        with patch.dict(os.environ, {"PAYSTACK_SECRET_KEY": "webhook-test-secret"}), patch.object(webhooks, "supabase", db), patch.object(webhooks, "_linked_subscription", return_value=linked), patch.object(webhooks, "_disable_orphaned_subscription", disable):
            result = await webhooks.paystack_webhook(signed_request(invoice_event("SUB_cancelled", "cancel-token")))

        self.assertEqual(result, {
            "received": True,
            "terminal_subscription_unchanged": True,
            "provider_renewal_disabled": True,
        })
        disable.assert_awaited_once_with("SUB_cancelled", "cancel-token")
        self.assertEqual(db.rows["learnora_subscriptions"][0]["status"], "cancelled")
        self.assertEqual(db.updates, [])

    async def test_late_success_event_cannot_reactivate_cancelled_subscription(self):
        db = FakeSupabase({
            "users": [{"id": "learner-2", "role": "normal", "email_verified_at": "2026-01-01T00:00:00Z", "sub_status": "expired", "is_paid": False}],
            "learnora_subscriptions": [{
                "id": "subscription-row-2",
                "user_id": "learner-2",
                "status": "cancelled",
                "provider_subscription_code": "SUB_cancelled",
                "provider_email_token": "cancel-token",
            }],
        })
        linked = {
            "id": "subscription-row-2",
            "user_id": "learner-2",
            "status": "cancelled",
            "provider_subscription_code": "SUB_cancelled",
            "provider_email_token": "cancel-token",
            "current_period_end": "2026-11-28T00:00:00Z",
        }
        event = invoice_event("SUB_cancelled", "cancel-token", "learner@example.com")
        event["event"] = "charge.success"
        disable = AsyncMock()
        with patch.dict(os.environ, {"PAYSTACK_SECRET_KEY": "webhook-test-secret"}), patch.object(webhooks, "supabase", db), patch.object(webhooks, "_linked_subscription", return_value=linked), patch.object(webhooks, "_disable_orphaned_subscription", disable):
            result = await webhooks.paystack_webhook(signed_request(event))

        self.assertEqual(result, {"received": True, "terminal_subscription_unchanged": True})
        disable.assert_not_awaited()
        self.assertEqual(db.rows["learnora_subscriptions"][0]["status"], "cancelled")
        self.assertEqual(db.rows["users"][0]["sub_status"], "expired")
        self.assertEqual(db.updates, [])


if __name__ == "__main__":
    unittest.main()
