"""Regression contract for page-scoped AI tutor restrictions."""
import inspect
import os
import unittest

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from routers import ai


class QuizTutorAccessTests(unittest.TestCase):
    def test_active_quiz_session_is_not_a_global_tutor_lock(self):
        source = inspect.getsource(ai.ask)
        self.assertNotIn("_assert_no_active_quiz_session", source)
        self.assertNotIn("quiz_active_sessions", source)
        self.assertFalse(hasattr(ai, "_assert_no_active_quiz_session"))

    def test_assessment_context_remains_blocked(self):
        source = inspect.getsource(ai.ask)
        self.assertIn("if body.assessment_id:", source)
        self.assertIn(
            "AI tutor is unavailable for quiz and assessment content.",
            source,
        )

    def test_tutor_api_does_not_query_other_tabs_or_sessions(self):
        source = inspect.getsource(ai)
        self.assertNotIn("_assert_no_active_quiz_session", source)
        self.assertNotIn("quiz_active_sessions", source)


if __name__ == "__main__":
    unittest.main()
