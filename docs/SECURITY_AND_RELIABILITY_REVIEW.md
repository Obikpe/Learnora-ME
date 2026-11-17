# Learnora ME Security and Reliability Review

Last reviewed: 17 November 2026

## Scope and limitations

This review covers the connected production Supabase project and repository configuration/code inspected through GitHub. It is not a certification that the application has zero vulnerabilities. The automated Daybreak repository scan could not be launched because the current workspace was denied Daybreak security access. GitHub Actions was not used. No deployment or new production migration was performed during this review.

## Controls verified

- PostgreSQL 17.11 project is active and healthy.
- Row-level security is enabled on all 108 public tables.
- No direct table grants to `anon` or `authenticated` were found in the public schema.
- The inspected public security-definer functions were not executable by `anon` or `authenticated`.
- Inspected security-definer functions have pinned search paths.
- The only browser-role sequence privilege found was USAGE on `public.admins_id_seq`. A migration to revoke that unnecessary privilege has been committed but is pending application.
- API-wide shared PostgreSQL throttling is configured for 60 requests per IP per 60 seconds in production and fails closed if the shared limiter is unavailable.
- Individual login now uses five failures in a five-minute window, then a five-minute lockout. It counts by account across IPs, account/IP, and IP-wide (20 failures per five minutes) to reduce credential stuffing and password spraying.
- Cohort login uses five failures per username in five minutes, a username/IP bucket, and a separate IP-wide threshold of 20 per five minutes.
- The application trusts Vercel's normalised `X-Real-IP` only when running on Vercel; it does not trust arbitrary client-supplied `X-Forwarded-For` values.
- Production CORS origins are explicit; credentials are enabled only with that allowlist.
- Production API docs/OpenAPI endpoints are disabled.
- API responses are marked `Cache-Control: no-store`; security headers include frame denial, MIME sniffing protection, referrer policy, permissions policy, production CSP, and HTTPS HSTS.
- Paystack webhook code inspected uses HMAC-SHA512 and constant-time signature comparison.
- Gmail OAuth and cron credentials are held in sensitive Vercel environment variables.

## Changes committed on main

- Five-attempt / five-minute individual login lockout and account/IP/IP-wide buckets.
- Five-attempt / five-minute cohort account lockout and separate IP-wide spray threshold.
- Regression contract tests for the lockout policy.
- Migration `20261117100000_revoke_admin_sequence_browser_access.sql` to remove browser-role access to the admin identity sequence.

## Items not yet verified or completed

1. **Automated repository scan:** Daybreak denied access in this workspace; no scan findings can be claimed.
2. **Runtime tests:** the backend test suite and build were not run in this environment. The new regression tests are committed but unexecuted.
3. **Deployment:** login changes are not active in production until the backend is deployed.
4. **Pending migration:** apply `20261117100000_revoke_admin_sequence_browser_access.sql` only after explicit production-migration approval, then verify the sequence grants are gone.
5. **SQL injection and XSS:** no complete route-by-route/source-to-sink audit or dynamic attack testing was performed. Supabase query-builder use is not by itself proof that every query is safe.
6. **Backups and restore:** provider backup availability, retention, point-in-time recovery and a restore drill were not verifiable from the connected project tools.
7. **Dependency vulnerabilities:** no complete lockfile/SCA scan was run. The frontend package manifest has no frontend lockfile in the inspected project path.
8. **Timeout/retry coverage:** a 25-second Gmail OAuth HTTP timeout and 20-second Paystack HTTP timeout were observed; all external calls and DB operations have not been exhaustively audited for bounded timeouts, retry budgets and idempotency.
9. **Database performance:** the advisor reported 73 foreign keys without supporting indexes, one duplicate index, and 129 unused indexes. No index changes were made because production data/traffic are too small to safely infer which unused indexes should be dropped. The foreign-key candidates need workload-aware review.
10. **Memory/load testing:** no sustained load, concurrency, memory profiling, or failover exercise was run.
11. **WebSockets/Kubernetes/TCP/UDP/load balancing:** these are not required application features in the current Vercel-managed architecture. They should not be introduced just to match a checklist.

## Release gate

Before calling the security work complete:
- Run backend tests and frontend production build.
- Perform a full repository SAST/dependency scan once security-scan access is available.
- Review all authenticated routes and dynamic SQL functions for ownership/tenant isolation and injection.
- Test XSS sinks and untrusted rich-text rendering.
- Verify backups and complete a restore drill.
- Apply and verify the pending sequence-privilege migration with approval.
- Deploy backend only with explicit authorisation, then verify login lockouts and normal successful-login recovery in production.
