"""Regression tests for tenant isolation in course-content reads.

Run from backend-python with:
    python -m unittest discover -s tests
"""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

# Allow isolated unit tests to import the application without production secrets.
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException

from routers import course_content, progress


class FakeQuery:
    def __init__(self, table_name, rows):
        self.table_name = table_name
        self.rows = rows
        self.filters = {}

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, key, value):
        self.filters[key] = value
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def in_(self, key, values):
        self.filters[key] = set(str(value) for value in values)
        return self

    def order(self, *_args, **_kwargs):
        return self

    def execute(self):
        matching = [
            row for row in self.rows
            if all(
                str(row.get(key)) in value if isinstance(value, set)
                else str(row.get(key)) == str(value)
                for key, value in self.filters.items()
            )
        ]
        return SimpleNamespace(data=matching)


class FakeSupabase:
    def __init__(self, course_access=None, enrolments=None, **tables):
        self.rows = {
            "course_access": course_access or [],
            "learnora_enrolments": enrolments or [],
            "organisations": [{"id": "org-a", "is_active": True}],
            **tables,
        }

    def table(self, name):
        return FakeQuery(name, self.rows.get(name, []))


def context(organisation_id="org-a", user_id="user-1", platform_admin=False, role="admin", account_type="learner", user_role=None):
    return SimpleNamespace(
        organisation_id=organisation_id,
        user_id=user_id,
        is_platform_admin=platform_admin,
        organisation_role=role,
        user=SimpleNamespace(
            role=user_role or ("normal" if role == "learner" else role),
            account_type=account_type,
        ),
    )


class CourseContentAccessTests(unittest.TestCase):
    def setUp(self):
        entitlement = patch.object(course_content, "_organisation_has_course_entitlement", return_value=True)
        entitlement.start()
        self.addCleanup(entitlement.stop)

    def test_scoped_course_assignment_does_not_grant_access_to_every_organisation_learner(self):
        course = {"id": "course-1", "ownership": "learnora", "organisation_id": None}
        db = FakeSupabase(course_access=[{
            "id": "grant-1", "course_id": "course-1",
            "organisation_id": "org-a", "status": "active", "access_type": "scoped",
        }])
        with patch.object(course_content, "supabase", db):
            with self.assertRaises(HTTPException) as raised:
                course_content._check_course_view_access(context(role="learner"), course)
        self.assertEqual(raised.exception.status_code, 403)

    def test_scoped_course_assignment_allows_the_enrolled_learner(self):
        course = {"id": "course-1", "ownership": "learnora", "organisation_id": None}
        db = FakeSupabase(
            course_access=[{
                "id": "grant-1", "course_id": "course-1",
                "organisation_id": "org-a", "status": "active", "access_type": "scoped",
            }],
            enrolments=[{
                "id": "enrolment-1", "course_id": "course-1",
                "user_id": "user-1", "organisation_id": "org-a",
                "status": "active", "source_type": "individual_assignment",
            }],
            organisation_members=[{
                "id": "org-member-1", "organisation_id": "org-a",
                "user_id": "user-1", "role": "learner", "status": "active",
            }],
        )
        with patch.object(course_content, "supabase", db):
            course_content._check_course_view_access(context(role="learner"), course)

    def test_scoped_enrolment_is_denied_when_contract_has_expired(self):
        course = {"id": "course-1", "ownership": "learnora", "organisation_id": None}
        db = FakeSupabase(
            course_access=[{"id": "grant-1", "course_id": "course-1", "organisation_id": "org-a", "status": "active", "access_type": "scoped"}],
            enrolments=[{"id": "enrolment-1", "course_id": "course-1", "user_id": "user-1", "organisation_id": "org-a", "status": "active", "source_type": "individual_assignment"}],
            organisations=[{"id": "org-a", "is_active": True, "settings": {}}],
            organisation_members=[{"id": "member-1", "organisation_id": "org-a", "user_id": "user-1", "role": "learner", "status": "active"}],
        )
        with patch.object(course_content, "supabase", db), patch.object(course_content, "_organisation_has_course_entitlement", return_value=False):
            with self.assertRaises(HTTPException) as raised:
                course_content._check_course_view_access(context(role="learner"), course)
        self.assertEqual(raised.exception.status_code, 403)

    def test_team_assignment_requires_active_team_membership(self):
        course = {"id": "course-1", "ownership": "learnora", "organisation_id": None}
        db = FakeSupabase(
            course_access=[{"id": "grant-1", "course_id": "course-1", "organisation_id": "org-a", "status": "active", "access_type": "scoped"}],
            enrolments=[{"id": "enrolment-1", "course_id": "course-1", "user_id": "user-1", "organisation_id": "org-a", "status": "active", "source_type": "team_assignment"}],
            organisations=[{"id": "org-a", "is_active": True, "settings": {"pilot_mode": True}}],
            organisation_members=[{"id": "org-member", "organisation_id": "org-a", "user_id": "user-1", "role": "learner", "status": "active"}],
            organisation_team_members=[{"team_id": "team-a", "user_id": "user-1", "status": "active"}],
            organisation_teams=[{"id": "team-a", "organisation_id": "org-a", "status": "active"}],
            team_course_assignments=[{"id": "assignment-a", "team_id": "team-a", "course_id": "course-1", "status": "active"}],
        )
        with patch.object(course_content, "supabase", db):
            course_content._check_course_view_access(context(role="learner"), course)

    def test_removed_team_member_loses_scoped_course_access(self):
        course = {"id": "course-1", "ownership": "learnora", "organisation_id": None}
        db = FakeSupabase(
            course_access=[{"id": "grant-1", "course_id": "course-1", "organisation_id": "org-a", "status": "active", "access_type": "scoped"}],
            enrolments=[{"id": "enrolment-1", "course_id": "course-1", "user_id": "user-1", "organisation_id": "org-a", "status": "active", "source_type": "team_assignment"}],
            organisation_members=[{"id": "org-member", "organisation_id": "org-a", "user_id": "user-1", "role": "learner", "status": "active"}],
            organisation_team_members=[{"team_id": "team-a", "user_id": "user-1", "status": "inactive"}],
            organisation_teams=[{"id": "team-a", "organisation_id": "org-a", "status": "active"}],
            team_course_assignments=[{"id": "assignment-a", "team_id": "team-a", "course_id": "course-1", "status": "active"}],
        )
        with patch.object(course_content, "supabase", db):
            with self.assertRaises(HTTPException) as raised:
                course_content._check_course_view_access(context(role="learner"), course)
        self.assertEqual(raised.exception.status_code, 403)

    def test_cohort_assignment_requires_active_cohort_membership(self):
        course = {"id": "course-1", "ownership": "learnora", "organisation_id": None}
        db = FakeSupabase(
            course_access=[{"id": "grant-1", "course_id": "course-1", "organisation_id": "org-a", "status": "active", "access_type": "scoped"}],
            enrolments=[{"id": "enrolment-1", "course_id": "course-1", "user_id": "user-1", "organisation_id": "org-a", "status": "active", "source_type": "cohort_assignment", "cohort_id": "cohort-a"}],
            organisation_members=[{"id": "org-member", "organisation_id": "org-a", "user_id": "user-1", "role": "learner", "status": "active"}],
            cohort_members=[{"cohort_id": "cohort-a", "user_id": "user-1", "status": "active"}],
            cohorts=[{"id": "cohort-a", "organisation_id": "org-a", "status": "active"}],
            cohort_course_assignments=[{"id": "assignment-a", "cohort_id": "cohort-a", "course_id": "course-1", "status": "active"}],
        )
        with patch.object(course_content, "supabase", db):
            course_content._check_course_view_access(context(role="learner"), course)

    def test_organisation_owned_course_is_readable_inside_own_tenant(self):
        course = {"id": "course-1", "ownership": "organisation", "organisation_id": "org-a"}
        with patch.object(course_content, "supabase", FakeSupabase()):
            course_content._check_course_view_access(context(), course)

    def test_organisation_owned_course_is_denied_to_another_tenant(self):
        course = {"id": "course-1", "ownership": "organisation", "organisation_id": "org-b"}
        with patch.object(course_content, "supabase", FakeSupabase()):
            with self.assertRaises(HTTPException) as raised:
                course_content._check_course_view_access(context("org-a"), course)
        self.assertEqual(raised.exception.status_code, 403)

    def test_learner_cannot_read_organisation_owned_course_without_grant(self):
        course = {"id": "course-1", "ownership": "organisation", "organisation_id": "org-a"}
        with patch.object(course_content, "supabase", FakeSupabase()):
            with self.assertRaises(HTTPException) as raised:
                course_content._check_course_view_access(context(role="learner"), course)
        self.assertEqual(raised.exception.status_code, 403)

    def test_learner_can_read_organisation_owned_course_with_active_grant(self):
        course = {"id": "course-1", "ownership": "organisation", "organisation_id": "org-a"}
        db = FakeSupabase(
            course_access=[{
                "id": "grant-1", "course_id": "course-1",
                "organisation_id": "org-a", "status": "active", "access_type": "assigned",
            }],
            organisations=[{"id": "org-a", "is_active": True, "settings": {"pilot_mode": True}}],
            organisation_members=[{
                "id": "member-1", "organisation_id": "org-a", "user_id": "user-1",
                "role": "learner", "status": "active",
            }],
        )
        with patch.object(course_content, "supabase", db):
            course_content._check_course_view_access(context(role="learner"), course)

    def test_organisation_wide_grant_does_not_bypass_inactive_learner_membership(self):
        course = {"id": "course-1", "ownership": "learnora", "organisation_id": None}
        db = FakeSupabase(
            course_access=[{
                "id": "grant-1", "course_id": "course-1",
                "organisation_id": "org-a", "status": "active", "access_type": "assigned",
            }],
            organisation_members=[],
        )
        with patch.object(course_content, "supabase", db):
            with self.assertRaises(HTTPException) as raised:
                course_content._check_course_view_access(context(role="learner"), course)
        self.assertEqual(raised.exception.status_code, 403)

    def test_learnora_course_requires_active_organisation_grant_or_enrolment(self):
        course = {"id": "course-1", "ownership": "learnora", "organisation_id": None}
        db = FakeSupabase(course_access=[{
            "id": "grant-1", "course_id": "course-1",
            "organisation_id": "org-a", "status": "active", "access_type": "assigned",
        }])
        with patch.object(course_content, "supabase", db):
            course_content._check_course_view_access(context(), course)

    def test_individual_enrolment_cannot_cross_tenant_boundary(self):
        course = {"id": "course-1", "ownership": "learnora", "organisation_id": None}
        db = FakeSupabase(enrolments=[{
            "id": "enrolment-1", "course_id": "course-1",
            "user_id": "user-1", "organisation_id": "org-b", "status": "active",
        }])
        with patch.object(course_content, "supabase", db):
            with self.assertRaises(HTTPException) as raised:
                course_content._check_course_view_access(context("org-a"), course)
        self.assertEqual(raised.exception.status_code, 403)

    def test_individual_unscoped_enrolment_is_preserved(self):
        course = {"id": "course-1", "ownership": "learnora", "organisation_id": None}
        db = FakeSupabase(enrolments=[{
            "id": "enrolment-1", "course_id": "course-1",
            "user_id": "user-1", "organisation_id": None, "status": "active",
        }])
        with patch.object(course_content, "supabase", db):
            course_content._check_course_view_access(context(None, role="learner"), course)

    def test_individual_free_launch_catalogue_access_is_preserved(self):
        course = {"id": "course-1", "ownership": "learnora", "organisation_id": None, "status": "published"}
        with patch.object(course_content, "free_access_mode_enabled", return_value=True):
            with patch.object(course_content, "supabase", FakeSupabase()):
                course_content._check_course_view_access(context(None, role="learner"), course)

    def test_new_cohort_account_cannot_use_generic_course_content_endpoint(self):
        course = {"id": "course-1", "ownership": "learnora", "organisation_id": None}
        with patch.object(course_content, "supabase", FakeSupabase()):
            with self.assertRaises(HTTPException) as raised:
                course_content._check_course_view_access(
                    context("org-a", role="cohort_learner", account_type="cohort"),
                    course,
                )
        self.assertEqual(raised.exception.status_code, 403)

    def test_legacy_cohort_member_cannot_use_organisation_wide_grant_without_cohort_assignment(self):
        course = {"id": "course-1", "ownership": "learnora", "organisation_id": None}
        db = FakeSupabase(
            course_access=[{"id": "grant-1", "course_id": "course-1", "organisation_id": "org-a", "status": "active", "access_type": "assigned"}],
            enrolments=[{"id": "enrolment-1", "course_id": "course-1", "user_id": "user-1", "organisation_id": "org-a", "cohort_id": "cohort-a", "status": "active", "source_type": "cohort_assignment"}],
            cohort_members=[{"id": "member-1", "user_id": "user-1", "cohort_id": "cohort-a", "status": "active"}],
            cohorts=[{"id": "cohort-a", "organisation_id": "org-a", "status": "active"}],
        )
        with patch.object(course_content, "supabase", db), patch.object(course_content, "_organisation_has_course_entitlement", return_value=True):
            with self.assertRaises(HTTPException) as raised:
                course_content._check_course_view_access(
                    context("org-a", role="learner", user_role="witstart"),
                    course,
                )
        self.assertEqual(raised.exception.status_code, 403)

    def test_legacy_cohort_member_can_read_only_course_assigned_to_their_cohort(self):
        course = {"id": "course-1", "ownership": "learnora", "organisation_id": None}
        db = FakeSupabase(
            course_access=[{"id": "grant-1", "course_id": "course-1", "organisation_id": "org-a", "status": "active", "access_type": "assigned"}],
            enrolments=[{"id": "enrolment-1", "course_id": "course-1", "user_id": "user-1", "organisation_id": "org-a", "cohort_id": "cohort-a", "status": "active", "source_type": "cohort_assignment"}],
            cohort_members=[{"id": "member-1", "user_id": "user-1", "cohort_id": "cohort-a", "status": "active"}],
            cohorts=[{"id": "cohort-a", "organisation_id": "org-a", "status": "active"}],
            cohort_course_assignments=[{"id": "assignment-1", "cohort_id": "cohort-a", "course_id": "course-1", "status": "active"}],
        )
        with patch.object(course_content, "supabase", db), patch.object(course_content, "_organisation_has_course_entitlement", return_value=True):
            course_content._check_course_view_access(
                context("org-a", role="learner", user_role="witstart"),
                course,
            )

    def test_legacy_cohort_progress_requires_the_cohort_course_assignment(self):
        db = FakeSupabase(
            organisations=[{"id": "org-a", "is_active": True}],
            cohort_accounts=[],
            organisation_members=[],
            cohort_members=[{"id": "member-1", "user_id": "user-1", "cohort_id": "cohort-a", "status": "active"}],
            cohorts=[{"id": "cohort-a", "organisation_id": "org-a", "status": "active"}],
            users=[{"id": "user-1", "role": "witstart"}],
            learnora_enrolments=[{
                "id": "enrolment-1", "user_id": "user-1", "course_id": "course-1",
                "organisation_id": "org-a", "cohort_id": "cohort-a", "status": "active",
                "source_type": "cohort_assignment",
            }],
        )
        with patch.object(progress, "supabase", db), patch.object(progress, "_has_active_scoped_course_source", return_value=True):
            result = progress._enrolment("user-1", "course-1")
        self.assertEqual(result["id"], "enrolment-1")

    def test_legacy_cohort_progress_does_not_inherit_an_unassigned_org_course(self):
        db = FakeSupabase(
            organisations=[{"id": "org-a", "is_active": True}],
            course_access=[{"id": "grant-1", "course_id": "course-1", "organisation_id": "org-a", "status": "active", "access_type": "assigned"}],
            cohort_accounts=[],
            organisation_members=[],
            cohort_members=[{"id": "member-1", "user_id": "user-1", "cohort_id": "cohort-a", "status": "active"}],
            cohorts=[{"id": "cohort-a", "organisation_id": "org-a", "status": "active"}],
            users=[{"id": "user-1", "role": "witstart"}],
            learnora_enrolments=[{
                "id": "enrolment-1", "user_id": "user-1", "course_id": "course-1",
                "organisation_id": "org-a", "cohort_id": "cohort-a", "status": "active",
                "source_type": "cohort_assignment",
            }],
        )
        with patch.object(progress, "supabase", db), patch.object(progress, "_has_active_scoped_course_source", return_value=False):
            result = progress._enrolment("user-1", "course-1")
        self.assertIsNone(result)

    def test_individual_learner_progress_keeps_global_enrolment_access(self):
        db = FakeSupabase(
            cohort_accounts=[],
            organisation_members=[],
            cohort_members=[],
            users=[{"id": "user-1", "role": "normal"}],
            learnora_enrolments=[{
                "id": "enrolment-1", "user_id": "user-1", "course_id": "course-1",
                "organisation_id": None, "cohort_id": None, "status": "active",
                "source_type": "self_enrolment",
            }],
        )
        with patch.object(progress, "supabase", db):
            result = progress._enrolment("user-1", "course-1")
        self.assertEqual(result["id"], "enrolment-1")

    def test_platform_admin_can_read_course_without_tenant_grant(self):
        course = {"id": "course-1", "ownership": "learnora", "organisation_id": None}
        with patch.object(course_content, "supabase", FakeSupabase()):
            course_content._check_course_view_access(context(None, platform_admin=True), course)


if __name__ == "__main__":
    unittest.main()
