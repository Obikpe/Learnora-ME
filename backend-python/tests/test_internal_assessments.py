"""Regression tests for global course assessment authoring rules."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import internal_assessments


class Query:
    def __init__(self, table, fixtures):
        self.table, self.fixtures = table, fixtures
        self.filters, self.action, self.values, self.limit_value = [], "select", None, None
    def select(self, *_args, **_kwargs): return self
    def eq(self, column, value): self.filters.append(("eq", column, value)); return self
    def is_(self, column, value): self.filters.append(("is", column, value)); return self
    def limit(self, value): self.limit_value = value; return self
    def order(self, *_args, **_kwargs): return self
    def execute(self):
        rows = list(self.fixtures.get(self.table, []))
        for kind, column, value in self.filters:
            if kind == "eq": rows = [row for row in rows if row.get(column) == value]
            elif kind == "is" and value == "null": rows = [row for row in rows if row.get(column) is None]
        if self.limit_value is not None: rows = rows[:self.limit_value]
        return SimpleNamespace(data=rows)


class FakeSupabase:
    def __init__(self, fixtures): self.fixtures = fixtures
    def table(self, name): return Query(name, self.fixtures)


class InternalAssessmentTests(unittest.TestCase):
    def setUp(self):
        self.fixtures = {
            "learnora_courses": [{"id": "course-1", "ownership": "learnora", "organisation_id": None, "status": "draft"}],
            "course_modules": [{"id": "module-1", "course_id": "course-1"}],
            "learnora_lessons": [{"id": "lesson-1", "module_id": "module-1"}],
            "quizzes": [{"id": "quiz-1", "course_id": "course-1", "module_id": "module-1", "is_published": False}],
            "quiz_questions": [],
        }

    def test_global_course_guard_rejects_tenant_owned_courses(self):
        self.fixtures["learnora_courses"][0]["organisation_id"] = "org-1"
        with patch.object(internal_assessments, "supabase", FakeSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                internal_assessments._course("course-1")
        self.assertEqual(raised.exception.status_code, 404)

    def test_lesson_must_belong_to_selected_course_module(self):
        self.fixtures["course_modules"][0]["course_id"] = "course-2"
        with patch.object(internal_assessments, "supabase", FakeSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                internal_assessments._validate_assessment_location("course-1", None, "lesson-1")
        self.assertEqual(raised.exception.status_code, 422)

    def test_quiz_cannot_be_published_without_questions(self):
        with patch.object(internal_assessments, "supabase", FakeSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                internal_assessments._assert_quiz_publishable("quiz-1")
        self.assertEqual(raised.exception.status_code, 409)

    def test_quiz_publication_requires_a_correct_answer(self):
        self.fixtures["quiz_questions"] = [{
            "id": "question-1", "quiz_id": "quiz-1", "question": "Choose one",
            "question_type": "multiple_choice", "options": ["A", "B"],
            "correct_answer": None, "points": 1,
        }]
        with patch.object(internal_assessments, "supabase", FakeSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                internal_assessments._assert_quiz_publishable("quiz-1")
        self.assertEqual(raised.exception.status_code, 409)

    def test_valid_quiz_can_pass_publication_readiness(self):
        self.fixtures["quiz_questions"] = [{
            "id": "question-1", "quiz_id": "quiz-1", "question": "Choose one",
            "question_type": "multiple_choice", "options": ["A", "B"],
            "correct_answer": "A", "points": 1,
        }]
        with patch.object(internal_assessments, "supabase", FakeSupabase(self.fixtures)):
            internal_assessments._assert_quiz_publishable("quiz-1")


if __name__ == "__main__":
    unittest.main()
