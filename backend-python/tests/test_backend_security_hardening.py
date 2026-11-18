"""Regression contracts for backend security hardening.

These tests intentionally inspect security-critical integration points without
requiring live Paystack, Supabase, Gmail or Vercel credentials.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class BackendSecurityHardeningTests(unittest.TestCase):
    def test_authentication_modules_compile(self):
        compile(read("routers/auth.py"), "routers/auth.py", "exec")
        compile(read("routers/internal_auth.py"), "routers/internal_auth.py", "exec")

    def test_learner_login_lockout_is_five_failures_in_five_minutes(self):
        source = read("routers/auth.py")
        self.assertRegex(source, r"MAX_FAILS\s*=\s*5\b")
        self.assertRegex(source, r"WINDOW\s*=\s*300\b")
        self.assertIn("IP_MAX_FAILS = 20", source)
        self.assertIn("login-account:", source)
        self.assertIn("login-account-ip:", source)
        self.assertIn("login-ip:", source)

    def test_internal_staff_login_uses_shared_persistent_lockout(self):
        source = read("routers/internal_auth.py")
        self.assertIn("auth._login_rate_keys(email, request)", source)
        self.assertIn("auth._login_is_limited(rate_keys)", source)
        self.assertIn("auth._record_login_failure(rate_keys)", source)
        self.assertIn('"Retry-After": str(auth.WINDOW)', source)

    def test_internal_staff_tokens_use_domain_separated_key_and_claims(self):
        source = read("routers/internal_auth.py")
        self.assertIn("hmac.new(", source)
        self.assertIn("learnora-internal-staff-jwt-v1", source)
        self.assertIn("INTERNAL_TOKEN_ISSUER", source)
        self.assertIn("INTERNAL_TOKEN_AUDIENCE", source)
        self.assertIn("issuer=INTERNAL_TOKEN_ISSUER", source)
        self.assertIn("audience=INTERNAL_TOKEN_AUDIENCE", source)
        self.assertIn("INTERNAL_JWT_SECRET", source)

    def test_password_change_revokes_tokens_with_subsecond_issue_time(self):
        source = read("routers/auth.py")
        self.assertIn("now = time.time()", source)
        self.assertIn("if float(issued_at) < changed_ts:", source)
        self.assertIn("_assert_session_not_before_password_change(payload", source)

    def test_password_policy_avoids_bcrypt_truncation_and_common_passwords(self):
        source = read("routers/auth.py")
        self.assertIn("if len(password) < 12:", source)
        self.assertIn('len(password.encode("utf-8")) > 72', source)
        self.assertIn("api.pwnedpasswords.com/range/", source)

    def test_payment_duration_is_derived_from_verified_amount(self):
        source = read("routers/billing.py")
        self.assertIn('("NGN", 1_200_000): "monthly"', source)
        self.assertIn('("NGN", 12_000_000): "yearly"', source)
        self.assertIn("paid_interval = validate_payment_amount(payment)", source)
        self.assertIn("billing_interval = paid_interval", source)
        interval_section = source.split("# 9. Derive the billing interval", 1)[1].split("# 10. Determine subscription expiry", 1)[0]
        self.assertNotIn("body.billing_interval", interval_section)
        self.assertIn("validate_payment_amount(payment)", source)
        self.assertIn(r'[A-Za-z0-9_.=-]{4,100}', source)
        self.assertIn("quote(reference, safe='')", source)

    def test_course_uploads_use_real_private_resource_bucket(self):
        source = read("routers/internal_content.py")
        self.assertIn('from_("learnora-resources")', source)
        self.assertNotIn('from_("learnora-course-resources")', source)
        self.assertIn("file_size_bytes: int = Field(..., gt=0, le=2147483648)", source)
        self.assertIn("file_size_bytes: int = Field(..., gt=0, le=104857600)", source)
        ops = (REPO / "supabase/ops/harden_course_upload_buckets.sql").read_text()
        self.assertIn("SET public = false", ops)
        self.assertIn("file_size_limit = 104857600", ops)

    def test_payout_status_is_a_typed_request_body(self):
        source = read("routers/creator_finance.py")
        self.assertIn('status: Literal["processing", "paid", "failed", "cancelled"]', source)
        self.assertIn("body: PayoutProcessIn", source)
        self.assertIn("status = body.status", source)

    def test_paystack_and_cron_signature_comparisons_use_bytes(self):
        webhook = read("routers/webhooks.py")
        notifications = read("routers/notifications.py")
        lifecycle = read("routers/account_lifecycle.py")
        self.assertIn("signature.encode(\"utf-8\"), expected.encode(\"ascii\")", webhook)
        self.assertIn('(authorization or "").encode("utf-8")', notifications)
        self.assertIn('(authorization or "").encode("utf-8")', lifecycle)

    def test_rate_limiter_uses_only_vercel_normalised_client_ip(self):
        auth_source = read("routers/auth.py")
        main_source = read("main.py")
        self.assertIn('os.getenv("VERCEL", "").strip() == "1"', auth_source)
        self.assertIn('request.headers.get("x-real-ip")', auth_source)
        self.assertIn('os.getenv("VERCEL", "").strip() == "1"', main_source)
        self.assertIn('request.headers.get("x-real-ip")', main_source)
        self.assertNotIn('request.headers.get("x-forwarded-for")', auth_source)
        self.assertNotIn('request.headers.get("x-forwarded-for")', main_source)

    def test_ready_endpoint_is_not_exempt_from_global_rate_limiting(self):
        source = read("main.py")
        match = re.search(r"_RATE_LIMIT_EXEMPT_PATHS\s*=\s*\{([^}]+)\}", source)
        self.assertIsNotNone(match)
        self.assertNotIn("/api/ready", match.group(1))

    def test_login_does_not_disclose_deactivated_or_disabled_account_state_before_password(self):
        auth_source = read("routers/auth.py")
        learner = auth_source.split("# LEARNER", 1)[1].split("# EMAIL VERIFICATION", 1)[0]
        self.assertLess(learner.index("valid, needs_rehash"), learner.index('if user.get("account_status")'))
        internal = read("routers/internal_auth.py")
        existing_staff = internal.split('    user, staff = found["user"], found["staff"]', 1)[1]
        self.assertLess(existing_staff.index("valid, needs_rehash"), existing_staff.index('if user.get("account_status")'))

    def test_registration_does_not_disclose_existing_email_addresses(self):
        source = read("routers/auth.py")
        self.assertIn("generic_registration_response", source)
        self.assertIn("return generic_registration_response", source)
        self.assertNotIn("Email already registered", source)
        self.assertNotIn("This email is already registered", source)

    def test_admin_password_creation_and_reset_update_session_revocation_timestamp(self):
        source = read("routers/admin.py")
        self.assertIn('"password_changed_at": now.isoformat()', source)
        self.assertIn('updates["password_changed_at"] = datetime.now(timezone.utc).isoformat()', source)
        auth_source = read("routers/auth.py")
        self.assertIn('"password_changed_at": now.isoformat()', auth_source)
        self.assertIn('"password_changed_at": datetime.now(timezone.utc).isoformat()', auth_source)

    def test_session_with_missing_issue_time_is_rejected_after_migration(self):
        source = read("routers/auth.py")
        self.assertIn('if issued_at is None:', source)
        self.assertIn('if not changed_at:', source)

    def test_password_change_migration_supplies_the_live_session_timestamp_column(self):
        migration = (REPO / "supabase/migrations/20261117110000_password_change_session_revocation.sql").read_text()
        self.assertIn("ALTER TABLE public.users", migration)
        self.assertIn("ALTER TABLE public.admins", migration)
        self.assertIn("password_changed_at", migration)

    def test_vulnerable_direct_dependencies_are_removed_or_upgraded(self):
        requirements = read("requirements.txt")
        self.assertIn("fastapi==0.142.4", requirements)
        self.assertIn("starlette==1.7.0", requirements)
        self.assertIn("python-multipart==0.0.32", requirements)
        self.assertIn("PyJWT[crypto]==2.15.1", requirements)
        self.assertNotIn("python-jose", requirements)
        self.assertNotIn("bleach", requirements)


if __name__ == "__main__":
    unittest.main()
