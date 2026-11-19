"""Regression tests for HttpOnly cookie sessions and bearer compatibility."""
import os
import time
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request
from routers import auth


def make_request(origin=None, cookie=None):
    headers = []
    if origin:
        headers.append((b"origin", origin.encode()))
    if cookie:
        headers.append((b"cookie", cookie.encode()))
    return Request({"type":"http","method":"POST","path":"/api/auth/login","headers":headers,"client":("127.0.0.1",12345),"server":("testserver",80),"scheme":"http"})


class CookieAuthContractTests(unittest.TestCase):
    def test_trusted_browser_gets_httponly_cookie_and_no_jwt_in_json(self):
        request = make_request("http://localhost:3000")
        response = Response()
        payload = {"success": True, "token": "secret-jwt", "access_token": "secret-jwt", "user": {"id": "u1"}}
        with patch.object(auth, "APP_ENV", "development"):
            result = auth.deliver_auth_token(request, response, "secret-jwt", payload)
        self.assertEqual(result, {"success": True, "user": {"id": "u1"}})
        cookie = response.headers.get("set-cookie", "").lower()
        self.assertIn("phx_token=secret-jwt", cookie)
        self.assertIn("httponly", cookie)
        self.assertIn("samesite=lax", cookie)
        self.assertIn("path=/", cookie)

    def test_production_cookie_is_secure(self):
        request = make_request("https://learnora-me-v02.vercel.app")
        response = Response()
        with patch.object(auth, "APP_ENV", "production"):
            result = auth.deliver_auth_token(request, response, "secret-jwt", {"access_token": "secret-jwt"})
        self.assertEqual(result, {})
        self.assertIn("secure", response.headers.get("set-cookie", "").lower())

    def test_untrusted_origin_cannot_establish_cookie_session(self):
        request = make_request("https://attacker.example")
        with patch.object(auth, "APP_ENV", "development"):
            with self.assertRaises(HTTPException) as raised:
                auth.deliver_auth_token(request, Response(), "secret-jwt", {"token": "secret-jwt"})
        self.assertEqual(raised.exception.status_code, 403)

    def test_non_browser_client_retains_bearer_token_response(self):
        request = make_request()
        payload = {"success": True, "access_token": "secret-jwt"}
        with patch.object(auth, "APP_ENV", "production"):
            result = auth.deliver_auth_token(request, Response(), "secret-jwt", payload)
        self.assertEqual(result["access_token"], "secret-jwt")

    def test_cookie_is_preferred_over_bearer_and_bearer_remains_supported(self):
        request = make_request(cookie="phx_token=cookie-jwt")
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="header-jwt")
        self.assertEqual(auth._request_auth_token(request, creds), "cookie-jwt")
        self.assertEqual(auth._request_auth_token(make_request(), creds), "header-jwt")

    def test_token_ttl_is_capped_at_fifteen_minutes(self):
        self.assertLessEqual(auth.TOKEN_TTL, 900)
        self.assertGreaterEqual(auth.TOKEN_TTL, 60)

    def test_logout_persists_a_hash_of_the_token(self):
        token = auth.jwt.encode({"sub": "learner@example.com", "exp": time.time() + 300}, auth.JWT_SECRET, algorithm=auth.ALGORITHM)
        class Query:
            def __init__(self): self.payload = None
            def delete(self): return self
            def lt(self, *_args): return self
            def upsert(self, payload, **_kwargs): self.payload = payload; return self
            def execute(self): return SimpleNamespace(data=[])
        query = Query()
        with patch.object(auth.supabase, "table", return_value=query) as table:
            self.assertTrue(auth.revoke_auth_token(token))
        table.assert_called_with("revoked_auth_tokens")
        self.assertEqual(len(query.payload["token_hash"]), 64)
        self.assertNotEqual(query.payload["token_hash"], token)
        self.assertNotIn("token", query.payload)

    def test_password_change_invalidates_sessions_issued_before_change(self):
        changed_at = "2026-11-19T22:00:00+00:00"
        with self.assertRaises(HTTPException) as raised:
            auth._assert_session_not_before_password_change(
                {"iat": time.time() - 60},
                {"password_changed_at": changed_at},
            )
        self.assertEqual(raised.exception.status_code, 401)

    def test_fresh_session_after_password_change_remains_valid(self):
        changed_at = datetime.now(timezone.utc).isoformat()
        fresh = auth.make_token("learner@example.com", "normal", "learner")
        payload = auth.jwt.decode(fresh, auth.JWT_SECRET, algorithms=[auth.ALGORITHM])
        auth._assert_session_not_before_password_change(payload, {"password_changed_at": changed_at})

    def test_revoked_token_is_rejected_on_authenticated_requests(self):
        digest = auth._auth_token_hash("signed-token-value")
        class Query:
            def select(self, *_args): return self
            def eq(self, *_args): return self
            def gt(self, *_args): return self
            def limit(self, *_args): return self
            def execute(self): return SimpleNamespace(data=[{"token_hash": digest}])
        with patch.object(auth.supabase, "table", return_value=Query()):
            with self.assertRaises(HTTPException) as raised:
                auth.assert_token_not_revoked("signed-token-value")
        self.assertEqual(raised.exception.status_code, 401)

    def test_password_change_reissues_only_the_current_browser_session(self):
        from types import SimpleNamespace

        class UpdateQuery:
            def __init__(self):
                self.payload = None
            def update(self, payload):
                self.payload = payload
                return self
            def eq(self, *_args):
                return self
            def execute(self):
                return SimpleNamespace(data=[{"id": "admin-1"}])

        class FakeDatabase:
            def __init__(self):
                self.query = UpdateQuery()
            def table(self, _name):
                return self.query

        database = FakeDatabase()
        request = make_request("http://localhost:3000")
        response = Response()
        user = SimpleNamespace(email="admin@example.com", role="admin", account_type="admin", id="admin-1")
        payload = auth.ChangePasswordRequest(
            current_password="OldSecurePassword123!",
            new_password="NewSecurePassword456!",
            confirm_password="NewSecurePassword456!",
        )
        with patch.object(auth, "check_password_rules"), \
             patch.object(auth, "_find_admin", return_value={"id": "admin-1", "password_hash": "stored"}), \
             patch.object(auth, "verify_password", return_value=(True, False)), \
             patch.object(auth, "hash_password", return_value="new-hash"), \
             patch.object(auth, "supabase", database), \
             patch.object(auth, "log_audit_event"), \
             patch.object(auth, "log_security_event"):
            result = auth.change_password(payload, request, response, user)

        self.assertEqual(result["status"], "success")
        self.assertNotIn("access_token", result)
        cookie = response.headers.get("set-cookie", "")
        self.assertIn("phx_token=", cookie)
        fresh_token = cookie.split("phx_token=", 1)[1].split(";", 1)[0]
        fresh_payload = auth.jwt.decode(fresh_token, auth.JWT_SECRET, algorithms=[auth.ALGORITHM])
        changed_at = datetime.fromisoformat(database.query.payload["password_changed_at"]).timestamp()
        self.assertGreaterEqual(float(fresh_payload["iat"]), changed_at)

    def test_logout_revokes_cookie_token_before_success(self):
        request = make_request(cookie="phx_token=signed-token")
        response = Response()
        with patch.object(auth, "revoke_auth_token") as revoke:
            result = auth.logout(request, response)
        revoke.assert_called_once_with("signed-token")
        self.assertTrue(result["success"])
        self.assertIn("max-age=0", response.headers.get("set-cookie", "").lower())

    def test_logout_cookie_is_expired(self):
        response = Response()
        with patch.object(auth, "APP_ENV", "development"):
            auth.clear_auth_cookie(response, auth.TEAM_COOKIE_NAME)
        cookie = response.headers.get("set-cookie", "").lower()
        self.assertIn("learnora_team_token=", cookie)
        self.assertIn("max-age=0", cookie)
        self.assertIn("httponly", cookie)


if __name__ == "__main__":
    unittest.main()
