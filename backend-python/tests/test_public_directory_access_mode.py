"""Public catalogue access-mode labelling tests."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import public_directory


class PublicDirectoryAccessModeTests(unittest.TestCase):
    def test_public_discovery_is_available_to_anonymous_and_individual_learners_only(self):
        public_directory._guard_public_discovery(None)
        public_directory._guard_public_discovery(SimpleNamespace(
            role="normal", account_type="learner", organisation_id=None,
        ))
        with self.assertRaises(HTTPException) as raised:
            public_directory._guard_public_discovery(SimpleNamespace(
                role="normal", account_type="learner", organisation_id="org-1",
            ))
        self.assertEqual(raised.exception.status_code, 403)
        with self.assertRaises(HTTPException) as cohort:
            public_directory._guard_public_discovery(SimpleNamespace(
                role="cohort_learner", account_type="cohort", organisation_id="org-1",
            ))
        self.assertEqual(cohort.exception.status_code, 403)

    def test_public_course_catalogue_uses_one_server_side_rpc(self):
        class FakeSupabase:
            def __init__(self):
                self.rpc_calls = []
                self.table_calls = []

            def rpc(self, name):
                self.rpc_calls.append(name)

                class Query:
                    def execute(self):
                        return SimpleNamespace(data=[{
                            "id": "course-1",
                            "organisation_id": None,
                            "creator_id": None,
                            "title": "Public course",
                            "slug": "public-course",
                            "short_description": "A public course",
                            "description": "Description",
                            "level": "beginner",
                            "status": "published",
                            "ownership": "learnora",
                            "thumbnail_url": None,
                            "estimated_hours": 2,
                            "settings": {},
                            "created_at": "2026-11-18T00:00:00Z",
                            "tracks": [{
                                "id": "track-1",
                                "name": "Public track",
                                "slug": "public-track",
                                "order_index": 0,
                                "required": True,
                            }],
                        }])

                return Query()

            def table(self, name):
                self.table_calls.append(name)
                raise AssertionError("Public catalogue must not make follow-up table requests")

        fake = FakeSupabase()
        with patch.object(public_directory, "supabase", fake):
            response = public_directory.public_courses(user=None)

        self.assertEqual(fake.rpc_calls, ["get_public_course_catalogue"])
        self.assertEqual(fake.table_calls, [])
        self.assertEqual(response["count"], 1)
        self.assertEqual(response["courses"][0]["tracks"][0]["id"], "track-1")

    def test_public_track_catalogue_uses_one_server_side_rpc(self):
        class FakeSupabase:
            def __init__(self):
                self.rpc_calls = []
                self.table_calls = []

            def rpc(self, name):
                self.rpc_calls.append(name)

                class Query:
                    def execute(self):
                        return SimpleNamespace(data=[{
                            "id": "track-1",
                            "name": "Public track",
                            "slug": "public-track",
                            "description": "Track description",
                            "status": "published",
                            "created_at": "2026-11-18T00:00:00Z",
                            "courses": [{
                                "id": "link-1",
                                "path_id": "track-1",
                                "course_id": "course-1",
                                "order_index": 0,
                                "required": True,
                                "course": {
                                    "id": "course-1",
                                    "title": "Public course",
                                    "slug": "public-course",
                                    "settings": {"is_free": True},
                                },
                            }],
                        }])

                return Query()

            def table(self, name):
                self.table_calls.append(name)
                raise AssertionError("Public track catalogue must not make follow-up table requests")

        fake = FakeSupabase()
        with patch.object(public_directory, "supabase", fake), patch.object(
            public_directory, "free_access_mode_enabled", return_value=False
        ):
            response = public_directory.public_tracks(user=None)

        self.assertEqual(fake.rpc_calls, ["get_public_track_catalogue"])
        self.assertEqual(fake.table_calls, [])
        self.assertEqual(response["count"], 1)
        self.assertEqual(response["tracks"][0]["course_count"], 1)
        self.assertEqual(response["tracks"][0]["self_enrol_available"], True)
        self.assertNotIn("settings", response["tracks"][0]["courses"][0]["course"])

    def test_free_launch_labels_only_global_learnora_courses_as_free(self):
        global_course = {"id": "global-1", "ownership": "learnora", "organisation_id": None, "settings": {}}
        tenant_course = {"id": "tenant-1", "ownership": "learnora", "organisation_id": "org-1", "settings": {}}
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "true"}):
            global_payload = public_directory._public_course_payload(global_course)
            tenant_payload = public_directory._public_course_payload(tenant_course)
        self.assertTrue(global_payload["settings"]["is_free"])
        self.assertFalse(tenant_payload["settings"]["is_free"])

    def test_public_track_enrolment_availability_requires_free_required_courses(self):
        track = {"id": "track-1", "status": "published"}
        links = [
            {"course_id": "course-1", "required": True},
            {"course_id": "course-2", "required": False},
        ]
        course_map = {
            "course-1": {"id": "course-1", "settings": {"is_free": True}},
            "course-2": {"id": "course-2", "settings": {"is_free": False, "internal_flag": "private"}},
        }
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "false"}):
            result = public_directory._public_track_payload_from_rows(track, links, course_map)
        self.assertTrue(result["self_enrol_available"])
        self.assertNotIn("settings", result["courses"][0]["course"])
        self.assertNotIn("settings", result["courses"][1]["course"])

    def test_restricted_required_course_disables_public_track_enrolment(self):
        track = {"id": "track-1", "status": "published"}
        links = [{"course_id": "course-1", "required": True}]
        course_map = {"course-1": {"id": "course-1", "settings": {"is_free": False}}}
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "false"}):
            result = public_directory._public_track_payload_from_rows(track, links, course_map)
        self.assertFalse(result["self_enrol_available"])

    def test_public_course_payload_exposes_only_curated_outcomes_and_requirements(self):
        course = {
            "id": "course-1",
            "ownership": "learnora",
            "organisation_id": None,
            "settings": {
                "learning_outcomes": ["Explain a concept", "Apply a method", 42],
                "requirements": ["Basic computer literacy"],
                "internal_flag": "do-not-expose",
            },
        }
        payload = public_directory._public_course_payload(course)
        self.assertEqual(payload["settings"]["learning_outcomes"], ["Explain a concept", "Apply a method"])
        self.assertEqual(payload["settings"]["requirements"], ["Basic computer literacy"])
        self.assertNotIn("internal_flag", payload["settings"])

    def test_explicitly_free_course_remains_free_when_launch_mode_is_disabled(self):
        course = {"id": "free-1", "ownership": "creator", "organisation_id": None, "settings": {"is_free": True}}
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "false"}):
            payload = public_directory._public_course_payload(course)
        self.assertTrue(payload["settings"]["is_free"])


if __name__ == "__main__":
    unittest.main()
