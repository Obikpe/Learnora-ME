# Shared rate-limit rollout

The following migrations are now committed on `main` as **pending release candidates**:

1. `20261026100000_pin_cohort_assignment_function_search_paths.sql`
2. `20261026150000_shared_auth_rate_limits.sql`
3. `20261026151000_shared_api_rate_limit.sql`

They have not been applied to any production database by this change. Do not deploy the updated backend until these migrations have been reviewed and applied to a disposable staging Supabase project, then verified against the migration ledger and rate-limit assertions.

## Runtime behaviour

- Production authentication failure counters use PostgreSQL RPCs, so serverless instances share lockout state.
- Production API request limits use a database-backed bucket and fail closed with HTTP 503 if the shared limiter is unavailable.
- Local development continues to use in-process authentication counters and bypasses the production API limiter.
- Bucket identifiers are SHA-256 digests; raw usernames and client IP addresses are not stored in the rate-limit table.
- Client IP selection trusts `X-Real-IP` only when `VERCEL=1`; otherwise the ASGI peer address is used.

## Staging verification checklist

- Run the backend regression and verification workflows.
- Apply the three pending migrations in timestamp order to a disposable project.
- Run `backend-python/tests/db/rate_limit_assertions.sql` in that disposable project.
- Verify that concurrent requests share a single limit bucket and that an unavailable RPC causes a fail-closed response.
- Confirm the active Supabase migration ledger before any production rollout.

This documentation does not authorise a production migration or deployment.
