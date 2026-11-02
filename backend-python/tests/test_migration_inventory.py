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
        self.assertIn("ENABLE ROW LEVEL SECURITY", sql)
        self.assertIn("REVOKE ALL PRIVILEGES", sql)
        self.assertIn("FROM PUBLIC, anon, authenticated", sql)
        self.assertIn("TO service_role", sql)
        self.assertIn("expires_at timestamptz NOT NULL", sql)
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

    def test_track_review_migration_enforces_consent_moderation_and_server_only_access(self):
        migration = ACTIVE_DIR / "20261102120000_track_reviews.sql"
        rollback = ROOT / "supabase" / "rollback" / "20261102120000_track_reviews.rollback.sql"
        self.assertTrue(migration.is_file())
        self.assertTrue(rollback.is_file())
        sql = migration.read_text(encoding="utf-8")
        for required in (
            "public_consent boolean NOT NULL DEFAULT false",
            "moderation_status text NOT NULL DEFAULT 'pending'",
            "UNIQUE (track_id, user_id)",
            "ENABLE ROW LEVEL SECURITY",
            "REVOKE ALL PRIVILEGES",
            "FROM PUBLIC, anon, authenticated",
            "TO service_role",
            "track_reviews.moderate",
            "learning_curriculum",
            "super_admin",
        ):
            with self.subTest(required=required):
                self.assertIn(required, sql)
        self.assertIn("DROP TABLE IF EXISTS public.learnora_track_reviews", rollback.read_text(encoding="utf-8"))

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
