"""Identity-scope regression tests for learner course enrolments."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from routers import progress


class Query:
    def __init__(self, rows):
        self.rows = list(rows)
        self.filters = {}

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, key, value):
        self.filters[key] = str(value)
        return self

    def in_(self, key, values):
        self.filters[key] = {str(value) for value in values}
        return self

    def order(self, *_args, **_kwargs):
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def execute(self):
        rows = []
        for row in self.rows:
            matched = True
            for key, value in self.filters.items():
                if isinstance(value, set):
                    matched = str(row.get(key)) in value
                else:
                    matched = str(row.get(key)) == value
                if not matched:
                    break
            if matched:
                rows.append(row)
        return SimpleNamespace(data=rows)


class FakeSupabase:
    def __init__(self, rows):
        self.rows = rows

    def table(self, name):
        return Query(self.rows.get(name, []))


class ProgressIdentityScopeTests(unittest.TestCase):
    def _personal_enrolment(self):
        return {
            "id": "enrolment-1",
            "user_id": "user-1",
            "course_id": "course-1",
            "organisation_id": None,
            "cohort_id": None,
            "status": "active",
        }

    def test_individual_learner_keeps_personal_enrolment(self):
        db = FakeSupabase({
            "users": [{"id": "user-1", "role": "normal"}],
            "learnora_enrolments": [self._personal_enrolment()],
        })
        with patch.object(progress, "supabase", db):
            result = progress._enrolment("user-1", "course-1")
        self.assertEqual(result["id"], "enrolment-1")

    def test_suspended_organisation_membership_cannot_fall_through_to_personal_enrolment(self):
        db = FakeSupabase({
            "organisation_members": [{
                "organisation_id": "org-1",
                "role": "learner",
                "status": "suspended",
            }],
            "users": [{"id": "user-1", "role": "normal"}],
            "learnora_enrolments": [self._personal_enrolment()],
        })
        with patch.object(progress, "supabase", db):
            result = progress._enrolment("user-1", "course-1")
        self.assertIsNone(result)

    def test_non_learner_organisation_role_cannot_use_personal_enrolment(self):
        db = FakeSupabase({
            "organisation_members": [{
                "organisation_id": "org-1",
                "role": "instructor",
                "status": "active",
            }],
            "users": [{"id": "user-1", "role": "normal"}],
            "learnora_enrolments": [self._personal_enrolment()],
        })
        with patch.object(progress, "supabase", db):
            result = progress._enrolment("user-1", "course-1")
        self.assertIsNone(result)

    def test_withdrawn_cohort_membership_cannot_use_personal_enrolment(self):
        db = FakeSupabase({
            "cohort_members": [{
                "id": "membership-1",
                "cohort_id": "cohort-1",
                "status": "withdrawn",
            }],
            "users": [{"id": "user-1", "role": "normal"}],
            "learnora_enrolments": [self._personal_enrolment()],
        })
        with patch.object(progress, "supabase", db):
            result = progress._enrolment("user-1", "course-1")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
