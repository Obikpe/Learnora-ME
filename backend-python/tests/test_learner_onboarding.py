"""Individual learner boundaries for optional AI onboarding and recommendations."""
import os
import unittest
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

    def test_staff_cannot_use_individual_onboarding(self):
        with self.assertRaises(HTTPException) as raised:
            learner_onboarding._assert_individual(SimpleNamespace(
                role="staff_admin", account_type="admin", organisation_id=None,
            ))
        self.assertEqual(raised.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
