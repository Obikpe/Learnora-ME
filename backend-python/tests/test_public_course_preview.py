"""Public course preview endpoint must expose only published preview lessons."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import public_directory


class _Query:
    def __init__(self, table_name):
        self.table_name = table_name
        self.filters = []
        self.selected = ""

    def select(self, value):
        self.selected = value
        return self

    def eq(self, key, value):
        self.filters.append(("eq", key, value))
        return self

    def in_(self, key, value):
        self.filters.append(("in", key, value))
        return self

    def order(self, *args, **kwargs):
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def execute(self):
        if self.table_name == "course_modules":
            assert ("eq", "status", "published") in self.filters
            return SimpleNamespace(data=[{"id": "module-1"}])
        if self.table_name == "learnora_lessons":
            assert ("eq", "status", "published") in self.filters
            assert ("eq", "is_preview", True) in self.filters
            assert ("in", "module_id", ["module-1"]) in self.filters
            assert self.limit_value == 1
            return SimpleNamespace(data=[{
                "id": "lesson-1",
                "module_id": "module-1",
                "title": "Preview lesson",
                "content": "# Public preview",
                "is_preview": True,
                "status": "published",
            }])
        raise AssertionError(f"Unexpected table: {self.table_name}")


class PublicCoursePreviewTests(unittest.TestCase):
    def test_endpoint_returns_only_first_published_preview_lesson(self):
        with patch.object(public_directory, "_public_course_lookup", return_value={
            "id": "course-1", "title": "Course", "slug": "course",
        }), patch.object(public_directory.supabase, "table", side_effect=lambda name: _Query(name)):
            result = public_directory.public_course_preview("course-1", None)

        self.assertTrue(result["success"])
        self.assertEqual(result["preview"]["id"], "lesson-1")
        self.assertTrue(result["preview"]["is_preview"])

    def test_endpoint_returns_404_when_no_published_preview_exists(self):
        class NoPreviewQuery(_Query):
            def execute(self):
                if self.table_name == "course_modules":
                    return SimpleNamespace(data=[{"id": "module-1"}])
                return SimpleNamespace(data=[])

        with patch.object(public_directory, "_public_course_lookup", return_value={
            "id": "course-1", "title": "Course", "slug": "course",
        }), patch.object(public_directory.supabase, "table", side_effect=lambda name: NoPreviewQuery(name)):
            with self.assertRaises(HTTPException) as raised:
                public_directory.public_course_preview("course-1", None)

        self.assertEqual(raised.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
