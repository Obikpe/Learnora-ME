"""Regression tests for literal, case-insensitive email account lookup patterns."""
import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from types import SimpleNamespace
from fastapi import HTTPException
from starlette.requests import Request

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from routers.auth import CurrentUser, _escape_ilike_literal, _find_admin, _find_cohort_accounts_by_email, _find_user, _get_client_ip, me


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

    def test_public_login_and_registration_respect_reserved_cohort_emails(self):
        source = (Path(__file__).resolve().parents[1] / "routers" / "auth.py").read_text(encoding="utf-8")
        login = source.split('@router.post("/login")', 1)[1].split("# REGISTER", 1)[0]
        register = source.split('"/register"', 1)[1].split("# VERIFY EMAIL", 1)[0]
        self.assertIn('_find_cohort_accounts_by_email(email)', login)
        self.assertIn('if cohort_accounts and not admin and not user:', login)
        self.assertIn('if (admin and user) or (cohort_accounts and (admin or user)):', login)
        self.assertIn('_find_cohort_accounts_by_email(email)', register)
        self.assertIn('reserved for an organisation-managed account', register)

    def test_organisation_context_resolution_fails_closed_on_multiple_tenants(self):
        source = (Path(__file__).resolve().parents[1] / "routers" / "auth.py").read_text(encoding="utf-8")
        resolver = source.split("def _active_organisation_context(", 1)[1].split("# AUTHORIZATION DEPENDENCIES", 1)[0]
        self.assertIn('organisation_ids = {item[0] for item in contexts}', resolver)
        self.assertIn('if len(organisation_ids) > 1:', resolver)
        self.assertIn('role_groups = {', resolver)
        self.assertIn('.select("cohort_id")', resolver)
        self.assertNotIn('.eq("status", "active")', resolver)
        self.assertIn('status_code=409', resolver)
        self.assertIn('if fail_closed:', resolver)
        self.assertIn('unresolved_cohort_ids = set(cohort_ids) - resolved_cohort_ids', resolver)
        self.assertIn('unresolved_cohort_identity_context', resolver)
        self.assertIn('fail_closed=role in {"normal", LEGACY_ASSIGNED_LEARNER_ROLE}', source)

    def test_optional_public_session_only_downgrades_expired_auth_to_anonymous(self):
        source = (Path(__file__).resolve().parents[1] / "routers" / "auth.py").read_text(encoding="utf-8")
        optional = source.split("def get_optional_current_user(", 1)[1].split("def get_current_user(", 1)[0]
        self.assertIn("if not _request_auth_token(request, creds):", optional)
        self.assertIn("if exc.status_code == 401:", optional)
        self.assertIn("return None", optional)
        self.assertIn("raise", optional)


    @patch("routers.auth.supabase")
    def test_current_user_endpoint_fails_closed_when_membership_lookup_fails(self, mock_supabase):
        query = Mock()
        mock_supabase.table.return_value = query
        query.select.return_value = query
        query.eq.return_value = query
        query.execute.side_effect = RuntimeError("database unavailable")
        user = CurrentUser(
            id="user-1",
            email="learner@example.com",
            role="normal",
            sub_status="free",
            account_type="learner",
        )

        with self.assertRaises(HTTPException) as raised:
            me(user)

        self.assertEqual(raised.exception.status_code, 503)

    @patch("routers.auth.supabase")
    def test_reserved_email_lookup_uses_literal_case_insensitive_match(self, mock_supabase):
        query = Mock()
        mock_supabase.table.return_value = query
        query.select.return_value = query
        query.ilike.return_value = query
        query.limit.return_value = query
        query.execute.return_value = SimpleNamespace(data=[{"id": "cohort-account-1"}])

        rows = _find_cohort_accounts_by_email(r"learner_test%*@example.com")

        self.assertEqual(rows, [{"id": "cohort-account-1"}])
        mock_supabase.table.assert_called_once_with("cohort_accounts")
        query.ilike.assert_called_once_with(
            "email",
            r"learner\_test\%\*@example.com",
        )
        query.limit.assert_called_once_with(10)

    @patch("routers.auth.supabase")
    def test_duplicate_individual_email_rows_are_rejected(self, mock_supabase):
        query = Mock()
        mock_supabase.table.return_value = query
        query.select.return_value = query
        query.ilike.return_value = query
        query.limit.return_value = query
        query.execute.return_value = SimpleNamespace(data=[{"id": "user-1"}, {"id": "user-2"}])

        with self.assertRaises(HTTPException) as raised:
            _find_user("learner@example.com")

        self.assertEqual(raised.exception.status_code, 409)
        mock_supabase.table.assert_called_once_with("users")
        query.limit.assert_called_once_with(2)

    def test_password_recovery_resolves_all_account_contexts(self):
        source = Path(__file__).resolve().parents[1] / "routers" / "auth.py"
        text = source.read_text(encoding="utf-8")
        resend = text.split("def resend_verification(", 1)[1].split("# FORGOT PASSWORD", 1)[0]
        forgot = text.split("def forgot_password(", 1)[1].split("# RESET PASSWORD", 1)[0]
        self.assertIn("_find_cohort_accounts_by_email(email)", resend)
        self.assertIn("_find_admin(email)", resend)
        self.assertIn("_find_user(email)", resend)
        self.assertIn("_find_cohort_accounts_by_email(email)", forgot)
        self.assertIn("_find_admin(email)", forgot)
        self.assertIn("_find_user(email)", forgot)

    def test_password_reset_claims_token_conditionally_before_password_update(self):
        source = Path(__file__).resolve().parents[1] / "routers" / "auth.py"
        text = source.read_text(encoding="utf-8")
        reset = text.split("def reset_password(", 1)[1].split("# CURRENT ACCOUNT", 1)[0]
        claim_index = reset.index('.is_("used_at", "null")')
        update_index = reset.index('"password_hash": new_hash')
        self.assertLess(claim_index, update_index)
        self.assertIn('.gt("expires_at", now.isoformat())', reset)
        self.assertIn("identity_matches_token", reset)

    @patch("routers.auth.supabase")
    def test_duplicate_admin_email_rows_are_rejected(self, mock_supabase):
        query = Mock()
        mock_supabase.table.return_value = query
        query.select.return_value = query
        query.ilike.return_value = query
        query.limit.return_value = query
        query.execute.return_value = SimpleNamespace(data=[{"id": "admin-1"}, {"id": "admin-2"}])

        with self.assertRaises(HTTPException) as raised:
            _find_admin("admin@example.com")

        self.assertEqual(raised.exception.status_code, 409)
        mock_supabase.table.assert_called_once_with("admins")
        query.limit.assert_called_once_with(2)

    @patch("routers.auth.supabase")
    def test_reserved_email_lookup_fails_closed_when_database_is_unavailable(self, mock_supabase):
        query = Mock()
        mock_supabase.table.return_value = query
        query.select.return_value = query
        query.ilike.return_value = query
        query.limit.return_value = query
        query.execute.side_effect = RuntimeError("database unavailable")

        with self.assertRaises(HTTPException) as raised:
            _find_cohort_accounts_by_email("learner@example.com")

        self.assertEqual(raised.exception.status_code, 503)

    def test_email_lookup_helper_escapes_all_pattern_wildcards(self):
        source = (Path(__file__).resolve().parents[1] / "routers" / "auth.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(source.count("_escape_ilike_literal(email)"), 3)


if __name__ == "__main__":
    unittest.main()
