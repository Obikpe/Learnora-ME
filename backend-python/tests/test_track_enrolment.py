"""Tests for enrolling an individual learner into a published global track."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import courses


class EnrolmentQuery:
    def __init__(self, table, fixtures):
        self.table = table
        self.fixtures = fixtures
        self.filters = []
        self.action = "select"
        self.values = None
        self.limit_value = None

    def select(self, *_args, **_kwargs): return self
    def eq(self, column, value): self.filters.append(("eq", column, value)); return self
    def is_(self, column, value): self.filters.append(("is", column, value)); return self
    def in_(self, column, values): self.filters.append(("in", column, list(values))); return self
    def order(self, *_args, **_kwargs): return self
    def limit(self, value): self.limit_value = value; return self
    def insert(self, values): self.action = "insert"; self.values = values; return self
    def update(self, values): self.action = "update"; self.values = values; return self

    def execute(self):
        rows = self.fixtures.setdefault(self.table, [])
        selected = list(rows)
        for kind, column, value in self.filters:
            if kind == "eq": selected = [row for row in selected if row.get(column) == value]
            elif kind == "is" and value == "null": selected = [row for row in selected if row.get(column) is None]
            elif kind == "in": selected = [row for row in selected if row.get(column) in value]
        if self.limit_value is not None: selected = selected[:self.limit_value]
        if self.action == "insert":
            values = self.values if isinstance(self.values, list) else [self.values]
            inserted = [dict(value) for value in values]
            rows.extend(inserted)
            return SimpleNamespace(data=inserted)
        if self.action == "update":
            for row in selected:
                row.update(self.values)
            return SimpleNamespace(data=[dict(row) for row in selected])
        return SimpleNamespace(data=selected)


class EnrolmentSupabase:
    def __init__(self, fixtures): self.fixtures = fixtures
    def table(self, name): return EnrolmentQuery(name, self.fixtures)


class TrackEnrolmentTests(unittest.TestCase):
    def setUp(self):
        self.track_id = "11111111-1111-4111-8111-111111111111"
        self.fixtures = {
            "learnora_learning_paths": [
                {"id": self.track_id, "name": "Track", "status": "published", "owner_user_id": None, "organisation_id": None}
            ],
            "learnora_learning_path_courses": [
                {"path_id": self.track_id, "course_id": "course-1", "order_index": 0, "required": True},
                {"path_id": self.track_id, "course_id": "course-2", "order_index": 1, "required": True},
            ],
            "learnora_courses": [
                {"id": "course-1", "title": "One", "status": "published", "ownership": "learnora", "organisation_id": None, "settings": {}},
                {"id": "course-2", "title": "Two", "status": "published", "ownership": "learnora", "organisation_id": None, "settings": {}},
            ],
            "learnora_enrolments": [],
        }

    def test_verified_individual_learner_is_enrolled_in_track_courses(self):
        user = SimpleNamespace(id="learner-1", role="normal", account_type="learner")
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "true"}), patch.object(courses, "supabase", EnrolmentSupabase(self.fixtures)):
            result = courses.self_enrol_in_track(self.track_id, user=user)
        self.assertEqual(result["new_enrolments"], 2)
        self.assertEqual(result["enrolled_courses"], 2)
        self.assertEqual({row["course_id"] for row in self.fixtures["learnora_enrolments"]}, {"course-1", "course-2"})
        self.assertTrue(all(row["source_type"] == f"track_enrolment:{self.track_id}" for row in self.fixtures["learnora_enrolments"]))

    def test_withdrawn_individual_enrolment_is_reactivated_instead_of_duplicated(self):
        self.fixtures["learnora_enrolments"] = [
            {"id": "old-1", "user_id": "learner-1", "course_id": "course-1", "organisation_id": None, "cohort_id": None, "status": "withdrawn", "source_type": "self_enrolment"}
        ]
        user = SimpleNamespace(id="learner-1", role="normal", account_type="learner")
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "true"}), patch.object(courses, "supabase", EnrolmentSupabase(self.fixtures)):
            result = courses.self_enrol_in_track(self.track_id, user=user)
        self.assertEqual(result["reactivated_enrolments"], 1)
        self.assertEqual(result["new_enrolments"], 1)
        self.assertEqual(len(self.fixtures["learnora_enrolments"]), 2)
        restored = self.fixtures["learnora_enrolments"][0]
        self.assertEqual(restored["status"], "active")
        self.assertEqual(restored["source_type"], f"track_enrolment:{self.track_id}")

    def test_suspended_enrolment_is_not_reactivated_by_public_track_enrolment(self):
        self.fixtures["learnora_enrolments"] = [
            {"id": "old-1", "user_id": "learner-1", "course_id": "course-1", "organisation_id": None, "cohort_id": None, "status": "suspended", "source_type": "self_enrolment"}
        ]
        user = SimpleNamespace(id="learner-1", role="normal", account_type="learner")
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "true"}), patch.object(courses, "supabase", EnrolmentSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                courses.self_enrol_in_track(self.track_id, user=user)
        self.assertEqual(raised.exception.status_code, 409)
        self.assertEqual(self.fixtures["learnora_enrolments"][0]["status"], "suspended")

    def test_witstart_organisation_learner_cannot_self_enrol_in_public_track(self):
        user = SimpleNamespace(id="learner-2", role="witstart", account_type="learner")
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "true"}), patch.object(courses, "supabase", EnrolmentSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                courses.self_enrol_in_track(self.track_id, user=user)
        self.assertEqual(raised.exception.status_code, 403)

    def test_individual_role_in_organisation_context_cannot_use_free_track_enrolment(self):
        user = SimpleNamespace(id="learner-2", role="normal", account_type="learner", organisation_id="org-1")
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "true"}), patch.object(courses, "supabase", EnrolmentSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                courses.self_enrol_in_track(self.track_id, user=user)
        self.assertEqual(raised.exception.status_code, 403)

    def test_track_with_tenant_scoped_course_is_not_granted_by_free_mode(self):
        self.fixtures["learnora_courses"][1]["organisation_id"] = "org-1"
        user = SimpleNamespace(id="learner-1", role="normal", account_type="learner")
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "true"}), patch.object(courses, "supabase", EnrolmentSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                courses.self_enrol_in_track(self.track_id, user=user)
        self.assertEqual(raised.exception.status_code, 409)
        self.assertEqual(self.fixtures["learnora_enrolments"], [])


if __name__ == "__main__":
    unittest.main()
