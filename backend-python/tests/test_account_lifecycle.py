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

    def test_managed_identity_is_rechecked_when_confirmation_link_is_used(self):
        source = (ROOT / "backend-python/routers/account_lifecycle.py").read_text(encoding="utf-8")
        confirmation = source.split('def confirm_account_deletion(', 1)[1]
        self.assertIn("auth._active_organisation_context(", confirmation)
        self.assertIn("fail_closed=True", confirmation)
        self.assertIn("organisation must release the account", confirmation)

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

    def test_confirmed_deletion_starts_a_30_day_recovery_period(self):
        source = (ROOT / "backend-python/routers/account_lifecycle.py").read_text(encoding="utf-8")
        migration = (ROOT / "supabase/migrations/20261109180000_learner_deletion_grace_and_marketing_consent.sql").read_text(encoding="utf-8")
        self.assertIn("ACCOUNT_RECOVERY_DAYS = 30", source)
        self.assertIn('@router.post("/reactivate")', source)
        self.assertIn('@router.get("/finalize-expired")', source)
        self.assertIn("account_status = 'deactivation_pending'", migration)
        self.assertIn("p_deleted_at + interval '30 days'", migration)
        self.assertIn("finalize_expired_learner_account_deletions", migration)
        self.assertIn("FOR UPDATE SKIP LOCKED", migration)

    def test_signup_routes_recoverable_accounts_to_email_reactivation(self):
        source = (ROOT / "backend-python/routers/auth.py").read_text(encoding="utf-8")
        registration = source.split('"/register"', 1)[1].split("# VERIFY EMAIL", 1)[0]
        self.assertIn('account_status") == "deactivation_pending"', registration)
        self.assertIn("/reactivate-account#token=", registration)
        self.assertIn("account_reactivation_expires_at", registration)
        self.assertIn("marketing_email_opt_in: bool = False", source)

    def test_marketing_consent_is_optional_and_can_be_withdrawn(self):
        migration = (ROOT / "supabase/migrations/20261109180000_learner_deletion_grace_and_marketing_consent.sql").read_text(encoding="utf-8")
        lifecycle = (ROOT / "backend-python/routers/account_lifecycle.py").read_text(encoding="utf-8")
        signup = (ROOT / "frontend-v02/app/register/page.tsx").read_text(encoding="utf-8")
        self.assertIn("marketing_email_opt_in boolean NOT NULL DEFAULT false", migration)
        self.assertIn("marketing_in_app_opt_in boolean NOT NULL DEFAULT false", migration)
        self.assertIn("learner_marketing_unsubscribe_tokens", migration)
        self.assertIn('@router.patch("/marketing-preferences")', lifecycle)
        self.assertIn('@router.post("/marketing-unsubscribe")', lifecycle)
        self.assertIn("auth._hash_token(raw_token)", lifecycle)
        self.assertIn("ACCOUNT_DELETION_FINALIZER_ENABLED", lifecycle)
        self.assertIn("marketingEmailOptIn,setMarketingEmailOptIn]=useState(false)", signup)
        self.assertIn("marketing_email_opt_in: marketingEmailOptIn", (ROOT / "frontend-v02/lib/api/auth.ts").read_text(encoding="utf-8"))

    def test_deletion_reasons_are_visible_to_authorised_admins(self):
        admin = (ROOT / "backend-python/routers/admin.py").read_text(encoding="utf-8")
        frontend = (ROOT / "frontend-v02/app/dashboard/admin/[section]/page.tsx").read_text(encoding="utf-8")
        self.assertIn('@router.get("/account-lifecycle")', admin)
        self.assertIn("deletion_reason_details", admin)
        self.assertIn("Account deletion activity", frontend)
        self.assertIn("deletion_reason", frontend)

    def test_mobile_drawer_and_notification_preview_render_outside_header(self):
        sidebar = (ROOT / "frontend-v02/components/dashboard/Sidebar.tsx").read_text(encoding="utf-8")
        topbar = (ROOT / "frontend-v02/components/dashboard/Topbar.tsx").read_text(encoding="utf-8")
        self.assertIn("createPortal", sidebar)
        self.assertIn("document.body", sidebar)
        self.assertIn("createPortal", topbar)
        self.assertIn("top-[4.5rem]", topbar)
        self.assertIn("w-[min(22rem,100vw)]", topbar)
        self.assertIn("onClick={() => setPreviewOpen(value => !value)}", topbar)


if __name__ == "__main__":
    unittest.main()
