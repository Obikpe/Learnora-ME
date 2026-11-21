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
    def test_video_upload_returns_private_signed_upload_details(self):
        db = UploadSupabase()
        payload = internal_content.VideoUploadRequest(
            filename="../lesson demonstration.mp4",
            content_type="video/mp4",
            file_size_bytes=2048,
            title="Lesson demonstration",
        )
        with patch.object(internal_content, "supabase", db):
            result = internal_content.create_video_upload(
                "lesson-1", payload, staff=SimpleNamespace(user_id="staff-1")
            )
        self.assertEqual(db.storage.bucket_name, "learnora-course-media")
        self.assertTrue(result["path"].startswith("courses/course-1/lessons/lesson-1/"))
        self.assertNotIn("../", result["path"])
        self.assertEqual(result["token"], "signed-token")
        self.assertEqual(result["title"], "Lesson demonstration")
        self.assertEqual(result["content_type"], "video/mp4")
        self.assertEqual(db.storage.bucket.options, {"upsert": "false"})

    def test_video_upload_rejects_unsupported_mime_types(self):
        with self.assertRaises(ValidationError):
            internal_content.VideoUploadRequest(
                filename="lesson.exe",
                content_type="application/x-msdownload",
                file_size_bytes=1024,
            )

    def test_video_upload_rejects_files_over_2gb(self):
        with self.assertRaises(ValidationError):
            internal_content.VideoUploadRequest(
                filename="lesson.mp4",
                content_type="video/mp4",
                file_size_bytes=2147483649,
            )

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
        self.assertEqual(db.storage.bucket_name, "learnora-resources")
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


    def test_course_studio_job_is_resolved_from_ai_course_settings(self):
        class BridgeQuery:
            def __init__(self, table):
                self.table = table
                self.fields = ""
                self.filters = {}
                self.single = False
            def select(self, fields): self.fields = fields; return self
            def eq(self, key, value): self.filters[key] = value; return self
            def is_(self, key, value): self.filters[key] = value; return self
            def limit(self, _value): return self
            def maybe_single(self): self.single = True; return self
            def execute(self):
                if self.table == "learnora_lessons":
                    data = [{"id": "10000000-0000-4000-8000-000000000001", "module_id": "20000000-0000-4000-8000-000000000001"}]
                elif self.table == "course_modules":
                    data = [{"id": "20000000-0000-4000-8000-000000000001", "course_id": "30000000-0000-4000-8000-000000000001"}]
                elif self.table == "learnora_courses" and "settings" in self.fields:
                    data = {"id": "30000000-0000-4000-8000-000000000001", "settings": {"ai_generated": True, "generation_job_id": "40000000-0000-4000-8000-000000000001"}}
                elif self.table == "learnora_courses":
                    data = [{"id": "30000000-0000-4000-8000-000000000001"}]
                elif self.table == "learnora_course_generation_jobs":
                    data = {"id": "40000000-0000-4000-8000-000000000001", "created_course_id": "30000000-0000-4000-8000-000000000001", "status": "created"}
                else:
                    data = None if self.single else []
                return SimpleNamespace(data=data)
        class BridgeSupabase:
            def table(self, name): return BridgeQuery(name)

        with patch.object(internal_content, "supabase", BridgeSupabase()):
            job_id = internal_content._course_studio_job_for_lesson("10000000-0000-4000-8000-000000000001")
        self.assertEqual(job_id, "40000000-0000-4000-8000-000000000001")

    def test_course_studio_job_resolver_rejects_non_ai_courses(self):
        class CourseQuery:
            def select(self, *_args, **_kwargs): return self
            def eq(self, *_args, **_kwargs): return self
            def maybe_single(self): return self
            def execute(self):
                return SimpleNamespace(data={"id": "course-1", "settings": {"ai_generated": False}})
        class CourseDatabase:
            def table(self, _name): return CourseQuery()

        with patch.object(internal_content, "_module_for_lesson", return_value={"id": "lesson-1", "module_id": "module-1"}), patch.object(
            internal_content, "_course_for_module", return_value={"id": "module-1", "course_id": "course-1"}
        ), patch.object(internal_content, "supabase", CourseDatabase()):
            with self.assertRaises(HTTPException) as raised:
                internal_content._course_studio_job_for_lesson("lesson-1")
        self.assertEqual(raised.exception.status_code, 409)

    def test_course_studio_job_resolver_rejects_generation_job_for_another_course(self):
        class ResolverQuery:
            def __init__(self, table): self.table = table
            def select(self, *_args, **_kwargs): return self
            def eq(self, *_args, **_kwargs): return self
            def maybe_single(self): return self
            def execute(self):
                if self.table == "learnora_courses":
                    data = {"id": "course-1", "settings": {"ai_generated": True, "generation_job_id": "job-1"}}
                else:
                    data = {"id": "job-1", "created_course_id": "different-course", "status": "created"}
                return SimpleNamespace(data=data)
        class ResolverDatabase:
            def table(self, name): return ResolverQuery(name)

        with patch.object(internal_content, "_module_for_lesson", return_value={"id": "lesson-1", "module_id": "module-1"}), patch.object(
            internal_content, "_course_for_module", return_value={"id": "module-1", "course_id": "course-1"}
        ), patch.object(internal_content, "supabase", ResolverDatabase()):
            with self.assertRaises(HTTPException) as raised:
                internal_content._course_studio_job_for_lesson("lesson-1")
        self.assertEqual(raised.exception.status_code, 409)

    def test_course_studio_job_resolver_rejects_non_draft_generation_jobs(self):
        class ResolverQuery:
            def __init__(self, table): self.table = table; self.fields = ""
            def select(self, fields): self.fields = fields; return self
            def eq(self, *_args, **_kwargs): return self
            def maybe_single(self): return self
            def execute(self):
                if self.table == "learnora_courses":
                    data = {"id": "course-1", "settings": {"ai_generated": True, "generation_job_id": "job-1"}}
                else:
                    data = {"id": "job-1", "created_course_id": "course-1", "status": "published"}
                return SimpleNamespace(data=data)
        class ResolverDatabase:
            def table(self, name): return ResolverQuery(name)

        with patch.object(internal_content, "_module_for_lesson", return_value={"id": "lesson-1", "module_id": "module-1"}), patch.object(
            internal_content, "_course_for_module", return_value={"id": "module-1", "course_id": "course-1"}
        ), patch.object(internal_content, "supabase", ResolverDatabase()):
            with self.assertRaises(HTTPException) as raised:
                internal_content._course_studio_job_for_lesson("lesson-1")
        self.assertEqual(raised.exception.status_code, 409)

    def test_course_studio_team_upload_finalization_uses_course_studio_verification(self):
        from routers import internal_course_studio
        payload = internal_content.CourseStudioVideoFinalizeRequest(
            object_key="courses/course/modules/module/lessons/lesson/video.mp4",
            file_size_bytes=1024,
            duration_seconds=120,
            title="Lesson video",
        )
        staff = SimpleNamespace(user_id="staff-1")
        expected = {"success": True, "video_id": "video-1"}
        with patch.object(internal_content, "_course_studio_job_for_lesson", return_value="40000000-0000-4000-8000-000000000001"), patch.object(
            internal_course_studio, "finalize_human_video_upload", return_value=expected
        ) as finalize:
            result = internal_content.finalize_course_studio_video_upload(
                "10000000-0000-4000-8000-000000000001", payload, staff
            )
        self.assertEqual(result, expected)
        self.assertEqual(finalize.call_args.args[3], staff)

    def test_course_studio_team_upload_delegates_to_r2_course_studio_flow(self):
        from routers import internal_course_studio
        payload = internal_content.CourseStudioVideoUploadRequest(
            filename="lesson.mp4",
            file_size_bytes=1024,
            duration_seconds=120,
            title="Lesson video",
        )
        staff = SimpleNamespace(user_id="staff-1")
        expected = {"success": True, "upload_url": "https://r2.example/upload", "object_key": "courses/course/lesson.mp4"}
        with patch.object(internal_content, "_course_studio_job_for_lesson", return_value="40000000-0000-4000-8000-000000000001"), patch.object(
            internal_course_studio, "create_human_video_upload", return_value=expected
        ) as upload:
            result = internal_content.create_course_studio_video_upload(
                "10000000-0000-4000-8000-000000000001", payload, staff
            )
        self.assertEqual(result, expected)
        self.assertEqual(upload.call_args.args[0], __import__("uuid").UUID("40000000-0000-4000-8000-000000000001"))
        self.assertEqual(upload.call_args.args[1], __import__("uuid").UUID("10000000-0000-4000-8000-000000000001"))
        self.assertEqual(upload.call_args.args[3], staff)

if __name__ == "__main__":
    unittest.main()
