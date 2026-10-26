"""Regression tests for literal, case-insensitive email account lookup patterns."""
import os
import unittest
from pathlib import Path
from unittest.mock import patch
from starlette.requests import Request

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from routers.auth import _escape_ilike_literal, _get_client_ip


class AuthEmailLookupSecurityTests(unittest.TestCase):
    def test_like_metacharacters_are_escaped_as_literals(self):
        value = r"first_last%*\\@example.com"
        self.assertEqual(
            _escape_ilike_literal(value),
            r"first\_last\%\*\\\\@example.com",
        )

    def test_client_supplied_real_ip_is_ignored_outside_vercel(self):
        request = Request({
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [(b"x-real-ip", b"198.51.100.2")],
            "client": ("203.0.113.44", 43123),
            "server": ("testserver", 80),
            "scheme": "http",
        })
        with patch.dict(os.environ, {"VERCEL": "0"}):
            self.assertEqual(_get_client_ip(request), "203.0.113.44")

    def test_vercel_edge_real_ip_is_used_when_platform_is_trusted(self):
        request = Request({
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [(b"x-real-ip", b"198.51.100.2")],
            "client": ("203.0.113.44", 43123),
            "server": ("testserver", 80),
            "scheme": "http",
        })
        with patch.dict(os.environ, {"VERCEL": "1"}):
            self.assertEqual(_get_client_ip(request), "198.51.100.2")

    def test_unknown_login_path_uses_dummy_password_verification(self):
        source = (Path(__file__).resolve().parents[1] / "routers" / "auth.py").read_text(encoding="utf-8")
        self.assertIn("DUMMY_LOGIN_PASSWORD_HASH = hash_password(secrets.token_urlsafe(32))", source)
        login = source.split('@router.post("/login")', 1)[1].split("# REGISTER", 1)[0]
        unknown_path = login.split("if not user:", 1)[1]
        self.assertIn("verify_password(", unknown_path)
        self.assertIn("DUMMY_LOGIN_PASSWORD_HASH", unknown_path)

    def test_email_lookup_helper_escapes_all_pattern_wildcards(self):
        source = (Path(__file__).resolve().parents[1] / "routers" / "auth.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(source.count("_escape_ilike_literal(email)"), 2)


if __name__ == "__main__":
    unittest.main()
