"""Security regression tests for cohort course and lesson access."""
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from routers import cohort_learning
from routers.auth import CurrentUser


class CohortLearningAccessTests(unittest.TestCase):
    def test_unassigned_course_is_denied_before_lesson_lookup(self):
        user = CurrentUser(
            id="5ed8ab6d-310a-40d4-baaa-bf6f21a0c9a8",
            name="Learner",
            email="learner@example.invalid",
            role="learner",
            sub_status="inactive",
            account_type="cohort",
        )
        member = {"id": "member-1", "cohort_id": "cohort-1", "track_id": "track-1", "status": "active"}
        query = MagicMock()
        query.select.return_value = query
        query.eq.return_value = query
        query.limit.return_value = query
        query.execute.return_value = SimpleNamespace(data=[])
        db = MagicMock()
        db.table.return_value = query

        with patch.object(cohort_learning, "_active_cohort_member", return_value=({"id": user.id}, member)), \
             patch.object(cohort_learning, "supabase", db):
            with self.assertRaises(HTTPException) as caught:
                cohort_learning.my_cohort_course_lessons("course-not-assigned", user)

        self.assertEqual(caught.exception.status_code, 403)
        self.assertEqual(db.table.call_count, 1)
        self.assertEqual(db.table.call_args.args[0], "cohort_member_course_assignments")

    def test_cross_course_lesson_assignment_is_rejected(self):
        lesson_query = MagicMock()
        lesson_query.select.return_value = lesson_query
        lesson_query.in_.return_value = lesson_query
        lesson_query.execute.return_value = SimpleNamespace(data=[
            {"id": "lesson-1", "module_id": "module-1", "status": "published"}
        ])
        module_query = MagicMock()
        module_query.select.return_value = module_query
        module_query.in_.return_value = module_query
        module_query.execute.return_value = SimpleNamespace(data=[
            {"id": "module-1", "course_id": "different-course"}
        ])
        db = MagicMock()
        db.table.side_effect = lambda name: lesson_query if name == "learnora_lessons" else module_query

        with patch.object(cohort_learning, "supabase", db):
            with self.assertRaises(HTTPException) as caught:
                cohort_learning._validate_lesson_ids("requested-course", ["lesson-1"])

        self.assertEqual(caught.exception.status_code, 400)
        self.assertIn("belong to the selected course", caught.exception.detail)



    def test_assigned_cohort_lesson_returns_ready_video_with_signed_url(self):
        user = CurrentUser(
            id="5ed8ab6d-310a-40d4-baaa-bf6f21a0c9a8",
            name="Learner",
            email="learner@example.invalid",
            role="learner",
            sub_status="inactive",
            account_type="cohort",
        )

        def query_with(data):
            query = MagicMock()
            for method in ("select", "eq", "limit", "order"):
                getattr(query, method).return_value = query
            query.execute.return_value = SimpleNamespace(data=data)
            return query

        queries = {
            "cohort_member_course_assignments": query_with([{"id": "assignment-1"}]),
            "cohort_member_lesson_assignments": query_with([{"id": "lesson-assignment-1"}]),
            "learnora_lessons": query_with([{
                "id": "lesson-1",
                "module_id": "module-1",
                "title": "What is data analytics?",
                "content": "A concise learner note.",
                "status": "published",
            }]),
            "course_modules": query_with([{"id": "module-1", "course_id": "course-1", "title": "Introduction"}]),
            "lesson_videos": query_with([{
                "id": "video-1",
                "lesson_id": "lesson-1",
                "provider": "cloudflare",
                "storage_path": "courses/course-1/lesson-1/video.mp4",
                "status": "ready",
            }]),
        }
        db = MagicMock()
        db.table.side_effect = lambda name: queries[name]

        def sign_assets(rows):
            return [
                {**row, "signed_url": "https://media.example.invalid/signed-video"}
                for row in rows
            ]

        with patch.object(cohort_learning, "_active_cohort_member", return_value=(
            {"id": "account-1", "cohort_id": "cohort-1"},
            {"id": "member-1"},
        )), patch.object(cohort_learning, "supabase", db), patch.object(
            cohort_learning, "_sign_lesson_assets", side_effect=sign_assets
        ) as sign:
            result = cohort_learning.my_cohort_lesson_content("course-1", "lesson-1", user)

        self.assertEqual(result["lesson"]["id"], "lesson-1")
        self.assertEqual(result["module"]["id"], "module-1")
        self.assertEqual(result["videos"][0]["id"], "video-1")
        self.assertEqual(result["videos"][0]["signed_url"], "https://media.example.invalid/signed-video")
        sign.assert_called_once()

    def test_progress_write_rejects_unassigned_lesson(self):
        user = CurrentUser(
            id="5ed8ab6d-310a-40d4-baaa-bf6f21a0c9a8",
            name="Learner",
            email="learner@example.invalid",
            role="learner",
            sub_status="inactive",
            account_type="cohort",
        )
        query = MagicMock()
        query.select.return_value = query
        query.eq.return_value = query
        query.limit.return_value = query
        query.execute.return_value = SimpleNamespace(data=[])
        db = MagicMock()
        db.table.return_value = query
        body = cohort_learning.LessonProgressIn(
            progress_percent=30,
            completed=False,
            last_position_seconds=90,
        )
        with patch.object(cohort_learning, "_active_course_assignment", return_value=(
            {"id": "account-1", "cohort_id": "cohort-1"},
            {"id": "assignment-1", "course_id": "course-1"},
        )), patch.object(cohort_learning, "_active_cohort_member", return_value=(
            {"id": "account-1"},
            {"id": "member-1"},
        )), patch.object(cohort_learning, "supabase", db):
            with self.assertRaises(HTTPException) as caught:
                cohort_learning.update_my_cohort_lesson_progress(
                    "course-1", "lesson-not-assigned", body, user
                )
        self.assertEqual(caught.exception.status_code, 403)
        self.assertEqual(db.table.call_count, 1)
        self.assertEqual(db.table.call_args.args[0], "cohort_member_lesson_assignments")

    def test_completed_progress_is_normalised_to_one_hundred_percent(self):
        user = CurrentUser(
            id="5ed8ab6d-310a-40d4-baaa-bf6f21a0c9a8",
            name="Learner",
            email="learner@example.invalid",
            role="learner",
            sub_status="inactive",
            account_type="cohort",
        )
        allowed_query = MagicMock()
        allowed_query.select.return_value = allowed_query
        allowed_query.eq.return_value = allowed_query
        allowed_query.limit.return_value = allowed_query
        allowed_query.execute.return_value = SimpleNamespace(data=[{"id": "lesson-assignment-1"}])
        progress_query = MagicMock()
        progress_query.upsert.return_value = progress_query
        progress_query.execute.return_value = SimpleNamespace(data=[{"progress_percent": 100, "completed": True}])
        db = MagicMock()
        db.table.side_effect = lambda name: (
            allowed_query if name == "cohort_member_lesson_assignments" else progress_query
        )
        body = cohort_learning.LessonProgressIn(
            progress_percent=35,
            completed=True,
            last_position_seconds=120,
        )
        with patch.object(cohort_learning, "_active_course_assignment", return_value=(
            {"id": "account-1", "cohort_id": "cohort-1"},
            {"id": "assignment-1", "course_id": "course-1"},
        )), patch.object(cohort_learning, "_active_cohort_member", return_value=(
            {"id": "account-1"},
            {"id": "member-1"},
        )), patch.object(cohort_learning, "supabase", db):
            result = cohort_learning.update_my_cohort_lesson_progress(
                "course-1", "lesson-1", body, user
            )
        payload = progress_query.upsert.call_args.args[0]
        self.assertEqual(payload["progress_percent"], 100)
        self.assertTrue(payload["completed"])
        self.assertEqual(result["progress"]["progress_percent"], 100)


if __name__ == "__main__":
    unittest.main()
