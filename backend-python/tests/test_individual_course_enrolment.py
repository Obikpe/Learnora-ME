"""Regression checks for individual self-enrolment identity and reactivation rules."""
from pathlib import Path
import unittest


class IndividualCourseEnrolmentSourceTests(unittest.TestCase):
    def test_single_course_enrolment_is_scoped_to_individual_rows(self):
        source = (
            Path(__file__).resolve().parents[1] / "routers" / "courses.py"
        ).read_text(encoding="utf-8")
        route = source.split(
            '@router.post("/{course_id}/enrol"', 1
        )[1].split(
            '@router.post("/tracks/{track_id}/enrol"', 1
        )[0]

        self.assertIn('.is_("organisation_id", "null")', route)
        self.assertIn('.is_("cohort_id", "null")', route)
        self.assertIn('if len(existing_rows) > 1:', route)

    def test_withdrawn_individual_enrolment_is_reactivated_instead_of_duplicated(self):
        source = (
            Path(__file__).resolve().parents[1] / "routers" / "courses.py"
        ).read_text(encoding="utf-8")
        route = source.split(
            '@router.post("/{course_id}/enrol"', 1
        )[1].split(
            '@router.post("/tracks/{track_id}/enrol"', 1
        )[0]

        self.assertIn('if enrolment_status != "withdrawn":', route)
        self.assertIn('"status": "active"', route)
        self.assertIn('"completed_at": None', route)
        self.assertIn('.eq("status", "withdrawn")', route)
        self.assertIn('"reactivated": True', route)

    def test_managed_and_ambiguous_enrolments_fail_closed(self):
        source = (
            Path(__file__).resolve().parents[1] / "routers" / "courses.py"
        ).read_text(encoding="utf-8")
        route = source.split(
            '@router.post("/{course_id}/enrol"', 1
        )[1].split(
            '@router.post("/tracks/{track_id}/enrol"', 1
        )[0]

        self.assertIn("Multiple individual enrolment records exist", route)
        self.assertIn("not available for self-service reactivation", route)


if __name__ == "__main__":
    unittest.main()
