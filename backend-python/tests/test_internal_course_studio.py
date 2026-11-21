"""Validation tests for the internal AI Course Studio draft contracts."""
import inspect
import os
import unittest

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from pydantic import ValidationError
from routers.internal_course_studio import (
    CurriculumOutput,
    CurriculumRevisionRequest,
    LessonPackageOutput,
    LessonPackageRequest,
    HumanVideoUploadRequest,
    HumanVideoFinalizeRequest,
    generate_curriculum,
    revise_course_curriculum,
    generate_lesson_package,
    _extract_json,
)


class CourseStudioContractTests(unittest.TestCase):
    def test_curriculum_generation_uses_the_dedicated_generation_permission(self):
        source = inspect.getsource(generate_curriculum)
        self.assertIn('require_internal_permission("content.generate")', source)

    def test_curriculum_prompt_requests_both_required_course_descriptions(self):
        source = inspect.getsource(generate_curriculum)
        self.assertIn("short_description", source)
        self.assertIn("course_description", source)
        self.assertIn("quality_review", source)

    def test_curriculum_revision_requires_the_validated_curriculum_contract(self):
        request = CurriculumRevisionRequest(curriculum={
            "course_title": "Revised Excel Fundamentals",
            "short_description": "Learn spreadsheet essentials.",
            "course_description": "A practical course for new spreadsheet users.",
            "learning_outcomes": ["Build a structured workbook."],
            "prerequisites": [],
            "modules": [{
                "title": "Foundations",
                "description": "Start with workbook basics.",
                "lessons": [{
                    "title": "Workbook structure",
                    "description": "Understand workbook components.",
                    "learning_objective": "Distinguish worksheets from workbooks.",
                    "lesson_format": "narrated_visual",
                    "estimated_minutes": 2,
                }],
            }],
            "quality_review": [],
        })
        self.assertEqual(request.curriculum.course_title, "Revised Excel Fundamentals")

    def test_curriculum_revision_is_permission_checked_and_archives_old_packages(self):
        source = inspect.getsource(revise_course_curriculum)
        self.assertIn('require_internal_permission("content.generate")', source)
        self.assertIn("update_learnora_course_generation_curriculum", source)
        self.assertIn("lesson_count > 60", source)

    def test_lesson_prompt_uses_the_practice_activity_schema_field(self):
        source = inspect.getsource(generate_lesson_package)
        self.assertIn("practice_activity", source)
        self.assertNotIn("practical_activity", source)

    def test_human_video_uploads_are_limited_to_five_minutes(self):
        upload = HumanVideoUploadRequest(
            filename="lesson.mp4",
            file_size_bytes=1024,
            duration_seconds=300,
            title="Lesson video",
        )
        finalize = HumanVideoFinalizeRequest(
            object_key="courses/course/modules/module/lessons/lesson/video.mp4",
            file_size_bytes=1024,
            duration_seconds=300,
            title="Lesson video",
        )
        self.assertEqual(upload.duration_seconds, 300)
        self.assertEqual(finalize.duration_seconds, 300)
        with self.assertRaises(ValidationError):
            HumanVideoUploadRequest(
                filename="long.mp4",
                file_size_bytes=1024,
                duration_seconds=301,
                title="Long lesson video",
            )
        with self.assertRaises(ValidationError):
            HumanVideoFinalizeRequest(
                object_key="courses/course/modules/module/lessons/lesson/long.mp4",
                file_size_bytes=1024,
                duration_seconds=301,
                title="Long lesson video",
            )

    def test_lesson_package_video_source_defaults_to_ai(self):
        request = LessonPackageRequest(
            job_id="e1000000-0000-4000-8000-000000000001",
            module_order=0,
            lesson_order=0,
        )
        self.assertEqual(request.video_source, "ai")

    def test_lesson_package_accepts_human_video_source(self):
        request = LessonPackageRequest(
            job_id="e1000000-0000-4000-8000-000000000001",
            module_order=0,
            lesson_order=0,
            video_source="human",
        )
        self.assertEqual(request.video_source, "human")

    def test_extracts_json_from_markdown_fence(self):
        value = _extract_json('```json\n{"course_title":"Excel"}\n```')
        self.assertEqual(value["course_title"], "Excel")

    def test_rejects_non_json_response(self):
        with self.assertRaises(ValueError):
            _extract_json("The course outline is ready.")

    def test_curriculum_contract_accepts_bite_sized_lesson(self):
        value = CurriculumOutput.model_validate({
            "course_title": "Excel Fundamentals",
            "short_description": "Learn the foundations of Excel.",
            "course_description": "A practical course for new spreadsheet users.",
            "learning_outcomes": ["Create and format a worksheet."],
            "prerequisites": [],
            "modules": [{
                "title": "Getting started",
                "description": "Understand the workbook interface.",
                "lessons": [{
                    "title": "What is a workbook?",
                    "description": "Explore workbooks and worksheets.",
                    "learning_objective": "Distinguish a workbook from a worksheet.",
                    "lesson_format": "narrated_visual",
                    "estimated_minutes": 2,
                }],
            }],
            "quality_review": [],
        })
        self.assertEqual(value.modules[0].lessons[0].estimated_minutes, 2)

    def test_curriculum_contract_rejects_lessons_over_five_minutes(self):
        payload = {
            "course_title": "Excel Fundamentals",
            "short_description": "Learn the foundations of Excel.",
            "course_description": "A practical course for new spreadsheet users.",
            "learning_outcomes": ["Create and format a worksheet."],
            "prerequisites": [],
            "modules": [{
                "title": "Getting started",
                "description": "Understand the workbook interface.",
                "lessons": [{
                    "title": "What is a workbook?",
                    "description": "Explore workbooks and worksheets.",
                    "learning_objective": "Distinguish a workbook from a worksheet.",
                    "lesson_format": "narrated_visual",
                    "estimated_minutes": 8,
                }],
            }],
            "quality_review": [],
        }
        with self.assertRaises(ValidationError):
            CurriculumOutput.model_validate(payload)

    def test_lesson_package_requires_knowledge_checks(self):
        with self.assertRaises(ValidationError):
            LessonPackageOutput.model_validate({
                "teaching_script": "This is a sufficiently long teaching script that explains one concept with a short example and a recap for learners.",
                "estimated_duration_seconds": 120,
                "concise_note": "A short definition and key takeaway.",
                "practice_activity": None,
                "video_plan": [],
                "fact_check_notes": [],
            })

    def test_lesson_package_duration_cannot_exceed_five_minutes(self):
        with self.assertRaises(ValidationError):
            LessonPackageOutput.model_validate({
                "teaching_script": "A sufficiently long teaching script that explains a concept using an example and a recap for learners.",
                "estimated_duration_seconds": 301,
                "concise_note": "A short definition and key takeaway.",
                "practice_activity": None,
                "knowledge_check": [
                    {"question": "Which option is correct?", "options": ["A", "B"], "correct_option": 1, "explanation": "B is correct."},
                    {"question": "Which value should be used?", "options": ["A", "B"], "correct_option": 0, "explanation": "A is correct."},
                ],
                "video_plan": [],
                "fact_check_notes": [],
            })


if __name__ == "__main__":
    unittest.main()
