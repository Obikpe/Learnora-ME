# Learnora backend security hardening — 18 November 2026

## Scope and production boundary

The reviewed code changes, regression tests, migration definitions, and CI test harness updates are committed to `main`.

**No production deployment was made. No live Supabase migration, storage-bucket change, or default-ACL change was applied.** Live Supabase checks below were read-only.

## Changes implemented on `main`

### Payments and billing

- Paystack references are validated against a strict character/length allow-list before any network request and are URL-encoded in the verification URL.
- Subscription duration is derived from the verified Paystack transaction currency and amount in minor units. The client-supplied billing interval is not authoritative.
- Added runtime tests for all configured NGN/USD amount mappings, unsupported amounts/currencies, path-injection references, and URL encoding.

### Authentication and sessions

- Learner and staff login paths use persistent account/IP rate-limit buckets. Cohort login additionally uses account, account-plus-IP, and IP-wide buckets.
- The Vercel client-IP path uses the normalized `x-real-ip` header only when running on Vercel; arbitrary `x-forwarded-for` values are not trusted.
- Login checks verify the password before disclosing account state. Registration responses avoid confirming whether an email address is already registered.
- Staff JWTs use a domain-separated signing key and issuer/audience claims.
- Password policy checks enforce a 12-character minimum, reject bcrypt inputs over 72 UTF-8 bytes, and use the Pwned Passwords range API.
- Password-change/reset code updates `password_changed_at`; token validation compares the full-precision JWT issue time against that timestamp.
- The canonical pending migration is `supabase/migrations/20261117210000_password_session_invalidation.sql`. It adds the timestamp to `public.users` and `public.admins`, backfills existing rows, and makes the column non-null. Its rollback is intentionally non-destructive because dropping the column would disable session revocation.

### Other backend protections

- Course-creation errors return generic client messages while details remain server-side.
- Admin payout status is validated against an explicit set of allowed states.
- Paystack webhook and cron authorization comparisons use bytes-safe constant-time comparisons.
- Resource upload requests validate MIME type and size and target the existing `learnora-resources` bucket.
- The pending `20261117220000_private_course_resources_bucket.sql` migration now targets `learnora-resources` (not the unused `learnora-course-resources` name).
- Quiz sessions have an authenticated heartbeat endpoint that renews only the caller's active session.
- The AI workspace checks quiz activity in the current browser tab; it does not globally block AI because a different tab has an active quiz.
- A module without a published quiz is not treated as an impossible completion gate for later modules.
- Community question email delivery uses the Gmail API helper.

### Frontend and dependencies

- The three public client-rendered pages that failed the supplied Vercel build now use server page wrappers for metadata and separate client components with `"use client"` at the top.
- The AI workspace disables tutor interaction while a quiz is active in the same tab.
- The legacy cohort JWT import was migrated from `python-jose` to PyJWT. Direct dependencies were updated; the CI dependency audit reports no known vulnerabilities.

## Verification completed

Successful GitHub Actions runs on commit `8be87f0692d3994fa9d08c3015719821b632f89b`:

- **Learnora production checks:** run `44270934608`.
  - 343 backend unit tests ran; 1 was skipped; all executed tests passed.
  - `pip-audit`: no known vulnerabilities found.
  - Python compilation and undefined-name/static checks passed.
  - Backend application import and HTTP startup smoke test passed.
  - Additive migration rehearsal and rollback checks passed.
  - Learner frontend production build passed.
  - Teams frontend production build passed.
- **Cohort Learning Access Tests:** run `44270934622`.
  - Cohort unit tests and database-backed lifecycle assertions passed.
  - Disposable API staging schema and PostgREST startup passed.
  - Full authenticated cohort lifecycle API journey passed.
  - Timestamped migration replay, deterministic seed checks, browser-role privilege checks, and service-role grant checks passed.

The API staging and migration replay used disposable CI PostgreSQL databases only.

## Read-only live Supabase findings

Project: `gihfupzvdpyrmynqgukz`.

- The live migration ledger includes `20261117204703` (administrator sequence browser-access revocation).
- `public.users.account_status` and `public.users.account_deactivation_until` exist in the live schema.
- `password_changed_at` is not yet present on either `public.users` or `public.admins`; therefore the password-session revocation feature is not active in production until migration `20261117210000` is applied.
- All 108 inspected public tables have RLS enabled. The read-only privilege check found no direct browser-role grants on public tables, functions, or sequences.
- Managed `supabase_admin` default ACLs still include browser-role privileges (16 table, 6 sequence, and 2 function ACL entries). The ordinary project connection is not a member of `supabase_admin`, so the manual remediation script could not be applied.
- `learnora-course-media` is private, limited to 2 GiB, and has the expected video MIME allow-list.
- `learnora-resources` is private but currently has no file-size limit or MIME allow-list. The pending resource-bucket migration and manual hardening script define the 100 MiB document/image allow-list.

### Migration-ledger caution

Some repository migration files are reconstructed equivalents of changes already present in the live schema under different migration version IDs. The API staging workflow applies these files only to a disposable database to recreate the expected schema. Do not replay those reconstructed account-lifecycle migrations against production without reconciling the exact live migration ledger first.

## Remaining production release gates

1. Apply `20261117210000_password_session_invalidation.sql` to production after explicit approval. This intentionally invalidates existing JWT sessions, so users will need to sign in again.
2. Apply `20261117220000_private_course_resources_bucket.sql` (or the reviewed `supabase/ops/harden_course_upload_buckets.sql`) after explicit approval to enforce the resource upload size and MIME restrictions.
3. Run `supabase/ops/revoke_supabase_admin_browser_defaults.sql` in a `supabase_admin`-authorized session. The ordinary project connection cannot perform this managed-role change.
4. The backend now expects the server-only Vercel variable `PAYSTACK_SECRET_KEY`. The backend Vercel project still contains the legacy sensitive variable `NEXT_PUBLIC_PAYSTACK_SECRET_KEY`; Vercel did not allow that sensitive variable's key name to be changed through the available API. Create `PAYSTACK_SECRET_KEY` with the existing Paystack secret in Vercel, then remove the legacy variable. The secret value was not retrieved or exposed.
5. After the environment variable is corrected, run a Paystack test-mode verification and verify the normalized client-IP header on a live Vercel request.
6. Deploy only after separate authorization.

**Production remains untouched.**

## AI-generated video storage boundary — 21 November 2026

- Existing human-uploaded lesson videos and resources continue to use the existing private Supabase Storage buckets and their current access checks.
- The AI lesson renderer now has source code to upload finished MP4s to a separate private Cloudflare R2 bucket. The backend creates temporary playback URLs only after the normal learner course/module/lesson access checks. R2 credentials remain server-side; the renderer uses a separate write-capable worker token.
- The R2 bucket, CORS policy, Vercel backend credentials and GitHub Actions worker secrets have **not** been configured. No live storage-bucket change or production deployment has occurred.
- The Course Studio migration adds a service-role-only render queue and publication RPC. Publication remains blocked until every video lesson has a completed render job and a ready private video record.
- See `docs/R2_VIDEO_BUCKET_SETUP.md` for the configuration checklist and `docs/AI_COURSE_PRODUCTION_AND_MEDIA_ARCHITECTURE.md` for the full workflow.