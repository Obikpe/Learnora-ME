"""Public catalogue access-mode labelling tests."""
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from routers import public_directory


class PublicDirectoryAccessModeTests(unittest.TestCase):
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

    def test_explicitly_free_course_remains_free_when_launch_mode_is_disabled(self):
        course = {"id": "free-1", "ownership": "creator", "organisation_id": None, "settings": {"is_free": True}}
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "false"}):
            payload = public_directory._public_course_payload(course)
        self.assertTrue(payload["settings"]["is_free"])


if __name__ == "__main__":
    unittest.main()
