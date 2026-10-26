"""Tests for database-backed authentication and API rate limiting."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from routers import auth


class PersistentRateLimitTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.original_client = auth.supabase
        auth.supabase = self.client
        self.addCleanup(setattr, auth, "supabase", self.original_client)

    def test_production_limit_uses_hashed_shared_database_bucket(self):
        self.client.rpc.return_value.execute.return_value = SimpleNamespace(data=True)
        with patch.object(auth, "APP_ENV", "production"):
            self.assertTrue(auth._limited("cohort:ada:203.0.113.1"))
        name, args = self.client.rpc.call_args.args
        self.assertEqual(name, "check_auth_rate_limit")
        self.assertEqual(len(args["p_bucket_key"]), 64)
        self.assertNotIn("ada", args["p_bucket_key"])
        self.assertEqual(args["p_max_attempts"], auth.MAX_FAILS)
        self.assertEqual(args["p_window_seconds"], auth.WINDOW)

    def test_persistent_limit_fails_closed_if_database_is_unavailable(self):
        self.client.rpc.side_effect = RuntimeError("database unavailable")
        with patch.object(auth, "APP_ENV", "production"):
            self.assertTrue(auth._limited("login:some-user:203.0.113.1"))

    def test_record_and_clear_use_service_role_rpc_with_digest(self):
        self.client.rpc.return_value.execute.return_value = SimpleNamespace(data=None)
        with patch.object(auth, "APP_ENV", "production"):
            auth._record_failure("login:some-user:203.0.113.1")
            auth._clear_failures("login:some-user:203.0.113.1")
        self.assertEqual(self.client.rpc.call_count, 2)
        self.assertEqual(self.client.rpc.call_args_list[0].args[0], "record_auth_rate_failure")
        self.assertEqual(self.client.rpc.call_args_list[1].args[0], "clear_auth_rate_limit")
        self.assertEqual(len(self.client.rpc.call_args_list[0].args[1]["p_bucket_key"]), 64)


class ReadinessProbeSecurityTests(unittest.TestCase):
    def test_production_readiness_requires_matching_secret_header(self):
        import main
        from starlette.requests import Request

        request = Request({
            "type": "http",
            "method": "GET",
            "path": "/api/ready",
            "headers": [],
            "client": ("203.0.113.21", 43123),
            "server": ("testserver", 80),
            "scheme": "https",
        })
        with patch.dict(os.environ, {"APP_ENV": "production", "READINESS_PROBE_TOKEN": "test-probe-secret"}):
            response = main.api_ready(request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body, b'{"status":"not_found"}')

class HttpOnlyCookieSessionTests(unittest.TestCase):
    def test_browser_login_payload_uses_httponly_cookie_and_removes_jwt(self):
        from fastapi import Response

        request = type("RequestStub", (), {"headers": {"origin": "https://learnora-me-v02.vercel.app"}})()
        response = Response()
        payload = {"status": "success", "token": "signed-jwt", "access_token": "signed-jwt", "user": {"id": "u1"}}
        with patch.object(auth, "APP_ENV", "production"):
            result = auth.deliver_auth_token(request, response, "opaque-session-value", payload)
        self.assertNotIn("token", result)
        self.assertNotIn("access_token", result)
        cookie = response.headers.get("set-cookie", "")
        self.assertIn("phx_token=signed-jwt", cookie)
        self.assertIn("httponly", cookie.lower())
        self.assertIn("samesite=lax", cookie.lower())
        self.assertIn("secure", cookie.lower())

    def test_unapproved_browser_origin_cannot_receive_a_session(self):
        from fastapi import HTTPException, Response

        request = type("RequestStub", (), {"headers": {"origin": "https://attacker.example"}})()
        with self.assertRaises(HTTPException) as raised:
            auth.deliver_auth_token(request, Response(), "signed-jwt", {"access_token": "signed-jwt"})
        self.assertEqual(raised.exception.status_code, 403)

    def test_current_user_reads_httponly_cookie_when_no_bearer_header(self):
        from jose import JWTError
        from starlette.requests import Request

        request = Request({
            "type": "http", "method": "GET", "path": "/api/auth/me",
            "headers": [(b"cookie", b"phx_token=cookie-jwt")],
            "client": ("127.0.0.1", 1234), "server": ("testserver", 80), "scheme": "https",
        })
        with patch.object(auth.jwt, "decode", side_effect=JWTError("invalid")) as decode:
            with self.assertRaises(Exception):
                auth.get_current_user(creds=None, request=request)
        decode.assert_called_once()
        self.assertEqual(decode.call_args.args[0], "cookie-jwt")


class StandardLoginTimingTests(unittest.TestCase):
    def test_unknown_email_still_runs_password_verification(self):
        from fastapi import HTTPException
        from starlette.requests import Request

        request = Request({
            "type": "http",
            "method": "POST",
            "path": "/api/auth/login",
            "headers": [],
            "client": ("203.0.113.22", 43123),
            "server": ("testserver", 80),
            "scheme": "https",
        })
        with (
            patch.object(auth, "_limited", return_value=False),
            patch.object(auth, "_find_admin", return_value=None),
            patch.object(auth, "_find_user", return_value=None),
            patch.object(auth, "_record_failure"),
            patch.object(auth, "log_security_event"),
            patch.object(auth, "verify_password", return_value=(False, False)) as verify,
        ):
            with self.assertRaises(HTTPException) as raised:
                auth.login(auth.LoginRequest(email="missing@example.com", password="wrong-password"), request)
        self.assertEqual(raised.exception.status_code, 401)
        verify.assert_called_once_with("wrong-password", auth.DUMMY_LOGIN_PASSWORD_HASH)


class SensitiveTokenUrlTests(unittest.TestCase):
    def test_verification_and_reset_tokens_use_fragments_not_query_strings(self):
        with patch.object(auth, "FRONTEND_URL", "https://learnora.example"):
            verification = auth._build_verification_url("opaque-token")
            reset = auth._build_password_reset_url("opaque-token")
        for url in (verification, reset):
            self.assertIn("#token=opaque-token", url)
            self.assertNotIn("?token=", url)


class DistributedApiMiddlewareTests(unittest.TestCase):
    def test_production_api_limit_is_shared_and_returns_429_when_limited(self):
        import asyncio
        import main
        from starlette.requests import Request

        original_client = main.auth.supabase
        mock_client = Mock()
        mock_client.rpc.return_value.execute.return_value = SimpleNamespace(data=True)
        main.auth.supabase = mock_client
        self.addCleanup(setattr, main.auth, "supabase", original_client)

        request = Request({
            "type": "http",
            "method": "POST",
            "path": "/api/auth/login",
            "headers": [],
            "client": ("203.0.113.20", 43123),
            "server": ("testserver", 80),
            "scheme": "https",
        })

        async def should_not_be_called(_request):
            self.fail("A limited request must not reach the route handler.")

        with patch.dict(os.environ, {"APP_ENV": "production", "API_RATE_LIMIT_REQUESTS": "60", "API_RATE_LIMIT_WINDOW_SECONDS": "60"}):
            response = asyncio.run(main.distributed_api_rate_limit(request, should_not_be_called))
        self.assertEqual(response.status_code, 429)
        self.assertIn("Retry-After", response.headers)
        mock_client.rpc.assert_called_once()
        self.assertEqual(mock_client.rpc.call_args.args[0], "consume_api_rate_limit")

if __name__ == "__main__":
    unittest.main()
