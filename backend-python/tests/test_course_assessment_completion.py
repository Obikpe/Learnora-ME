"""Isolated tests for assessment-based course completion."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from routers import progress


class Query:
    def __init__(self, table, fixtures):
        self.table = table
        self.fixtures = fixtures
        self.filters = []
        self.ordering = None

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, column, value):
        self.filters.append(("eq", column, value))
        return self

    def in_(self, column, values):
        self.filters.append(("in", column, set(values)))
        return self

    def order(self, column, desc=False):
        self.ordering = (column, desc)
        return self

    def execute(self):
        rows = list(self.fixtures.get(self.table, []))
        for kind, column, value in self.filters:
            if kind == "eq":
                rows = [row for row in rows if row.get(column) == value]
            else:
                rows = [row for row in rows if row.get(column) in value]
        if self.ordering:
            column, desc = self.ordering
            rows.sort(key=lambda row: row.get(column) or "", reverse=desc)
        return SimpleNamespace(data=rows)


class FakeSupabase:
    def __init__(self, fixtures):
        self.fixtures = fixtures

    def table(self, name):
        return Query(name, self.fixtures)


class CourseAssessmentCompletionTests(unittest.TestCase):
    def setUp(self):
        self.fixtures = {
            "quizzes": [
                {"id": "quiz-pass", "course_id": "course-1", "passing_score": 80, "is_published": True},
                {"id": "quiz-draft", "course_id": "course-1", "passing_score": 70, "is_published": False},
            ],
            "quiz_attempts": [
                {"quiz_id": "quiz-pass", "user_id": "learner-1", "score": 75, "passed": True, "submitted_at": "2026-11-01T10:00:00Z"},
            ],
            "assignments": [
                {"id": "assignment-pass", "course_id": "course-1", "max_score": 100, "is_published": True},
                {"id": "assignment-draft", "course_id": "course-1", "max_score": 100, "is_published": False},
            ],
            "assignment_submissions": [
                {"id": "old-pass", "assignment_id": "assignment-pass", "user_id": "learner-1", "status": "graded", "score": 90, "graded_at": "2026-10-30T10:00:00Z", "submitted_at": "2026-10-30T09:00:00Z"},
                {"id": "latest-fail", "assignment_id": "assignment-pass", "user_id": "learner-1", "status": "graded", "score": 60, "graded_at": "2026-11-01T10:00:00Z", "submitted_at": "2026-11-01T09:00:00Z"},
            ],
        }

    def test_published_quiz_requires_configured_passing_threshold(self):
        with patch.object(progress, "supabase", FakeSupabase(self.fixtures)):
            result = progress._course_assessment_summary("learner-1", "course-1")
        self.assertEqual(result["total_quizzes"], 1)
        self.assertEqual(result["passed_quizzes"], 0)
        self.assertEqual(result["completed_assessments"], 0)

    def test_latest_assignment_submission_controls_completion(self):
        self.fixtures["quiz_attempts"][0]["score"] = 85
        self.fixtures["quiz_attempts"][0]["passed"] = True
        with patch.object(progress, "supabase", FakeSupabase(self.fixtures)):
            result = progress._course_assessment_summary("learner-1", "course-1")
        self.assertEqual(result["total_assignments"], 1)
        self.assertEqual(result["passed_assignments"], 0)
        self.assertEqual(result["completed_assessments"], 1)

    def test_unpublished_assessments_do_not_block_completion(self):
        self.fixtures["quizzes"][0]["is_published"] = False
        self.fixtures["assignments"][0]["is_published"] = False
        with patch.object(progress, "supabase", FakeSupabase(self.fixtures)):
            result = progress._course_assessment_summary("learner-1", "course-1")
        self.assertEqual(result["total_assessments"], 0)
        self.assertTrue(result["completed"])


if __name__ == "__main__":
    unittest.main()
