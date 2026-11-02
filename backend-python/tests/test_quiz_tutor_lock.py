"""Regression tests for the active-quiz AI tutor lock."""
import os
import unittest
from unittest.mock import patch
from types import SimpleNamespace

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import ai


class Query:
    def __init__(self, rows=None, error=None):
        self.rows = rows or []
        self.error = error
        self.filters = []
    def select(self, *_args, **_kwargs): return self
    def eq(self, key, value): self.filters.append(("eq", key, value)); return self
    def gt(self, key, value): self.filters.append(("gt", key, value)); return self
    def limit(self, _value): return self
    def execute(self):
        if self.error:
            raise self.error
        return SimpleNamespace(data=self.rows)


class FakeSupabase:
    def __init__(self, rows=None, error=None):
        self.query = Query(rows, error)
    def table(self, name):
        if name != "quiz_active_sessions":
            raise AssertionError("Unexpected table: "+name)
        return self.query


class ActiveQuizTutorLockTests(unittest.TestCase):
    def test_active_quiz_blocks_tutor(self):
        with patch.object(ai, "supabase", FakeSupabase([{"id": "session-1"}])):
            with self.assertRaises(HTTPException) as raised:
                ai._assert_no_active_quiz_session("learner-1")
        self.assertEqual(raised.exception.status_code, 403)

    def test_no_active_quiz_allows_tutor(self):
        with patch.object(ai, "supabase", FakeSupabase([])):
            self.assertIsNone(ai._assert_no_active_quiz_session("learner-1"))

    def test_session_lookup_failure_fails_closed(self):
        with patch.object(ai, "supabase", FakeSupabase(error=RuntimeError("db unavailable"))):
            with self.assertRaises(HTTPException) as raised:
                ai._assert_no_active_quiz_session("learner-1")
        self.assertEqual(raised.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
