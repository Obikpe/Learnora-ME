"""Individual learner boundaries for optional AI onboarding and recommendations."""
import os
import unittest
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import learner_onboarding


class LearnerOnboardingBoundaryTests(unittest.TestCase):
    def test_individual_learner_can_use_onboarding(self):
        learner_onboarding._assert_individual(SimpleNamespace(
            role="normal", account_type="learner", organisation_id=None,
        ))

    def test_cohort_account_cannot_use_individual_onboarding(self):
        with self.assertRaises(HTTPException) as raised:
            learner_onboarding._assert_individual(SimpleNamespace(
                role="normal", account_type="cohort", organisation_id="org-1",
            ))
        self.assertEqual(raised.exception.status_code, 403)

    def test_organisation_learner_cannot_use_individual_onboarding(self):
        with self.assertRaises(HTTPException) as raised:
            learner_onboarding._assert_individual(SimpleNamespace(
                role="normal", account_type="learner", organisation_id="org-1",
            ))
        self.assertEqual(raised.exception.status_code, 403)

    def test_recommendations_use_the_same_public_course_visibility_rules(self):
        source = (Path(__file__).resolve().parents[1] / "routers" / "learner_onboarding.py").read_text(encoding="utf-8")
        recommendations = source.split('def recommendations(', 1)[1]
        self.assertIn("_is_public_course(row, organisation_map, creator_map)", recommendations)
        self.assertIn("_public_course_payload(row)", recommendations)
        self.assertIn('select("id,organisation_id,creator_id,title,slug', recommendations)


    def test_completed_setup_records_first_completion_and_starts_welcome_delivery(self):
        source = (Path(__file__).resolve().parents[1] / "routers" / "learner_onboarding.py").read_text(encoding="utf-8")
        save = source.split('def save_onboarding(', 1)[1].split('@router.get("/recommendations")', 1)[0]
        self.assertIn('"onboarding_completed_at": completed_at', save)
        self.assertIn('from services.notification_service import send_post_setup_welcome', save)
        self.assertIn('send_post_setup_welcome(str(user.id))', save)
        self.assertIn('onboarding_completed_at', source)

    def test_staff_cannot_use_individual_onboarding(self):
        with self.assertRaises(HTTPException) as raised:
            learner_onboarding._assert_individual(SimpleNamespace(
                role="staff_admin", account_type="admin", organisation_id=None,
            ))
        self.assertEqual(raised.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
