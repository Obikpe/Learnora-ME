# Learnora ME scalability audit — 18 November 2026

**Status:** In progress. This is a repository, configuration and live-database audit, not a production load test. No production database changes or deployments have been made.

## Executive assessment

Learnora ME is **not currently demonstrated to be ready for one million monthly active users, and it is not ready for one million concurrent users**. The current hosting plans, request pattern, rate limiter and database query patterns need work before that target is credible.

“One million users” must be separated into:
- **Registered accounts:** total accounts, including inactive users.
- **Monthly active users (MAU):** unique people using Learnora in a month.
- **Concurrent users:** people using it at the same time.

One million registered accounts may be achievable with a much smaller MAU. One million MAU or one million concurrent users is a materially different infrastructure and cost requirement.

## Current hosting and database baseline

- Supabase organisation plan: **Free** (50,000 MAU included; 500 MB database; 5 GB uncached egress, 5 GB cached egress and 1 GB file storage on the current plan).
- Supabase project region: **eu-west-3 (Paris)**.
- Vercel team plan: **Hobby** (1 million function invocations/month and 4 CPU-hours/month; Hobby is for non-commercial personal projects). If Learnora is being operated as a commercial service, the current Vercel plan is not appropriate.
- Current deployed backend region: **iad1 (Washington, D.C.)**.
- The backend configuration has been changed to **cdg1 (Paris)** to align the function with the Supabase project, but that configuration is not active until a deployment is authorised.
- Live database snapshot: approximately **19 MB**, **110 public tables**, approximately **192 estimated live rows** across tracked tables. All 110 public tables have RLS enabled. The current application uses the service-role backend model; direct table privileges for `anon` and `authenticated` are currently zero.
- PostgreSQL settings include **60 maximum connections**, approximately **224 MB shared buffers**, and approximately **384 MB effective cache size**.

These numbers describe a very small current dataset and do not predict high-concurrency behaviour.

## Live latency observations

Supabase edge logs for the 24-hour window contained a small sample of successful requests. The measurements below are origin-time statistics, not end-to-end browser timings.

| Supabase endpoint | Requests | p50 | p95 | p99 |
|---|---:|---:|---:|---:|
| `rpc/consume_api_rate_limit` | 129 | 293 ms | 1,129.8 ms | 1,302.6 ms |
| `learnora_courses` | 110 | 274 ms | 364.6 ms | 791.3 ms |
| `learnora_learning_path_courses` | 106 | 271 ms | 297.5 ms | 687.8 ms |
| `learnora_learning_paths` | 105 | 274 ms | 328.6 ms | 420.9 ms |

The rate-limit RPC is a significant latency contributor in this sample. The requests originated through the IAD edge location, consistent with the current Vercel backend region. This sample is too small to claim a stable production percentile or to isolate network time from database execution time.

Vercel runtime logs showed very little recent traffic. There is no meaningful concurrency benchmark yet.

## Findings and risks

### 1. Database-backed rate limiting is on the hot path

The FastAPI middleware calls `consume_api_rate_limit` for each non-exempt production API request. The configured default is **60 requests per minute per client IP**; no production override for that setting was present in the Vercel environment-variable inventory.

The rate-limit function locks and updates a bucket row. The middleware now verifies a signed JWT and uses a hashed per-account bucket for authenticated users; anonymous or invalid-token requests remain IP-bucketed. This prevents ordinary learners behind the same school, office or mobile-carrier NAT from consuming one another's 60-request allowance. It does not provide a coarse IP-wide cap for authenticated traffic, so edge/WAF protection still needs to be configured and reviewed. Requests from one account still contend on that account's bucket row.

The Supabase client used by the middleware is synchronous, while the middleware is asynchronous. The call has been moved to Starlette's thread pool so its network wait does not block the ASGI event loop. The backend now also reuses one bounded HTTP/2 HTTPX connection pool across Supabase services. These changes do **not** remove the database rate-limit round trip or its row lock.

### 2. Dashboard request fan-out and periodic polling

The learner dashboard loads several independent endpoints, including progress, learning summary, learning plan, public course catalogue, evidence and credentials. The session tracker also starts a learning session and sends heartbeats.

Both the learning-session heartbeat and dashboard summary refresh were reduced from 30 seconds to 60 seconds. The database heartbeat function credits up to 60 seconds per heartbeat, so a 60-second cadence remains within its existing accounting cap. This halves the periodic request rate but does not solve the larger fan-out.

At the new cadence, an open learner dashboard generates approximately **two periodic API requests per minute** before other learner activity. One million concurrent dashboards would therefore create about **2 million requests per minute (roughly 33,333 requests per second)** from these two periodic calls alone. That is a workload calculation, not a measured capacity result.

### 3. Authentication and progress endpoints perform repeated access checks

For an ordinary individual account, `get_current_user` checks the cohort-account, administrator and learner identity tables separately to preserve the single-email/single-context rule. That is multiple database lookups on every authenticated API request. Cohort-account resolution performs additional membership and cohort lookups. A future single-query account-context resolver can preserve the same checks with fewer round trips, but it requires a tracked database migration and must wait until migration history is reconciled.

The `/progress/me` path iterates through enrolments and calls the per-course `_enrolment` access resolver for each one. That resolver performs multiple database lookups, including identity, organisation/cohort context and scoped-course access checks. This creates an N+1-style query pattern as a learner's course count grows.

The access rules must remain intact. The correct remediation is a batch access resolver that evaluates the same individual, organisation, cohort and scoped-assignment rules across all relevant course IDs in a small number of queries. Do not remove access checks or trust client-supplied course IDs to make this faster.

### 5. Public course catalogue uses sequential database reads

The public courses route reads course rows, then organisation/creator status where relevant, then track membership data. The track membership helper performs additional reads. The route does not impose an explicit pagination limit on the full course list.

The browser API client has per-browser/session caching and request de-duplication. That helps repeat visits in one browser, but it is not a shared server/CDN cache and does not reduce the first request from each visitor. Any shared cache must preserve the managed-account discovery restrictions; a cached anonymous 200 response must never bypass an authenticated learner's access guard.

### 6. Database index findings

The Supabase performance advisor currently reports:
- **70 foreign keys without covering indexes**.
- **138 indexes not observed as used**.
- **1 duplicate index warning**.

The duplicate is `uq_learnora_platform_admin_role`, which duplicates the unique constraint index `learnora_platform_admins_admin_role_unique` on `(admin_id, platform_role)`. It is a candidate for removal after migration provenance is reconciled.

The 138 “unused” indexes must not be mass-deleted: the live dataset is tiny and usage statistics are not representative. The 70 foreign-key findings should be prioritised against real query paths, especially assignments, enrolments, lesson progress, quizzes/questions, course-track links and cohort/team assignments.

### 7. Migration history is not aligned

The repository contains 51 migration files and the live project reports 51 applied migrations, but the two sets are not identical:
- 3 repository migrations do not appear in the live ledger.
- 3 live migrations have no matching repository migration name.
- 11 same-name migrations have different version timestamps.

Repository-only names include `pin_cohort_assignment_function_search_paths`, `revoke_browser_privileges_and_defaults` and `learner_account_deletion`. Live-only names include `add_lesson_video_transcript_text`, `learner_account_deletion_lifecycle` and `feature_foreign_key_indexes`.

The equal migration count is not proof of alignment. Do not run `supabase db push`, replay migrations or apply new index migrations until the source and live history have been reconciled.

### 8. Future default privileges need administrative hardening

Current direct table grants to `anon` and `authenticated` are zero, and all 110 public tables have RLS enabled. The security advisor's no-policy findings are consistent with the current backend-only access model; do not add browser policies simply to silence the advisor.

However, the `supabase_admin` default ACLs still grant browser-role privileges on future public objects (tables, sequences and functions). The repository contains `supabase/ops/revoke_supabase_admin_browser_defaults.sql`, marked manual/admin-only. The ordinary project database role cannot assume `supabase_admin`, so this has not been applied. Existing table grants are currently restricted, but future objects created by that managed owner could inherit broader defaults.

### 9. Dependency and build warnings

The frontend's reported raw-image and React Hook warnings have been corrected. The successful CI run reported no ESLint warnings or errors.

Other warnings still need attention:
- The Python requirements moved from yanked `email-validator==2.1.0` to 2.3.0.
- Supabase Python SDK moved from 2.32.0 to 2.34.1, and the backend now supplies a shared HTTPX client; the SDK timeout/verify deprecation warnings disappeared in CI.
- GitHub Actions `setup-python` and `setup-node` were updated to v7.1.0 (Node 24); the Node 20 action deprecation warning disappeared.
- npm still reports deprecated transitive packages, including `inflight`, `rimraf@3`, `glob@7/10`, `@humanwhocodes/*`, and ESLint 8.57.1. The current Next 14 ESLint configuration constrains the compatible ESLint major; do not force ESLint 9/10 without a coordinated Next.js/tooling upgrade.
- The Vercel build also reported an unknown npm `cache-dir` configuration. No matching NPM environment variable or repository `.npmrc` was found, so its source appears to be outside the committed project configuration.
- Node's built-in `punycode` deprecation remains under trace using `NODE_OPTIONS=--trace-deprecation` in CI.
- Neither frontend currently has a committed npm lockfile. This leaves dependency resolution less reproducible between CI and Vercel and should be corrected.

## Changes made so far

- Fixed the reported JSX apostrophe lint errors.
- Fixed the public navigation click-handler typing issue.
- Replaced the reported raw `<img>` usages with Next.js Image components; externally supplied image URLs use unoptimized rendering where host allow-listing cannot be guaranteed.
- Corrected the reported React Hook dependencies and stabilised the dashboard empty-course fallback.
- Moved the synchronous rate-limit RPC off the ASGI event loop.
- Changed authenticated API rate-limit buckets to verified account identity, retaining IP buckets for anonymous/invalid-token requests.
- Added a bounded shared HTTP/2 HTTPX connection pool for Supabase requests.
- Configured the backend Vercel function region as `cdg1` (Paris).
- Changed the session heartbeat and dashboard summary refresh cadence from 30 to 60 seconds.
- Updated the yanked email-validator dependency, Supabase Python SDK and GitHub Actions setup actions.

The frontend/backend changes, per-account rate-limit tests, 60-second polling change and shared Supabase HTTP client have passed the repository's backend tests and both frontend production builds. The latest workflow change is tracing the remaining Node `punycode` warning.

**No production deployment has been triggered.** Both Vercel projects have deployment-on-push disabled in their configuration.

## Capacity implications

The current Vercel Hobby quota is 1 million function invocations per month. Two periodic calls per open dashboard use 120 invocations per dashboard-hour, so that monthly allowance would cover only about **8,333 dashboard-hours** from polling alone, before initial page loads or any learning activity. The current Supabase Free plan includes 50,000 MAU, not one million. Supabase Pro currently includes 100,000 MAU and charges for additional MAU; at one million MAU, the MAU overage alone would be approximately **$2,925/month**, before compute, storage, bandwidth and other usage. See the official pricing pages below.

One million registered accounts with a much smaller MAU is a different target and may be achievable with appropriate data sizing and usage. One million MAU is beyond the current Supabase Free allowance. One million concurrent users would create a fundamentally different workload and is not credible on the current plans or architecture without substantial redesign, higher-capacity infrastructure and progressive load testing.

## Prioritised next work

1. Reconcile the migration ledger and recover the source of live-only migrations before any schema change.
2. Complete edge-level abuse protection for authenticated traffic and review whether the per-account 60/minute allowance should vary by route. The per-account bucket change has already removed the shared-NAT collision for valid sessions.
3. Batch the `/progress/me` access checks without weakening individual, organisation, cohort or scoped assignment permissions.
4. Consolidate dashboard reads where practical and review polling/session event flow.
5. Add only the high-value missing foreign-key indexes after query-plan review and migration reconciliation; remove the confirmed duplicate index in a tracked migration.
6. Apply the managed-role default-ACL hardening through an authorised administrative session.
7. Add npm lockfiles and complete a coordinated Next.js/ESLint dependency upgrade plan.
8. Use a separate staging environment with synthetic accounts for progressive load tests (10, 50, 100, 250, 500 and 1,000 concurrent users initially). Measure p50/p95/p99 latency, throughput, 429/5xx rates, Vercel function duration/concurrency, Postgres CPU, connections, locks, cache hit rate and egress. Do not load-test production.

## Official plan references

- Supabase plans and included limits: https://supabase.com/pricing
- Vercel Hobby plan limits and non-commercial restriction: https://vercel.com/docs/plans/hobby
- Vercel plans and usage pricing: https://vercel.com/pricing
- Vercel function region configuration: https://vercel.com/docs/functions/configuring-functions/region
