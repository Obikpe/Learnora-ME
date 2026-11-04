"""Regression tests for account-context isolation in the central access resolver."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from services import access


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


class AccessIdentityScopeTests(unittest.TestCase):
    def _course(self):
        return [{
            "id": "course-1",
            "organisation_id": None,
            "ownership": "learnora",
            "status": "published",
            "creator_id": None,
        }]

    def test_suspended_organisation_identity_cannot_use_free_launch_or_personal_purchase(self):
        db = FakeSupabase({
            "learnora_courses": self._course(),
            "organisation_members": [{
                "organisation_id": "org-1", "role": "learner", "status": "suspended",
            }],
            "learnora_course_purchases": [{
                "id": "purchase-1", "user_id": "user-1",
                "course_id": "course-1", "status": "paid",
            }],
        })
        with patch.object(access, "supabase", db), patch.object(access, "free_access_mode_enabled", return_value=True):
            result = access.resolve_course_access("user-1", "course-1", allow_free_access=True)
        self.assertIsNone(result)

    def test_cohort_identity_cannot_use_individual_purchase_path(self):
        db = FakeSupabase({
            "learnora_courses": self._course(),
            "cohort_accounts": [{"id": "cohort-account-1"}],
            "learnora_course_purchases": [{
                "id": "purchase-1", "user_id": "cohort-account-1",
                "course_id": "course-1", "status": "paid",
            }],
        })
        with patch.object(access, "supabase", db):
            result = access.resolve_course_access("cohort-account-1", "course-1")
        self.assertIsNone(result)

    def test_active_individual_learner_retains_free_launch_access(self):
        db = FakeSupabase({"learnora_courses": self._course()})
        with patch.object(access, "supabase", db), patch.object(access, "free_access_mode_enabled", return_value=True):
            result = access.resolve_course_access("user-1", "course-1", allow_free_access=True)
        self.assertEqual(result["source"], "free_launch")

    def test_active_organisation_assignment_does_not_need_an_individual_purchase(self):
        db = FakeSupabase({
            "learnora_courses": self._course(),
            "organisation_members": [{
                "organisation_id": "org-1", "role": "learner", "status": "active",
            }],
            "course_access": [{
                "id": "grant-1", "organisation_id": "org-1",
                "course_id": "course-1", "status": "active",
            }],
            "learnora_organisation_lifecycle": [{
                "organisation_id": "org-1", "status": "active",
            }],
            "organisations": [{"id": "org-1", "is_active": True}],
        })
        with patch.object(access, "supabase", db):
            result = access.resolve_course_access("user-1", "course-1")
        self.assertEqual(result["source"], "organisation_assignment")


if __name__ == "__main__":
    unittest.main()
