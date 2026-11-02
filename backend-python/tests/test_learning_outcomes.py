"""Focused contracts for certificates, project reviews and evidence trust."""

import os
import unittest

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")
os.environ.setdefault("JWT_SECRET", "learnora-outcomes-unit-test-secret-2026")

from pydantic import ValidationError
from routers import credentials, evidence, internal_projects


class LearningOutcomeContractTests(unittest.TestCase):
    def test_learner_credentials_fall_back_until_revocation_columns_are_migrated(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from routers import auth

        class Query:
            def __init__(self, table):
                self.table = table
                self.fields = ""
            def select(self, fields):
                self.fields = fields
                return self
            def eq(self, *_args, **_kwargs):
                return self
            def order(self, *_args, **_kwargs):
                return self
            def in_(self, *_args, **_kwargs):
                return self
            def execute(self):
                if self.table == "certificates" and "revoked_at" in self.fields:
                    raise RuntimeError("column revoked_at does not exist")
                return SimpleNamespace(data=[])

        class FakeSupabase:
            def table(self, name):
                return Query(name)

        user = auth.CurrentUser(
            id="learner-1",
            email="learner@example.com",
            role="normal",
            sub_status="active",
            account_type="learner",
        )
        with patch.object(credentials, "supabase", FakeSupabase()):
            result = credentials.my_credentials(user)
        self.assertEqual(result["certificates"], [])
        self.assertEqual(result["eligible_courses"], [])

    def test_course_certificate_number_is_stable_and_identity_scoped(self):
        first = credentials._certificate_number("learner-a", "course-a")
        repeated = credentials._certificate_number("learner-a", "course-a")
        other_learner = credentials._certificate_number("learner-b", "course-a")
        other_course = credentials._certificate_number("learner-a", "course-b")

        self.assertEqual(first, repeated)
        self.assertRegex(first, r"^LRN-COURSE-[A-F0-9]{24}$")
        self.assertNotEqual(first, other_learner)
        self.assertNotEqual(first, other_course)

    def test_public_certificate_projection_does_not_expose_account_data(self):
        view = credentials._certificate_view({
            "id": "certificate-id",
            "user_id": "private-user-id",
            "course_id": "course-id",
            "certificate_number": "LRN-COURSE-ABC123",
            "issued_at": "2026-11-02T10:00:00Z",
            "metadata": {
                "recipient_name": "Learner Name",
                "course_title": "Data Foundations",
                "email": "private@example.com",
            },
        })
        self.assertEqual(view["recipient_name"], "Learner Name")
        self.assertEqual(view["course_title"], "Data Foundations")
        self.assertNotIn("user_id", view)
        self.assertNotIn("email", view)

    def test_certificate_projection_marks_revocation_without_exposing_private_data(self):
        valid = credentials._certificate_view({
            "id": "certificate-id", "user_id": "private-user-id", "course_id": "course-id",
            "certificate_number": "LRN-COURSE-ABC123", "issued_at": "2026-11-02T10:00:00Z",
            "metadata": {"recipient_name": "Learner Name", "course_title": "Data Foundations"},
            "revoked_at": None, "revocation_reason": None,
        })
        revoked = credentials._certificate_view({
            "id": "certificate-id", "user_id": "private-user-id", "course_id": "course-id",
            "certificate_number": "LRN-COURSE-ABC123", "issued_at": "2026-11-02T10:00:00Z",
            "metadata": {"recipient_name": "Learner Name", "course_title": "Data Foundations"},
            "revoked_at": "2026-11-03T10:00:00Z", "revocation_reason": "Credential issued in error.",
        })
        self.assertTrue(valid["valid"])
        self.assertFalse(revoked["valid"])
        self.assertEqual(revoked["revocation_reason"], "Credential issued in error.")
        self.assertNotIn("user_id", revoked)

    def test_project_review_is_bounded_and_decision_is_explicit(self):
        approved = internal_projects.ProjectReviewIn(
            score=85,
            feedback="Good work.",
            decision="approved",
        )
        self.assertEqual(approved.decision, "approved")
        with self.assertRaises(ValidationError):
            internal_projects.ProjectReviewIn(score=101, decision="approved")
        with self.assertRaises(ValidationError):
            internal_projects.ProjectReviewIn(score=80, decision="publish")

    def test_learners_cannot_self_create_verified_evidence_types(self):
        self.assertEqual(evidence.ALLOWED_EVIDENCE_TYPES, {"manual"})

    def test_project_creation_requires_a_real_brief(self):
        with self.assertRaises(ValidationError):
            internal_projects.ProjectCreate(
                title="SQL",
                instructions="",
                skills=[],
            )
        valid = internal_projects.ProjectCreate(
            title="SQL analysis challenge",
            instructions="Analyse the supplied data and explain your approach.",
            skills=[],
        )
        self.assertEqual(valid.title, "SQL analysis challenge")


if __name__ == "__main__":
    unittest.main()
