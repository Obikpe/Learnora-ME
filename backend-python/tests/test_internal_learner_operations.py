"""Tests for the internal learner oversight and analytics APIs."""
import os
import unittest
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import internal_operations


class FakeQuery:
    def __init__(self, table, fixtures):
        self.table_name = table
        self.fixtures = fixtures
        self.filters = []
        self.start = None
        self.end = None
        self.limit_value = None
        self.ordering = None
        self.head = False

    def select(self, *_args, **kwargs):
        self.head = bool(kwargs.get("head"))
        return self

    def in_(self, column, values):
        self.filters.append(("in", column, list(values)))
        return self

    def eq(self, column, value):
        self.filters.append(("eq", column, value))
        return self

    def is_(self, column, value):
        self.filters.append(("is", column, value))
        return self

    def gte(self, column, value):
        self.filters.append(("gte", column, value))
        return self

    def ilike(self, column, value):
        self.filters.append(("ilike", column, value.strip("%").lower()))
        return self

    def order(self, column, desc=False):
        self.ordering = (column, desc)
        return self

    def range(self, start, end):
        self.start, self.end = start, end
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def execute(self):
        rows = list(self.fixtures.get(self.table_name, []))
        for kind, column, value in self.filters:
            if kind == "in":
                rows = [row for row in rows if row.get(column) in value]
            elif kind == "eq":
                rows = [row for row in rows if row.get(column) == value]
            elif kind == "is" and value == "null":
                rows = [row for row in rows if row.get(column) is None]
            elif kind == "gte":
                rows = [row for row in rows if (row.get(column) or "") >= value]
            elif kind == "ilike":
                rows = [row for row in rows if value in str(row.get(column) or "").lower()]
        if self.ordering:
            column, desc = self.ordering
            rows.sort(key=lambda row: row.get(column) or "", reverse=desc)
        count = len(rows)
        if self.start is not None:
            rows = rows[self.start:self.end + 1]
        if self.limit_value is not None:
            rows = rows[:self.limit_value]
        return SimpleNamespace(data=[] if self.head else rows, count=count)


class FakeSupabase:
    def __init__(self, fixtures):
        self.fixtures = fixtures

    def table(self, name):
        return FakeQuery(name, self.fixtures)


class InternalLearnerOperationsTests(unittest.TestCase):
    def setUp(self):
        recent = datetime.now(timezone.utc).isoformat()
        self.fixtures = {
            "users": [
                {"id": "u1", "name": "Alice", "email": "alice@example.com", "role": "normal", "email_verified_at": recent, "created_at": recent, "sub_status": "expired"},
                {"id": "u2", "name": "Bob", "email": "bob@example.com", "role": "witstart", "email_verified_at": None, "created_at": recent, "sub_status": "trialing"},
                {"id": "u3", "name": "Admin", "email": "admin@example.com", "role": "super_admin", "created_at": recent},
            ],
            "learnora_enrolments": [
                {"id": "e1", "user_id": "u1", "course_id": "c1", "status": "completed", "enrolled_at": recent, "completed_at": recent},
                {"id": "e2", "user_id": "u1", "course_id": "c2", "status": "active", "enrolled_at": recent, "completed_at": None},
            ],
            "learnora_lesson_progress": [
                {"user_id": "u1", "lesson_id": "l1", "completed": True, "progress_percent": 100, "last_accessed_at": recent},
                {"user_id": "u1", "lesson_id": "l2", "completed": False, "progress_percent": 40, "last_accessed_at": recent},
            ],
            "learnora_courses": [
                {"id": "c1", "title": "Course One", "slug": "course-one", "status": "published", "ownership": "learnora"},
                {"id": "c2", "title": "Course Two", "slug": "course-two", "status": "published", "ownership": "learnora"},
            ],
        }

    def test_learner_list_filters_to_individual_roles_and_aggregates_progress(self):
        with patch.object(internal_operations, "supabase", FakeSupabase(self.fixtures)):
            result = internal_operations.learners(q="alice", limit=25, offset=0, staff=SimpleNamespace())
        self.assertEqual([row["id"] for row in result["learners"]], ["u1"])
        summary = result["learners"][0]["learning_summary"]
        self.assertEqual(summary["enrolled_courses"], 2)
        self.assertEqual(summary["completed_courses"], 1)
        self.assertEqual(summary["tracked_lessons"], 2)
        self.assertEqual(summary["completed_lessons"], 1)

    def test_learner_detail_returns_enrolments_and_progress_without_credentials(self):
        with patch.object(internal_operations, "supabase", FakeSupabase(self.fixtures)):
            result = internal_operations.learner_detail("u1", staff=SimpleNamespace())
        self.assertEqual(result["learner"]["email"], "alice@example.com")
        self.assertNotIn("password_hash", result["learner"])
        self.assertEqual(result["enrolments"][0]["course"]["title"], "Course One")
        self.assertEqual(result["learning_summary"]["completed_lessons"], 1)

    def test_learner_detail_does_not_expose_non_learner_accounts(self):
        with patch.object(internal_operations, "supabase", FakeSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                internal_operations.learner_detail("u3", staff=SimpleNamespace())
        self.assertEqual(raised.exception.status_code, 404)

    def test_analytics_reports_backend_counts_and_recent_activity(self):
        with patch.object(internal_operations, "supabase", FakeSupabase(self.fixtures)):
            result = internal_operations.analytics_overview(staff=SimpleNamespace())
        metrics = result["metrics"]
        self.assertEqual(metrics["individual_learners"], 1)
        self.assertEqual(metrics["new_individual_learners_30d"], 1)
        self.assertEqual(metrics["published_learnora_courses"], 2)
        self.assertEqual(metrics["published_global_tracks"], 0)
        self.assertEqual(metrics["active_course_enrolments"], 1)
        self.assertEqual(metrics["completed_course_enrolments"], 1)
        self.assertEqual(metrics["active_learners_30d"], 1)
        self.assertEqual(metrics["lesson_completions_30d"], 1)


if __name__ == "__main__":
    unittest.main()
