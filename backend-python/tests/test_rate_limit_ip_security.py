"""Regression tests for the API limiter's trusted-proxy IP selection."""
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from starlette.requests import Request
import main


def make_request(real_ip):
    headers = []
    if real_ip is not None:
        headers.append((b"x-real-ip", real_ip.encode()))
    return Request({
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": headers,
        "client": ("203.0.113.44", 43123),
        "server": ("testserver", 80),
        "scheme": "http",
    })


class RateLimitIpSecurityTests(unittest.TestCase):
    def test_untrusted_real_ip_header_is_ignored_outside_vercel(self):
        with patch.dict(os.environ, {"VERCEL": "0"}):
            self.assertEqual(main._trusted_rate_limit_ip(make_request("198.51.100.2")), "203.0.113.44")

    def test_vercel_normalised_real_ip_is_used(self):
        with patch.dict(os.environ, {"VERCEL": "1"}):
            self.assertEqual(main._trusted_rate_limit_ip(make_request("198.51.100.2")), "198.51.100.2")

    def test_invalid_vercel_real_ip_falls_back_to_peer_address(self):
        with patch.dict(os.environ, {"VERCEL": "1"}):
            self.assertEqual(main._trusted_rate_limit_ip(make_request("not-an-ip")), "203.0.113.44")

    def test_global_limiter_uses_the_trusted_ip_function(self):
        source = (main.__file__)
        with open(source, encoding="utf-8") as file:
            content = file.read()
        self.assertIn("async def distributed_api_rate_limit", content)
        self.assertIn('rpc("consume_api_rate_limit"', content)


if __name__ == "__main__":
    unittest.main()
