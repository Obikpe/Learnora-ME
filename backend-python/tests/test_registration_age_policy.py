"""Regression tests for the public registration age gate and birthday declarations."""
import os
import unittest
from datetime import date
from pathlib import Path

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from routers.auth import _age_on_date


ROOT = Path(__file__).resolve().parents[2]


class RegistrationAgePolicyTests(unittest.TestCase):
    def test_thirteenth_birthday_is_eligible_on_the_exact_date(self):
        self.assertEqual(_age_on_date(date(2013, 11, 20), date(2026, 11, 20)), 13)

    def test_day_before_thirteenth_birthday_is_not_eligible(self):
        self.assertEqual(_age_on_date(date(2013, 11, 21), date(2026, 11, 20)), 12)

    def test_leap_day_age_is_not_rounded_up_before_march_first(self):
        self.assertEqual(_age_on_date(date(2012, 2, 29), date(2025, 2, 28)), 12)
        self.assertEqual(_age_on_date(date(2012, 2, 29), date(2025, 3, 1)), 13)

    def test_registration_requires_server_checked_dob_and_both_declarations(self):
        source = (ROOT / "backend-python" / "routers" / "auth.py").read_text(encoding="utf-8")
        register = source.split('"/register"', 1)[1].split("# VERIFY EMAIL", 1)[0]
        self.assertIn("payload.date_of_birth > local_today", register)
        self.assertIn("_age_on_date(payload.date_of_birth, local_today)", register)
        self.assertIn("if age < 13:", register)
        self.assertIn("payload.age_13_plus_confirmed", register)
        self.assertIn("payload.age_information_truthful", register)
        self.assertIn('"age_attestation_at": now.isoformat()', register)
        self.assertIn('"age_attestation_version": "age-attestation-v1"', register)

    def test_birthday_worker_uses_user_time_zone_and_idempotent_year_key(self):
        source = (ROOT / "backend-python" / "services" / "notification_service.py").read_text(encoding="utf-8")
        worker = source.split("def _process_birthday_messages(", 1)[1].split("def process_automated_learner_notifications", 1)[0]
        self.assertIn('ZoneInfo(timezone_name)', worker)
        self.assertIn('event_key = f"birthday:{local_now.year}"', worker)
        self.assertIn('notification_type="birthday"', worker)
        self.assertIn("_send_automated_email_once(", worker)
        self.assertIn("_create_in_app_once(", worker)
        self.assertIn("user.get(\"email_verified\") is True", worker)


if __name__ == "__main__":
    unittest.main()
