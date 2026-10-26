"""Regression tests for HttpOnly cookie sessions and bearer compatibility."""
import os
import unittest
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
        request = make_request("https://learnora-taupe.vercel.app")
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
