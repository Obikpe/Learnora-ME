"""Migration inventory checks aligned with the active Supabase migration strategy.

The timestamped supabase/migrations directory is the active release chain.
The old numbered chain is archived under supabase/legacy_migrations for
historical analysis only and must not be replayed as the current schema.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
ACTIVE_DIR = ROOT / "supabase" / "migrations"
LEGACY_DIR = ROOT / "supabase" / "legacy_migrations"


class MigrationInventoryTests(unittest.TestCase):
    def test_legacy_numbered_chain_is_archived_and_contiguous_001_to_015(self):
        files = sorted(LEGACY_DIR.glob("[0-9][0-9][0-9]_*.sql"))
        numbers = [int(path.name[:3]) for path in files]
        self.assertEqual(numbers, list(range(1, 16)))
        for path in files:
            self.assertTrue(path.read_text(encoding="utf-8").strip(), path.name)

    def test_current_security_remediation_migrations_are_present(self):
        expected = (
            "20261020230826_learnora_audit_remediation.sql",
            "20261020230906_restore_shared_learner_grants_and_lock_trigger_routines.sql",
            "20261020232148_allow_unlimited_monthly_ai_quota.sql",
            "20261020234717_pin_shared_timestamp_trigger_search_path.sql",
            "20261020234813_revoke_browser_grants_from_org_control_tables.sql",
            "20261021220303_revoke_browser_table_grants.sql",
            "20261021220321_process_creator_payout_atomically.sql",
            "20261021220327_encrypt_cohort_date_of_birth.sql",
            "20261021220333_cohort_login_rate_limits.sql",
            "20261021220849_revoke_trigger_function_browser_execute.sql",
            "20261026153000_revoke_browser_privileges_and_defaults.sql",
            "20261117210000_password_session_invalidation.sql",
        )
        for name in expected:
            with self.subTest(migration=name):
                sql_path = ACTIVE_DIR / name
                self.assertTrue(sql_path.is_file(), f"Missing active migration: {name}")
                self.assertTrue(sql_path.read_text(encoding="utf-8").strip())

    def test_historical_reconstructed_sources_are_not_misrepresented_as_originals(self):
        readme = (LEGACY_DIR / "README.md").read_text(encoding="utf-8").lower()
        self.assertIn("reconstruct", readme)
        for name in (
            "20261008100924_add_learnora_ai_profiles.sql",
            "20261011051442_learner_onboarding_profiles.sql",
        ):
            self.assertTrue((ACTIVE_DIR / name).is_file(), name)

    def test_active_quiz_session_migration_is_server_only_and_reversible(self):
        migration = ACTIVE_DIR / "20261102100000_quiz_active_sessions.sql"
        rollback = ROOT / "supabase" / "rollback" / "20261102100000_quiz_active_sessions.rollback.sql"
        self.assertTrue(migration.is_file())
        self.assertTrue(rollback.is_file())
        sql = migration.read_text(encoding="utf-8")
        self.assertIn("enable row level security", sql.lower())
        self.assertIn("revoke all privileges", sql.lower())
        self.assertIn("from public, anon, authenticated", sql.lower())
        self.assertIn("to service_role", sql.lower())
        self.assertIn("expires_at timestamptz NOT NULL", sql)
        self.assertIn("client_session_id uuid NOT NULL", sql)
        self.assertIn("UNIQUE (user_id, quiz_id, client_session_id)", sql)
        self.assertIn("DROP TABLE IF EXISTS public.quiz_active_sessions", rollback.read_text(encoding="utf-8"))

    def test_certificate_revocation_migration_is_additive_and_reversible(self):
        migration = ACTIVE_DIR / "20261102110000_certificate_revocation.sql"
        rollback = ROOT / "supabase" / "rollback" / "20261102110000_certificate_revocation.rollback.sql"
        self.assertTrue(migration.is_file())
        self.assertTrue(rollback.is_file())
        sql = migration.read_text(encoding="utf-8")
        self.assertIn("ADD COLUMN IF NOT EXISTS revoked_at", sql)
        self.assertIn("revoked_by uuid", sql)
        self.assertIn("revocation_reason text", sql)
        self.assertIn("DROP COLUMN IF EXISTS revoked_at", rollback.read_text(encoding="utf-8"))

    def test_project_submission_integrity_migration_is_additive_and_reversible(self):
        migration = ACTIVE_DIR / "20261102120000_project_submission_integrity.sql"
        rollback = ROOT / "supabase" / "rollback" / "20261102120000_project_submission_integrity.rollback.sql"
        self.assertTrue(migration.is_file())
        self.assertTrue(rollback.is_file())
        sql = migration.read_text(encoding="utf-8")
        self.assertIn("project_submissions_one_active_per_learner_idx", sql)
        self.assertIn("skill_evidence_project_submission_skill_unique_idx", sql)
        self.assertIn("WHERE status IN ('submitted','reviewed','approved')", sql)
        self.assertIn("WHERE evidence_type = 'project' AND source_id IS NOT NULL", sql)
        rollback_sql = rollback.read_text(encoding="utf-8")
        self.assertIn("DROP INDEX IF EXISTS public.project_submissions_one_active_per_learner_idx", rollback_sql)
        self.assertIn("DROP INDEX IF EXISTS public.skill_evidence_project_submission_skill_unique_idx", rollback_sql)

    def test_learning_sessions_and_streak_migration_is_server_only_and_reversible(self):
        migration = ACTIVE_DIR / "20261103155243_learner_learning_sessions_and_streaks.sql"
        rollback = ROOT / "supabase" / "rollback" / "20261103155243_learner_learning_sessions_and_streaks.rollback.sql"
        self.assertTrue(migration.is_file())
        self.assertTrue(rollback.is_file())
        sql = migration.read_text(encoding="utf-8")
        self.assertIn("create table if not exists public.learning_sessions", sql.lower())
        self.assertIn("create table if not exists public.learner_learning_days", sql.lower())
        self.assertIn("enable row level security", sql.lower())
        self.assertIn("revoke all on public.learning_sessions from anon, authenticated", sql.lower())
        self.assertIn("revoke all on public.learner_learning_days from anon, authenticated", sql.lower())
        self.assertIn("to service_role", sql.lower())
        rollback_sql = rollback.read_text(encoding="utf-8")
        self.assertIn("drop table if exists public.learner_learning_days", rollback_sql.lower())
        self.assertIn("drop table if exists public.learning_sessions", rollback_sql.lower())
        self.assertIn("drop function if exists public.record_learner_learning_day", rollback_sql.lower())
        self.assertIn("drop function if exists public.get_learner_learning_seconds", rollback_sql.lower())

    def test_account_deletion_migration_preserves_a_restricted_history_record(self):
        migration = ACTIVE_DIR / "20261109160440_learner_account_deletion_lifecycle.sql"
        self.assertTrue(migration.is_file())
        sql = migration.read_text(encoding="utf-8")
        self.assertIn("CREATE TABLE IF NOT EXISTS public.deleted_account_history", sql)
        self.assertIn("ENABLE ROW LEVEL SECURITY", sql)
        self.assertIn("REVOKE ALL ON public.deleted_account_history FROM PUBLIC, anon, authenticated", sql)
        self.assertIn("complete_learner_account_deletion", sql)
        self.assertIn("password_hash = NULL", sql)
        self.assertIn("account_status = 'deleted'", sql)
        self.assertNotIn("DELETE FROM PUBLIC.USERS", sql.upper())


    def test_notification_automation_migration_is_server_only_and_reversible(self):
        migration = ACTIVE_DIR / "20261116120000_notification_email_automation.sql"
        rollback = ROOT / "supabase" / "rollback" / "20261116120000_notification_email_automation.rollback.sql"
        self.assertTrue(migration.is_file())
        self.assertTrue(rollback.is_file())
        sql = migration.read_text(encoding="utf-8")
        self.assertIn("learner_notification_deliveries", sql)
        self.assertIn("ENABLE ROW LEVEL SECURITY", sql)
        self.assertIn("REVOKE ALL ON public.learner_notification_deliveries FROM PUBLIC, anon, authenticated", sql)
        self.assertIn("GRANT ALL ON public.learner_notification_deliveries TO service_role", sql)
        self.assertIn("claim_learner_notification_delivery", sql)
        self.assertIn("finish_learner_notification_delivery", sql)
        rollback_sql = rollback.read_text(encoding="utf-8")
        self.assertIn("DROP TABLE IF EXISTS public.learner_notification_deliveries", rollback_sql)
        self.assertIn("DROP COLUMN IF EXISTS last_inactivity_email_at", rollback_sql)
        self.assertIn("DROP COLUMN IF EXISTS onboarding_completed_at", rollback_sql)

    def test_password_change_session_revocation_migration_is_non_destructive(self):
        migration = ACTIVE_DIR / "20261117210000_password_session_invalidation.sql"
        rollback = ROOT / "supabase" / "rollback" / "20261117210000_password_session_invalidation.rollback.sql"
        self.assertTrue(migration.is_file())
        self.assertTrue(rollback.is_file())
        sql = migration.read_text(encoding="utf-8")
        self.assertIn("ALTER TABLE public.users", sql)
        self.assertIn("ALTER TABLE public.admins", sql)
        self.assertIn("password_changed_at timestamptz", sql)
        self.assertIn("SET DEFAULT now()", sql)
        self.assertIn("SET NOT NULL", sql)
        self.assertNotIn("DROP COLUMN", rollback.read_text(encoding="utf-8"))

    def test_quota_fix_preserves_unlimited_monthly_limit_contract(self):
        sql = (ACTIVE_DIR / "20261020232148_allow_unlimited_monthly_ai_quota.sql").read_text(
            encoding="utf-8"
        )
        self.assertNotRegex(
            sql,
            r"(?is)IF\s+p_requests_per_month\s+IS\s+NULL\s+THEN",
            "A NULL monthly limit must remain valid (unlimited).",
        )

    def test_browser_grant_revocation_covers_shared_and_control_tables(self):
        sql = (ACTIVE_DIR / "20261021220303_revoke_browser_table_grants.sql").read_text(
            encoding="utf-8"
        )
        self.assertRegex(sql, r"(?is)REVOKE\s+ALL\s+PRIVILEGES\s+ON\s+ALL\s+TABLES\s+IN\s+SCHEMA\s+public")
        for role in ("anon", "authenticated"):
            self.assertIn(role, sql)
        self.assertIn("ALTER DEFAULT PRIVILEGES", sql)


if __name__ == "__main__":
    unittest.main()
