"""Regression tests for the reversible individual-learner free-launch policy."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from routers import auth, course_content
from services import access
from services.free_access import free_access_mode_enabled, is_individual_learner


class FreeAccessModeTests(unittest.TestCase):
    def test_flag_is_off_by_default_and_only_accepts_explicit_true_values(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(free_access_mode_enabled())
        for value in ("1", "true", "YES", "on"):
            with self.subTest(value=value), patch.dict(os.environ, {"FREE_ACCESS_MODE": value}):
                self.assertTrue(free_access_mode_enabled())
        for value in ("", "0", "false", "off", "enabled"):
            with self.subTest(value=value), patch.dict(os.environ, {"FREE_ACCESS_MODE": value}):
                self.assertFalse(free_access_mode_enabled())

    def test_only_global_individual_learner_accounts_are_eligible(self):
        self.assertTrue(is_individual_learner("normal", "learner"))
        self.assertTrue(is_individual_learner("witstart", "learner"))
        for role, account_type in (
            ("super_admin", "admin"),
            ("staff_admin", "admin"),
            ("normal", "cohort"),
            ("normal", "organisation"),
            ("creator", "creator"),
            ("organisation_prospect", "learner"),
        ):
            with self.subTest(role=role, account_type=account_type):
                self.assertFalse(is_individual_learner(role, account_type))

    def test_verified_expired_learner_gets_free_access_without_mutating_billing_history(self):
        learner = {
            "id": "learner-1",
            "role": "normal",
            "email_verified_at": "2026-10-01T10:00:00Z",
            "sub_status": "expired",
            "is_paid": False,
            "trial_ends_at": "2026-10-08T10:00:00Z",
            "expires_at": None,
        }
        db = Mock()
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "true"}), patch.object(auth, "supabase", db):
            result = auth._resolve_learner_access(learner)
        self.assertTrue(result["course_access"])
        self.assertEqual(result["access_state"], "free")
        self.assertFalse(result["is_paid"])
        self.assertEqual(result["sub_status"], "expired")
        self.assertEqual(result["trial_ends_at"], learner["trial_ends_at"])
        db.table.assert_not_called()

    def test_unverified_learner_does_not_receive_free_access(self):
        learner = {
            "id": "learner-1",
            "role": "normal",
            "email_verified_at": None,
            "sub_status": "pending",
            "is_paid": False,
        }
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "true"}):
            result = auth._resolve_learner_access(learner)
        self.assertFalse(result["course_access"])
        self.assertEqual(result["access_state"], "pending")

    def test_admin_or_prospect_role_does_not_receive_individual_free_access(self):
        for role in ("super_admin", "staff_admin", "organisation_prospect"):
            learner = {
                "id": "account-1",
                "role": role,
                "email_verified_at": "2026-10-01T10:00:00Z",
                "sub_status": "expired",
                "is_paid": False,
            }
            with self.subTest(role=role), patch.dict(os.environ, {"FREE_ACCESS_MODE": "true"}):
                result = auth._resolve_learner_access(learner)
            self.assertFalse(result["course_access"])

    def test_turning_mode_off_restores_existing_expiry_check(self):
        learner = {
            "id": "learner-1",
            "role": "normal",
            "email_verified_at": "2026-10-01T10:00:00Z",
            "sub_status": "trialing",
            "is_paid": False,
            "trial_ends_at": "2026-10-02T10:00:00Z",
            "expires_at": None,
        }
        db = Mock()
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "false"}), patch.object(auth, "supabase", db):
            result = auth._resolve_learner_access(learner)
        self.assertFalse(result["course_access"])
        self.assertEqual(result["access_state"], "expired")
        db.table.assert_called_once_with("users")

    def test_free_mode_allows_only_published_learnora_courses_for_global_learners(self):
        context = SimpleNamespace(
            is_platform_admin=False,
            user_id="learner-1",
            organisation_id=None,
            organisation_role=None,
            user=SimpleNamespace(role="normal", account_type="learner"),
        )
        course = {"id": "course-1", "ownership": "learnora", "status": "published"}
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "true"}), patch.object(course_content, "supabase", Mock()):
            self.assertIsNone(course_content._check_course_view_access(context, course))

    def test_free_mode_does_not_grant_unpublished_or_creator_content(self):
        context = SimpleNamespace(
            is_platform_admin=False,
            user_id="learner-1",
            organisation_id=None,
            organisation_role=None,
            user=SimpleNamespace(role="normal", account_type="learner"),
        )
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "true"}), patch.object(course_content, "supabase", Mock()):
            for course in (
                {"id": "draft-1", "ownership": "learnora", "status": "draft"},
                {"id": "creator-1", "ownership": "creator", "status": "published"},
            ):
                with self.subTest(course=course):
                    with self.assertRaises(Exception):
                        course_content._check_course_view_access(context, course)

    def test_central_access_resolver_returns_free_launch_source_only_when_explicitly_allowed(self):
        course = {"id": "course-1", "ownership": "learnora", "status": "published"}
        with patch.dict(os.environ, {"FREE_ACCESS_MODE": "true"}), patch.object(access, "_course", return_value=course), patch.object(access, "supabase", Mock()):
            result = access.resolve_course_access("learner-1", "course-1", allow_free_access=True)
        self.assertEqual(result, {"allowed": True, "source": "free_launch"})


if __name__ == "__main__":
    unittest.main()
