"""Regression contracts for learner-only subscription cancellation."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from pathlib import Path

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import billing, auth

ROOT = Path(__file__).resolve().parents[2]


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows
        self.updated = []

    def select(self, *_args, **_kwargs): return self
    def eq(self, *_args, **_kwargs): return self
    def in_(self, *_args, **_kwargs): return self
    def order(self, *_args, **_kwargs): return self
    def limit(self, *_args, **_kwargs): return self

    def update(self, fields):
        self.updated.append(fields)
        return self

    def execute(self):
        return SimpleNamespace(data=self.rows)


class FakeSupabase:
    def __init__(self, rows):
        self.query = FakeQuery(rows)

    def table(self, _name):
        return self.query


class SubscriptionCancellationTests(unittest.TestCase):
    def setUp(self):
        self.user = auth.CurrentUser(
            id="learner-1",
            email="learner@example.com",
            role="normal",
            sub_status="active",
            account_type="learner",
            is_paid=True,
        )

    def test_subscription_read_never_exposes_provider_cancellation_token(self):
        row = {
            "id": "subscription-1",
            "status": "active",
            "plan_code": "monthly",
            "billing_interval": "monthly",
            "currency": "NGN",
            "amount_minor": 1200000,
            "provider": "paystack",
            "current_period_end": "2026-11-28T00:00:00Z",
            "cancelled_at": None,
            "provider_subscription_code": "SUB_test",
            "provider_email_token": "secret-token",
        }
        client = FakeSupabase([row])
        with patch.object(billing, "supabase", client):
            result = billing.get_learner_subscription(self.user)
        self.assertTrue(result["can_cancel"])
        self.assertNotIn("provider_email_token", result)
        self.assertNotIn("provider_subscription_code", result)

    def test_cancel_calls_paystack_before_marking_local_record_cancelled(self):
        row = {
            "id": "subscription-1",
            "status": "active",
            "provider": "paystack",
            "provider_subscription_code": "SUB_test",
            "provider_email_token": "secret-token",
            "current_period_end": "2026-11-28T00:00:00Z",
        }
        client = FakeSupabase([row])
        with patch.object(billing, "supabase", client), patch.object(
            billing, "_disable_paystack_subscription", return_value={}
        ) as disable:
            result = billing.cancel_learner_subscription(self.user)
        disable.assert_called_once_with("SUB_test", "secret-token")
        self.assertEqual(client.query.updated[0]["status"], "cancelled")
        self.assertEqual(result["cancelled_count"], 1)

    def test_missing_provider_cancellation_credentials_do_not_claim_success(self):
        row = {
            "id": "subscription-1",
            "status": "active",
            "provider": "paystack",
            "provider_subscription_code": None,
            "provider_email_token": None,
        }
        client = FakeSupabase([row])
        with patch.object(billing, "supabase", client), patch.object(
            billing, "_disable_paystack_subscription"
        ) as disable:
            with self.assertRaises(HTTPException) as raised:
                billing.cancel_learner_subscription(self.user)
        self.assertEqual(raised.exception.status_code, 409)
        disable.assert_not_called()
        self.assertEqual(client.query.updated, [])

    def test_non_learner_cannot_manage_individual_subscription(self):
        staff = auth.CurrentUser(
            id="staff-1",
            email="staff@example.com",
            role="staff_admin",
            sub_status="active",
            account_type="admin",
        )
        with self.assertRaises(HTTPException) as raised:
            billing.get_learner_subscription(staff)
        self.assertEqual(raised.exception.status_code, 403)

    def test_login_and_dashboard_loading_use_skeletons_in_frontend_v02(self):
        login = (ROOT / "frontend-v02/app/login/page.tsx").read_text(encoding="utf-8")
        dashboard = (ROOT / "frontend-v02/app/dashboard/page.tsx").read_text(encoding="utf-8")
        sections = (ROOT / "frontend-v02/app/dashboard/[section]/page.tsx").read_text(encoding="utf-8")
        self.assertIn('import Skeleton from "../../components/feedback/Skeleton"', login)
        self.assertIn('if (busy) return <main', login)
        self.assertIn('if(!u||loading)return <Shell active="overview"><Skeleton', dashboard)
        self.assertIn('Skeleton variant="compact"', sections)

    def test_subscription_page_is_linked_and_calls_authenticated_backend(self):
        page = (ROOT / "frontend-v02/app/dashboard/subscription/page.tsx").read_text(encoding="utf-8")
        sidebar = (ROOT / "frontend-v02/components/dashboard/Sidebar.tsx").read_text(encoding="utf-8")
        self.assertIn('["subscription","Subscription",CreditCard]', sidebar)
        self.assertIn('request<Subscription>("/billing/subscription")', page)
        self.assertIn('request<any>("/billing/subscription/cancel"', page)
        self.assertIn('role="dialog"', page)
        self.assertIn('aria-modal="true"', page)
        self.assertIn('Confirm cancellation', page)
        self.assertNotIn("window.confirm(", page)

    def test_provider_credentials_are_server_only_and_webhooks_guard_orphans(self):
        migration = (ROOT / "supabase/migrations/20261028171902_paystack_subscription_cancellation.sql").read_text(encoding="utf-8")
        webhook = (ROOT / "backend-python/routers/webhooks.py").read_text(encoding="utf-8")
        self.assertIn("provider_subscription_code", migration)
        self.assertIn("provider_email_token", migration)
        self.assertIn("_disable_orphaned_subscription", webhook)
        self.assertIn('event_type == "invoice.create"', webhook)
        terminal_branch = webhook[webhook.index('if existing_by_code and existing_by_code[0].get("status") in {"cancelled", "expired"}:'):webhook.index("existing = existing_by_code or", webhook.index('if existing_by_code and existing_by_code[0].get("status") in {"cancelled", "expired"}:'))]
        self.assertIn("await _disable_orphaned_subscription(code, email_token)", terminal_branch)
        self.assertNotIn('.update(\n                {"sub_status": "active", "is_paid": True}).eq("email", email)', webhook)


if __name__ == "__main__":
    unittest.main()
