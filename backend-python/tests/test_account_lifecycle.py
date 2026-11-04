"""Account deletion confirmation and retained-history regression contracts."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class AccountLifecycleContractTests(unittest.TestCase):
    def test_deletion_requires_a_single_use_email_confirmation(self):
        source = (ROOT / "backend-python/routers/account_lifecycle.py").read_text(encoding="utf-8")
        self.assertIn('@router.post("/request-deletion")', source)
        self.assertIn('@router.post("/confirm-deletion")', source)
        self.assertIn("auth._generate_raw_token()", source)
        self.assertIn("auth._hash_token(raw_token)", source)
        self.assertIn("DELETION_TOKEN_TTL_MINUTES = 60", source)
        self.assertIn("ConfirmDeletionRequest", source)

    def test_organisation_and_cohort_members_must_be_released_before_self_deletion(self):
        source = (ROOT / "backend-python/routers/account_lifecycle.py").read_text(encoding="utf-8")
        guard = source.split("def _require_individual_learner(", 1)[1].split("@router.post(\"/request-deletion\")", 1)[0]
        self.assertIn('table("organisation_members")', guard)
        self.assertIn('table("cohort_members")', guard)
        self.assertIn('if (', guard)
        self.assertIn("organisation must release the account", guard)

    def test_active_recurring_subscriptions_are_cancelled_before_deletion(self):
        source = (ROOT / "backend-python/routers/account_lifecycle.py").read_text(encoding="utf-8")
        cancel_at = source.index("billing.cancel_learner_subscription(learner)")
        finalize_at = source.index('auth.supabase.rpc(\n        "complete_learner_account_deletion"')
        self.assertLess(cancel_at, finalize_at)
        self.assertIn('["active", "past_due", "paused"]', source)

    def test_history_is_retained_without_preserving_authentication_secrets(self):
        migration = (ROOT / "supabase/migrations/20261102130000_learner_account_deletion.sql").read_text(encoding="utf-8")
        self.assertIn("CREATE TABLE IF NOT EXISTS public.deleted_account_history", migration)
        self.assertIn("original_user_id uuid NOT NULL UNIQUE", migration)
        self.assertIn("account_snapshot jsonb NOT NULL", migration)
        self.assertIn("password_hash = NULL", migration)
        self.assertIn("account_status = 'deleted'", migration)
        self.assertIn("SET status = 'suspended'", migration)
        self.assertIn("expires_at = NULL", migration)
        self.assertIn("trial_ends_at = NULL", migration)
        self.assertIn("email = 'deleted+'", migration)
        self.assertNotIn("DELETE FROM PUBLIC.USERS", migration.upper())

    def test_account_deletion_history_is_not_browser_readable(self):
        migration = (ROOT / "supabase/migrations/20261102130000_learner_account_deletion.sql").read_text(encoding="utf-8")
        self.assertIn("ENABLE ROW LEVEL SECURITY", migration)
        self.assertIn("REVOKE ALL ON public.deleted_account_history FROM PUBLIC, anon, authenticated", migration)
        self.assertIn("GRANT ALL ON public.deleted_account_history TO service_role", migration)

    def test_learner_settings_and_confirmation_page_are_connected(self):
        settings = (ROOT / "frontend-v02/components/dashboard/AccountSettings.tsx").read_text(encoding="utf-8")
        confirmation = (ROOT / "frontend-v02/app/confirm-account-deletion/page.tsx").read_text(encoding="utf-8")
        self.assertIn("/account-lifecycle/request-deletion", settings)
        self.assertIn("Request account deletion", settings)
        self.assertIn("/account-lifecycle/confirm-deletion", confirmation)
        self.assertIn("mailto:learnorame@gmail.com", confirmation)


if __name__ == "__main__":
    unittest.main()
