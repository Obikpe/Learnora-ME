"""Unit tests for server-authoritative Paystack payment verification."""
import os
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-with-enough-entropy-123456")

from fastapi import HTTPException
from routers import billing


class PaystackPaymentValidationTests(unittest.TestCase):
    def test_verified_minor_units_determine_the_subscription_interval(self):
        expected = {
            ("NGN", 1_200_000): "monthly",
            ("NGN", 12_000_000): "yearly",
            ("USD", 1_000): "monthly",
            ("USD", 10_000): "yearly",
            ("USD", 1_500): "monthly",
            ("USD", 15_000): "yearly",
        }
        for (currency, amount), interval in expected.items():
            with self.subTest(currency=currency, amount=amount):
                self.assertEqual(
                    billing.validate_payment_amount(
                        {"currency": currency, "amount": amount}
                    ),
                    interval,
                )

    def test_unrecognised_currency_or_amount_is_rejected(self):
        for payment in (
            {"currency": "NGN", "amount": 1_200},
            {"currency": "USD", "amount": 12_000},
            {"currency": "EUR", "amount": 1_000},
            {"currency": "NGN", "amount": None},
        ):
            with self.subTest(payment=payment):
                with self.assertRaises(HTTPException) as raised:
                    billing.validate_payment_amount(payment)
                self.assertEqual(raised.exception.status_code, 402)

    def test_invalid_reference_is_rejected_before_network_access(self):
        with patch.object(billing.httpx, "get") as request:
            with self.assertRaises(HTTPException) as raised:
                billing.verify_paystack_transaction("../../outside", "test-secret")
        self.assertEqual(raised.exception.status_code, 400)
        request.assert_not_called()

    def test_reference_is_url_encoded_before_paystack_verification(self):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "status": True,
            "data": {"status": "success", "reference": "ref=1234"},
        }
        with patch.object(billing.httpx, "get", return_value=response) as request:
            result = billing.verify_paystack_transaction("ref=1234", "test-secret")
        self.assertEqual(result["status"], "success")
        self.assertEqual(
            request.call_args.args[0],
            "https://api.paystack.co/transaction/verify/ref%3D1234",
        )


if __name__ == "__main__":
    unittest.main()
