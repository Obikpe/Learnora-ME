"""Regression tests for backend-confirmed completion of public tracks."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import progress


class Query:
    def __init__(self, table, fixtures):
        self.table = table
        self.fixtures = fixtures
        self.filters = []
        self.limit_value = None

    def select(self, *_args, **_kwargs): return self
    def eq(self, column, value): self.filters.append(("eq", column, value)); return self
    def is_(self, column, value): self.filters.append(("is", column, value)); return self
    def in_(self, column, values): self.filters.append(("in", column, list(values))); return self
    def lt(self, column, value): self.filters.append(("lt", column, value)); return self
    def gte(self, column, value): self.filters.append(("gte", column, value)); return self
    def order(self, *_args, **_kwargs): return self
    def limit(self, value): self.limit_value = value; return self

    def execute(self):
        rows = list(self.fixtures.get(self.table, []))
        for kind, column, value in self.filters:
            if kind == "eq": rows = [row for row in rows if row.get(column) == value]
            elif kind == "is" and value == "null": rows = [row for row in rows if row.get(column) is None]
            elif kind == "in": rows = [row for row in rows if row.get(column) in value]
            elif kind == "lt": rows = [row for row in rows if (row.get(column) or 0) < value]
            elif kind == "gte": rows = [row for row in rows if (row.get(column) or 0) >= value]
        if self.limit_value is not None: rows = rows[:self.limit_value]
        return SimpleNamespace(data=rows)


class TrackProgressSupabase:
    def __init__(self, fixtures): self.fixtures = fixtures
    def table(self, name): return Query(name, self.fixtures)


class PublicTrackProgressTests(unittest.TestCase):
    def setUp(self):
        self.track_id = "11111111-1111-4111-8111-111111111111"
        self.fixtures = {
            "learnora_learning_paths": [
                {"id": self.track_id, "name": "Foundations", "slug": "foundations", "description": "", "status": "published", "owner_user_id": None, "organisation_id": None}
            ],
            "learnora_learning_path_courses": [
                {"id": "link-1", "path_id": self.track_id, "course_id": "course-1", "order_index": 0, "required": True},
                {"id": "link-2", "path_id": self.track_id, "course_id": "course-2", "order_index": 1, "required": True},
            ],
            "learnora_courses": [
                {"id": "course-1", "title": "One", "status": "published", "ownership": "learnora", "organisation_id": None},
                {"id": "course-2", "title": "Two", "status": "published", "ownership": "learnora", "organisation_id": None},
            ],
            "learnora_enrolments": [
                {"id": "e1", "user_id": "learner-1", "course_id": "course-1", "status": "completed", "source_type": f"track_enrolment:{self.track_id}"},
                {"id": "e2", "user_id": "learner-1", "course_id": "course-2", "status": "active", "source_type": f"track_enrolment:{self.track_id}"},
            ],
        }
        self.user = SimpleNamespace(id="learner-1", role="normal", account_type="learner")

    def test_track_progress_is_based_on_required_course_completion(self):
        summaries = {
            "course-1": {"total_lessons": 4, "completed_lessons": 4, "progress_percent": 100, "completed": True},
            "course-2": {"total_lessons": 4, "completed_lessons": 2, "progress_percent": 50, "completed": False},
        }
        with patch.object(progress, "supabase", TrackProgressSupabase(self.fixtures)), patch.object(progress, "_course_summary", side_effect=lambda _user, course_id, **_kwargs: summaries[course_id]):
            result = progress.track_progress(self.track_id, user=self.user)
        self.assertTrue(result["enrolled"])
        self.assertFalse(result["completed"])
        self.assertEqual(result["completed_required_courses"], 1)
        self.assertEqual(result["required_courses"], 2)
        self.assertEqual(result["progress_percent"], 75)

    def test_track_is_complete_only_when_every_required_course_is_complete(self):
        summaries = {
            "course-1": {"total_lessons": 4, "completed_lessons": 4, "progress_percent": 100, "completed": True},
            "course-2": {"total_lessons": 4, "completed_lessons": 4, "progress_percent": 100, "completed": True},
        }
        self.fixtures["learnora_enrolments"][1]["status"] = "completed"
        with patch.object(progress, "supabase", TrackProgressSupabase(self.fixtures)), patch.object(progress, "_course_summary", side_effect=lambda _user, course_id, **_kwargs: summaries[course_id]):
            result = progress.track_progress(self.track_id, user=self.user)
        self.assertTrue(result["completed"])
        self.assertEqual(result["progress_percent"], 100)

    def test_existing_learners_keep_progress_access_after_track_unpublish(self):
        self.fixtures["learnora_learning_paths"][0]["status"] = "draft"
        summaries = {
            "course-1": {"total_lessons": 4, "completed_lessons": 4, "progress_percent": 100, "completed": True},
            "course-2": {"total_lessons": 4, "completed_lessons": 2, "progress_percent": 50, "completed": False},
        }
        with patch.object(progress, "supabase", TrackProgressSupabase(self.fixtures)), patch.object(progress, "_course_summary", side_effect=lambda _user, course_id, **_kwargs: summaries[course_id]):
            result = progress.track_progress(self.track_id, user=self.user)
        self.assertTrue(result["enrolled"])
        self.assertEqual(result["track"]["status"], "draft")

    def test_unpublished_track_is_hidden_when_enrolments_belong_to_other_sources(self):
        self.fixtures["learnora_learning_paths"][0]["status"] = "archived"
        for row in self.fixtures["learnora_enrolments"]:
            row["source_type"] = "self_enrolment"
        with patch.object(progress, "supabase", TrackProgressSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                progress.track_progress(self.track_id, user=self.user)
        self.assertEqual(raised.exception.status_code, 404)

    def test_unpublished_track_is_hidden_from_learners_without_existing_enrolments(self):
        self.fixtures["learnora_learning_paths"][0]["status"] = "archived"
        self.fixtures["learnora_enrolments"] = []
        with patch.object(progress, "supabase", TrackProgressSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                progress.track_progress(self.track_id, user=self.user)
        self.assertEqual(raised.exception.status_code, 404)

    def test_archived_course_progress_is_retained_for_existing_track_learner(self):
        self.fixtures["learnora_courses"][1]["status"] = "archived"
        summaries = {
            "course-1": {"total_lessons": 4, "completed_lessons": 4, "progress_percent": 100, "completed": True},
            "course-2": {"total_lessons": 4, "completed_lessons": 2, "progress_percent": 50, "completed": False},
        }
        with patch.object(progress, "supabase", TrackProgressSupabase(self.fixtures)), patch.object(progress, "_course_summary", side_effect=lambda _user, course_id, **_kwargs: summaries[course_id]) as summary_mock:
            result = progress.track_progress(self.track_id, user=self.user)
        summary_mock.assert_any_call("learner-1", "course-2", include_archived=True)
        self.assertEqual(result["courses"][1]["progress"]["progress_percent"], 50)

    def test_course_summary_ignores_draft_modules_and_lessons(self):
        fixtures = {
            "learnora_courses": [{"id": "course-1", "status": "published"}],
            "users": [{"id": "learner-1", "role": "normal"}],
            "learnora_enrolments": [
                {"id": "enrol-1", "user_id": "learner-1", "course_id": "course-1", "status": "active"}
            ],
            "course_modules": [
                {"id": "module-published", "course_id": "course-1", "status": "published", "order_index": 0},
                {"id": "module-draft", "course_id": "course-1", "status": "draft", "order_index": 1},
            ],
            "learnora_lessons": [
                {"id": "lesson-published", "module_id": "module-published", "status": "published", "order_index": 0},
                {"id": "lesson-draft", "module_id": "module-published", "status": "draft", "order_index": 1},
                {"id": "lesson-in-draft-module", "module_id": "module-draft", "status": "published", "order_index": 0},
            ],
            "learnora_lesson_progress": [
                {"user_id": "learner-1", "lesson_id": "lesson-published", "completed": True, "progress_percent": 100},
                {"user_id": "learner-1", "lesson_id": "lesson-draft", "completed": False, "progress_percent": 0},
                {"user_id": "learner-1", "lesson_id": "lesson-in-draft-module", "completed": False, "progress_percent": 0},
            ],
        }
        with patch.object(progress, "supabase", TrackProgressSupabase(fixtures)):
            result = progress._course_summary("learner-1", "course-1")
        self.assertEqual(result["total_lessons"], 1)
        self.assertEqual(result["completed_lessons"], 1)
        self.assertEqual(result["progress_percent"], 100)
        self.assertTrue(result["completed"])

    def test_archived_course_summary_keeps_module_assessment_locks(self):
        fixtures = {
            "learnora_courses": [{"id": "course-1", "status": "archived"}],
            "users": [{"id": "learner-1", "role": "normal"}],
            "learnora_enrolments": [
                {"id": "enrol-1", "user_id": "learner-1", "course_id": "course-1", "status": "active"}
            ],
            "course_modules": [
                {"id": "module-1", "course_id": "course-1", "status": "archived", "order_index": 0},
                {"id": "module-2", "course_id": "course-1", "status": "archived", "order_index": 1},
            ],
            "learnora_lessons": [
                {"id": "lesson-1", "module_id": "module-1", "status": "archived", "order_index": 0},
                {"id": "lesson-2", "module_id": "module-2", "status": "archived", "order_index": 0},
            ],
            "quizzes": [
                {"id": "quiz-1", "course_id": "course-1", "module_id": "module-1", "passing_score": 70, "is_published": True}
            ],
            "quiz_attempts": [],
            "learnora_lesson_progress": [],
        }
        with patch.object(progress, "supabase", TrackProgressSupabase(fixtures)):
            result = progress._course_summary("learner-1", "course-1", include_archived=True)
        self.assertEqual(result["total_lessons"], 2)
        self.assertFalse(result["modules"][1]["locked"])

    def test_organisation_learner_cannot_use_individual_public_track_progress(self):
        user = SimpleNamespace(id="learner-2", role="witstart", account_type="learner")
        with patch.object(progress, "supabase", TrackProgressSupabase(self.fixtures)):
            with self.assertRaises(HTTPException) as raised:
                progress.track_progress(self.track_id, user=user)
        self.assertEqual(raised.exception.status_code, 403)


    def test_module_without_published_quiz_does_not_deadlock_the_track(self):
        fixtures = {
            "learnora_courses": [{"id": "course-1", "status": "published"}],
            "course_modules": [
                {"id": "module-1", "course_id": "course-1", "order_index": 1, "status": "published"},
                {"id": "module-2", "course_id": "course-1", "order_index": 2, "status": "published"},
            ],
            "quizzes": [],
            "quiz_attempts": [],
        }
        with patch.object(progress, "supabase", TrackProgressSupabase(fixtures)):
            progress._assert_module_unlocked("learner-1", "module-2")

    def test_module_unlock_respects_quiz_configured_threshold(self):
        fixtures = {
            "learnora_courses": [{"id": "course-1", "status": "published"}],
            "course_modules": [
                {"id": "module-1", "course_id": "course-1", "order_index": 1, "status": "published"},
                {"id": "module-2", "course_id": "course-1", "order_index": 2, "status": "published"},
            ],
            "quizzes": [
                {"id": "quiz-1", "title": "Module 1 quiz", "module_id": "module-1", "passing_score": 85, "is_published": True},
            ],
            "quiz_attempts": [
                {"id": "attempt-1", "quiz_id": "quiz-1", "user_id": "learner-1", "score": 80, "passed": True},
            ],
        }
        with patch.object(progress, "supabase", TrackProgressSupabase(fixtures)):
            with self.assertRaises(HTTPException) as raised:
                progress._assert_module_unlocked("learner-1", "module-2")
        self.assertEqual(raised.exception.status_code, 423)

    def test_module_unlock_succeeds_at_configured_quiz_threshold(self):
        fixtures = {
            "course_modules": [
                {"id": "module-1", "course_id": "course-1", "order_index": 1, "status": "published"},
                {"id": "module-2", "course_id": "course-1", "order_index": 2, "status": "published"},
            ],
            "quizzes": [
                {"id": "quiz-1", "title": "Module 1 quiz", "module_id": "module-1", "passing_score": 85, "is_published": True},
            ],
            "quiz_attempts": [
                {"id": "attempt-1", "quiz_id": "quiz-1", "user_id": "learner-1", "score": 85, "passed": True},
            ],
        }
        with patch.object(progress, "supabase", TrackProgressSupabase(fixtures)):
            progress._assert_module_unlocked("learner-1", "module-2")

    def test_published_quizzes_and_assignments_are_completion_gates(self):
        fixtures = {
            "quizzes": [{"id": "quiz-1", "title": "Module check", "passing_score": 70, "course_id": "course-1", "is_published": True}],
            "quiz_attempts": [{"quiz_id": "quiz-1", "user_id": "learner-1", "score": 69, "passed": False}],
            "assignments": [{"id": "assignment-1", "title": "Practical task", "course_id": "course-1", "max_score": 100, "is_published": True}],
            "assignment_submissions": [{"id": "submission-1", "assignment_id": "assignment-1", "user_id": "learner-1", "status": "graded", "score": 69, "graded_at": "2026-11-01T12:00:00Z"}],
        }
        with patch.object(progress, "supabase", TrackProgressSupabase(fixtures)):
            result = progress._course_assessment_summary("learner-1", "course-1")
        self.assertEqual(result["total_assessments"], 2)
        self.assertEqual(result["completed_assessments"], 0)
        self.assertFalse(result["completed"])

    def test_quiz_pass_and_assignment_grade_at_seventy_percent_complete_gates(self):
        fixtures = {
            "quizzes": [{"id": "quiz-1", "title": "Module check", "passing_score": 80, "course_id": "course-1", "is_published": True}],
            "quiz_attempts": [{"quiz_id": "quiz-1", "user_id": "learner-1", "score": 80, "passed": True}],
            "assignments": [{"id": "assignment-1", "title": "Practical task", "course_id": "course-1", "max_score": 100, "is_published": True}],
            "assignment_submissions": [{"id": "submission-1", "assignment_id": "assignment-1", "user_id": "learner-1", "status": "graded", "score": 70, "graded_at": "2026-11-01T12:00:00Z"}],
        }
        with patch.object(progress, "supabase", TrackProgressSupabase(fixtures)):
            result = progress._course_assessment_summary("learner-1", "course-1")
        self.assertEqual(result["completed_assessments"], 2)
        self.assertTrue(result["completed"])

    def test_ungraded_assignment_does_not_count_as_complete(self):
        fixtures = {
            "quizzes": [],
            "quiz_attempts": [],
            "assignments": [{"id": "assignment-1", "title": "Practical task", "course_id": "course-1", "max_score": 100, "is_published": True}],
            "assignment_submissions": [{"id": "submission-1", "assignment_id": "assignment-1", "user_id": "learner-1", "status": "submitted", "score": None, "graded_at": None}],
        }
        with patch.object(progress, "supabase", TrackProgressSupabase(fixtures)):
            result = progress._course_assessment_summary("learner-1", "course-1")
        self.assertEqual(result["completed_assessments"], 0)
        self.assertFalse(result["completed"])


if __name__ == "__main__":
    unittest.main()
