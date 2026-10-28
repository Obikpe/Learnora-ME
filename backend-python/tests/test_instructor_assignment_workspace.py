"""Tests for the organisation instructor's scoped teaching workspace."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import auth, cohort_learning


class Query:
    def __init__(self, db, table):
        self.db = db
        self.table_name = table
        self.filters = []

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, key, value):
        self.filters.append((key, "eq", str(value)))
        return self

    def in_(self, key, values):
        self.filters.append((key, "in", {str(value) for value in values}))
        return self

    def order(self, *_args, **_kwargs):
        return self

    def execute(self):
        rows = self.db.rows.get(self.table_name, [])
        for key, operation, value in self.filters:
            if operation == "eq":
                rows = [row for row in rows if str(row.get(key)) == value]
            else:
                rows = [row for row in rows if str(row.get(key)) in value]
        return SimpleNamespace(data=rows)


class FakeSupabase:
    def __init__(self, rows):
        self.rows = rows

    def table(self, name):
        return Query(self, name)


def learner_user(user_id="instructor-1"):
    return auth.CurrentUser(
        id=user_id,
        email="instructor@example.com",
        role="normal",
        sub_status="active",
        account_type="learner",
        is_paid=False,
    )


class InstructorAssignmentWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.db = FakeSupabase({
            "organisation_members": [
                {"organisation_id": "org-1", "user_id": "instructor-1", "role": "instructor", "status": "active"},
                {"organisation_id": "org-2", "user_id": "instructor-1", "role": "learner", "status": "active"},
            ],
            "organisations": [
                {"id": "org-1", "name": "North Academy", "is_active": True},
                {"id": "org-2", "name": "Inactive Academy", "is_active": False},
            ],
            "cohort_member_course_assignments": [
                {"id": "assignment-1", "tutor_user_id": "instructor-1", "cohort_member_id": "member-1", "cohort_id": "cohort-1", "course_id": "course-1", "status": "active", "assigned_at": "2026-10-01T00:00:00Z", "updated_at": "2026-10-01T00:00:00Z"},
                {"id": "assignment-2", "tutor_user_id": "someone-else", "cohort_member_id": "member-1", "cohort_id": "cohort-1", "course_id": "course-1", "status": "active", "assigned_at": "2026-10-02T00:00:00Z", "updated_at": "2026-10-02T00:00:00Z"},
            ],
            "cohorts": [{"id": "cohort-1", "name": "October cohort", "organisation_id": "org-1", "status": "active", "start_date": "2026-10-01", "end_date": "2026-12-01"}],
            "cohort_members": [{"id": "member-1", "cohort_id": "cohort-1", "cohort_account_id": "account-1", "user_id": None, "track_id": "track-1", "status": "active"}],
            "cohort_accounts": [{"id": "account-1", "first_name": "Ada", "last_name": "Learner", "username": "ada.learner", "status": "active"}],
            "learnora_courses": [{"id": "course-1", "title": "Data Fundamentals", "slug": "data-fundamentals", "status": "published", "estimated_hours": 12}],
            "cohort_member_lesson_assignments": [
                {"course_assignment_id": "assignment-1", "lesson_id": "lesson-1", "status": "active"},
                {"course_assignment_id": "assignment-1", "lesson_id": "lesson-2", "status": "active"},
            ],
            "learnora_lessons": [
                {"id": "lesson-1", "title": "Introduction", "order_index": 1, "duration_minutes": 15},
                {"id": "lesson-2", "title": "Working with data", "order_index": 2, "duration_minutes": 25},
            ],
            "cohort_account_lesson_progress": [
                {"course_assignment_id": "assignment-1", "lesson_id": "lesson-1", "progress_percent": 100, "completed": True},
                {"course_assignment_id": "assignment-1", "lesson_id": "lesson-1", "progress_percent": 20, "completed": False},
                {"course_assignment_id": "assignment-1", "lesson_id": "lesson-2", "progress_percent": 40, "completed": False},
                {"course_assignment_id": "assignment-1", "lesson_id": "revoked-lesson", "progress_percent": 100, "completed": True},
            ],
            "users": [],
        })

    def test_returns_only_this_instructors_active_assignments(self):
        with patch.object(cohort_learning, "supabase", self.db):
            result = cohort_learning.my_instructor_assignments(learner_user())
        self.assertEqual(len(result["assignments"]), 1)
        assignment = result["assignments"][0]
        self.assertEqual(assignment["cohort"]["organisation_name"], "North Academy")
        self.assertEqual(assignment["learner"]["name"], "Ada Learner")
        self.assertEqual(assignment["course"]["title"], "Data Fundamentals")
        self.assertEqual(assignment["assigned_lesson_count"], 2)
        self.assertEqual(assignment["completed_lesson_count"], 1)
        self.assertEqual(assignment["in_progress_lesson_count"], 1)
        self.assertEqual(assignment["completion_percent"], 50)
        self.assertEqual(
            assignment["lesson_progress"],
            [
                {"lesson_id": "lesson-1", "title": "Introduction", "order_index": 1, "duration_minutes": 15, "progress_percent": 100, "completed": True, "status": "completed"},
                {"lesson_id": "lesson-2", "title": "Working with data", "order_index": 2, "duration_minutes": 25, "progress_percent": 40, "completed": False, "status": "in_progress"},
            ],
        )
        self.assertNotIn("email", assignment["learner"])

    def test_learner_membership_cannot_open_instructor_workspace(self):
        self.db.rows["organisation_members"] = [
            {"organisation_id": "org-1", "user_id": "instructor-1", "role": "learner", "status": "active"}
        ]
        with patch.object(cohort_learning, "supabase", self.db):
            with self.assertRaises(HTTPException) as raised:
                cohort_learning.my_instructor_assignments(learner_user())
        self.assertEqual(raised.exception.status_code, 403)

    def test_organisation_roster_includes_scoped_learner_course_progress(self):
        context = SimpleNamespace(is_platform_admin=True, organisation_id=None)
        with patch.object(cohort_learning, "supabase", self.db):
            result = cohort_learning.list_learner_course_assignments(
                "org-1", "cohort-1", "member-1", context
            )
        assignments = {item["id"]: item for item in result["assignments"]}
        self.assertEqual(assignments["assignment-1"]["assigned_lesson_count"], 2)
        self.assertEqual(assignments["assignment-1"]["completed_lesson_count"], 1)
        self.assertEqual(assignments["assignment-1"]["in_progress_lesson_count"], 1)
        self.assertEqual(assignments["assignment-1"]["completion_percent"], 50)
        self.assertEqual(assignments["assignment-2"]["assigned_lesson_count"], 0)
        self.assertEqual(assignments["assignment-2"]["completion_percent"], 0)


if __name__ == "__main__":
    unittest.main()
