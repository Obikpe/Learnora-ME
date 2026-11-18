"""Project submission and mastery evidence integrity regression tests."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import internal_projects


class Query:
    def __init__(self, db, table):
        self.db=db
        self.table=table
        self.operation="select"
        self.payload=None
        self.filters=[]
    def select(self,*_args,**_kwargs): return self
    def eq(self,key,value): self.filters.append((key,value)); return self
    def limit(self,*_args,**_kwargs): return self
    def insert(self,payload): self.operation="insert";self.payload=payload;return self
    def update(self,payload): self.operation="update";self.payload=payload;return self
    def execute(self):
        self.db.calls.append((self.table,self.operation,self.payload))
        if self.table=="skill_evidence" and self.operation=="insert" and self.db.fail_evidence_insert:
            raise RuntimeError("simulated evidence write failure")
        rows=list(self.db.rows.get(self.table,[]))
        for key,value in self.filters:
            rows=[row for row in rows if str(row.get(key))==str(value)]
        if self.operation=="insert":
            row={"id":"evidence-new",**(self.payload or {})}
            self.db.rows.setdefault(self.table,[]).append(row)
            return SimpleNamespace(data=[row])
        if self.operation=="update":
            for row in rows: row.update(self.payload or {})
            return SimpleNamespace(data=rows)
        return SimpleNamespace(data=rows)


class FakeSupabase:
    def __init__(self,rows=None,fail_evidence_insert=False):
        self.rows=rows or {}
        self.calls=[]
        self.fail_evidence_insert=fail_evidence_insert
    def table(self,name): return Query(self,name)


class ProjectSubmissionIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.staff=SimpleNamespace(user_id="staff-1",staff_id="staff-1",email="staff@example.test")

    def test_project_brief_and_skill_mapping_freeze_after_first_submission(self):
        db=FakeSupabase({"project_submissions":[{"id":"submission-1","project_id":"project-1"}]})
        with patch.object(internal_projects,"_project",return_value={"id":"project-1","is_published":False}), patch.object(internal_projects,"supabase",db):
            with self.assertRaises(HTTPException) as raised:
                internal_projects.update_project("project-1",internal_projects.ProjectWrite(title="Changed brief"),self.staff)
        self.assertEqual(raised.exception.status_code,409)
        self.assertFalse(any(table=="projects" and operation=="update" for table,operation,_ in db.calls))

    def test_failed_evidence_write_does_not_approve_submission(self):
        db=FakeSupabase({"project_submissions":[{"id":"submission-1","project_id":"project-1","user_id":"learner-1","status":"submitted"}]},fail_evidence_insert=True)
        review=internal_projects.ProjectReviewIn(score=90,feedback="Strong work",decision="approved")
        with patch.object(internal_projects,"_project",return_value={"id":"project-1","skills":["skill-1"]}), patch.object(internal_projects,"supabase",db), patch.object(internal_projects,"log_audit_event"):
            with self.assertRaises(HTTPException) as raised:
                internal_projects.review_project_submission("project-1","submission-1",review,self.staff)
        self.assertEqual(raised.exception.status_code,503)
        self.assertFalse(any(table=="project_submissions" and operation=="update" for table,operation,_ in db.calls))


if __name__ == "__main__":
    unittest.main()
