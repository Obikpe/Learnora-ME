# Learnora Engineering History, Decisions and Open Risks

**Last updated:** 26 October 2026  
**Purpose:** preserve product decisions and the work already carried out so a new engineer can understand the present state without relying on chat history.  
**Scope:** Learnora ME, Learnora Teams, their shared backend, and Supabase schema/migration work.  
**Branch rule for the current documentation task:** all three new engineering documents are committed to `main`; no alternate branch is to be used for this documentation work.

This is an evidence register, not a claim that every historic issue is resolved. Historical CI links are tied to the exact SHA/run described and must not be treated as evidence for current `main` unless the SHA matches.

## 1. Product and repository decisions

### 1.1 Application ownership

- Learnora ME customer-facing frontend is `frontend-v02/`.
- Learnora Teams internal workforce/Super Admin frontend is `frontend-team/`.
- Legacy `frontend/` is not the target for new ME work.
- Shared backend is `backend-python/` (FastAPI).
- Supabase SQL source and schema assets are under `supabase/`.
- Customer organisation workflows belong to Learnora ME; internal platform staff operations belong to Teams.
- Reuse existing schema entities where possible; avoid parallel tables for the same domain.
- Keep product claims grounded in real records and label unverified skill evidence clearly.

### 1.2 Organisation/cohort invariants recorded

The organisation data-model plan documents the following requirements and implementation decisions:

- Reuse `organisations`, `organisation_members`, `organisation_teams`, `organisation_team_members`, `cohorts`, `cohort_members`, programme/course assignment structures, contract/entitlement structures and AI usage/limit structures.
- Add/maintain an explicit team-course assignment relationship; do not treat a team assignment as a cohort assignment.
- Validate active team/cohort membership and organisation scope before creating enrolments.
- Prevent cross-tenant team membership, stale membership reuse, and assignment to unpublished/ineligible courses.
- Distinguish `course_access.access_type = 'assigned'` (explicit organisation-wide access) from `'scoped'` (access record supporting individual/team/cohort assignment). Scoped records must not be interpreted as organisation-wide grants.
- Require current active learner membership plus the correct individual/team/cohort assignment for scoped course access.
- Avoid duplicate enrolment checks across unrelated tenants.
- Cohort-specific track does not change mid-cohort.
- On cohort closure, deactivate the cohort-specific access and relevant active state while retaining the user record for reference/statistics.
- Capacity and AI quota need atomic reservation rather than Python-only read-then-write checks.
- Database-side tenant integrity is needed because application-only validation does not protect future alternate write paths.

The source plan is `backend-python/migrations/STEP_4_ORGANISATION_DATA_MODEL_PLAN.md`; it contains design rationale and older point-in-time state that should be revalidated against main/live catalogs.

## 2. Work and verification recorded so far

### 2.1 Product, frontend and release work

The repository history records earlier PRs for platform foundations, public Learnora ME experience, course flows/metadata, organisation onboarding, and frontend/backend hardening. The GitHub PR listing inspected on 26 October reported:
- PR #1 platform foundations and learner/organisation onboarding — merged 10 October.
- PR #3 Learnora ME release and Teams/backend hardening — merged 20 October.
- PRs #5 and #6 follow-up polish/course metadata — merged 20 October.
- PRs #7 and #8 audit/cohort work — GitHub reports merged 21 October.
- PRs #9 and #10 integration of audit hardening with cohort lifecycle — GitHub reports merged 21 October.

These PR statuses establish that the PRs were merged, not that every original branch change remains present or that all release checks are currently green. Recheck `main` and rerun the relevant tests when acting on a finding.

The UI/UX research decision record (`docs/learnora-ui-ux-research.md`) specifies dark graphite surfaces, warm gold accent, generous whitespace, deliberate typography, the existing navigation, page-specific layouts, responsive/accessibility requirements, real data, and complete empty/loading/error/permission states. It records that Figma/Mobbin MCP connections were unavailable during that research; do not claim those tools were used.

### 2.2 Organisation schema planning and applied migration notes

The organisation data model plan says the user explicitly requested applying the migration work to the active Pheonix Supabase project on 20 October. The notes record a transactional dry run/rollback, then migration application and post-migration checks for versions `20261020230826` and `20261020230906`. The active project reference in those notes is `gihfupzvdpyrmynqgukz`.

The plan also records that team-course assignments were added, tenant relationship validation was strengthened, and course-access scope was separated into organisation-wide and scoped grants. The exact active database state must be checked through current catalogs; a note that a migration was applied is not a substitute for verifying current grants, RLS, policies and object definitions.

### 2.3 Cohort workflow and CI design

A revised cohort workflow was built around two separate disposable PostgreSQL contexts:
- A catalog-derived current-schema snapshot is restored for current authenticated FastAPI/PostgREST cohort API acceptance.
- The legacy migration chain is replayed separately for historical analysis, seed checks and a report-only schema fingerprint.
- The legacy replay is not treated as the current API acceptance schema.
- The workflow is disposable and should not require production data or mutate the active Supabase project.
- The comparison is non-blocking historical reporting, not a parity claim.

The historical run reported successful completion for Cohort Learning Access Tests at [run 39676949757](https://github.com/Obikpe/Pheonix-Analytics/actions/runs/39676949757). Backend verification was reported successful at [run 39676949661](https://github.com/Obikpe/Pheonix-Analytics/actions/runs/39676949661), and frontend builds at [run 39676949219](https://github.com/Obikpe/Pheonix-Analytics/actions/runs/39676949219). Learnora quality checks were cancelled at [run 39676949150](https://github.com/Obikpe/Pheonix-Analytics/actions/runs/39676949150). These runs belong to a prior candidate SHA and are historical evidence, not proof that the current main SHA passes.

A quality-workflow concurrency setting was changed on a prior branch to avoid cancelling in-progress checks, but that branch change must not be assumed present in main. Verify the current `.github/workflows/learnora-quality.yml` and ensure the next main run finishes with conclusion `success`.

## 3. Security findings register

The findings below were raised in the security review. Status means **status at the time this record was assembled**; unless a current-main test or live verification is cited, the item remains open/needs revalidation.

### High severity

#### H1 — Browser roles have broad table grants

Finding: a grant-restoration migration, `20261020230906`, restored `ALL PRIVILEGES` for `anon` and `authenticated` on a group of public tables. A locked-down test baseline could hide this if the replayed schema is not tested for grants. RLS with no policies currently blocks ordinary direct row access in the observed configuration, but relying on that alone is brittle.

Read-only live inspection performed during this session returned:
- `anon`: table grants on 53 distinct public tables, 371 privilege rows.
- `authenticated`: table grants on 53 distinct public tables, 371 privilege rows.
- `pg_default_acl` showed public-schema default table privileges for both `postgres` and `supabase_admin` including `anon` and `authenticated`; default sequence/function ACLs also included browser roles.

This confirms broad grant/default-ACL exposure exists in the inspected project, but it does not by itself establish that all 53 tables are exploitable or should be revoked. Perform a table-by-table client/use-case inventory. Verify the exact owners that create tables and sequences. Do not execute a blanket production revoke without approval, disposable replay tests, and an exact rollback.

#### H2 — CI schema fixture does not model the grant posture being reviewed

Finding: the catalog-derived baseline can be more locked down than the actual/replayed schema. A green API journey against the baseline is insufficient evidence for grant cleanup.

Required fix: test explicit grant assertions against the replayed chain and against the schema to which the grant migration is applied; preserve legitimate public reads via an explicit allowlist. CI should fail when prohibited grants/default privileges return.

#### H3 — Audit and cohort changes previously diverged

Finding: audit/security work and cohort work were developed on separate branches. PR metadata later showed PRs #7–#10 merged to main on 21 October, including integration PRs. This reduces but does not eliminate the risk: compare every finding and its regression test to current main, because merged PR metadata is not proof of complete integration.

Required fix: maintain one reviewed main baseline; confirm course-content guards, atomic AI quota, module unlock checks, team membership guards, cohort lifecycle and their tests are present.

#### H4 — Cohort login wildcard matching

Finding: username `ilike` patterns could treat `%` and `_` as wildcards, potentially matching another account while varying rate-limit keys.

Required fix: exact equality, strict username allowlist (generated lowercase format), generic auth failure, dummy-hash verification for unknown users, per-IP plus per-username throttling, and regression tests for wildcard names and lockout.

#### H5 — In-memory rate limits are not shared

Finding: both custom failure counters and SlowAPI in-memory state reset per serverless process/instance. Rotating usernames or reaching another instance can evade a per-process counter.

Required fix: use a shared durable store for production rate limits, define expiry/atomic increments, and test across multiple app instances. The username/IP change is only partial mitigation until shared storage exists.

#### H6 — Trust in forwarded client IP

Finding: selecting the leftmost `X-Forwarded-For` value is safe only if the trusted edge overwrites/sanitises the header.

Required fix: verify actual Vercel/proxy behaviour and configure trusted proxy handling explicitly; do not assume an unverified header is authoritative.

### Medium severity

#### M1 — Browser token storage and missing security headers

Finding: review observed `phx_token` in localStorage with a 24-hour lifetime and no configured CSP/security headers. This conflicts with older documentation describing HttpOnly JWT sessions.

Required fix: inspect current main and choose one explicit session model; prefer HttpOnly Secure cookies with a CSRF strategy if compatible with the deployed architecture. Add CSP and other security headers with tests.

#### M2 — Date of birth privacy and account enumeration

Finding: cohort DOB was stored in plaintext and returned to the organisation. Unknown usernames could skip password hash verification and create timing differences.

Required fix: minimise DOB exposure; justify role access, protect retained values and set retention rules. Implement dummy-hash verification and generic responses.

#### M3 — Payout and ledger consistency / separation of duties

Finding: payout status and ledger insert were separate operations, potentially leaving a paid payout without a ledger entry. A shared user-update permission could also permit both account edits and payouts.

Required fix: execute payout state transition plus ledger write atomically (transaction/RPC), use idempotency, test ledger failure, and split permissions.

#### M4 — Instructor grading scope and audit trail

Finding: an instructor may be able to read/grade all submissions in an organisation rather than only authorised course submissions; grade edits may be repeated without an audit event.

Required fix: require course/instructor assignment at each endpoint; define grade revision rules and write an audit event for each change.

#### M5 — CORS, public API docs

Finding: preview-origin matching was broad and allowed credentials; `/docs` and `/redoc` were publicly reachable in production.

Required fix: exact allowlist of trusted origins, safe credential policy, protect or disable API documentation in production, and verify with deployment-level tests.

#### M6 — Migration source provenance

Finding: `20261008100924_add_learnora_ai_profiles.sql` and `20261011051442_learner_onboarding_profiles.sql` were reconstructed from the live catalog rather than verified originals. Five 20 October timestamped files were not independently verified against original history.

Required fix: search trusted archives/commit history/deployment artefacts, compare object definitions and seed values, and label each source as original/reconstructed/unverified/superseded. Do not fabricate historical ledger entries.

### Low severity

- `validate_cohort_member_*` functions use `search_path = public` instead of an empty/pinned path.
- `update_admins_updated_at` has no pinned search path.
- Activation tokens travel in URL query strings.
- `/api/ready` is unauthenticated; review its response for information leakage.
- A PostgREST `.or_()` filter interpolates organisation ID. A scope check was reported, but parameterisation/escaping is safer, especially for platform-admin paths.

### Positive controls recorded by the review

The review reported no real keys in branch history (only CI test values), new SECURITY DEFINER functions revoking execute from PUBLIC/anon/authenticated, consistent organisation scope checks in organisation routes, hashed single-use activation tokens, and cohort accounts being rechecked against the database on each request. Revalidate these controls against current main after relevant changes.

## 4. Schema and migration provenance register

### 4.1 Active versus legacy

- Active timestamped migration files belong in `supabase/migrations/` according to the current repository workflow.
- Historical numbered migrations 001–015 are preserved under `supabase/legacy_migrations/` for analysis; they must not be treated as pending active migrations.
- The catalog-derived snapshot is a disposable fixture for current-schema API acceptance, not proof that the historical migration chain can recreate production.
- Schema comparison is diagnostic and must not automatically drop/remap data.

### 4.2 Provenance gaps

Files previously identified as reconstructed from catalog:
- `20261008100924_add_learnora_ai_profiles.sql`
- `20261011051442_learner_onboarding_profiles.sql`

Five timestamped SQL files dated 20 October were reported to replay but not independently verified against original source history:
- `20261020230826_learnora_audit_remediation.sql`
- `20261020230906_restore_shared_learner_grants_and_lock_trigger_routines.sql`
- `20261020232148_allow_unlimited_monthly_ai_quota.sql`
- `20261020234717_pin_shared_timestamp_trigger_search_path.sql`
- `20261020234813_revoke_browser_grants_from_org_control_tables.sql`

Do not label these five as verified originals unless provenance evidence is later found. The active migration ledger version/name inventory matching repository files is necessary but not sufficient to prove original execution history.

### 4.3 Historical schema/data differences

Earlier reports recorded differences between the live catalog and replayed chain: columns, constraints, indexes, triggers, RLS states, policies and a view. Counts differ across historical reports and snapshots, so do not copy a count forward as current truth without a pinned schema snapshot and repeatable diff.

Legacy tables absent from the inspected current schema included `tracks`, `enrollments`, `user_progress`, `user_project_progress`, and `community_qna`; newer Learnora tables appear to replace some concepts. Names alone do not prove a safe one-to-one mapping.

The prior read-only data-lineage checks found a Witstart identity/membership mismatch despite equal aggregate counts: one legacy-role user lacked the expected organisation/cohort membership, while one membership in each set belonged to a user outside the legacy role. No automatic repair was performed. Resolve using explicit identity evidence, not aggregate counts.

Seed checks found `ai.view` and `ai.manage` keys and a global wildcard AI-limit row, but complete role-to-permission mapping and quota key/value equivalence were not proven.

## 5. Decisions and safety boundaries

1. Use the catalog-derived snapshot for disposable current-schema staging; preserve the old chain for historical analysis.
2. Do not automatically drop, rename, merge, or remap legacy data.
3. Do not run production SQL merely to make CI green.
4. Do not insert synthetic migration-ledger rows to make history appear contiguous.
5. Do not merge/deploy a security migration without staging tests, reviewed exact grants, and rollback.
6. Do not call a cancelled workflow a pass.
7. Keep real secrets out of source control and browser bundles.
8. The active Pheonix project reference in notes is not proof of the deployed backend target.
9. All findings should be rechecked against current `main`, because old branch/run results can be stale.
10. For the current documentation request, commits are made to `main` only.

## 6. Immediate next actions

1. Verify current `main` head and the three new documentation files.
2. Run or inspect the full CI set on that exact main SHA.
3. Compare the current-main login implementation and tests against H4.
4. Complete read-only table/default-grant inventory and client dependency review before proposing a migration.
5. Add negative grant assertions to disposable CI and test the intended post-revocation API journey.
6. Resolve provenance and seed/identity differences through evidence-backed reports.
7. Address payout atomicity, grading scope, session storage, CORS/docs exposure, privacy and distributed rate limiting.
8. Update `docs/ROADMAP.md` and this log only when each item has code/test evidence and a commit SHA.

## 7. Updating this document

Append entries using:

```markdown
### YYYY-MM-DD — concise action
- Commit (main): `<sha>`
- Scope: <files/behaviour>
- Verification: <test command or CI URL and conclusion>
- Database/deployment impact: <disposable/read-only/approved live action>
- Result: <observed result>
- Remaining risks: <explicit list>
```


## 8. 2026-10-26 — Product engineering documentation created on main

- **Branch:** `main` only. No branch was created or checked out for this documentation task.
- **Product engineering specification:** [`docs/PRODUCT_ENGINEERING_SPEC.md`](PRODUCT_ENGINEERING_SPEC.md), created in commit `4a51d42bcd89a7137cfed9aee2b61f3f636b1375`.
- **Roadmap:** [`docs/ROADMAP.md`](ROADMAP.md), created in commit `e66cb30270d792aaddf11e5b98afa5fa2e9d9727`.
- **Engineering history/decision register:** this file was created in commit `ff8f933b3075a4fcb30011d6bfc231be749b08f6`.
- **Repository entry point:** `README.md` links all three documents and the existing UX/migration records; updated in commit `b25e9b7443e5854cfec82a68ff50dcd5128cb11a`.
- **Scope recorded:** application ownership and architecture; Learnora ME and Teams user groups/workflows; organisation/team/cohort/course access invariants; local setup; CI/release gates; security findings; migration provenance; schema/identity lineage; roadmap priorities and acceptance criteria.
- **Verification:** GitHub main branch and recursive tree were queried after the writes. All three new Markdown files and the README are present on main; main head at verification was `b25e9b7443e5854cfec82a68ff50dcd5128cb11a`.
- **Tests:** no application code or SQL was changed in this documentation task. No new workflow run for the documentation commits was visible at verification time; previously successful CI runs are historical and are not represented as tests of this documentation commit.
- **Production impact:** no Supabase migration, data mutation, or deployment was performed.
- **Remaining work:** implement and verify the P0–P6 roadmap. Documentation records the known risks but does not fix the underlying security/schema issues.


## 9. 2026-10-26 — first remediation batch and CI evidence

- **Branch:** direct commits to `main`; no branch was created or checked out.
- **Repository identity:** the GitHub repository is now addressed canonically as `Obikpe/Learnora-ME`; it is the same repository previously referenced as `Obikpe/Pheonix-Analytics`.
- **Local development:** root scripts now target `frontend-v02/`, `frontend-team/`, and `backend-python/`. README and `HOW_TO_RUN.md` were corrected. Development frontend defaults now use localhost rather than sending local work to the production API; `backend-python/.env.example` defaults to development and localhost origins.
- **Authentication and finance:** email account lookups escape LIKE metacharacters; unknown-account login performs dummy bcrypt verification; disabled admin status is checked after password verification; new verification/reset tokens use URL fragments and the UI retains compatibility with old query-string links; Learnora ME bearer tokens are session-scoped and legacy persistent tokens are cleared. Client IP headers are trusted only when the backend is running on Vercel. Creator sales record/release/refund operations now require the existing `creator_payouts.process` permission (or super-admin bypass) because `courses.assign` was too broad. These are mitigations, not the final HttpOnly-cookie or atomic-finance design.
- **API disclosure:** readiness responses no longer disclose internal configuration/database checks. Course-content and video-upload errors return generic client messages and log only exception types.
- **CI reliability:** backend, frontend, cohort and quality workflows now trigger together for code/migration/workflow changes. The quality concurrency key includes the commit SHA so a newer push cannot cancel the evidence for an earlier candidate.
- **Verification candidate:** `92c3900e5186a0e05fa8f2010a05716320412a48`.
  - [Backend regression tests](https://github.com/Obikpe/Learnora-ME/actions/runs/40416347429) — success.
  - [Backend verification](https://github.com/Obikpe/Learnora-ME/actions/runs/40416347467) — success.
  - [Frontend builds](https://github.com/Obikpe/Learnora-ME/actions/runs/40416347428) — success for Learnora ME and Learnora Teams.
  - [Cohort-learning access tests](https://github.com/Obikpe/Learnora-ME/actions/runs/40416347453) — success.
  - [Quality checks](https://github.com/Obikpe/Learnora-ME/actions/runs/40416347457) — success.
- **Production impact:** a read-only Vercel deployment lookup returned no deployment for this commit. No production deployment or Supabase mutation was performed.
- **Remaining release blockers:** HttpOnly-cookie sessions; shared production authentication/API rate limiting; creator sales permission separation and atomic sale/refund writes; managed `supabase_admin` default ACL remediation by an authorised operator; historical migration provenance and identity-lineage reconciliation; and complete browser-driven acceptance across both applications.


## 10. 2026-10-26 — HttpOnly browser sessions and finance permission containment

- **Source candidate:** `5ef2cc1193bf2b87106c276edd42181726243b82`.
- **Browser auth:** Learnora ME, cohort login, and Learnora Teams now issue HttpOnly cookies for trusted browser origins. Cookies use `SameSite=Lax`, `Secure` in production, root path, and the configured token lifetime. Browser login payloads omit JWTs; clients keep only a non-secret `cookie-session` marker and use same-origin `/api` rewrites. Non-browser clients without an Origin header retain bearer-token responses for compatibility.
- **Session handling:** both frontends clear legacy localStorage JWTs; old JWTs found in sessionStorage are discarded. Logout expires the correct cookie. Learnora ME cache keys use a per-login session epoch and a logout marker to prevent stale cached users from resurfacing after logout/re-login.
- **Proxy configuration:** each frontend's `next.config.mjs` proxies `/api/:path*` to `API_PROXY_TARGET`; development defaults to `http://localhost:8000`, production defaults to `https://learnora-backend.vercel.app`. Cookie auth requires backend and frontend deployments to move together.
- **Finance authorization:** creator sale record/release/refund routes use the existing `creator_payouts.process` permission (or the existing super-admin bypass), not the broad `courses.assign` permission. Dedicated creator-sales permissions and atomic sale/refund writes are still pending.
- **Verification on the exact source SHA:**
  - [Backend regression tests](https://github.com/Obikpe/Learnora-ME/actions/runs/40418508267) — success.
  - [Backend verification](https://github.com/Obikpe/Learnora-ME/actions/runs/40418508234) — success.
  - [Frontend builds](https://github.com/Obikpe/Learnora-ME/actions/runs/40418508351) — success for both applications.
  - [Cohort-learning access tests](https://github.com/Obikpe/Learnora-ME/actions/runs/40418508220) — success.
  - [Quality checks](https://github.com/Obikpe/Learnora-ME/actions/runs/40418508224) — success.
- **Deployment status:** read-only Vercel lookup returned no deployment for this SHA. No production deployment or Supabase mutation was performed.
- **Remaining release blockers:** shared production auth/API rate limiting; atomic creator sale/refund and payout-request writes; dedicated creator-sales permissions; managed `supabase_admin` default ACL remediation by an authorised operator; migration source provenance and identity-lineage reconciliation; complete browser-driven acceptance; and a coordinated staging/production rollout of the cookie-auth source.
