"""Finance endpoints must not treat course assignment as finance authority."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import creator_finance


class CreatorFinanceSecurityTests(unittest.TestCase):
    def setUp(self):
        self.context = SimpleNamespace(
            is_super_admin=False,
            has_permission=lambda _permission: False,
        )
        self.db = Mock()

    def test_sale_recording_denies_non_finance_user_before_database_access(self):
        body = creator_finance.SaleIn(
            creator_id="creator-1",
            course_id="course-1",
            gross_amount_minor=10000,
            currency="NGN",
            platform_fee_minor=1000,
            creator_earnings_minor=9000,
        )
        with patch.object(creator_finance, "supabase", self.db):
            with self.assertRaises(HTTPException) as raised:
                creator_finance.record_sale(body, self.context)
        self.assertEqual(raised.exception.status_code, 403)
        self.db.table.assert_not_called()

    def test_sale_release_denies_non_finance_user_before_database_access(self):
        with patch.object(creator_finance, "supabase", self.db):
            with self.assertRaises(HTTPException) as raised:
                creator_finance.release_sale("sale-1", self.context)
        self.assertEqual(raised.exception.status_code, 403)
        self.db.table.assert_not_called()

    def test_sale_refund_denies_non_finance_user_before_database_access(self):
        with patch.object(creator_finance, "supabase", self.db):
            with self.assertRaises(HTTPException) as raised:
                creator_finance.refund_sale("sale-1", self.context)
        self.assertEqual(raised.exception.status_code, 403)
        self.db.table.assert_not_called()

    def test_explicit_creator_finance_permission_can_pass_the_temporary_guard(self):
        creator_finance._require_creator_finance_permission(
            SimpleNamespace(
                is_super_admin=False,
                has_permission=lambda permission: permission == "creator_payouts.process",
            )
        )

    def test_super_admin_can_pass_the_temporary_guard(self):
        creator_finance._require_creator_finance_permission(
            SimpleNamespace(is_super_admin=True, has_permission=lambda _permission: False)
        )


if __name__ == "__main__":
    unittest.main()
