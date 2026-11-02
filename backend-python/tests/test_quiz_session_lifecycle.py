"""Per-tab quiz session lifecycle and recovery regression tests."""
import os
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from routers import progress


class Query:
    def __init__(self, db, table):
        self.db=db;self.table=table;self.filters=[];self.operation="select";self.payload=None;self.conflict=None
    def select(self,*_args,**_kwargs): return self
    def eq(self,key,value): self.filters.append(("eq",key,value));return self
    def gt(self,key,value): self.filters.append(("gt",key,value));return self
    def order(self,*_args,**_kwargs): return self
    def limit(self,*_args,**_kwargs): return self
    def upsert(self,payload,on_conflict=None): self.operation="upsert";self.payload=payload;self.conflict=(on_conflict or "").split(",");return self
    def update(self,payload): self.operation="update";self.payload=payload;return self
    def delete(self): self.operation="delete";return self
    def execute(self):
        rows=self.db.tables.setdefault(self.table,[])
        filtered=list(rows)
        for kind,key,value in self.filters:
            if kind=="eq": filtered=[row for row in filtered if str(row.get(key))==str(value)]
            elif kind=="gt": filtered=[row for row in filtered if str(row.get(key,""))>str(value)]
        if self.operation=="upsert":
            found=next((row for row in rows if self.conflict and all(str(row.get(key))==str(self.payload.get(key)) for key in self.conflict)),None)
            if found: found.update(self.payload);saved=found
            else: saved={"id":"session-1",**self.payload};rows.append(saved)
            return SimpleNamespace(data=[saved])
        if self.operation=="update":
            for row in filtered: row.update(self.payload or {})
            return SimpleNamespace(data=filtered)
        if self.operation=="delete":
            for row in filtered:
                if row in rows: rows.remove(row)
            return SimpleNamespace(data=filtered)
        return SimpleNamespace(data=filtered)


class FakeSupabase:
    def __init__(self,tables=None): self.tables=tables or {}
    def table(self,name): return Query(self,name)


class QuizSessionLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.user=SimpleNamespace(id="learner-1")
        self.tab_id=UUID("11111111-1111-4111-8111-111111111111")

    def test_opening_same_quiz_twice_in_same_tab_reuses_one_session(self):
        db=FakeSupabase({
            "quizzes":[{"id":"quiz-1","course_id":"course-1","lesson_id":None,"module_id":None,"title":"Quiz","is_published":True}],
            "quiz_questions":[],
            "quiz_attempts":[],
            "quiz_active_sessions":[],
        })
        with patch.object(progress,"supabase",db), patch.object(progress,"_enrolment",return_value={"status":"active"}):
            first=progress.get_quiz("quiz-1",self.tab_id,self.user)
            second=progress.get_quiz("quiz-1",self.tab_id,self.user)
        self.assertEqual(first["session_id"],second["session_id"])
        self.assertEqual(len(db.tables["quiz_active_sessions"]),1)
        self.assertEqual(db.tables["quiz_active_sessions"][0]["client_session_id"],str(self.tab_id))

    def test_active_session_lookup_returns_tab_identity(self):
        db=FakeSupabase({"quiz_active_sessions":[{
            "id":"session-1","quiz_id":"quiz-1","course_id":"course-1",
            "client_session_id":str(self.tab_id),
            "expires_at":(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),
            "user_id":"learner-1",
        }]})
        with patch.object(progress,"supabase",db):
            result=progress.my_active_quiz_session(self.user)
        self.assertTrue(result["active"])
        self.assertEqual(result["sessions"][0]["client_session_id"],str(self.tab_id))

    def test_heartbeat_renews_only_the_calling_users_session(self):
        db=FakeSupabase({"quiz_active_sessions":[{
            "id":"session-1","quiz_id":"quiz-1","course_id":"course-1",
            "client_session_id":str(self.tab_id),"user_id":"learner-1",
            "expires_at":(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),
        }]})
        with patch.object(progress,"supabase",db):
            result=progress.heartbeat_quiz_session("quiz-1","session-1",self.user)
        self.assertTrue(result["success"])
        self.assertGreater(datetime.fromisoformat(result["expires_at"]),datetime.now(timezone.utc)+timedelta(minutes=100))

    def test_unsubmitted_session_cannot_be_closed_to_restore_tutor_access(self):
        db=FakeSupabase({
            "quiz_active_sessions":[{"id":"session-1","quiz_id":"quiz-1","user_id":"learner-1","started_at":"2026-11-02T10:00:00+00:00"}],
            "quiz_attempts":[],
        })
        with patch.object(progress,"supabase",db):
            with self.assertRaises(HTTPException) as raised:
                progress.close_quiz_session("quiz-1","session-1",self.user)
        self.assertEqual(raised.exception.status_code,409)
        self.assertEqual(len(db.tables["quiz_active_sessions"]),1)

    def test_submitted_attempt_closes_only_the_calling_users_session(self):
        db=FakeSupabase({
            "quiz_active_sessions":[
                {"id":"session-1","quiz_id":"quiz-1","user_id":"learner-1","started_at":"2026-11-02T10:00:00+00:00"},
                {"id":"session-2","quiz_id":"quiz-1","user_id":"learner-2","started_at":"2026-11-02T10:00:00+00:00"},
            ],
            "quiz_attempts":[{"id":"attempt-1","quiz_id":"quiz-1","user_id":"learner-1","submitted_at":"2026-11-02T10:15:00+00:00"}],
        })
        with patch.object(progress,"supabase",db):
            result=progress.close_quiz_session("quiz-1","session-1",self.user)
        self.assertTrue(result["success"])
        self.assertEqual([row["id"] for row in db.tables["quiz_active_sessions"]],["session-2"])


if __name__ == "__main__":
    unittest.main()
