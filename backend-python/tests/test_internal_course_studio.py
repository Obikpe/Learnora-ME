"""Validation tests for the internal AI Course Studio draft contracts."""
import os
import unittest

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from pydantic import ValidationError
from routers.internal_course_studio import (
    CurriculumOutput,
    LessonPackageOutput,
    _extract_json,
)


class CourseStudioContractTests(unittest.TestCase):
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
