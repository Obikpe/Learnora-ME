# Shared rate-limit rollout

The following rate-limit migrations are committed on `main` and are recorded in the connected production Supabase migration ledger:

1. `20261026100000_pin_cohort_assignment_function_search_paths.sql`
2. `20261026150000_shared_auth_rate_limits.sql`
3. `20261026151000_shared_api_rate_limit.sql`
4. `20261026153000_revoke_browser_privileges_and_defaults.sql`

The migration ledger currently records all four versions as applied. This document does not authorise further production schema changes.

## Runtime behaviour

- Production authentication failure counters use PostgreSQL RPCs, so serverless instances share lockout state.
- Individual learner and cohort login allow five failed attempts in a five-minute window, then block the relevant account bucket for five minutes.
- Individual login tracks account, account/IP, and IP-wide buckets; the IP-wide threshold is 20 failures per five minutes to reduce password spraying without applying the account threshold to shared networks.
- Cohort login tracks username, username/IP, and IP-wide buckets; the current cohort IP bucket uses the five-failure threshold.
- A successful individual or cohort login clears only the account and account/IP buckets; it does not erase the IP-wide history.
- Production API request limits use a database-backed bucket and fail closed with HTTP 503 if the shared limiter is unavailable.
- Local development continues to use in-process authentication counters and bypasses the production API limiter.
- Bucket identifiers are SHA-256 digests; raw usernames and client IP addresses are not stored in the rate-limit table.
- Client IP selection trusts `X-Real-IP` only when `VERCEL=1`; otherwise the ASGI peer address is used.

## Staging verification checklist

- Run the backend regression and verification tests for individual and cohort login.
- Verify the five-failure threshold and five-minute expiry using concurrent requests against a disposable project.
- Verify that account-level limits persist across different source IP addresses.
- Verify that the IP-wide bucket blocks password spraying across many usernames.
- Verify that an unavailable shared limiter fails closed.
- Confirm the production migration ledger before any future schema change.

The separate administrator-only operation `supabase/ops/revoke_supabase_admin_browser_defaults.sql` addresses default ACLs owned by `supabase_admin`; it must be run only by an authorised administrator session, not by the normal migration role.\n\nThis documentation does not authorise a production migration or deployment.
