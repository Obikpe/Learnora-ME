import unittest
from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID

from fastapi import HTTPException

from routers import progress


class FakeRpcCall:
    def __init__(self, data):
        self.data = data

    def execute(self):
        return SimpleNamespace(data=self.data)


class FakeSupabase:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def rpc(self, name, params):
        self.calls.append((name, params))
        return FakeRpcCall(self.responses[name])


class LearningSessionRouteTests(unittest.TestCase):
    def setUp(self):
        self.user = SimpleNamespace(
            id="11111111-1111-4111-8111-111111111111",
            account_type="cohort",
            role="cohort_learner",
        )
        self.session_id = UUID("22222222-2222-4222-8222-222222222222")

    def test_start_reuses_database_session_and_keeps_cohort_scope(self):
        session = {
            "id": str(self.session_id),
            "learner_id": self.user.id,
            "account_type": "cohort",
            "status": "active",
        }
        db = FakeSupabase({"start_learner_learning_session": session})
        with patch.object(progress, "supabase", db):
            result = progress.start_learning_session(
                progress.LearningSessionStartIn(timezone="Africa/Lagos"),
                self.user,
            )

        self.assertEqual(result["session"]["id"], str(self.session_id))
        self.assertEqual(db.calls[0][0], "start_learner_learning_session")
        self.assertEqual(db.calls[0][1]["p_learner_id"], self.user.id)
        self.assertEqual(db.calls[0][1]["p_account_type"], "cohort")

    def test_start_rejects_malformed_rpc_response(self):
        db = FakeSupabase({"start_learner_learning_session": None})
        with patch.object(progress, "supabase", db):
            with self.assertRaises(HTTPException) as raised:
                progress.start_learning_session(
                    progress.LearningSessionStartIn(),
                    self.user,
                )
        self.assertEqual(raised.exception.status_code, 503)

    def test_heartbeat_uses_authenticated_learner_and_atomic_rpc(self):
        db = FakeSupabase({"heartbeat_learner_learning_session": 30})
        with patch.object(progress, "supabase", db):
            result = progress.heartbeat_learning_session(
                self.session_id,
                progress.LearningSessionHeartbeatIn(active=True),
                self.user,
            )

        self.assertEqual(result["counted_seconds"], 30)
        self.assertEqual(db.calls[0][0], "heartbeat_learner_learning_session")
        self.assertEqual(db.calls[0][1]["p_learner_id"], self.user.id)
        self.assertEqual(db.calls[0][1]["p_session_id"], str(self.session_id))
        self.assertTrue(db.calls[0][1]["p_active"])

    def test_heartbeat_does_not_allow_another_learners_session(self):
        db = FakeSupabase({"heartbeat_learner_learning_session": -1})
        with patch.object(progress, "supabase", db):
            with self.assertRaises(HTTPException) as raised:
                progress.heartbeat_learning_session(
                    self.session_id,
                    progress.LearningSessionHeartbeatIn(active=True),
                    self.user,
                )
        self.assertEqual(raised.exception.status_code, 404)

    def test_end_is_idempotent_for_already_ended_sessions(self):
        db = FakeSupabase({"end_learner_learning_session": 0})
        with patch.object(progress, "supabase", db):
            result = progress.end_learning_session(
                self.session_id,
                progress.LearningSessionHeartbeatIn(active=False),
                self.user,
            )
        self.assertTrue(result["success"])
        self.assertEqual(result["counted_seconds"], 0)

    def test_rpc_integer_handles_postgrest_scalar_shapes(self):
        self.assertEqual(progress._rpc_integer(SimpleNamespace(data=17)), 17)
        self.assertEqual(progress._rpc_integer(SimpleNamespace(data=[17])), 17)
        self.assertEqual(progress._rpc_integer(SimpleNamespace(data={"seconds": 17})), 17)


if __name__ == "__main__":
    unittest.main()
