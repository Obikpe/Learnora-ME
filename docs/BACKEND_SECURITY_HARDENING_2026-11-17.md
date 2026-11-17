# Backend security hardening — 17 November 2026

This report records the repository changes and live Supabase checks made during the security review. It distinguishes code changes from production configuration that still requires an authorised database action or a deployment.

## Implemented in the repository

- Paystack verification binds the subscription interval to the verified currency and amount. Payment references are format-validated and URL-encoded before the verification request.
- Learner login already enforces five failed attempts per account and account/IP pair within a five-minute window, plus an IP-wide threshold of twenty. Internal staff login now uses the same persistent limiter and returns HTTP 429 with a five-minute `Retry-After` after lockout.
- Internal staff JWTs now use a domain-separated signing key and explicit issuer/audience claims. Staff and learner tokens cannot be substituted for one another.
- JWT issuance now preserves sub-second `iat` precision. The session check compares the full timestamp with `password_changed_at`, avoiding the same-second invalidation gap.
- Registration now returns a generic response for existing and new identities instead of exposing whether an email belongs to a learner, administrator or cohort account.
- Password requirements are twelve characters minimum, reject passwords found in the Pwned Passwords range service, and reject inputs exceeding bcrypt's 72-byte limit.
- Legacy SHA-256 password hashes remain temporarily supported and are scheduled to require reset after `LEGACY_SHA256_LOGIN_DEADLINE=2027-01-01T00:00:00Z`.
- Course-management failures return generic client messages while recording exception details server-side.
- Cron and Paystack webhook signature comparisons use byte strings, avoiding non-ASCII header exceptions.
- `/api/ready` is not exempt from the global API rate limiter.
- Payout status changes now use a typed request body with an explicit allowed-value set.
- The resource-upload endpoint now targets the existing private `learnora-resources` bucket; its request model already restricts MIME types and caps uploads at 100 MiB.
- The backend example environment file documents `PAYSTACK_SECRET_KEY` as server-only. Do not use a `NEXT_PUBLIC_` prefix for a payment secret.
- The current requirements already use FastAPI 0.142.4, Starlette 1.7.0, python-multipart 0.0.32 and PyJWT 2.15.1. The vulnerable direct `python-jose` and `bleach` dependencies are absent.
- Added `pip-audit` to the quality workflow and added focused security regression tests.

## Live Supabase checks

Project: `gihfupzvdpyrmynqgukz`.

- All 108 public tables have Row Level Security enabled.
- There are no public-schema RLS policies. This is deny-by-default and matches the current architecture: browser clients do not query the database directly; FastAPI uses the service-role key.
- Direct grants to `anon` and `authenticated` were not found on public tables, functions or sequences.
- The live `learnora-course-media` bucket is private, has a 2 GiB size limit and allows only the five video MIME types used by the upload API.
- The live `learnora-resources` bucket is private, but currently has no file-size limit and no MIME allow-list. The endpoint now points to this bucket, so the storage hardening script must be applied before enabling staff resource uploads.

### Managed-role default privileges remain open

The live `supabase_admin` default ACLs still grant browser-role privileges on future objects. This does not mean the current public tables are directly exposed: current direct grants are absent and RLS is enabled with no policies. It does mean a future object created under `supabase_admin` could inherit unsafe defaults.

The existing manual script is `supabase/ops/revoke_supabase_admin_browser_defaults.sql`. The current project connection is not a member of `supabase_admin`, so this session cannot apply it. Run it only from a database session authorised to alter defaults for that managed role, then run `supabase/ops/verify_live_schema.sql` and recheck default ACLs. Do not treat this item as resolved until the verification query returns no browser-role defaults.

## Database migration awaiting approval

`supabase/migrations/20261117110000_password_change_session_revocation.sql` adds `password_changed_at` to both `public.users` and `public.admins`, with a non-null default.

The live schema currently does not contain either column. This migration is therefore required before deploying the updated password-change/session-validation code. It sets the initial timestamp to the migration time, intentionally invalidating all existing JWT sessions once applied; users and staff will need to sign in again. The paired rollback is deliberately non-destructive because dropping the column would remove session revocation protection.

**This migration has not been applied.**

## Storage hardening awaiting approval

`supabase/ops/harden_course_upload_buckets.sql` keeps both buckets private and configures:

- `learnora-course-media`: 2 GiB maximum; video MIME allow-list.
- `learnora-resources`: 100 MiB maximum; document, spreadsheet, presentation, image, text, ZIP and JSON MIME allow-list.

**This script has not been applied.** Apply and verify it before enabling staff resource uploads in production.

## Items requiring live verification or operational follow-up

1. **Rate-limit IP through Vercel rewrites:** the backend uses Vercel's `x-real-ip` header when running on Vercel and falls back to the request peer. Code review supports per-visitor buckets, but a live request through the public frontend rewrite and a direct backend request have not been compared. Do not trust arbitrary forwarded headers from non-Vercel sources.
2. **Managed default ACLs:** see the blocking item above.
3. **Storage bucket policy:** see the pending script above.
4. **Dependency audit:** `pip-audit` is now in CI, but it has not run in this review. No claim is made that the full resolved dependency graph is advisory-free until the audit passes.
5. **Vercel payment configuration:** the frontend Vercel project currently has only `NEXT_PUBLIC_API_URL`. The backend project has a legacy `NEXT_PUBLIC_PAYSTACK_SECRET_KEY` variable name, but it is not referenced by the backend source and is not present in the frontend project's environment. Before paid billing is re-enabled, provision a fresh Paystack secret as a sensitive, server-only `PAYSTACK_SECRET_KEY` in the backend project and remove the legacy variable. Rotate the Paystack key if it has ever been placed in browser code or a public build.
6. **Rate-limit availability:** persistent rate limiting intentionally fails closed when Supabase cannot be reached. This protects authentication but can make API requests unavailable during a database outage. Replacing it with a dedicated shared rate-limit store is an architectural follow-up, not a safe fail-open change.
7. **Lookup cost:** the repeated identity lookups remain a performance concern. They were not cached because caching role and account state can delay revocation; profile this before changing the authorization path.
8. **Legacy environment variables:** the backend Vercel project contains old payment-provider and mail variables. They should be removed only after confirming no active deployment or rollback depends on them.

## Release gates

Before deployment:

1. Apply and verify the password-change migration.
2. Apply and verify the storage bucket hardening script.
3. Have an authorised `supabase_admin` session run the default-ACL remediation and verify no browser-role defaults remain.
4. Run the backend test suite, compile check and `pip-audit`; resolve every new finding.
5. Test learner and staff lockout, password reset invalidation, legacy-password deadline behaviour, generic registration responses, Paystack sandbox amount/interval binding, and signed uploads.
6. Compare the real client IP observed through the frontend rewrite and direct backend path.
7. Deploy only after the above gates are approved.

No production deployment or database mutation was performed as part of this review.
