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

    def test_explicitly_free_course_remains_free_when_launch_mode_is_disabled(self):
        course = {"id": "free-1", "ownership": "creator", "organisation_id": None, "settings": {"is_free": True}}
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "false"}):
            payload = public_directory._public_course_payload(course)
        self.assertTrue(payload["settings"]["is_free"])


if __name__ == "__main__":
    unittest.main()
