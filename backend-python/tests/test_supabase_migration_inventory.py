"""Guard the active Supabase migration directory against legacy replay drift."""
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_MIGRATIONS = REPO_ROOT / "supabase" / "migrations"
LEGACY_MIGRATIONS = REPO_ROOT / "supabase" / "legacy_migrations"

# Applied versions are the repository migration files confirmed in the live ledger.
# Pending files are release candidates; some replace catalog-equivalent changes made
# under different live version IDs and must be reconciled before production replay.
APPLIED_VERSIONS = [
    "20261008100924",
    "20261009225421",
    "20261009230311",
    "20261009230330",
    "20261009230703",
    "20261009231536",
    "20261009231754",
    "20261009232328",
    "20261011051442",
    "20261020230826",
    "20261020230906",
    "20261020232148",
    "20261020234717",
    "20261020234813",
    "20261021112845",
    "20261021113145",
    "20261021113310",
    "20261021113447",
    "20261021113710",
    "20261021114646",
    "20261021114859",
    "20261021115303",
    "20261021161009",
    "20261021161056",
    "20261021161237",
    "20261021182222",
    "20261021220303",
    "20261021220321",
    "20261021220327",
    "20261021220333",
    "20261021220849",
    "20261028171902",
    "20261102210054",
    "20261102210056",
    "20261103041002",
    "20261103155243",
    "20261103155546",
    "20261103155555",
    "20261103160004",
    "20261109160440",
    "20261109190939",
    "20261109190944",
    "20261116072916",
    "20261117204703",
    "20261118090829",
    "20261118090830",
    "20261118090832",
    "20261118090839",
    "20261118090841",
    "20261118090842",
    "20261118091000",
    "20261119223222",
]

# Repository filenames still using an older version timestamp, mapped to the
# matching applied live version. SQL bodies were checked against the live
# migration ledger; do not use db push until these filenames are reconciled.
LIVE_VERSION_ALIASES = {
    "20261026150000": "20261102210054",
    "20261026151000": "20261102210056",
    "20261109180000": "20261109190939",
    "20261109190000": "20261109190944",
    "20261116120000": "20261116072916",
    "20261102090000": "20261118090829",
    "20261102100000": "20261118090830",
    "20261102110000": "20261118090832",
    "20261102120000": "20261118090839",
    "20261117210000": "20261118090841",
    "20261117220000": "20261118090842",
}

PENDING_VERSIONS = ["20261026153000", "20261118141100"]
EXPECTED_VERSIONS = sorted(
    (set(APPLIED_VERSIONS) - set(LIVE_VERSION_ALIASES.values()))
    | set(LIVE_VERSION_ALIASES)
    | set(PENDING_VERSIONS)
)


class SupabaseMigrationInventoryTests(unittest.TestCase):
    def test_repository_migration_inventory_includes_reviewed_pending_versions(self):
        files = sorted(ACTIVE_MIGRATIONS.glob("*.sql"))
        versions = [path.name.split("_", 1)[0] for path in files]
        self.assertEqual(versions, EXPECTED_VERSIONS)
        self.assertTrue(set(LIVE_VERSION_ALIASES).issubset(set(versions)))
        self.assertTrue(set(PENDING_VERSIONS).issubset(set(versions)))
        self.assertTrue(set(LIVE_VERSION_ALIASES.values()).issubset(set(APPLIED_VERSIONS)))
        self.assertTrue(all(re.fullmatch(r"\d{14}", version) for version in versions))
        self.assertTrue(all(path.stat().st_size > 0 for path in files))
        account_deletion = (ACTIVE_MIGRATIONS / "20261109160440_learner_account_deletion_lifecycle.sql").read_text(encoding="utf-8")
        self.assertIn("deleted_account_history", account_deletion)
        self.assertIn("complete_learner_account_deletion", account_deletion)
        self.assertIn("SECURITY DEFINER", account_deletion)
        self.assertIn("account_status = 'deleted'", account_deletion)
        self.assertNotIn("DELETE FROM PUBLIC.USERS", account_deletion.upper())

    def test_unreconciled_legacy_candidates_are_not_active_migrations(self):
        self.assertFalse(any(ACTIVE_MIGRATIONS.glob("00[1-9]_*.sql")))
        self.assertFalse(any(ACTIVE_MIGRATIONS.glob("01[0-5]_*.sql")))
        legacy_names = {path.name for path in LEGACY_MIGRATIONS.glob("*.sql")}
        self.assertEqual(len(legacy_names), 20)
        original_legacy_names = {name for name in legacy_names if re.match(r"^\d{3}_", name)}
        self.assertEqual(len(original_legacy_names), 15)
        self.assertTrue((LEGACY_MIGRATIONS / "001_initial.sql").is_file())
        self.assertTrue((LEGACY_MIGRATIONS / "015_learnora_ai_permissions.sql").is_file())
        users_bootstrap = (LEGACY_MIGRATIONS / "002z_reconstructed_users_registry.sql").read_text(encoding="utf-8")
        admins_bootstrap = (LEGACY_MIGRATIONS / "003z_reconstructed_admins_registry.sql").read_text(encoding="utf-8")
        timestamp_bootstrap = (LEGACY_MIGRATIONS / "zz_reconstructed_set_updated_at.sql").read_text(encoding="utf-8")
        contract_templates = (LEGACY_MIGRATIONS / "zz_reconstructed_contract_templates.sql").read_text(encoding="utf-8")
        contract_clauses = (LEGACY_MIGRATIONS / "zzz_reconstructed_contract_clauses.sql").read_text(encoding="utf-8")
        self.assertIn("CATALOG-RECONSTRUCTED prerequisite", users_bootstrap)
        self.assertIn("CATALOG-RECONSTRUCTED prerequisite", admins_bootstrap)
        self.assertIn("CATALOG-RECONSTRUCTED prerequisite", timestamp_bootstrap)
        self.assertIn("CATALOG-RECONSTRUCTED prerequisite", contract_templates)
        self.assertIn("CATALOG-RECONSTRUCTED prerequisite", contract_clauses)

    def test_expected_permission_seed_keys_are_unique_and_sorted(self):
        key_file = REPO_ROOT / "supabase" / "baselines" / "expected_permission_keys.txt"
        keys = key_file.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(keys), 42)
        self.assertEqual(keys, sorted(set(keys)))

    def test_catalog_reconstructed_sources_are_not_misrepresented_as_original(self):
        for name in (
            "20261008100924_add_learnora_ai_profiles.sql",
            "20261011051442_learner_onboarding_profiles.sql",
        ):
            source = (ACTIVE_MIGRATIONS / name).read_text(encoding="utf-8")
            self.assertIn("CATALOG-RECONSTRUCTED SOURCE", source)
            self.assertIn("not a byte-for-byte recovery", source.lower())


if __name__ == "__main__":
    unittest.main()
