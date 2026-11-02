"""Tests for optional learning plans and canonical track separation."""
import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import learning_plans


class LearningPlanTests(unittest.TestCase):
    def test_only_individual_learners_can_use_personal_plans(self):
        learning_plans._assert_individual(SimpleNamespace(
            role="normal", account_type="learner", organisation_id=None,
        ))
        for user in (
            SimpleNamespace(role="normal", account_type="cohort", organisation_id="org-1"),
            SimpleNamespace(role="normal", account_type="learner", organisation_id="org-1"),
            SimpleNamespace(role="staff_admin", account_type="admin", organisation_id=None),
        ):
            with self.subTest(user=user):
                with self.assertRaises(HTTPException) as raised:
                    learning_plans._assert_individual(user)
                self.assertEqual(raised.exception.status_code, 403)

    def test_schedule_uses_only_supplied_catalogue_course_ids(self):
        courses = [
            {"id": "course-a", "title": "Foundations", "estimated_hours": 2, "required": True},
            {"id": "course-b", "title": "Applied work", "estimated_hours": 3, "required": False},
        ]
        weeks = learning_plans._schedule(courses, 120)
        scheduled_ids = {
            task["course_id"]
            for week in weeks
            for task in week["tasks"]
        }
        self.assertEqual(scheduled_ids, {"course-a", "course-b"})
        self.assertEqual(weeks[0]["tasks"][0]["course_id"], "course-a")
        self.assertTrue(weeks[0]["tasks"][0]["required"])
        self.assertFalse(weeks[1]["tasks"][0]["required"])

    def test_schedule_respects_weekly_capacity(self):
        courses = [{"id": "course-a", "title": "Course A", "estimated_hours": 5, "required": True}]
        weeks = learning_plans._schedule(courses, 120)
        self.assertEqual(len(weeks), 3)
        self.assertEqual([week["minutes"] for week in weeks], [120, 120, 60])

    def test_schedule_keeps_a_safe_minimum_weekly_capacity(self):
        courses = [{"id": "course-a", "title": "Course A", "estimated_hours": 1, "required": True}]
        weeks = learning_plans._schedule(courses, 0)
        self.assertEqual([week["minutes"] for week in weeks], [15, 15, 15, 15])
        self.assertTrue(all(week["tasks"] for week in weeks))

    def test_schedule_never_returns_an_empty_week(self):
        courses = [{"id": "course-a", "title": "Course A", "estimated_hours": 1, "required": True}]
        weeks = learning_plans._schedule(courses, 180)
        self.assertEqual(len(weeks), 1)
        self.assertGreater(weeks[0]["minutes"], 0)
        self.assertEqual(weeks[0]["tasks"][0]["course_id"], "course-a")


if __name__ == "__main__":
    unittest.main()
