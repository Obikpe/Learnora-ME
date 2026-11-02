"""Track review completion, consent and public projection tests."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import track_reviews


class Query:
    def __init__(self, table, fixtures):
        self.table = table
        self.fixtures = fixtures
        self.filters = []
        self.operation = "select"
        self.payload = None
    def select(self, *_args, **_kwargs): return self
    def eq(self, key, value): self.filters.append(("eq", key, value)); return self
    def is_(self, key, value): self.filters.append(("is", key, value)); return self
    def in_(self, key, values): self.filters.append(("in", key, set(values))); return self
    def order(self, *_args, **_kwargs): return self
    def limit(self, *_args, **_kwargs): return self
    def insert(self, payload): self.operation="insert"; self.payload=payload; return self
    def update(self, payload): self.operation="update"; self.payload=payload; return self
    def execute(self):
        rows=list(self.fixtures.get(self.table, []))
        for kind,key,value in self.filters:
            if kind=="eq": rows=[r for r in rows if str(r.get(key))==str(value)]
            elif kind=="is": rows=[r for r in rows if (r.get(key) is None)==(value=="null")]
            else: rows=[r for r in rows if r.get(key) in value]
        if self.operation=="insert":
            saved={"id":"review-new",**self.payload}
            self.fixtures.setdefault(self.table,[]).append(saved)
            return SimpleNamespace(data=[saved])
        if self.operation=="update":
            for row in rows: row.update(self.payload)
            return SimpleNamespace(data=rows)
        return SimpleNamespace(data=rows)


class FakeSupabase:
    def __init__(self, fixtures): self.fixtures=fixtures
    def table(self, name): return Query(name,self.fixtures)


class TrackReviewTests(unittest.TestCase):
    def setUp(self):
        self.user=SimpleNamespace(id="learner-1",role="normal",account_type="learner",organisation_id=None)

    def test_review_is_rejected_until_required_track_courses_are_complete(self):
        with patch.object(track_reviews,"track_progress",return_value={"completed":False}), patch.object(track_reviews,"supabase",FakeSupabase({})):
            with self.assertRaises(HTTPException) as raised:
                track_reviews.create_track_review("track-1",track_reviews.TrackReviewIn(rating=5),self.user)
        self.assertEqual(raised.exception.status_code,409)

    def test_private_review_is_saved_without_public_consent(self):
        db=FakeSupabase({"learnora_track_reviews":[]})
        with patch.object(track_reviews,"track_progress",return_value={"completed":True}), patch.object(track_reviews,"supabase",db):
            result=track_reviews.create_track_review("track-1",track_reviews.TrackReviewIn(rating=4,comment="Useful track"),self.user)
        self.assertFalse(result["review"]["public_consent"])
        self.assertEqual(result["review"]["moderation_status"],"pending")

    def test_public_results_include_only_approved_and_consented_reviews(self):
        db=FakeSupabase({
            "learnora_learning_paths":[{"id":"track-1","name":"Data track","slug":"data-track","status":"published"}],
            "learnora_track_reviews":[
                {"id":"public","track_id":"track-1","rating":5,"comment":"Excellent","public_consent":True,"moderation_status":"approved","created_at":"2026-11-01"},
                {"id":"pending","track_id":"track-1","rating":1,"comment":"Pending","public_consent":True,"moderation_status":"pending"},
                {"id":"private","track_id":"track-1","rating":2,"comment":"Private","public_consent":False,"moderation_status":"approved"},
            ],
        })
        with patch.object(track_reviews,"supabase",db):
            result=track_reviews.public_track_reviews("track-1")
        self.assertEqual(result["rating_count"],1)
        self.assertEqual(result["average_rating"],5)
        self.assertEqual([row["id"] for row in result["reviews"]],["public"])
        self.assertNotIn("user_id",result["reviews"][0])

    def test_editing_a_review_resets_moderation_and_can_withdraw_consent(self):
        db=FakeSupabase({"learnora_track_reviews":[{
            "id":"review-1","track_id":"track-1","user_id":"learner-1","rating":5,
            "comment":"Good","public_consent":True,"moderation_status":"approved",
            "moderated_by":"staff-1","moderated_at":"2026-11-01",
        }]})
        with patch.object(track_reviews,"track_progress",return_value={"completed":True}), patch.object(track_reviews,"supabase",db):
            result=track_reviews.update_track_review("track-1",track_reviews.TrackReviewIn(rating=4,comment="Updated",public_consent=False),self.user)
        self.assertFalse(result["review"]["public_consent"])
        self.assertEqual(result["review"]["moderation_status"],"pending")
        self.assertIsNone(result["review"]["moderated_by"])
        self.assertIsNone(result["review"]["moderated_at"])


if __name__ == "__main__":
    unittest.main()
