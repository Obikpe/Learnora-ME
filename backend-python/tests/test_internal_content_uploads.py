"""Tests for private signed lesson resource uploads."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from pydantic import ValidationError
from routers import internal_content


class UploadQuery:
    def __init__(self, table):
        self.table_name = table
    def select(self, *_args, **_kwargs): return self
    def eq(self, *_args, **_kwargs): return self
    def is_(self, *_args, **_kwargs): return self
    def limit(self, *_args, **_kwargs): return self
    def execute(self):
        if self.table_name == "learnora_lessons":
            return SimpleNamespace(data=[{"id": "lesson-1", "module_id": "module-1"}])
        if self.table_name == "course_modules":
            return SimpleNamespace(data=[{"id": "module-1", "course_id": "course-1"}])
        if self.table_name == "learnora_courses":
            return SimpleNamespace(data=[{"id": "course-1", "ownership": "learnora", "organisation_id": None}])
        return SimpleNamespace(data=[])


class UploadBucket:
    def __init__(self): self.path = None; self.options = None
    def create_signed_upload_url(self, path, options=None):
        self.path = path
        self.options = options
        return SimpleNamespace(data={
            "token": "signed-token",
            "signedUrl": "https://storage.example/upload?token=signed-token",
            "path": path,
        })


class UploadStorage:
    def __init__(self): self.bucket_name = None; self.bucket = UploadBucket()
    def from_(self, name):
        self.bucket_name = name
        return self.bucket


class UploadSupabase:
    def __init__(self):
        self.storage = UploadStorage()
    def table(self, name): return UploadQuery(name)


class InternalContentUploadTests(unittest.TestCase):
    def test_resource_upload_returns_private_signed_upload_details(self):
        db = UploadSupabase()
        payload = internal_content.ResourceUploadRequest(
            filename="../course notes final.pdf",
            content_type="application/pdf",
            file_size_bytes=1024,
            title="Course notes",
        )
        with patch.object(internal_content, "supabase", db):
            result = internal_content.create_resource_upload(
                "lesson-1", payload, staff=SimpleNamespace(user_id="staff-1")
            )
        self.assertEqual(db.storage.bucket_name, "learnora-course-media")
        self.assertTrue(result["path"].startswith("courses/course-1/lessons/lesson-1/resources/"))
        self.assertNotIn("../", result["path"])
        self.assertEqual(result["token"], "signed-token")
        self.assertEqual(result["title"], "Course notes")
        self.assertEqual(db.storage.bucket.options, {"upsert": "false"})

    def test_resource_upload_rejects_unsupported_mime_types(self):
        with self.assertRaises(ValidationError):
            internal_content.ResourceUploadRequest(
                filename="script.exe",
                content_type="application/x-msdownload",
                file_size_bytes=1024,
            )

    def test_resource_upload_rejects_files_over_100mb(self):
        with self.assertRaises(ValidationError):
            internal_content.ResourceUploadRequest(
                filename="large.pdf",
                content_type="application/pdf",
                file_size_bytes=104857601,
            )


if __name__ == "__main__":
    unittest.main()
