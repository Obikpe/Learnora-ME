"""Regression tests for literal, case-insensitive email account lookup patterns."""
import os
import unittest

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from routers.auth import _escape_ilike_literal


class AuthEmailLookupSecurityTests(unittest.TestCase):
    def test_like_metacharacters_are_escaped_as_literals(self):
        value = r"first_last%*\\@example.com"
        self.assertEqual(
            _escape_ilike_literal(value),
            r"first\_last\%\*\\\\@example.com",
        )

    def test_email_lookup_helper_escapes_all_pattern_wildcards(self):
        from pathlib import Path
        source = (Path(__file__).resolve().parents[1] / "routers" / "auth.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(source.count("_escape_ilike_literal(email)"), 2)


if __name__ == "__main__":
    unittest.main()
