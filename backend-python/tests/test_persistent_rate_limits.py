"""Tests for database-backed authentication and API rate limiting."""
import asyncio
import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from routers import auth
from starlette.requests import Request
from starlette.responses import Response


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

class PersistentApiRateLimitTests(unittest.TestCase):
    def _request(self):
        return Request({
            "type": "http",
            "method": "GET",
            "path": "/api/test",
            "headers": [],
            "client": ("203.0.113.44", 43123),
            "server": ("testserver", 80),
            "scheme": "https",
        })

    def test_production_api_requests_use_shared_database_bucket(self):
        import main

        client = Mock()
        client.rpc.return_value.execute.return_value = SimpleNamespace(data=False)
        next_handler = AsyncMock(return_value=Response("ok"))
        with patch.object(main.auth, "supabase", client), patch.dict(os.environ, {"APP_ENV": "production", "VERCEL": "0"}):
            response = asyncio.run(main.distributed_api_rate_limit(self._request(), next_handler))
        self.assertEqual(response.status_code, 200)
        client.rpc.assert_called_once_with(
            "consume_api_rate_limit",
            {
                "p_bucket_key": client.rpc.call_args.args[1]["p_bucket_key"],
                "p_max_requests": main.API_RATE_LIMIT_REQUESTS,
                "p_window_seconds": main.API_RATE_LIMIT_WINDOW_SECONDS,
            },
        )
        self.assertEqual(len(client.rpc.call_args.args[1]["p_bucket_key"]), 64)
        next_handler.assert_awaited_once()

    def test_production_api_limiter_fails_closed_if_database_is_unavailable(self):
        import main

        client = Mock()
        client.rpc.side_effect = RuntimeError("database unavailable")
        next_handler = AsyncMock(return_value=Response("should not run"))
        with patch.object(main.auth, "supabase", client), patch.dict(os.environ, {"APP_ENV": "production", "VERCEL": "0"}):
            response = asyncio.run(main.distributed_api_rate_limit(self._request(), next_handler))
        self.assertEqual(response.status_code, 503)
        next_handler.assert_not_awaited()

    def test_production_api_limiter_returns_429_when_bucket_is_limited(self):
        import main

        client = Mock()
        client.rpc.return_value.execute.return_value = SimpleNamespace(data=True)
        next_handler = AsyncMock(return_value=Response("should not run"))
        with patch.object(main.auth, "supabase", client), patch.dict(os.environ, {"APP_ENV": "production", "VERCEL": "0"}):
            response = asyncio.run(main.distributed_api_rate_limit(self._request(), next_handler))
        self.assertEqual(response.status_code, 429)
        next_handler.assert_not_awaited()

