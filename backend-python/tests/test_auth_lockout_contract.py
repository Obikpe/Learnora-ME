"""Regression contracts for shared individual and cohort login throttling."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class LoginLockoutContractTests(unittest.TestCase):
    def test_individual_login_uses_five_attempt_five_minute_lockout(self):
        source = (ROOT / "backend-python/routers/auth.py").read_text(encoding="utf-8")
        self.assertIn("MAX_FAILS = 5", source)
        self.assertIn("WINDOW = 300", source)
        self.assertIn("IP_MAX_FAILS = 20", source)
        self.assertIn('f"login-account:{email}"', source)
        self.assertIn('f"login-account-ip:{email}:{client_ip}"', source)
        self.assertIn('f"login-ip:{client_ip}"', source)
        self.assertIn("def _login_is_limited(", source)
        self.assertIn("def _record_login_failure(", source)
        self.assertIn("def _clear_login_failures(", source)

    def test_cohort_login_uses_shared_account_and_ip_buckets(self):
        source = (ROOT / "backend-python/routers/cohort_learners.py").read_text(encoding="utf-8")
        self.assertIn("COHORT_LOGIN_MAX_FAILS = 5", source)
        self.assertIn("COHORT_LOGIN_WINDOW_SECONDS = 300", source)
        self.assertIn("COHORT_LOGIN_IP_MAX_FAILS = 20", source)
        self.assertIn('f"cohort-account:{username}"', source)
        self.assertIn('f"cohort:{username}:{client_ip}"', source)
        self.assertIn('f"cohort-ip:{client_ip}"', source)
        self.assertIn("_cohort_rate_limited(account_rate_key)", source)
        self.assertIn("_cohort_record_failure(account_rate_key)", source)
        self.assertIn("_cohort_clear_failures(account_rate_key)", source)
        self.assertIn("_cohort_rate_limited(ip_rate_key, max_failures=COHORT_LOGIN_IP_MAX_FAILS)", source)

    def test_persistent_rate_limit_fails_closed(self):
        source = (ROOT / "backend-python/routers/auth.py").read_text(encoding="utf-8")
        limiter = source.split("def _limited(", 1)[1].split("def _record_failure(", 1)[0]
        self.assertIn("return True", limiter)
        self.assertIn("Persistent auth rate-limit check failed", limiter)


if __name__ == "__main__":
    unittest.main()
