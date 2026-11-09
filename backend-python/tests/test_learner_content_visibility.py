"""Regression checks for learner-facing course and lesson publication guards."""
from pathlib import Path
import unittest


class LearnerContentVisibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (
            Path(__file__).resolve().parents[1] / "routers" / "progress.py"
        ).read_text(encoding="utf-8")

    def test_lesson_context_checks_lesson_module_and_course_status(self):
        helper = self.source.split(
            "def _available_lesson_context(", 1
        )[1].split(
            "def _lesson_context(", 1
        )[0]
        self.assertIn("content,status,course_modules!inner(course_id,status)", helper)
        self.assertIn('course_status not in {"published", "archived"}', helper)
        self.assertIn('module_status not in {"published", "archived"}', helper)
        self.assertIn('lesson_status not in {"published", "archived"}', helper)
        self.assertIn('course_status != "archived" and lesson_status != "published"', helper)

    def test_enrolment_rejects_draft_or_missing_courses(self):
        helper = self.source.split(
            "def _enrolment(", 1
        )[1].split(
            "def effective_passing_score(", 1
        )[0]
        self.assertIn('select("id,status")', helper)
        self.assertIn('not in {"published", "archived"}', helper)

    def test_lesson_notes_media_and_progress_use_shared_visibility_guard(self):
        for name in (
            "get_lesson_content",
            "get_lesson_workspace",
            "get_lesson_note",
            "save_lesson_note",
            "lesson_media",
            "update_lesson_progress",
        ):
            start = self.source.index(f"def {name}(")
            end = self.source.find("\n@router.", start)
            block = self.source[start:end if end >= 0 else None]
            self.assertIn("_lesson_context(lesson_id, str(user.id))", block, name)

    def test_lesson_to_module_resolution_uses_same_visibility_guard(self):
        helper = self.source.split(
            "def _module_for_lesson(", 1
        )[1].split(
            "def _module_for_quiz(", 1
        )[0]
        self.assertIn("_available_lesson_context(lesson_id)", helper)


if __name__ == "__main__":
    unittest.main()
