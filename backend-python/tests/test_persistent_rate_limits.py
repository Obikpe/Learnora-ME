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

