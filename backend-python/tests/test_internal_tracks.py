"""Tests for global track management over the existing learning-path schema."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import internal_tracks


class TrackQuery:
    def __init__(self, table, fixtures):
        self.table = table
        self.fixtures = fixtures
        self.filters = []
        self.action = "select"
        self.values = None
        self.ordering = None
        self.limit_value = None

    def select(self, *_args, **_kwargs): return self
    def eq(self, column, value): self.filters.append(("eq", column, value)); return self
    def neq(self, column, value): self.filters.append(("neq", column, value)); return self
    def is_(self, column, value): self.filters.append(("is", column, value)); return self
    def in_(self, column, values): self.filters.append(("in", column, list(values))); return self
    def order(self, column, desc=False): self.ordering = (column, desc); return self
    def limit(self, value): self.limit_value = value; return self
    def insert(self, values): self.action = "insert"; self.values = values; return self
    def update(self, values): self.action = "update"; self.values = values; return self
    def delete(self): self.action = "delete"; return self

    def execute(self):
        rows = self.fixtures.setdefault(self.table, [])
        selected = list(rows)
        for kind, column, value in self.filters:
            if kind == "eq": selected = [row for row in selected if row.get(column) == value]
            elif kind == "neq": selected = [row for row in selected if row.get(column) != value]
            elif kind == "is" and value == "null": selected = [row for row in selected if row.get(column) is None]
            elif kind == "in": selected = [row for row in selected if row.get(column) in value]
        if self.ordering:
            column, desc = self.ordering
            selected.sort(key=lambda row: row.get(column) or 0, reverse=desc)
        if self.limit_value is not None:
            selected = selected[:self.limit_value]

        if self.action == "insert":
            values = self.values if isinstance(self.values, list) else [self.values]
            rows.extend(dict(value) for value in values)
            return SimpleNamespace(data=[dict(value) for value in values])
        if self.action == "update":
            updated = []
            for row in selected:
                row.update(self.values)
                updated.append(dict(row))
            return SimpleNamespace(data=updated)
        if self.action == "delete":
            deleted = [dict(row) for row in selected]
            for row in deleted:
                rows.remove(next(item for item in rows if item.get("id") == row.get("id")))
            return SimpleNamespace(data=deleted)
        return SimpleNamespace(data=selected)


class TrackSupabase:
    def __init__(self, fixtures):
        self.fixtures = fixtures

    def table(self, name):
        return TrackQuery(name, self.fixtures)


class InternalTracksTests(unittest.TestCase):
    def setUp(self):
        self.fixtures = {
            "learnora_learning_paths": [
                {"id": "11111111-1111-4111-8111-111111111111", "owner_user_id": None, "organisation_id": None, "name": "Global", "slug": "global", "description": "", "status": "draft"},
                {"id": "22222222-2222-4222-8222-222222222222", "owner_user_id": "user-1", "organisation_id": None, "name": "Personal", "slug": "personal", "status": "published"},
                {"id": "33333333-3333-4333-8333-333333333333", "owner_user_id": None, "organisation_id": "org-1", "name": "Org", "slug": "org", "status": "published"},
            ],
            "learnora_learning_path_courses": [
                {"id": "link-1", "path_id": "11111111-1111-4111-8111-111111111111", "course_id": "course-1", "order_index": 0, "required": True},
                {"id": "link-2", "path_id": "11111111-1111-4111-8111-111111111111", "course_id": "course-2", "order_index": 1, "required": True},
            ],
            "learnora_courses": [
                {"id": "course-1", "title": "One", "status": "published", "ownership": "learnora", "organisation_id": None},
                {"id": "course-2", "title": "Two", "status": "published", "ownership": "learnora", "organisation_id": None},
            ],
            "course_modules": [
                {"id": "module-1", "course_id": "course-1", "status": "published"},
                {"id": "module-2", "course_id": "course-2", "status": "published"},
            ],
            "learnora_lessons": [
                {"id": "lesson-1", "module_id": "module-1", "status": "published"},
                {"id": "lesson-2", "module_id": "module-2", "status": "published"},
            ],
        }

    def test_global_track_scope_excludes_personal_and_organisation_paths(self):
        with patch.object(internal_tracks, "supabase", TrackSupabase(self.fixtures)):
            result = internal_tracks._global_track("11111111-1111-4111-8111-111111111111")
            with self.assertRaises(HTTPException) as personal:
                internal_tracks._global_track("22222222-2222-4222-8222-222222222222")
            with self.assertRaises(HTTPException) as organisation:
                internal_tracks._global_track("33333333-3333-4333-8333-333333333333")
        self.assertEqual(result["name"], "Global")
        self.assertEqual(personal.exception.status_code, 404)
        self.assertEqual(organisation.exception.status_code, 404)

    def test_publish_requires_published_global_learnora_courses_and_required_content(self):
        with patch.object(internal_tracks, "supabase", TrackSupabase(self.fixtures)):
            internal_tracks._assert_publishable("11111111-1111-4111-8111-111111111111")
            self.fixtures["learnora_courses"][1]["status"] = "draft"
            with self.assertRaises(HTTPException) as raised:
                internal_tracks._assert_publishable("11111111-1111-4111-8111-111111111111")
        self.assertEqual(raised.exception.status_code, 409)

    def test_reorder_updates_only_track_course_positions(self):
        with patch.object(internal_tracks, "supabase", TrackSupabase(self.fixtures)):
            result = internal_tracks.reorder_track_courses(
                "11111111-1111-4111-8111-111111111111",
                [
                    internal_tracks.TrackCourseOrder(id="link-2", order_index=0),
                    internal_tracks.TrackCourseOrder(id="link-1", order_index=1),
                ],
                staff=SimpleNamespace(),
            )
        ordered = sorted(result["courses"], key=lambda row: row["order_index"])
        self.assertEqual([row["id"] for row in ordered], ["link-2", "link-1"])
        self.assertEqual([row["order_index"] for row in ordered], [0, 1])

    def test_published_track_course_list_cannot_be_mutated(self):
        self.fixtures["learnora_learning_paths"][0]["status"] = "published"
        with patch.object(internal_tracks, "supabase", TrackSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                internal_tracks.remove_track_course(
                    "11111111-1111-4111-8111-111111111111",
                    "course-1",
                    staff=SimpleNamespace(),
                )
        self.assertEqual(raised.exception.status_code, 409)


if __name__ == "__main__":
    unittest.main()
