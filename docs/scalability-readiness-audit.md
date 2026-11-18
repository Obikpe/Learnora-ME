# Learnora ME scalability readiness audit

**Assessment date:** 18 November 2026  
**Scope:** `frontend-v02`, `backend-python`, active Pheonix Supabase project, Vercel production projects.

## Executive finding

The application has a workable serverless foundation, but there is no evidence yet that it can safely support one million active or concurrent users. It has not been load-tested at meaningful concurrency, and its current hosting tiers are not sized or contracted for a million-user workload.

"One million users" must be split into distinct targets:

- **Registered accounts:** total accounts stored.
- **Monthly active users (MAU):** accounts active in a month.
- **Concurrent users:** users making requests at the same time.
- **Peak request rate:** requests per second, which depends on how many requests each active user generates.

A million registered accounts with a small active fraction is a very different system from one million concurrent learners.

## Verified hosting constraints

The connected Supabase organisation is on the **Free** plan. The current published Free allowance includes 50,000 MAUs, a 500 MB database, 5 GB egress, and 200 peak database connections. It is not a one-million-MAU tier. See [Supabase pricing](https://supabase.com/pricing).

The connected Vercel team is on **Hobby**. Vercel documents one million Function Invocations per month in the Hobby allowance, plus 4 CPU-hours and 360 GB-hours of provisioned memory. Those are monthly usage allowances, not a guarantee of one million concurrent users. Hobby runtime-log retention is one hour. See [Vercel Hobby limits](https://vercel.com/docs/plans/hobby) and [Vercel platform limits](https://vercel.com/docs/limits).

The active Supabase database currently occupies approximately **19 MB**. The rate-limit bucket table has 69 rows, 18 older than one day. Current data volume is far too small to establish production-scale query behaviour.

## Production observations

The sampled Supabase edge logs show:

- The rate-limit RPC had an average origin time around 486 ms and a 95th percentile around 1.13 seconds.
- Public course catalogue requests averaged roughly 250 ms at the Supabase edge.
- PostgreSQL `pg_stat_statements` showed the rate-limit function's mean database execution around 3.2 ms. That makes the database function's CPU time an unlikely explanation for the entire edge delay; network/request overhead is material, although the samples are not a controlled benchmark.
- Vercel recorded two backend runtime error groups in the sampled hour, including `httpx.RemoteProtocolError: Server disconnected` while resolving public course track memberships.

The backend's deployed region was **Washington (`iad1`)**, while the Supabase project is in **Paris (`eu-west-3`)**. The repository now configures the backend for Vercel's Paris region (`cdg1`), but the production backend has not received that configuration.

## Changes made in the repository

- The synchronous shared rate-limit RPC is now offloaded from the ASGI event loop to Starlette's thread pool. This prevents the synchronous network wait from blocking unrelated coroutines in the same instance; it does not remove the RPC round trip.
- Learner session heartbeat and dashboard summary refresh intervals were increased from 30 to 60 seconds to reduce background request volume.
- The public course catalogue now calls a single service-role-only Postgres RPC instead of performing several sequential PostgREST requests for courses, organisations, creators and track memberships. The SQL preserves the existing rules: published Learnora global courses, approved/active creators, and organisations that explicitly opt into both public catalogue and public directory visibility.
- The new RPC migration also adds a course-first index to `learnora_learning_path_courses`, which the catalogue membership query filters by `course_id`.
- CI now uses `npm ci`, generates missing lockfiles for review, prints deprecated dependency paths, and is configured not to cancel an in-flight main-branch validation when a newer commit arrives.

**These changes are repository changes, not production changes.** The catalogue RPC migration has not been applied to the live database, and the backend code/Paris region have not been deployed.

## Warnings and dependency decisions

The previous Vercel build log contained real React Hook dependency and unoptimised-image warnings. Those were addressed in the frontend, and the successful GitHub production-check run at commit `1e85fc9` reported no React Hook or `no-img-element` ESLint warnings. The remaining Edge-runtime/static-generation notice is associated with the dynamic Open Graph image route; it is intentional for that route and does not disable static generation across the rest of the site.

The npm deprecation chain is confirmed:

- ESLint 8.57.1 pulls in the deprecated `@humanwhocodes/*` packages and an older `rimraf`/ `glob` chain that includes `inflight`.
- Next.js 14's ESLint plugin pulls in `glob@10.3.10`.
- Removing these safely requires a coordinated Next.js/ESLint major-version migration. Blindly forcing newer transitive `glob` or `rimraf` versions could break the tooling, so no overrides were added.
- The `cache-dir` warning is present in Vercel's install environment but is not defined in the repository's tracked npm configuration or the connected project environment variables. It should be resolved with Vercel/build-environment configuration rather than hidden by suppressing npm warnings.

## Supabase migration release gate

The active database has 51 applied migration versions. The repository has the corresponding SQL sources, but 11 filenames still use older version timestamps even though their SQL bodies match the live ledger. Two repository-only migrations are pending review:

- `20261026153000_revoke_browser_privileges_and_defaults.sql` — security-sensitive privilege revocation; do not apply until service-role function grants and default ACL effects are reviewed.
- `20261118141100_public_course_catalogue_rpc.sql` — additive performance migration; it has a disposable-database CI assertion but has not been applied to production.

Do **not** run `supabase db push` until the 11 version aliases have been reconciled and the pending security migration reviewed. No live schema, data, grants or migration ledger were changed during this audit.

## Production deployment gate

Both `frontend-v02/vercel.json` and `backend-python/vercel.json` explicitly set `git.deploymentEnabled` to `false`. This is why pushes to `main` do not update production automatically. That setting has been preserved; automatic deployment was not silently enabled and no manual deployment was triggered.

The latest code therefore still needs an explicitly authorised release through the existing Vercel release process before production measurements can validate the code-level improvements.

## Controlled load-test plan

A k6 script is provided at `tools/load-tests/public-catalogue.js`. It tests the public catalogue endpoint with a staged ramp of 10, 50, 100, 250, 500 and up to 1,000 virtual users. Remote targets require an explicit opt-in, and production targets require a second explicit opt-in. **It has not been run against production.**

The next test stages should be:

1. Create or identify a non-production environment with a production-like schema, indexes and synthetic accounts/content.
2. Validate 10, 50 and 100 concurrent users; record p50/p95/p99, throughput, error rate, Vercel function duration and Supabase edge/database metrics.
3. Increase to 250, 500 and 1,000 concurrent users only while error rate and latency remain stable.
4. Profile the authenticated learner journey separately (login, dashboard, course open, lesson progress, notifications). The public-catalogue script alone does not validate authenticated workloads.
5. Only after those tests, estimate capacity and cost for the expected MAU, peak concurrency and request rate. One million concurrent users would require a separate architecture and capacity plan, not just larger function limits.

## Current status

- **Code-level performance improvements:** committed; pending full CI verification and release.
- **Public catalogue RPC migration:** committed and covered by disposable-DB assertions; not applied to production.
- **Frontend dependency lockfiles:** CI is generating and validating them; commit job has not yet been confirmed successful.
- **Next.js/ESLint major upgrade:** investigated, not started; requires a controlled migration.
- **Migration filename/version drift:** documented; `supabase db push` remains blocked.
- **Production deployment:** intentionally not triggered.
- **Load testing:** script prepared; no production load generated.
