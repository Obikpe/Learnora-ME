"""Course publication readiness tests for the Teams content API."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import internal_content


class PublishQuery:
    def __init__(self, table, fixtures):
        self.table = table
        self.fixtures = fixtures
        self.filters = []
        self.limit_value = None
    def select(self, *_args, **_kwargs): return self
    def eq(self, column, value): self.filters.append(("eq", column, value)); return self
    def in_(self, column, values): self.filters.append(("in", column, list(values))); return self
    def is_(self, column, value): self.filters.append(("is", column, value)); return self
    def order(self, *_args, **_kwargs): return self
    def limit(self, value): self.limit_value = value; return self
    def execute(self):
        rows = list(self.fixtures.get(self.table, []))
        for kind, column, value in self.filters:
            if kind == "eq": rows = [row for row in rows if row.get(column) == value]
            elif kind == "in": rows = [row for row in rows if row.get(column) in value]
            elif kind == "is" and value == "null": rows = [row for row in rows if row.get(column) is None]
        if self.limit_value is not None: rows = rows[:self.limit_value]
        return SimpleNamespace(data=rows)


class PublishSupabase:
    def __init__(self, fixtures): self.fixtures = fixtures
    def table(self, name): return PublishQuery(name, self.fixtures)


class CoursePublicationTests(unittest.TestCase):
    def setUp(self):
        self.fixtures = {
            "course_modules": [
                {"id": "module-1", "course_id": "course-1", "order_index": 0, "status": "published"},
                {"id": "module-2", "course_id": "course-1", "order_index": 1, "status": "published"},
            ],
            "learnora_lessons": [
                {"id": "lesson-1", "module_id": "module-1", "status": "published"}
            ],
            "quizzes": [
                {"id": "quiz-1", "module_id": "module-1", "is_published": True}
            ],
            "quiz_questions": [
                {"id": "question-1", "quiz_id": "quiz-1", "question_type": "multiple_choice", "options": ["A", "B"], "correct_answer": "A"}
            ],
        }

    def test_published_course_requires_a_published_module(self):
        self.fixtures["course_modules"] = []
        with patch.object(internal_content, "supabase", PublishSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                internal_content._assert_course_publishable("course-1")
        self.assertEqual(raised.exception.status_code, 409)

    def test_published_course_requires_at_least_one_published_lesson(self):
        self.fixtures["learnora_lessons"] = []
        with patch.object(internal_content, "supabase", PublishSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                internal_content._assert_course_publishable("course-1")
        self.assertEqual(raised.exception.status_code, 409)

    def test_each_non_final_module_requires_a_published_assessment(self):
        self.fixtures["quizzes"] = []
        with patch.object(internal_content, "supabase", PublishSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                internal_content._assert_course_publishable("course-1")
        self.assertEqual(raised.exception.status_code, 409)

    def test_valid_course_curriculum_can_be_published(self):
        with patch.object(internal_content, "supabase", PublishSupabase(self.fixtures)):
            internal_content._assert_course_publishable("course-1")

    def test_global_content_manager_rejects_organisation_owned_courses(self):
        self.fixtures["learnora_courses"] = [
            {"id": "tenant-course", "ownership": "learnora", "organisation_id": "org-1"}
        ]
        with patch.object(internal_content, "supabase", PublishSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                internal_content._global_learnora_course("tenant-course")
        self.assertEqual(raised.exception.status_code, 404)

    def test_global_content_manager_rejects_creator_owned_courses(self):
        self.fixtures["learnora_courses"] = [
            {"id": "creator-course", "ownership": "creator", "organisation_id": None}
        ]
        with patch.object(internal_content, "supabase", PublishSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                internal_content._global_learnora_course("creator-course")
        self.assertEqual(raised.exception.status_code, 404)

    def test_course_creation_rejects_organisation_ownership_in_global_workspace(self):
        payload = internal_content.CourseCreate(title="Tenant course", slug="tenant-course", ownership="organisation", organisation_id="org-1")
        with self.assertRaises(HTTPException) as raised:
            internal_content.create_course(payload, staff=SimpleNamespace(user_id="staff-1"))
        self.assertEqual(raised.exception.status_code, 403)

    def test_course_creation_must_start_as_draft(self):
        payload = internal_content.CourseCreate(title="Empty course", slug="empty-course", status="published")
        with self.assertRaises(HTTPException) as raised:
            internal_content.create_course(payload, staff=SimpleNamespace(user_id="staff-1"))
        self.assertEqual(raised.exception.status_code, 409)


    def test_published_assessment_requires_at_least_one_answerable_question(self):
        self.fixtures["quiz_questions"] = []
        with patch.object(internal_content, "supabase", PublishSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                internal_content._assert_course_publishable("course-1")
        self.assertEqual(raised.exception.status_code, 409)


if __name__ == "__main__":
    unittest.main()
