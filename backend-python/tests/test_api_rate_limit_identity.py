"""Authenticated API rate limits must not be shared by users behind one NAT."""
import os
import unittest

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from starlette.requests import Request
import main
from routers import auth


def make_request(real_ip="203.0.113.44", token=None, bearer=False):
    headers = [(b"x-real-ip", real_ip.encode())]
    if token and bearer:
        headers.append((b"authorization", f"Bearer {token}".encode()))
    elif token:
        headers.append((b"cookie", f"{auth.AUTH_COOKIE_NAME}={token}".encode()))
    return Request({
        "type": "http",
        "method": "GET",
        "path": "/api/test",
        "headers": headers,
        "client": (real_ip, 43123),
        "server": ("testserver", 80),
        "scheme": "https",
    })


class ApiRateLimitIdentityTests(unittest.TestCase):
    def test_different_authenticated_learners_on_same_ip_get_separate_buckets(self):
        first = auth.make_token("learner.one@example.com", "learner", "individual")
        second = auth.make_token("learner.two@example.com", "learner", "individual")
        first_key = main._api_rate_limit_bucket_key(make_request(token=first), "203.0.113.44")
        second_key = main._api_rate_limit_bucket_key(make_request(token=second), "203.0.113.44")
        self.assertNotEqual(first_key, second_key)
        self.assertEqual(len(first_key), 64)
        self.assertEqual(len(second_key), 64)

    def test_same_authenticated_learner_has_same_bucket_across_ips(self):
        token = auth.make_token("learner@example.com", "learner", "individual")
        first_key = main._api_rate_limit_bucket_key(make_request("203.0.113.44", token), "203.0.113.44")
        second_key = main._api_rate_limit_bucket_key(make_request("198.51.100.12", token), "198.51.100.12")
        self.assertEqual(first_key, second_key)

    def test_cohort_and_individual_contexts_have_separate_buckets(self):
        individual = auth.make_token("learner@example.com", "learner", "individual")
        cohort = auth.make_token("learner@example.com", "learner", "cohort")
        individual_key = main._api_rate_limit_bucket_key(make_request(token=individual), "203.0.113.44")
        cohort_key = main._api_rate_limit_bucket_key(make_request(token=cohort), "203.0.113.44")
        self.assertNotEqual(individual_key, cohort_key)

    def test_bearer_tokens_use_the_same_account_bucket(self):
        token = auth.make_token("learner@example.com", "learner", "individual")
        cookie_key = main._api_rate_limit_bucket_key(make_request(token=token), "203.0.113.44")
        bearer_key = main._api_rate_limit_bucket_key(make_request(token=token, bearer=True), "203.0.113.44")
        self.assertEqual(cookie_key, bearer_key)

    def test_anonymous_and_invalid_tokens_fall_back_to_trusted_ip_bucket(self):
        expected = auth._rate_limit_digest("api:ip:203.0.113.44")
        anonymous_key = main._api_rate_limit_bucket_key(make_request(), "203.0.113.44")
        invalid_key = main._api_rate_limit_bucket_key(make_request(token="not-a-valid-jwt"), "203.0.113.44")
        self.assertEqual(anonymous_key, expected)
        self.assertEqual(invalid_key, expected)


if __name__ == "__main__":
    unittest.main()
