# Learnora Engineering History, Decisions and Open Risks

**Last updated:** 21 November 2026  
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

- **Source candidate:** `0cc35c58913ed198e7a9f2c15f91203b398b8221`.
- **Browser auth:** Learnora ME, cohort login, and Learnora Teams now issue HttpOnly cookies for trusted browser origins. Cookies use `SameSite=Lax`, `Secure` in production, root path, and the configured token lifetime. Browser login payloads omit JWTs; clients keep only a non-secret `cookie-session` marker and use same-origin `/api` rewrites. Non-browser clients without an Origin header retain bearer-token responses for compatibility.
- **Session handling:** both frontends clear legacy localStorage JWTs; old JWTs found in sessionStorage are discarded. Logout expires the correct cookie. Learnora ME cache keys use a per-login session epoch and a logout marker to prevent stale cached users from resurfacing after logout/re-login. The global API limiter and auth failure buckets use `X-Real-IP` only behind the Vercel edge, with IP validation and peer-address fallback.
- **Proxy configuration:** each frontend's `next.config.mjs` proxies `/api/:path*` to `API_PROXY_TARGET`; development defaults to `http://localhost:8000`, production defaults to `https://learnora-backend.vercel.app`. Cookie auth requires backend and frontend deployments to move together.
- **Finance authorization:** creator sale record/release/refund routes use the existing `creator_payouts.process` permission (or the existing super-admin bypass), not the broad `courses.assign` permission. Dedicated creator-sales permissions and atomic sale/refund writes are still pending.
- **Verification on the exact source SHA:**
  - [Backend regression tests](https://github.com/Obikpe/Learnora-ME/actions/runs/40418907118) — success.
  - [Backend verification](https://github.com/Obikpe/Learnora-ME/actions/runs/40418907031) — success.
  - [Frontend builds](https://github.com/Obikpe/Learnora-ME/actions/runs/40418907067) — success for both applications.
  - [Cohort-learning access tests](https://github.com/Obikpe/Learnora-ME/actions/runs/40418907010) — success.
  - [Quality checks](https://github.com/Obikpe/Learnora-ME/actions/runs/40418907269) — success.
- **Deployment status:** read-only Vercel lookup returned no deployment for this SHA. No production deployment or Supabase mutation was performed.
- **Remaining release blockers:** shared production auth/API rate limiting; atomic creator sale/refund and payout-request writes; dedicated creator-sales permissions; managed `supabase_admin` default ACL remediation by an authorised operator; migration source provenance and identity-lineage reconciliation; complete browser-driven acceptance; and a coordinated staging/production rollout of the cookie-auth source.


## 11. 2026-10-31 — staged free launch before paid expansion

- **Decision source:** product-owner direction confirmed on 31 October 2026.
- **Plan document:** [Free Launch → Paid Expansion Plan](FREE_LAUNCH_AND_PAID_EXPANSION_PLAN.md). This is an additive strategy document; the original product specification, roadmap phases, security findings, organisation/cohort plans, instructor/creator plans, and billing history are retained.
- **Product sequence:** temporarily free individual learner access first; complete Learnora Teams content operations and the Learnora ME learner journey; add optional post-track ratings/reviews with consent and moderation; then return to organisation/instructor work and later paid courses/Pro.
- **Applications:** Learnora ME remains frontend-v02/; Learnora Teams remains frontend-team/; shared FastAPI remains backend-python/. Legacy frontend/ is not the current implementation target.
- **Database clarification:** the product owner confirmed Learnora continues to use the already-active Pheonix Supabase project. Do not create or switch to a separate Learnora Supabase project. Existing engineering records identify project reference gihfupzvdpyrmynqgukz; confirm configured project identity through safe metadata before database operations and never expose credentials.
- **Free-mode design decision:** implement a central, reversible, server-enforced mode. It must remove payment-method, checkout, paid-subscription and trial-expiry barriers for the intended individual learner journey while preserving payment/Paystack, subscription, trial, expiry, entitlement and Pro code/data. Disabling free mode must restore the original paid enforcement. Do not rewrite historical subscription records or weaken authentication, staff permissions, tenant boundaries, RLS or private-media controls.
- **Teams scope:** track and ordered track-course management; course creation/editing/publishing; modules/lessons; video and resource uploads; learner information/progress; reliable platform statistics.
- **Learner scope:** public discovery, track/course enrolment, lesson/media access, supported activities, progress/resume, and backend-confirmed completion.
- **Feedback scope:** after backend-confirmed track completion, offer an optional dismissible 1–5 rating and comment. Public display requires separate consent and moderation. Do not promise Google rich-result stars for self-serving reviews.
- **Deferred, not cancelled:** organisation, cohort, instructor/tutor/creator, creator sales/payouts, contracts/entitlements, and paid/Pro services remain in the original plan and existing code/schema. Their implementation is sequenced later; no deletion or security-boundary weakening is authorised.
- **Documentation commits on main:**
  - Additive strategy document: commit 1de61620a770fb6a025c230f179cc0ca09d48d45.
  - Roadmap sequencing addendum: commit 02ee18490eea998317b2b6ea10da5a141761c8ba.
  - Product specification addendum: commit 9f292e088b8f51c991330e2a454512e6a5f08419.
- **Verification and impact:** documentation-only changes. No application code, SQL migration, Supabase data, or deployment was changed by these commits. No CI result is claimed for these documentation commits.
- **Next action:** begin implementation with a read-only baseline check of main, the configured active Pheonix Supabase target, current track/course schema, and billing/access enforcement; then implement and test the reversible free-access mode before moving to Teams content workflows.


## 12. 2026-10-31 — first free-launch and Teams oversight implementation

- **Scope:** learner access enforcement, learner-facing free-launch presentation, internal individual-learner oversight and first platform analytics. Work was committed directly to `main`; no branch was created.
- **Free mode:** added `backend-python/services/free_access.py` with the server-only `FREE_ACCESS_MODE` switch (default false) and individual learner eligibility helper. Eligible accounts are verified role-`normal` learners only. Witstart/organisation learners, cohort identities, prospects, creator accounts, staff, administrators, unverified accounts and inactive accounts do not receive this free grant.
- **Access enforcement:** integrated the reversible mode into learner entitlement resolution, the central course access resolver, course-content authorization and self-enrolment. Free access is limited to published, global Learnora-owned catalogue courses with no organisation scope. Existing paid/trial rows are not rewritten; the ordinary expiry and paid checks remain the fallback when the flag is off.
- **Learner UI:** exposed a non-sensitive public access-mode endpoint; updated catalogue course labels, course-detail enrolment copy, subscription status view and learner navigation. Email verification messaging now distinguishes the free launch from the existing seven-day trial. Email verification itself remains required.
- **Teams:** added internal permission-protected individual learner list/detail APIs, a platform analytics API, and Teams learner/analytics pages. Metrics document their definitions; active learners are currently derived from a 10,000-row recent-progress sample and explicitly report when capped.
- **Tests:** added `test_free_access_mode.py` and `test_internal_learner_operations.py`, covering free-mode eligibility, paid-mode fallback, inactive and organisation boundaries, course ownership/publication constraints, learner list/detail summaries and analytics counts. These tests are committed but are not claimed as passed because CI did not execute them.
- **Schema finding:** the checked-in Pheonix baseline contains `learnora_tracks`, but its `cohort_track_courses` relation requires a cohort. The separate `learnora_learning_paths` model was not repurposed. A global track/course relation is missing from the baseline; a dedicated migration and test fixture are required before building public track enrolment/completion. The current `learnora_feedback` structure also lacks track linkage, consent and moderation state for public reviews.
- **Supabase target:** safe project metadata confirms active project Pheonix, ref `gihfupzvdpyrmynqgukz`, status `ACTIVE_HEALTHY`. Live SQL introspection was blocked by read-only database-user password authentication. No SQL migration was created/applied and no production data was changed.
- **CI evidence:** GitHub Actions jobs on these commits completed as failures before runner assignment (empty runner name, zero steps); job logs were unavailable. No passing CI or local test run is claimed. The CI runner/account configuration must be restored before the suite can provide acceptance evidence.
- **Deployment:** none. `FREE_ACCESS_MODE` remains false by default and has not been set in Vercel or another production runtime. The implementation is not live until configuration and deployment are separately authorised.
- **Remaining immediate work:** resolve CI runner availability; verify live schema through a working read-only connection; create and test the general track/course relationship under the approved migration workflow; implement Teams track management and learner track enrolment; finish the learner discovery/resume/completion journey; implement track completion and optional consented/moderated reviews; run full browser and regression acceptance before requesting release approval.



### Track MVP implementation addendum — 2026-10-31

- **Schema reuse decision:** global learner tracks use `learnora_learning_paths` with `owner_user_id IS NULL` and `organisation_id IS NULL`, plus the existing ordered `learnora_learning_path_courses` relation. This is the generic course-sequence model in the checked-in baseline. The cohort-specific `learnora_tracks` / `cohort_track_courses` model is left untouched. Personal and organisation paths remain scoped by their existing non-NULL owner/organisation fields.
- **Teams:** added a permission-protected global track API and a Teams editor for creating, editing, ordering, publishing, unpublishing and archiving tracks. Tracks only accept global Learnora-owned courses. Publishing requires at least one required course and published modules/lessons. Published curriculum cannot be modified until the track is unpublished; linked courses cannot be unpublished/archived while used by a published global track.
- **Learner app:** added public track discovery/detail pages, track navigation, individual learner track enrolment (creates ordinary course enrolments), and backend-derived track progress/completion from required course completion. The sign-in flow now safely returns an individual learner to the requested track route after authentication.
- **Progress correctness:** course and module completion/unlock calculations now count learner-visible published modules and lessons rather than draft/archived content.
- **Reviews:** not implemented yet. The existing feedback table has no track foreign key, separate public-consent field or moderation state; do not encode track IDs into unrelated columns. A dedicated schema change is still required before review collection/public display.
- **Migration status:** no migration was required for the global track MVP according to the checked-in baseline, but live SQL schema introspection remains blocked. No database change was applied.


- **Review preparation:** added `docs/TRACK_REVIEW_SCHEMA_PROPOSAL.md` defining a dedicated track-linked review record, explicit opt-in public consent, moderation status/audit, privacy rules and regression tests. This is a proposal only; no migration/table or public review endpoint exists yet.

- **Track continuity hardening:** track curriculum is frozen once any linked course has active/completed learner enrolments. Unpublished/archived tracks disappear from public discovery and new enrolment, but the authenticated progress endpoint still serves the saved track to learners with required-course enrolments. Analytics now counts only global Learnora courses and reports published global tracks.

### Release verification record — 2026-10-31

- Main HEAD was `41735ba6cdedcc810420693a0cd77aa4d6ce48da` at the verification check. The five workflows triggered for that SHA failed before running any steps (zero steps; runner name blank), so CI has not executed the new tests or frontend builds.
- Vercel Git deployments are disabled in repository configuration; the latest Learnora ME deployment predates the current code. No deployment was made. The backend Vercel project still references the older `Pheonix-Analytics` repository, unlike the learner frontend project linked to `Learnora-ME`; this must be reconciled before release.
- `FREE_ACCESS_MODE` remains off by default and was not set in Vercel. No production environment change, database migration/data mutation, or deployment was performed. Live Pheonix SQL schema verification remains blocked by the read-only connection authentication failure.


### Free launch and track hardening — 2026-11-01

- Organisation membership is resolved before free-launch entitlement calculation. Active organisation members do not inherit the individual free grant. Membership lookup errors fail closed when free mode is enabled.
- Global track enrolments use a track-specific `source_type` marker. Curriculum locking and unpublished-track progress visibility use that marker, preventing unrelated course enrolments from freezing or exposing a track.
- Track enrolment only considers global individual enrolments, reactivates withdrawn rows, and refuses invited/suspended rows. Track curriculum controls reject archived tracks at the API layer.
- Archived-course progress summaries include historical module/lesson rows but still execute the module assessment-lock check.
- Tests were added for free-access organisation boundaries, public catalogue labelling, track enrolment lifecycle, independent course enrolments, archived track visibility and module locks. GitHub Actions jobs currently fail before executing steps and provide no logs; these tests remain unverified. Live Pheonix schema verification failed due read-only DB authentication. No production migration, environment change or deployment occurred.



### Learner journey phases 1–5 implementation — 2026-11-02

- **Implementation checkpoint:** `5e6527009fb07e160696869e0864ceb207fd9310` on `main`. Documentation-only commits follow this code checkpoint; no production release was made.
- **Phase 1 — architecture:** retained the checked-in generic global track model `learnora_learning_paths` → `learnora_learning_path_courses` → `learnora_courses` → `course_modules` → `learnora_lessons`. Cohort-specific `learnora_tracks` / `cohort_track_courses` remain untouched. Existing quiz/assignment tables were reused. No competing curriculum model was introduced.
- **Phase 2 — discovery:** `public_directory.py` now returns published global track memberships on public course payloads. Learnora ME course filtering uses those relationships; the track browser supports search and course-level filters.
- **Phase 3 — optional AI plan:** added `backend-python/routers/learning_plans.py`, learner plan workspace and dashboard entry. Plans use saved onboarding preferences and actual published catalogue course IDs. Weekly allocations are calculated from estimated course hours; AI generates validated weekly focus/practice/reflection guidance. Invalid/unavailable AI output falls back to explicit rule-based guidance. Plans are stored separately from curriculum. Added `learner_learning_plans` migration and rollback; neither has been applied to the active Pheonix project. The plan API must not be deployed before the migration is replayed and verified in disposable/staging.
- **Phase 4 — assessments:** added internal assessment APIs and Teams workspace for quiz settings/question editing, assignment creation/editing (lesson association, instructions, due date and max score), multiple-choice and true/false validation, publication controls, assignment grading and course learner performance. Course progress/completion includes published quizzes and assignments alongside published lessons. Quiz attempts use each configured threshold; latest assignment submissions must be graded at 70% or higher of max score. Module unlocking respects quiz thresholds and does not deadlock on modules without quizzes. Unpublished drafts do not block completion. Course/track publication checks reject incomplete auto-graded quizzes.
- **Phase 5 — contextual tutor:** learner course player hands off course, lesson and optional quiz identifiers. Backend validates enrolment, lesson/course membership, publication, module unlock and quiz-to-lesson/module scope; it loads lesson content, saved progress, recent quiz attempts and assignment feedback, never answer keys. Course content and feedback are treated as untrusted reference data. Contextual handoffs use a fresh tutor conversation.
- **Teams scope:** existing track, course, module, lesson, resource/video upload and publishing workflows were retained. New assessment navigation and performance views extend Teams rather than replacing its content manager.
- **Free-launch protection:** no change to `FREE_ACCESS_MODE`, Paystack, checkout, subscription, trial, expiry, entitlement, Pro or payment-history logic. The central free flag remains default-off. No payment requirement was added to the learner journey.
- **Tests added/updated:** `test_internal_assessments.py`, `test_learning_plans.py`, `test_learner_onboarding.py`, `test_course_assessment_completion.py`, and `test_public_track_progress.py`; publication fixtures/readiness and subscription-contract fixtures were updated. Backend regression tests, backend verification, all three frontend builds, quality checks, and cohort/disposable migration tests passed on checkpoint `8e21f264744a1a49d26d0f81b3272f1c5d72f24a`.
- **CI evidence at the checkpoint:** all five workflows were queued, not completed. [Backend regression tests](https://github.com/Obikpe/Learnora-ME/actions/runs/41416399989), [backend verification](https://github.com/Obikpe/Learnora-ME/actions/runs/41416400119), [frontend builds](https://github.com/Obikpe/Learnora-ME/actions/runs/41416399968), [quality checks](https://github.com/Obikpe/Learnora-ME/actions/runs/41416400031), and [cohort-learning tests](https://github.com/Obikpe/Learnora-ME/actions/runs/41416400015). Queued is not a pass; no CI success is claimed.
- **Database and deployment:** schema decisions were checked against the repository baseline, not live SQL. The additive plan migration remains unapplied. No production data change, environment-variable change, Vercel deployment or production migration was performed.
- **Remaining acceptance gates:** live Pheonix schema revalidation (read-only DB authentication failure), browser/mobile acceptance for discovery, plan generation/fallback, assessment grading/completion and contextual tutor, provider/fallback behaviour, and separately approved live migration/deployment. The in-place Teams question/assignment editors are implemented. Each staff grading action is logged in `audit_logs`; immutable grade-revision history and learner resubmission remain future work. The five phases are implementation-complete and automated-CI-verified, but are **not production-release verified**.


### Quiz tutor restriction and next milestone — 2026-11-02

- **Product/security decision:** the AI tutor must never be visible or accessible during an active quiz attempt. Hide the launcher and chat surface and block alternate keyboard/accessibility entry points and contextual handoffs for answering, question navigation, review and submission. Backend tutor requests associated with an active quiz attempt must also be denied; do not rely on the tutor prompt or answer-key omission alone. Tutor use remains available on normal learning surfaces outside active quizzes.
- **Acceptance requirement:** browser tests must confirm the tutor is absent throughout the quiz lifecycle and that direct/contextual tutor requests cannot be used to obtain quiz help. This is an explicit acceptance requirement; documentation does not itself prove the UI/backend enforcement has shipped.
- **Sequence clarification (2 November 2026):** the product owner supplied the next product-level phases as Phase 6 certificates and verification, Phase 7 Practice Lab and project submissions, and Phase 8 skill mastery map and learner portfolio. This sequence is documented in `LEARNER_OUTCOMES_PHASES_6_8.md` and supersedes the earlier phase numbering for the next learner-outcome work. The track-completion feedback proposal remains backlog work.
- **Live schema verification:** the active Pheonix project was rechecked read-only. The existing certificate, project, submission, skill and evidence tables are present, RLS-enabled and restricted to service-role direct grants. No migration was applied.
- **Remaining release gates:** passing CI and browser/mobile acceptance of phases 6–8, plus the previously documented phase 1–5 browser acceptance and AI tutor quiz restriction. Production migration, data mutation, environment changes and deployment remain separately authorised.

### Learner outcomes phases 6–8 implementation — 2026-11-02

- **Product order revised by the owner:** phases 6–8 are Certificates and verification; Practice Lab and project submissions; Skill mastery map and learner portfolio. Phase 9 learning companion/community remains later. The earlier immediate Phase 6 track-feedback proposal is retained as deferred backlog work, not silently removed.
- **Phase 6 implementation:** added course-completion credential listing/eligibility/claim APIs, HMAC-derived idempotent certificate numbers, a public minimal-data verification endpoint, learner claim UI and a print/save-to-PDF verification page. Issuance checks the existing course completion summary, including published lessons, quizzes and assignments.
- **Phase 7 implementation:** added internal project/skill catalogue APIs and connected the existing Teams project workspace; added learner Practice Lab challenge discovery, link-based submissions and project history; added staff review with audit logging. Approved submissions at 70% or above create skill evidence for the skills actually mapped to that project. Manual learner notes cannot self-assert verified evidence.
- **Phase 8 implementation:** added evidence-derived skill mastery and a private printable portfolio containing approved projects, verified skills and issued certificates. Public hosted portfolios, raw file uploads and a hosted code-execution sandbox are explicitly not claimed.
- **Live schema verification:** read-only PostgreSQL access to the active Pheonix project now works. Relevant columns, status/evidence checks, unique indexes, RLS and grants were inspected. The relevant tables exist and are currently empty; RLS is enabled and direct grants were limited to `service_role`. No live schema/data mutation was performed.
- **Existing migration dependency:** the active ledger ends at `20261028171902`; `20261102090000_learner_learning_plans` is not applied and `learner_learning_plans` is absent. This remains a separate Phase 3 release dependency.
- **Free-launch protection at the implementation checkpoint:** no changes to Paystack, checkout, subscription, trial, expiry, Pro or payment history. A later release-preparation checkpoint added the reversible `FREE_ACCESS_MODE=true` Production environment setting; see the entry appended below.
- **Verification:** one combined backend contract test file was added. CI and browser-driven acceptance have not yet been established for this feature batch; do not claim production-release verification.


### Phase 6–8 follow-up hardening — 2 November 2026

- **Quiz tutor restriction:** the course player removes lesson-tutor entry points and hides the tutor navigation while a quiz is opening or active. The global learner shell checks backend sessions across tabs, and a learner can resume a server-held quiz after browser restart. The session-close endpoint rejects unsubmitted sessions, so client-side state or direct API calls cannot unlock the tutor mid-assessment.- **Quiz tutor restriction:** the course player removes lesson-tutor entry points and hides the tutor navigation while a quiz is opening or active. The AI page checks the backend session endpoint, and the backend denies tutor requests while any unexpired quiz session exists. The lock is held through the results view and released when the learner closes results after submission. Closing an unsubmitted quiz keeps its session locked and resumable; abandoned sessions expire after two hours. The new quiz_active_sessions migration is service-role-only with RLS and a rollback script.
- **Certificate revocation:** added nullable revocation timestamp, staff actor and reason fields through an additive migration. An internal endpoint requires the existing content.manage permission, writes an audit event, and is exposed in a Teams certificate register. Public verification reports revoked certificates as invalid and does not expose internal revocation notes.
- **Project review and mastery:** approved evidence is prepared before the submission status changes to approved; mastery reads only evidence whose source submission is approved and whose skill is mapped to the source project. Returned work no longer contributes to mastery. Learner history distinguishes approved, returned, reviewed and awaiting-review states and shows feedback.
- **Tests and CI:** contract tests cover quiz tutor lock, certificate projection privacy/revocation and migration inventory. Both new migrations and rollback rehearsals are included in the disposable database workflow. GitHub Actions on the evolving main branch were still queued at the last status check; no success is claimed for the final candidate SHA until a run completes.
- **Live database and release boundary:** no production migration, data mutation, environment change, free-mode activation or deployment was performed. The quiz-session and certificate-revocation migrations remain pending the disposable replay gate and separate explicit approval for the active Pheonix database. Existing Paystack, subscriptions, trials, entitlements and Pro implementation are unchanged.

### Release preparation and deployment evidence — 2 November 2026

- Built the current `Learnora-ME` source explicitly into the existing Vercel projects using the monorepo roots `frontend-v02`, `frontend-team` and `backend-python`. All three staging deployments reached READY; the learner and Teams builds completed Next.js compile/typecheck/static generation, and the backend build completed under Python 3.12.
- Staging deployment IDs: learner `dpl_4mC59NuvVS3HadiU3pTWZfo1RDiT`; Teams `dpl_7hiqZUWwurpQSaAncjgCyYSzceEv`; backend `dpl_8JoHQYyighk6542J6AmazrJ9wxHs`. No production alias was promoted.
- Added `FREE_ACCESS_MODE=true` to the backend Vercel Production environment only. It is reversible and applies on the next production deployment. Existing paid billing paths were not deleted or rewritten.
- The live Supabase ledger still ends at `20261028171902`; the four 2 November migrations remain unapplied. Catalog inspection confirms the quiz session table and certificate revocation columns are absent. Do not deploy the new backend to production until those dependencies have passed disposable replay and received separate production migration approval.
- Consolidated general CI to one workflow/job and narrowed the expensive cohort database workflow to cohort-specific paths. The latest general workflow remained queued; the queued state is not a pass.
- Existing production Teams/backend deployment metadata referenced `Pheonix-Analytics`; the new staging deployments explicitly reference `Learnora-ME`. Manual production deployment can use the current repository source, but future automatic Git deployment linkage still needs a deliberate Vercel Git connection check.
- Vercel showed no runtime error clusters for the existing production projects in the previous 24 hours. This is not a substitute for authenticated learner/staff acceptance on the new staging deployments.


### Gmail API email transport — 2 November 2026

- Replaced the direct Gmail SMTP and Resend email transport in `backend-python/routers/auth.py` with the Gmail API over HTTPS. OAuth refresh-token exchange and `users.messages.send` use the least-privilege `gmail.send` scope; MIME messages are base64url encoded.
- Verification email, resend-verification, password-reset content, token hashing/expiry, and account state transitions are unchanged. The transport deliberately does not retry an ambiguous message-send failure to avoid duplicate emails.
- Added `docs/GMAIL_API_SETUP.md`, the backend environment example, and targeted Gmail API contract tests. No Google OAuth credentials have been provisioned and no production environment variables or deployment have been changed. Production email delivery remains blocked until the owner creates/authorises the Google OAuth client and supplies the Gmail API variables in the backend Vercel project.
- Google classifies `gmail.send` as a sensitive OAuth scope. External OAuth apps left in Testing issue refresh tokens that expire after seven days; complete the applicable verification/publishing steps for ongoing production use. See the linked Google OAuth and Gmail API guidance in the setup document.


### Learner experience repair and account deletion — 2 November 2026

- Committed learner experience changes to `main` in `Obikpe/Learnora-ME`: dedicated personal learning-track workspace at `/dashboard/tracks`; `/tracks` remains the public track catalogue and `/courses` remains the public course catalogue. The `/api/progress/me` projection now includes `source_type` so the learner UI can derive the global track IDs from existing enrolments and request backend-calculated track progress.
- Removed the profile-editing explanation and the identified internal implementation notes from the learner settings, evidence and course catalogue surfaces.
- Updated the shared frontend API client to return a safe, support-oriented message for server errors instead of exposing raw request paths and 500 status details.
- Added a persisted light/dark theme switch to both public navigation and authenticated dashboard navigation. Light is the default; dark remains selectable. Added light-mode overrides for existing dark utility surfaces, readable contrast for status text, and custom scrollbars.
- Added support mail links to `learnorame@gmail.com` in public navigation, dashboard navigation and the account deletion confirmation page.
- Added `backend-python/routers/account_lifecycle.py`, the learner Settings deletion request UI, and `/confirm-account-deletion`. A signed-in individual learner requests deletion; a 60-minute single-use token is hashed and stored, then sent through the existing Gmail API transport. Confirmation cancels active/past-due/paused Paystack recurring subscriptions through the existing cancellation flow before invoking the database finalisation function. If cancellation cannot be confirmed, deletion is not finalised.
- Added `20261102130000_learner_account_deletion.sql`. Finalisation writes a limited identity/account snapshot to service-role-only `deleted_account_history`, deactivates organisation memberships/team memberships, removes manager assignment, clears password and auth-token fields, anonymises the user email, and marks the retained users row as a deleted tombstone. The tombstone intentionally preserves historical foreign-key relationships; hard-deleting the users row would cascade-delete learning records and is blocked by restrictive financial/creator foreign keys.
- Added `backend-python/tests/test_account_lifecycle.py`, updated both migration inventory test files, and recorded the new pending migration versions.
- **Not verified:** no local test suite or CI run was performed; GitHub Actions was deliberately not triggered to conserve the monthly quota. No frontend build, browser acceptance, production SQL migration, production data mutation, Vercel environment change, or deployment was performed.
- **Release gates:** apply/rehearse the 2 November migrations (including learning plans, quiz sessions, certificate revocation, project integrity and account deletion) in the reviewed sequence, obtain explicit approval for the active Pheonix production migration, then deploy the backend and learner frontend from the intended `Learnora-ME` source. Vercel team access to `obikpes-projects` returned 403, so production deployment source/root and current live route behaviour remain unverified.

**Follow-up implementation checks — 2 November 2026:** The learner credentials endpoint now retries with the pre-revocation certificate column set when the additive revocation columns are not yet present, so Portfolio and Certificates can continue loading while the revocation migration awaits approval. Added the learner-specific `/dashboard/tracks` route and changed the sidebar to use it; public `/tracks` and `/courses` remain catalogue routes. Removed the remaining identified developer-facing notes from the AI, certificate, admin, team and landing-page surfaces. The new migration and frontend changes remain unbuilt/unreleased pending the production migration and Vercel access gates.


**Account-deletion migration review:** The production schema was checked before finalising the migration. Organisation-owner accounts are blocked from self-service deletion until ownership is transferred; active organisation memberships are suspended (the valid status in the live schema), team memberships are deactivated, and manager assignments are cleared. The retained user tombstone has its password, verification/reset tokens, email, display name, trial dates and access dates cleared or anonymised. The original email/name and a limited account snapshot remain in the service-role-only history table. The migration has not been applied to production.


**Migration ledger reconciliation note:** A read-only check of the live `supabase_migrations.schema_migrations` table found two additional applied versions, `20261102210054` (`shared_auth_rate_limits`) and `20261102210056` (`shared_api_rate_limit`), which do not currently have matching timestamped files in `supabase/migrations`. The repository also contains earlier files with related names. These entries must be reconciled against their recorded SQL before using a bulk migration push; they have not been replayed or modified during this work.

### Quiz-page-scoped AI tutor access — 3 November 2026

- Corrected the overly broad quiz lock. An active or unfinished quiz session is not a global AI tutor lock. The restriction applies only while the learner is on the active quiz/test interface.
- `Sidebar.tsx` no longer queries `/progress/quiz-sessions/me` to decide whether the AI tutor navigation item is visible. The course player supplies the explicit `hideTutor` state while quiz content is open/opening.
- The AI page no longer checks the user's server-side active quiz sessions or blocks itself because a session exists in another tab or a prior page. Leaving the quiz interface restores AI access even if the assessment session remains unfinished.
- The course player no longer treats an orphaned session as a reason to hide the AI tutor or remove the lesson-level AI action. The learner can resume the quiz or use AI after leaving the quiz interface.
- The backend AI endpoint no longer applies a user-wide `quiz_active_sessions` lock. It continues to reject requests that explicitly include `assessment_id`, keeping assessment-specific tutor context unavailable.
- Replaced the old global-lock regression tests with a contract asserting that active sessions do not globally block tutor requests while explicit assessment context remains prohibited.
- No tests, builds, browser checks, CI, migrations, or production deployment were run.
- Quiz-session recovery in the course player now matches the current browser tab's client session ID only. An active quiz in another tab no longer creates a false 'unfinished quiz in this tab' state.

## Live catalogue seed: Introduction to Data Analytics — 3 November 2026

Seeded and verified the first published global Learnora learning track and course in the production Supabase project. This is data-only; no schema or application code was changed.

- Track: **Data Analytics** (`data-analytics`), ID `63715469-8b41-4972-b686-830fe55327e8`, published, global (no owner or organisation).
- Course: **Introduction to Data Analytics** (`introduction-to-data-analytics`), ID `e89cdf59-f4ad-4453-ab14-73e372fbce7e`, published, global Learnora-owned, beginner level, free for individual learners, linked as the required first course in the track.
- Module: **Foundations of Data Analytics**, ID `546aa84c-70d4-47aa-8371-6a3464599e32`, published.
- Lesson: **What Is Data Analytics?**, ID `9f051008-29e4-48b5-b1c2-c0b45954b812`, published, article, preview enabled, 35 minutes, approximately 10.6k characters of lesson content.
- The lesson covers data vs information vs insight, organisational uses, descriptive/diagnostic/predictive/prescriptive analytics, the analytics workflow, analyst responsibilities, an applied example, key points and reflection questions.

Read-only verification confirmed the track-course relationship, published statuses, exactly one module and one lesson for this new course, and one published global course/track in the catalogue. The existing 201 draft courses and the pre-existing Data Analytics Foundations course/module/lesson were left untouched. The public discovery API source exposes `GET /api/public/courses`, `GET /api/public/courses/{course_id}`, `GET /api/public/courses/{course_id}/structure`, `GET /api/public/tracks` and `GET /api/public/tracks/{track_id}`; these routes are registered in `backend-python/main.py`. A live HTTP request to the deployed Vercel API could not be completed from this environment, so production browser/API availability is not claimed as independently tested.


### Public Learnora ME landing page rebuild — 3 November 2026

- Replaced the previous editorial homepage with a responsive React/TypeScript landing page based on the owner-supplied HTML/CSS layout. The implementation remains inside the active Next.js application at `frontend-v02/` and reuses the existing public navigation, footer, theme tokens, image constants, and same-origin FastAPI request client.
- The homepage loads its course and track content from the existing public API endpoints: `GET /api/public/courses` and `GET /api/public/tracks`. Course cards, track cards, topic links, course counts, required-course counts, availability labels, thumbnails and estimated durations are derived from those API records. The UI includes loading, empty, and retryable error states.
- Search submits to the existing catalogue route using `/courses?search=...`. Course and track links use their existing public detail routes.
- Uses actual course thumbnail URLs when present and existing photographic assets from `frontend-v02/lib/constants.ts` for editorial sections and missing course imagery. No generated catalogue entries or sample metrics are inserted.
- Deliberately omitted fabricated university/partner logos, course ratings/review counts, learner testimonials, career outcome percentages, invented career listings, AI series claims, and other non-backed catalogue data from the supplied prototype. The prototype's Professional Certificates / Professional Certifications content is not included.
- No backend route, database schema, migration, billing behaviour, authentication behaviour, or deployment configuration was changed. This page consumes the already-registered public discovery endpoints and reflects the access fields returned by the backend.
- **Verification limitation:** GitHub source updates were made directly on `main`; a local dependency install, TypeScript/Next.js production build, browser acceptance test, live production API request, CI run, migration, and deployment were not performed in this environment. The live catalogue's actual content remains whatever the backend returns at request time.


### Learnora for Organisations landing page — 3 November 2026

- Replaced the generic audience-page presentation at `/for-organisations` with the supplied business-oriented landing page layout, adapted to Learnora's broader organisation audience: businesses, schools, universities, academies/training providers, non-profits, government institutions, and teams/departments.
- Kept the existing public navigation and footer. The page uses the repository's shared theme tokens and actual photographic assets from `frontend-v02/lib/constants.ts`; no new font, image dependency, component library, or fabricated partner branding was introduced.
- The catalogue section calls the existing public FastAPI endpoints `GET /api/public/tracks` and `GET /api/public/courses`. Track cards, course cards, search matches, published track/course counts, and course placements are derived from those returned records. Loading, empty, retryable error, and no-match states are included.
- The organisation enquiry form posts through the existing `submitOrganisationRequest` client helper to `POST /api/commercial/organisation-requests`. It submits the backend's required request fields, numeric headcount fields, organisation type, request purpose, and prospect portal password. Password confirmation is client-side only and is not sent. The UI reflects the actual request ID and email-verification response; it does not claim that a workspace is created or activated.
- The backend endpoint creates a pending prospect portal identity, sends the verification flow, and records an organisation request. Existing-account conflicts and backend validation/delivery errors are surfaced to the visitor. Contract review and explicit Learnora approval remain required before workspace activation.
- Omitted the prototype's invented employee productivity/retention/engagement percentages, fake customer logos and partner claims, fabricated course/certificate/lab/video counts, mock course search results and ratings, invented customer totals, analyst reports and unsupported regulatory resources. The prototype AI assistant was a non-functional UI shell and was not carried over. Professional-certification claims were not added.
- No backend route, schema, migration, entitlement, billing, authentication, or organisation permission logic was changed. No production data was modified.
- **Verification limitation:** GitHub changes were committed directly to `main`. No dependency installation, TypeScript compilation, Next.js production build, browser/form acceptance test, live API request, CI run, migration, or deployment was performed. The public catalogue and enquiry endpoint are wired to existing source contracts; live production availability has not been independently verified.


## 2.2 Public course detail and individual enrolment flow (3 November 2026)

- The public course detail route is `frontend-v02/app/courses/[id]/page.tsx`. It continues to fetch the actual public course record and published course structure; it does not use a fabricated catalogue or price display.
- Anonymous visitors see the public navigation and footer. The primary action for an eligible free course is labelled **Enrol for free** and routes to sign-in with a safe same-origin `next` path containing `?enrol=1`.
- The existing login handler already validates `next` as an internal path and redirects normal learner accounts to it. On return, the course detail page checks `/progress/me`; if the selected course is not already enrolled, it invokes the existing authenticated `POST /courses/{course_id}/enrol` endpoint. The endpoint enrols only that course, not the containing learning track. Existing enrolments route directly to the course learning workspace.
- Signed-in users see the shared dashboard `Shell` (the same Sidebar and Topbar used by dashboard routes) instead of `PublicNav`/`PublicFooter`. The course content itself remains the same. The signed-in CTA becomes **Continue learning** when an active/completed enrolment already exists.
- The existing backend remains authoritative for role, ownership, publication, organisation assignment and free-access eligibility. This frontend change does not widen course access or change the paid-access policy.
- Verification limitation: source files and endpoint contracts were inspected and the frontend route was updated. No CI, production build, browser acceptance test, database mutation or deployment was run as part of this change.


### Canonical course learning workspace — 3 November 2026

- The owner-supplied course-learning HTML is now the design direction for the enrolled learner experience. `/courses/{course_id}` is the canonical route: an enrolled learner opening a course sees the course workspace, while a visitor who is not enrolled continues to see the public course information and the existing access/enrolment flow.
- Extracted the existing learning player into `frontend-v02/components/course/CourseWorkspace.tsx` and adapted its shell to a dedicated course header and two-column course-navigation/content layout. The existing lesson content, signed video playback, YouTube/Vimeo embeds, lesson resources, progress tracking, private notes, course discussions, AI lesson handoff, quizzes, quiz-session recovery/heartbeat/submission/review, assignments and project submissions were retained rather than replaced with a static mock-up.
- The left course navigation now displays ordered modules and nested lessons, completion indicators, module lock state, and module quiz entries. The initial lesson selection is restricted to unlocked modules. The header displays the live course title, support link and theme toggle.
- The existing `/dashboard/learning/{course_id}` route now redirects to `/courses/{course_id}`; older links therefore resolve to the canonical workspace instead of maintaining a second player experience. Enrolment remains course-only and returns to the same canonical course route.
- The authenticated course activities response now includes each published quiz's `module_id`, allowing module-level quizzes (including quizzes without a lesson association) to appear in the module navigation. The quiz detail endpoint remains enrolment- and module-gated; quiz questions are not exposed by the activities listing. For legacy lesson-linked quizzes whose `module_id` is null, the backend resolves the module from the associated lesson both when listing activities and when enforcing quiz access, so those quizzes cannot bypass the module gate.
- Strengthened the backend module gate: every earlier published module must have at least one published quiz, and the learner must pass every published quiz in that module at the effective threshold (never below 70%, or the configured higher threshold). A module without a published quiz now remains locked instead of silently allowing the learner to skip the required module assessment. The backend remains authoritative for direct lesson, media, notes and quiz access; the UI lock is not the security boundary.
- After a passing quiz submission, the workspace refreshes the backend course-progress projection so the next module's newly unlocked state is reflected without requiring a manual page reload.
- The free-access and paid-access rules, Paystack/subscription code, track enrolment and course access eligibility logic were not changed. Anonymous visitors still need to sign in and complete the existing eligible course enrolment flow before learning content is available.
- **Verification limitation:** source-level inspection confirmed the new route wiring, activity response field, lock handling, and preservation of the existing player workflows. No frontend build, Python test suite, browser acceptance, CI workflow, database migration, production data mutation, or deployment was run. The source changes are committed to `main`; build/runtime correctness and actual browser presentation still require verification on the local development environment.


### My Learning enrolment and course-completion lifecycle — 3 November 2026

- The learner-facing My Learning route is `frontend-v02/app/dashboard/page.tsx` (`/dashboard`). It now follows the supplied My Learning layout direction and uses live API records for In Progress, Completed, Skills and Certificates. In Progress includes every active enrolment, including a learner who has registered but has not started a lesson. Completed is based on the persisted enrolment status and verified course-completion calculation. Cards link to the canonical `/courses/{course_id}` workspace.
- The dashboard no longer contains sample courses, fabricated due dates, sample certificates, upgrade-to-unlock prompts, paid trial CTAs or pay-to-unlock UI. Skills and certificates are displayed only when returned by the existing evidence and credentials APIs. The calendar/daily-goal mock was not carried across because no authoritative daily-goal activity endpoint was established in this task.
- The live Supabase schema already has the required persistence fields on `public.learnora_enrolments`: `status`, `enrolled_at`, and nullable `completed_at`. No additional completion table or schema migration is needed. Completion is persisted by changing the learner's enrolment row from `active` to `completed` and setting `completed_at` once the course's published lesson and required assessment rules are satisfied.
- Added `_sync_enrolment_completion` to `backend-python/routers/progress.py`. Lesson completion and quiz submission now invoke it; assignment grading in `backend-python/routers/internal_assessments.py` also invokes it. `GET /api/progress/me` now calculates full course progress, lesson/assessment totals, completion state, next learning item and last activity; it also repairs an active enrolment to completed if existing saved records already satisfy the completion rules. Dashboard summaries omit lesson body content to avoid downloading course content unnecessarily. The single-course progress read and learning-track progress read also run the same synchronisation, so opening a course or track repairs any eligible older enrolment rather than displaying stale `active` state.
- Existing completion definition remains authoritative: every published lesson must be completed, every published quiz must have a passing attempt at its effective threshold (minimum 70%), and every published assignment must have a latest graded submission meeting the existing 70% assignment threshold. A course with no lessons or assessments is not automatically marked completed. Project submissions are not currently part of the course-completion calculation.
- Track completion continues to be calculated from required course enrolments/completions by the existing `/api/progress/tracks/{track_id}` endpoint; it does not create a second, conflicting course-completion record. The course enrolment row is the source of truth for an individual course.
- Read-only inspection of the active Learnora Supabase project (`gihfupzvdpyrmynqgukz`) confirmed the enrolment columns and found no current rows in `learnora_enrolments`; therefore there were no existing learner records to backfill and no live learner completion could be demonstrated with production data. The implementation will classify future/current enrolments from persisted lesson and assessment records.
- No billing, Paystack, subscription or free-access implementation was changed. The My Learning page does not present payment as a condition of continuing an enrolled course.
- **Verification limitation:** inspected the live Supabase schema and migration history and ran read-only enrolment-state queries. No schema migration was required or applied. No frontend build, Python test suite, CI workflow, browser acceptance or deployment was run.

## Learner experience corrections — 3 November 2026

- Restored the My Learning calendar with month navigation. Calendar markers are derived only from persisted enrolment, per-course last-activity and course-completion timestamps; the current progress API does not expose a complete day-by-day activity log.
- When a learner has no enrolments, the In Progress view recommends up to three published catalogue courses, excluding courses already on the learner's record. Available recommendations are ranked against the learner's saved learning goal when one exists.
- Restored the learner AI assistant in the My Learning header. It uses the existing AI coach endpoint and passes the current published catalogue and saved learning goal as context. Matched course recommendations link to their real course pages. The AI permission check now recognises individual learner accounts for learner-facing features; organisation permission and assessment restrictions remain in place.
- Replaced the My Learning black empty-state cards with plain text states. Completed courses use the heading "No completed courses" and the text link "Nothing here yet. Explore courses". Certificate retrieval no longer displays the generic temporary-unavailability message.
- Updated the learner certificate endpoint to select columns that exist in the active Supabase schema. Course-title and course-eligibility calculations are isolated so their failures do not prevent issued certificate records from being returned. The existing certificates and learnora_enrolments tables remain the source of truth; no migration was required.
- Public course detail and outline remain available for preview, but public outline responses contain lesson metadata only, not lesson body content. Enrolment intent (?enrol=1) now redirects unauthenticated visitors to sign-in and returns them to the requested course. Automatic enrolment runs only when the signed-in account is eligible. The backend enrolment endpoint remains authenticated.
- Added the shared audience navigation strip to learner and instructor audience pages and aligned its order across audience pages.
- Removed the learner-facing "Progress and evidence" commentary panel and other redundant explanatory notes identified in the course workspace.
- Replaced the Teams lesson-content Markdown textarea with a WYSIWYG editor. New lesson content is submitted as formatted HTML and sanitised by the internal content API before it is stored in the existing learnora_lessons.content text column. Existing Markdown lesson content is rendered as formatted headings, lists, emphasis, links, quotes and code; opening and saving a legacy lesson converts it to the rich-text format. No database migration was required.
- No billing or Paystack behaviour was changed. The free-launch access rules and existing paid implementation remain intact.
- Source-level checks were performed on the changed routes and components. No frontend build, Python test suite, CI workflow, browser acceptance run or deployment was triggered, to preserve the user's CI allowance.

## My Learning fidelity and page-performance work — 3 November 2026

- Restored the supplied My Learning calendar card structure (.sc, .cal-h, .cal) and retained month navigation and activity markers derived from persisted enrolment, last-activity and completion timestamps.
- Restored the header AI sparkle control (id="aib") and its panel. The panel includes the original “Plan my week” and “What should I finish first?” prompts, plus course recommendation. Its prompt context now includes the learner's saved goal, current enrolled courses and progress, and the published catalogue. It does not invent course records.
- Restored the neutral dashed .empty state without a black card background. Completed uses “No completed courses” followed by “Nothing here yet. Explore courses to get started.”
- Kept the audience strip on learner/instructor pages and removed the extra explanatory copy from the learner course workspace.
- The My Learning load sequence now waits only for core progress and public catalogue data before rendering the page. Skills/evidence and certificates load afterward so a slow secondary endpoint cannot hold the entire dashboard behind its loading state. Failed certificate retrieval is distinct from a successful empty response.
- The certificate endpoint /api/credentials/me and public.certificates table exist in the current source/schema. A read-only database check found zero issued certificate rows and one active enrolment in the inspected project at the time of the check. An empty certificate list is therefore a valid state; a request failure is shown separately. No certificate was fabricated and no schema change was applied.
- Added session-scoped response caching and in-flight request deduplication to the Learnora ME and Teams API clients. Public course/track data is cached for five minutes; learner progress for one minute; evidence and certificates for five minutes; onboarding for two minutes; other eligible GET reads for short bounded periods. Notifications, AI, billing, payment, audit, analytics and other dynamic endpoints are excluded. Private cache keys include the active session epoch and organisation context; logout, session changes and mutations invalidate the cache. Private responses are kept in the current tab's session storage, not shared between accounts.
- The learner identity profile is restored from a short-lived tab cache for faster repeat navigation. The profile cache is cleared when the session changes or logs out.
- Shared learner skeletons and the public course catalogue skeleton now wait 180 ms before appearing, preventing a brief fast response from flashing a placeholder. Course detail metadata no longer waits for authentication, course structure and progress requests to finish before it can render. Curriculum details load separately. Enrolment-intent URLs (?enrol=1) remain gated behind sign-in and return to the requested course after authentication.
- Next.js compiles TypeScript into versioned JavaScript/CSS assets at build time. The browser caches those generated static assets; TypeScript source files are not shipped as the runtime cache. No manual cache of .ts source files was added.
- The My Learning “Explore courses” actions use Next.js client-side links to /courses; frontend-v02/app/courses/page.tsx is the catalogue route. The route has no root redirect in the current Next.js config.
- No billing, Paystack, free-launch or pay-to-unlock behaviour was added or changed.
- Verification limitation: inspected current source, checked the live Supabase certificate/enrolment schema and records read-only, and inspected Vercel deployment/error metadata. No frontend build, Python tests, CI run, browser acceptance or deployment was run. The current production frontend deployment inspected was still on commit e06994c8c2f5b94545ddf629c3644397a880a4b4; the newer main changes in this section are committed but are not live until a deployment is made. The Vercel Hobby runtime-log window did not include older requests, so the earlier certificate error could not be traced to a specific production request.

## Learner loading performance audit and corrections — 3 November 2026

### Findings
- The active Supabase project `gihfupzvdpyrmynqgukz` is in `eu-west-3` (Paris). The deployed Vercel backend function for `learnora-backend.vercel.app` was running in `iad1` (US East), creating a cross-region network hop for every database request. The frontend v02 rewrite targets `https://learnora-backend.vercel.app`.
- The learner progress endpoint previously called the full per-course summary for every enrolment. Each summary loaded modules, lessons, all user lesson-progress rows, assessment records and repeatedly queried previous-module quizzes and attempts. The module lock calculation repeated those database reads for each module.
- The course workspace progress response included the body of every lesson. Routine video progress writes also recalculated the entire course summary every 15 seconds, even when the learner had not completed a lesson.
- The course workspace fetched project submissions before the learner opened project work and checked for active quiz sessions even when the current tab had no active quiz.
- My Learning waited for the course catalogue before showing the dashboard, even when the learner already had enrolments and did not need recommendations.
- The current database has approximately one course, one module and one lesson; the queried quiz, assignment, assignment-submission, media and note tables had no live rows at audit time. This does not support attributing current delays to large course-table volume.
- Supabase performance advisors reported 73 unindexed foreign keys, 130 unused indexes and one duplicate index. No blanket index changes were applied: unused-index advice is not proof that an index is harmful, and the course/assessment tables are currently almost empty. Query-specific indexes should be evaluated as real data volume grows.
- Supabase PostgREST logs contained 359 `Warp server error: Thread killed by timeout manager` messages in the inspected 24-hour window. The returned log metadata did not identify the originating application route, so these are recorded as a separate platform signal, not attributed to a specific Learnora endpoint.

### Changes committed to main
- The My Learning progress endpoint now batches course, module, lesson, learner-progress, quiz, attempt, assignment and submission reads across all of the learner's enrolments instead of running a full summary once per course.
- Course summary progress reads are restricted to lesson IDs belonging to that course. Module lock state is computed in memory from batched assessment data; the passed-attempt and configured passing-score checks remain enforced.
- Course workspace progress responses no longer include all lesson bodies. A new authenticated lesson workspace endpoint returns only the selected lesson's content, notes, media and resources after enrolment and module-access checks. The learner workspace uses this single request when the selected lesson changes.
- Routine lesson progress saves no longer rebuild the full course summary. Completion is synchronised when a lesson is actually completed; intermediate video progress saves only update the lesson progress record. Video progress writes are now at 30-second intervals, with an additional save on pause and completion.
- Quiz submission, assignment grading, track progress and course progress reads request compact summaries without lesson bodies.
- Project submissions are loaded only when project work is opened. The active-quiz-session lookup runs only when the current tab already has an active quiz session.
- My Learning starts loading its records alongside the learner onboarding check. It displays the dashboard after progress arrives and fetches the public course catalogue only when the learner has no enrolments and recommendations are needed.
- The root Vercel function configuration now assigns `backend-python/main.py` to `cdg1` (Paris), matching the active Supabase region. This takes effect only after a deployment using the updated root `vercel.json`.

### Release and verification status
- The Vercel Git integration is disabled in the root and v02 Vercel configuration. A commit does not automatically deploy these changes.
- At audit time, the `learnora-backend.vercel.app` production deployment was still on commit `e06994c8c2f5b94545ddf629c3644397a880a4b4` in `iad1`; the latest `learnora-me-v02` frontend deployment was also on that older commit. The separate `learnora-backend-v02` project was deployed from the `learnora-platform-foundations` branch, not current `main`. The v02 frontend's configured API target is `learnora-backend.vercel.app`, not the separate backend-v02 project.
- The code and region configuration are committed to `main`, but no deployment, frontend build, Python test suite, CI workflow or browser acceptance run was triggered. Live speed improvement has therefore not yet been measured.
- No Supabase migration or production data change was made for this performance work.

## Frontend v02 full source audit and corrections — 3 November 2026

### Scope
- Reviewed the complete tracked `frontend-v02/` tree on `main`: 107 files across App Router pages, shared components, API clients, utilities, CSS, TypeScript configuration, Next.js configuration, package metadata and Vercel headers.
- No Vercel deployment was created or triggered during this audit. No GitHub Actions workflow or CI run was triggered.

### Confirmed issues corrected
- Fixed the course catalogue state declaration that caused the reported Next.js parse error: `const [query, setQuery = useState("")` is now a valid `useState` destructuring declaration. Simplified the catalogue's derived level/track/filter expressions and image-set initialization to make the TSX easier to parse and maintain.
- Added the missing `RichContent` import in `components/course/CourseWorkspace.tsx`. The component was rendered by the course player but was not imported, which would have produced a subsequent compile failure after the catalogue syntax error was removed.
- Corrected the course workspace so AI tutor entry points remain hidden while a quiz session is active or being recovered. A failed quiz-session close no longer clears the local quiz lock and exposes tutor access while the backend session may still be active.
- Updated the lesson rich-content URL sanitizer to reject protocol-relative external URLs and control characters/backslashes, in addition to disallowed URL schemes.
- Updated the frontend Vercel Content Security Policy to explicitly permit the YouTube/Vimeo iframe providers used by the course player and HTTPS/blob media sources used for signed lesson video playback. Previously, the restrictive default policy could block those legitimate player sources.
- Corrected certificate verification links in both the Certificates and Portfolio pages to use Learnora's local `/verify-certificate/{certificate_number}` route instead of relying on an optional `verification_url` field not guaranteed by the certificate record.
- Corrected Creator Studio status handling: creator accounts with status `active` were allowed through the data-loading branch but were subsequently shown the unapproved state. Both checks now accept `approved` and `active`.
- Reset the course auto-enrol guard when the dynamic course ID changes, so a previous course's auto-enrol attempt does not suppress an enrolment intent for the next course during client-side navigation.
- Corrected `.env.example` to document `API_PROXY_TARGET`, the environment variable actually read by `next.config.mjs`; the previous `NEXT_PUBLIC_API_URL` example was unused.
- Aligned the landing-page audience navigation order with the learner, instructor and organisation pages, and marked the active organisation audience link with `aria-current`.

### Review observations
- The v02 admin route layout intentionally redirects `/dashboard/admin/*` to the separate Learnora Teams sign-in. The local admin page files remain in the tree but are not the active admin surface under that layout; this was not changed.
- The root `vercel.json` backend function region is separate from the frontend project's build-machine region. A Vercel build log showing `iad1` identifies where that build ran; it does not by itself establish the runtime region of the frontend or backend function.
- The frontend API client uses same-origin `/api/*` requests and the Next.js rewrite in `next.config.mjs`; production defaults to `https://learnora-backend.vercel.app`. The previous env example did not match that configuration and has been corrected.
- No new database migration or production data mutation was needed for these frontend corrections.

### Verification status
- Confirmed the reported malformed state declaration is corrected on `main`.
- Re-fetched the modified course workspace, catalogue page, CSP, certificate pages, Creator Studio page, course detail page, rich-content utility and environment example from `main` after editing.
- These are source-level corrections only. No local TypeScript compiler, dependency install, Next.js production build, browser acceptance test, CI workflow or Vercel deployment was run. The frontend is therefore not yet certified build-clean; the next build should be attempted only after the remaining local/source checks are complete and with the user's deployment cap in mind.

**Responsive dashboard navigation correction — 9 November 2026:** The mobile/tablet hamburger must open a slide-out drawer containing the learner's permitted destinations, not a search panel or a header-only shell. Desktop horizontal navigation remains unchanged. The drawer includes the permitted learning destinations from the same role-aware navigation set (My Learning, Practice, Projects, Skills, Portfolio, Evidence, Certificates, Community, AI Tutor when allowed, Learning Calendar, and Discover Courses/Learning Tracks only for unrestricted individual learners). Profile, settings, theme and sign-out remain in the avatar menu; notifications remain in their separate notification preview/panel. Cohort and organisation learners must not receive discovery/enrolment destinations. The drawer renders each destination as an explicit full-width row so it does not depend on desktop navigation or the desktop More menu.


**Authenticated learning-track discovery — 9 November 2026:** The Explore tracks action inside My Learning Tracks must not send an authenticated learner to the public marketing/catalogue surface. Added a dedicated signed-in discovery route at `/dashboard/tracks/explore` and signed-in track detail route at `/dashboard/tracks/explore/[id]`. Both use the existing dashboard `Shell`, preserving horizontal desktop navigation and the responsive hamburger drawer on tablet/mobile. The signed-in catalogue reads published tracks from the existing public track API; detail pages use the existing track detail/progress/enrolment endpoints. The public `/tracks` routes remain available for logged-out visitors. Assigned cohort/organisation learners remain excluded from public discovery and self-enrolment, consistent with the existing access model. No certificate design changes, database migration, deployment or browser test were included in this change.


## Account deletion request failure investigation — 9 November 2026

### Finding
- The signed-in Settings flow calls `POST /api/account-lifecycle/request-deletion` after the user types `DELETE`. This request first resolves the authenticated user through `auth.get_current_user`; account deletion does not begin until that dependency succeeds.
- The frontend API client previously replaced every HTTP 5xx response with the same generic “Something went wrong while loading your information” text. That concealed safe FastAPI error details, including the explicit 503 returned when Gmail confirmation email delivery fails.
- Vercel production runtime error aggregation for `learnora-backend` showed 31 ASGI error occurrences across 3 users in the selected 7-day window, with the latest at 2026-11-09 15:50:37 UTC. The captured stack includes `httpx.RemoteProtocolError: Server disconnected` while `auth.get_current_user` was executing `_find_user` against Supabase PostgREST. The trace is an authentication dependency failure, before the account-deletion route body. The aggregated route label was `/fastapi`, so this is strong evidence of a backend transport failure at the time, but does not uniquely prove that a particular user's deletion request generated that exact trace.
- The backend production deployment serving `learnora-backend.vercel.app` was confirmed to contain the account lifecycle router and the account-deletion migration. Runtime log detail for an individual request was not available because the project's current Vercel log retention does not cover the requested window.

### Changes committed
- Added bounded retries (initial attempt plus two short retries) for idempotent Supabase PostgREST identity SELECTs used by learner, administrator and reserved cohort-account lookup. Retries are limited to `httpx.TransportError`; SQL/API errors are not retried.
- When transient transport retries are exhausted, authentication lookup now returns a safe HTTP 503 rather than an unhandled ASGI 500.
- Updated the frontend API client to display safe backend `detail`, `message` or `error` strings for failed requests instead of discarding all 5xx response details. Generic internal-server-error responses still use the generic fallback; raw exception details are not exposed.
- Added backend regression tests for one transient disconnect followed by success, and for retries being exhausted and returning a safe 503.

### Verification and release
- Source files were re-fetched from `main` after the changes. The backend test suite has not been executed in this session.
- No Supabase data or schema was changed. No Vercel deployment was triggered. The retry and error-message changes will not affect production until the backend and frontend are deployed through the user's normal release process.


## Account deletion schema mismatch — 9 November 2026

### Production diagnosis
- The production backend had been updated to commit `62294529305e90780d8a83730f45034c0807cb23`, but the active Supabase database had not received the corresponding learner-account-deletion migration.
- Vercel runtime logs captured `POST /api/account-lifecycle/request-deletion` on the production deployment. The request failed when PostgREST attempted to select `users.account_status` and `users.account_deletion_expires_at`; Supabase returned PostgreSQL error `42703` because `users.account_status` did not exist.
- A read-only inspection of `public.users` confirmed that all five lifecycle columns were missing. The migration-history table had no row for migration version `20261102130000`, and the `complete_learner_account_deletion(text,timestamptz)` RPC was absent.
- The account-deletion migration was already present in `supabase/migrations/20261102130000_learner_account_deletion.sql`. The migration's referenced organisation tables and required columns were verified to exist before applying it.

### Live correction and verification
- Applied the existing `20261102130000_learner_account_deletion.sql` migration to the active Supabase project `gihfupzvdpyrmynqgukz` using the Supabase migration operation. The migration adds lifecycle fields to `public.users`, creates the restricted `deleted_account_history` table, and creates the account-deletion completion RPC.
- Verified all five lifecycle columns exist, `public.deleted_account_history` exists, and `public.complete_learner_account_deletion(text,timestamptz)` exists. Function execute privileges are limited to `service_role` and the database owner role; PUBLIC, anon and authenticated were revoked by the migration.
- Checked the affected learner row after migration: `account_status='active'`, no deletion token, no deletion-request timestamp and no deleted timestamp. The failed request did not leave a partially pending deletion or delete the account.
- The production backend and frontend were not redeployed as part of this schema-only correction. The backend already contains the route code; the database schema was the missing dependency.
- Vercel Hobby runtime logs have a short retention window (one hour). A 30-minute query returned the failed request records; a wider query was rejected by the logs API. This explains why some attempts to inspect logs appeared empty or unavailable. When diagnosing a fresh reproduction, query the latest 30 minutes and filter for `request-deletion`.

### Remaining verification
- The request endpoint has not yet been re-exercised after applying the migration. The next user-initiated request should confirm whether the confirmation email is sent. Typing `DELETE` only requests the email; the account is deleted only after the confirmation link is used.
- No user account was deleted, no existing learning records were removed, and no frontend or backend deployment was triggered by this correction.


## Responsive navigation, learner account recovery and notification consent — 9 November 2026

### Mobile and tablet navigation
- The previous mobile drawer was rendered inside the sticky header. The header's backdrop filter can establish a containing block for fixed descendants, which can clip a viewport-fixed drawer to the header. The drawer now renders through a React body portal at a higher stacking level, so it covers the Learnora ME brand/header area and displays the complete permitted navigation.
- The notification preview now renders through a body portal as a right-side drawer below the sticky header. Its width is constrained to `min(22rem, 100vw)`, text is smaller, content wraps safely, and the header remains interactive so clicking the bell again closes the drawer.
- These changes are source-level corrections; browser acceptance on real phone/tablet viewports has not yet been run.

### Account deletion and 30-day recovery
- Deletion requests now require a structured reason with optional details. The 60-minute confirmation email remains a separate step.
- Confirming deletion changes the learner to `deactivation_pending` for 30 days rather than immediately anonymising the account. Sign-in and authenticated requests are blocked during this period.
- A registration attempt using the same email during the recovery period issues a 24-hour reactivation link to the existing email. Reactivation restores the original account and learning history; it does not create a duplicate account or replace the existing password.
- A new database migration `supabase/migrations/20261109180000_learner_deletion_grace_and_marketing_consent.sql` adds the recovery state, token fields, deletion reason and finalisation RPC. The daily Vercel cron is configured at `/api/account-lifecycle/finalize-expired`; production must have a strong `CRON_SECRET` environment variable set before deployment.
- Finalisation after 30 days creates a restricted history row, records the deletion reason in audit activity, anonymises the live user row and releases the original email for future registration. The live account is not anonymised during the recovery period.
- Learnora admin Users now exposes learner account status, pending recovery-period deletions and completed deletion history/reasons. The admin activity stream also receives lifecycle audit events.
- Existing organisation/cohort and organisation-owner safeguards remain in place.

### Marketing consent and unsubscribe
- Registration now has an optional, unticked marketing email opt-in. The backend records the opt-in flag, timestamp and source; no marketing consent is inferred from registration or use.
- Account Settings can opt the learner in or out. A signed, purpose-specific unsubscribe endpoint and confirmation page are available for future marketing email footers. The token is carried in the URL fragment so it is not sent in ordinary HTTP request URLs.
- Consent evidence is retained when the learner withdraws consent; withdrawal is recorded separately. Future marketing sends must check the current opt-in/suppression state immediately before delivery.
- Added `docs/LEARNER_NOTIFICATIONS_AND_MARKETING_AUTOMATION.md` defining transactional versus marketing messages, event-driven recipient targeting, course-enrolment updates, inferred interest signals, durable outbox/delivery handling, campaign controls and compliance safeguards.
- The automated event/outbox worker, search-interest capture, campaign authoring/sending and actual marketing templates are not implemented yet. The unsubscribe URL helper is ready for a future sender to use.

### Migration and release status
- The new migration is committed but has **not** been applied to the active Pheonix Supabase project. Apply it before deploying the updated backend; the new backend queries reference columns introduced by this migration.
- Set `CRON_SECRET` in the production Vercel environment before deploying the backend. Confirm the daily cron runs and finalises only accounts whose recovery period has expired.
- No frontend or backend deployment was triggered. No production schema migration was applied in this work.
- Backend tests and frontend build/typecheck were not executed in this session. Static regression contracts were added to `backend-python/tests/test_account_lifecycle.py`; they still need to be run.
- Browser acceptance remains required at phone, tablet and desktop breakpoints, including drawer visibility/close behaviour, notification drawer viewport width and bell toggle.


### Additional privacy and verification findings
- The marketing unsubscribe mechanism now uses opaque random per-email tokens. Only token hashes are stored in the service-only `learner_marketing_unsubscribe_tokens` table; the raw token is carried in the URL fragment and outstanding tokens are consumed when a learner unsubscribes.
- A read-only inventory of the active Pheonix schema found many learner-linked tables beyond `public.users` (enrolments, progress, sessions, notes, quiz/assignment/project submissions, certificates, AI conversations, discussions, notifications, subscriptions, purchases and audit records). The new finaliser does not yet delete or irreversibly anonymise every one of these rows.
- The deletion-history record retains original email and UUID, so it is restricted/pseudonymised personal data, not anonymous data. A table-by-table erasure/retention matrix is a production blocker. Do not enable the finalisation cron until that policy is approved and implemented.
- The latest GitHub Actions workflow run for source commit `736f001ca8a19db99559951fe93f3954b7b4fbad` concluded `failure` before any job steps were created (`steps: null`, no logs URL). This is not evidence of a test assertion or compile failure; CI did not provide an executable job/log. Re-run CI when the runner/workflow infrastructure is available.
- Vercel's latest production deployments for both `learnora-me-v02` and `learnora-backend` still point to the earlier commit `62294529305e90780d8a83730f45034c0807cb23`. No deployment was triggered by this work; the new source changes are not live.


### Finaliser safety gate
- The daily account-finalisation endpoint now no-ops unless `ACCOUNT_DELETION_FINALIZER_ENABLED=true`. The environment example defaults it to false.
- Registration attempts after the 30-day deadline also refuse to trigger finalisation while the gate is disabled. This prevents a user sign-up request or an accidentally configured cron from executing a finalisation policy before the linked-data retention matrix has been approved.
- Set `CRON_SECRET` and explicitly enable the finaliser only after the erasure/retention policy and table-level processing are approved.


### Marketing channel consent and public notice
- The signup opt-in now covers both marketing email and promotional in-app notifications. Separate fields (`marketing_email_opt_in`, `marketing_in_app_opt_in`) are stored, and the same preference control/unsubscribe flow withdraws both channels.
- The marketing-email URL helper issues opaque per-message tokens stored as hashes in a service-only table. The sender must use this helper and include the link in every campaign footer when the campaign worker is built.
- Both privacy-policy routes now disclose optional marketing consent, withdrawal, essential service communications and the 30-day account recovery process. They remain drafts until Learnora's legal operator/contact details and retention schedule are completed and reviewed.

## Account deletion decision — 30-day recovery, then complete learner erasure

The approved product rule is:

- Confirmed deletion starts a 30-day deactivation and recovery window. No learner data is erased during this period.
- Reactivation during the window restores the existing account with its password, enrolments, progress, notes, submissions and other learner records intact.
- At the end of the 30 days, the finalisation process deletes the learner's `public.users` row and all account-linked learner records, including learning/progress data, notes, assessments, submissions, certificates, discussions, AI conversations/usage, notifications, activity records, account tokens, membership links and learner-owned commercial/profile rows.
- The only learner-specific record retained is the restricted `public.deleted_account_history` row. It contains the deletion-history fields and reason; it is not a reusable learner account.
- The finaliser must fail atomically if a dependent learner record cannot be deleted. It must never report completion after partial cleanup.
- Shared platform catalogue and organisation resources are not deleted solely because a learner created or was assigned as their actor; the learner attribution is detached where appropriate.

The implementation is represented by migrations `20261109180000_learner_deletion_grace_and_marketing_consent.sql` and `20261109190000_erase_learner_records_after_recovery.sql`. They remain unapplied to production until separately authorised. Keep `ACCOUNT_DELETION_FINALIZER_ENABLED=false` until migrations, schema checks and deletion tests are complete. The Terms and Privacy Policy wording will be reviewed and updated in a separate documentation/legal-review pass after the feature set is complete.
## Learnora ME visual and navigation repair — 19 November 2026

### Documentation reviewed before implementation
- `docs/learnora-ui-ux-research.md`: preserve the existing public top-navigation structure, use the existing Next.js/React/Tailwind/Lucide stack, use real catalogue data, keep layouts page-specific, and make motion subordinate to comprehension and accessibility.
- `docs/PRODUCT_ENGINEERING_SPEC.md`: `frontend-v02/` is the active customer-facing Learnora ME application; preserve the customer/internal-app boundary and existing architecture.
- `docs/ENGINEERING_HISTORY_AND_DECISIONS.md`, `docs/ROADMAP.md`, and `docs/LEARNER_JOURNEY_PHASES_1_5.md`: preserve learner access restrictions and distinguish source-level checks from runtime/browser acceptance.

### Changes committed to `main`
- Corrected the administrator brand/home link to `/dashboard/admin`; the previous `/dashboard/admin/overview` destination did not exist.
- Kept learner links that are handled by the learner dynamic route and retained only administrator destinations supported by the admin route handler. The public navigation, footer, account settings and instructor destinations were checked against the app route tree.
- Moved the animated theme toggle into the shared dashboard Topbar so it is available on learner and administrator dashboard pages, removing the duplicate control from the My Learning page. Added compact sizing for narrow mobile headers.
- Removed broad global dark-background catch-all and global white/slate text recolouring rules that overrode Tailwind utilities. Legacy surface colours now map by surface level (page, soft surface, card) rather than flattening all surfaces into one card colour. Public navigation/footer retain their scoped theme rules.
- Restored the mobile landing-page featured-course preview, added a restrained Learnora eyebrow and accessible manual controls for the rotating hero messages. The temporary floating learning-path overlay remains removed.

### Source-level verification
- Re-fetched the route tree and checked all 21 learner/admin/instructor sidebar destinations against static routes or the supported dynamic route sections; all matched.
- Checked all public navigation and footer destinations against the route tree; all matched.
- Confirmed the administrator brand link no longer points to `/dashboard/admin/overview`, the shared dashboard theme toggle is present, the landing hero controls and mobile preview are present, the broad global colour overrides are absent, and the edited global CSS braces are balanced.

### Acceptance boundary
- These checks are source-level assertions, not an authenticated browser walkthrough. Desktop/mobile rendering, navigation clicks, sign-in/dashboard loading and theme persistence still require browser acceptance.
- The latest GitHub Actions run for the candidate source was pending with no jobs reported when this note was written; no successful build or test result is claimed.
- No Vercel deployment, production database change or migration was performed.
## Landing-page motion enhancement — 19 November 2026

### Documentation reviewed before implementation
- `docs/learnora-ui-ux-research.md`: motion must remain subordinate to comprehension, preserve semantic and keyboard-accessible controls, and work on mobile.
- `docs/PRODUCT_ENGINEERING_SPEC.md`: keep the existing responsive Next.js UI architecture and accessibility requirements.

### Changes
- Added a one-time IntersectionObserver reveal for the landing page's major content sections, including the personalised Continue Learning panel. Sections reveal as they enter the viewport and are unobserved after reveal.
- Added a sequenced hero entrance for the eyebrow, rotating headline/description, action, search, topic chips, learning points, slide controls and live course preview.
- Added a restrained animated course-preview ring and occasional light sweep, with a subtle icon breathing effect.
- Added short staggered entrances for course, track, principles, audience and evidence cards; gentle hover lift/image zoom; animated action arrows; and FAQ open-state transitions.
- Kept the existing hero headline carousel's reduced-motion behaviour and added explicit reduced-motion overrides for the new motion system. IntersectionObserver has a graceful fallback for unsupported browsers.
- No content, routes, data source, or navigation behaviour was changed.

### Verification boundary
- Source inspected after changes to confirm all reveal sections have the `landing-reveal` class and the observer disconnects on unmount.
- Reduced-motion styles are included. No browser rendering, device-level performance test, frontend build, or preview deployment is claimed in this entry.


## 7. Frontend lint baseline and incremental enforcement — 19 November 2026

The production-check workflow exposed a pre-existing Learnora ME lint backlog on candidate `7a0fec45e272fdefd57b7c488ad2102d02d5dc5b`. The landing-page motion commit changed CSS only; repository-wide ESLint nevertheless scanned the entire frontend and failed with 710 errors and 49 warnings. Reported categories included explicit `any` types, synchronous state updates inside effects, and internal-route anchors. These findings span files outside that CSS-only change and were not introduced by the motion work.

The original candidate was not deployed. Backend compilation, migration/rollback rehearsals, backend static checks, import, regression suite and HTTP smoke test passed; the learner frontend stopped at repository-wide ESLint before its production build, and Teams build was skipped. No production database or deployment was changed. The existing lint debt remains open and must be addressed in focused, behaviour-preserving batches; it must not be represented as resolved by changing lint severity.

### Workflow repair — 19 November 2026

The incremental-lint workflow edit was subsequently found to contain malformed trailing shell lines and a duplicated Teams build section. The malformed workflow caused GitHub Actions runs to fail before job creation. This was corrected by restoring the known-good workflow structure, removing the orphaned commands and duplicate build, and retaining the backend checks and both full frontend production builds.

The frontend lint steps now lint only changed JavaScript/TypeScript files relative to the push or pull-request base. Full production builds remain mandatory for both `frontend-v02` and `frontend-team`; the existing repository-wide lint backlog is not represented as resolved. Checkout now fetches full history for the comparison. The changed-file list is passed to ESLint through `xargs`; an empty list skips only the incremental lint invocation, not the production build.

- Workflow repair commit: `91d727f777fadfa5455d79d1c70db90fa30b5a89`.
- Follow-up correction to changed-file input formatting: `9844198f0cb5eec759c3bb64ec51dfa011ba8445`.
- The repaired workflow was recognised by GitHub and created a real job. At the time of this note, run `44624319758` had passed backend dependency audit, compilation, migration/rollback rehearsal, Python static checks, backend import, the complete backend test suite and HTTP startup smoke test; the learner production build was still running. A subsequent run for the formatting correction was queued.
- No production deployment or production database change was performed. Release readiness remains unconfirmed until the latest-main run completes successfully, including both frontend builds.

## Route scroll, visible landing motion and server-side session revocation — 19 November 2026

### Route navigation
- Added a root-level pathname listener that returns the document to the top after client-side route changes. Same-page hash navigation remains browser-native.

### Landing-page motion
- Added an ambient moving gradient, orbiting outline, animated accent treatment and gentle featured-course float to the hero.
- Strengthened section entrance and staggered card animations. Content remains visible when JavaScript or IntersectionObserver is unavailable; reduced-motion preferences still disable non-essential movement.

### Session security
- Reduced the backend JWT lifetime to 15 minutes and clamp the configured lifetime so production environment overrides cannot extend it beyond 15 minutes. Learner, cohort and internal staff tokens use the same cap.
- Added a server-side revoked-token store. Only a SHA-256 fingerprint and token expiry are stored; the bearer token itself is never persisted.
- Learner and internal staff logout endpoints revoke the presented cookie/bearer token before returning success. Every learner/cohort/staff authenticated request checks the revocation store and fails closed if that store is unavailable.
- Frontend logout waits for the server response instead of launching a fire-and-forget request.

### Database and release boundary
- Migration `20261119223222_revoked_auth_tokens.sql` matches the live migration ledger. The RLS-protected table is applied in production, and verification confirmed browser roles have no table privileges while `service_role` has the required read/write permissions.


## 4. Recent learner dashboard, session and achievement corrections — 19 November 2026

- Dashboard overall progress now uses all accessible enrolled courses, including completed enrolments, and weights lessons plus published assessments. Completed courses contribute 100%; the active-course count remains separate.
- The dashboard no longer exposes a manual Refresh control. It revalidates learning records on focus/visibility and periodically while open; evidence and credential cache lifetimes are shorter to keep achievement updates current.
- Current and longest streak values both render explicit day units.
- Password changes update `password_changed_at`, which invalidates older learner, admin and internal staff JWTs on their next authenticated request. The password-change response issues a fresh short-lived session only to the browser performing the change; other devices must sign in again. Password-reset flows continue to invalidate all existing sessions.
- Added a criteria-driven `course_completion` badge awarder. The live Pheonix database had an empty skill and badge catalogue; the migration seeds the Data Analytics Foundations skill and badge for the Introduction to Data Analytics course, and backfills the badge to existing completed enrolments. This is course-completion recognition only and does not inflate verified mastery, which still requires approved project evidence.
- The live migration `20261119224623_course_completion_skill_badges` was applied and verified. The course had two completed enrolments and both were awarded the badge.


## 21 November 2026 — AI course production, video rendering and publication

- Added a staff-only Course Studio route inside Learnora ME. Curriculum and lesson-package generation use the existing AI gateway and the `content.generate` permission; creators, tutors and customer organisations do not receive this capability.
- Added private generation-job and versioned lesson-package schema, atomic draft creation, asynchronous video-render jobs, worker lease recovery and atomic final publication. The selected global track is linked only at publication, after checking active/completed track enrolments.
- Added sequential generation of missing lesson packages, draft global-track creation, and a final course/track publication action for staff with `content.manage`. The generic content editor cannot bypass the Course Studio publication checks for AI-generated courses.
- Added a Kokoro ONNX + Pillow + FFmpeg renderer that creates narrated visual MP4 lessons with captions, plus a private R2 upload and signed-playback integration. The current renderer provides deterministic slides, diagrams, tables, code examples and guided steps; actual software screen recordings remain a separate media-production path.
- Added per-lesson AI/human video-source selection. AI video lessons use the R2 render worker; human-produced videos upload directly to the same private R2 bucket through a short-lived staff-only PUT URL. Both can be previewed by staff and are required to pass the final publication checks.
- Confirmed that the learner workspace already supports native signed video playback, YouTube/Vimeo embeds, lesson content, resources and private learner notes. The AI course format uses one primary video per lesson followed by a concise note.
- Prepared pilot briefs for Data Analytics, Excel Fundamentals and Front-end Web Development. The mock Introduction to Data Analytics course is not deleted; its retirement is deferred until the replacement is published and its existing learner history is preserved.
- Added migration assertions, backend tests and a CI smoke test for real Kokoro narration and FFmpeg MP4 rendering. A CI checkpoint passed the renderer smoke test, migration rehearsal and backend suite; later changes are awaiting a complete run.
- **Release boundary:** no production Supabase migration, R2 bucket/secret configuration, Vercel environment change or deployment has been performed. These remain explicit approval gates.
## 21 November 2026 — cohort lesson media and release verification

- The individual learner workspace already returned ready lesson videos and generated short-lived Supabase/R2 playback URLs after the normal course enrolment and module-unlock checks.
- The cohort lesson API previously returned only the assigned lesson and module. It now returns ready lesson-video records only after active cohort membership, active course assignment, active lesson assignment, published lesson status and course/module ownership have all been verified.
- Cohort lesson responses use the shared media signer. Private Cloudflare R2 and legacy private Supabase videos receive short-lived signed URLs; supported YouTube/Vimeo records remain available to the existing player. Render jobs, draft lesson packages and private teaching scripts are never returned to learners.
- A read-only check of live Pheonix confirmed the legacy video signer defaults to private `learnora-course-media`, resources use private `learnora-resources`, and a separate private `learnora-videos` bucket also exists but is empty. All three buckets have zero objects; `lesson_videos` has zero rows and no `storage_bucket` column. The shared signer previously defaulted Supabase files to a non-existent `course-resources` bucket; it now accepts a media-specific default and uses the correct video/resource bucket. A unit test verifies both mappings. No live storage objects or bucket settings were changed.
- The cohort learner page now plays the primary video before the concise lesson notes and persists video position/percentage to the existing cohort progress record. It resumes from the saved position when the video metadata is loaded.
- The standard individual learner video player also resumes native MP4 playback from `learnora_lesson_progress.last_position_seconds` when video metadata loads; this reuses the existing progress record and introduces no schema change.
- Regression coverage was added for an assigned cohort learner receiving a ready video with a signed URL. The Cohort Learning Access Tests workflow passed on commit `e776c2613f`.
- An earlier production check exposed a nullable Course Studio job ID passed to the video-status refresh function. The action now checks the ID and is disabled while it is absent. The full Learnora production checks passed on commit `e776c2613f`, including both website builds.
- The scheduled renderer workflow's latest run completed successfully as a workflow but skipped its rendering steps because the required Supabase and R2 worker secrets are not configured. This must not be described as an end-to-end render test.
- The landing page currently passes `hideBrand={false}` to `PublicNav`; the shared `Logo` renders “Learnora ME”. The signed-in dashboard navigation also renders the wordmark. The earlier missing-brand report is not reproducible from current `main` source, so no additional logo edits were made.
- No deployment, production migration, live R2 bucket creation, production secret change, or test-course retirement was performed.
- A follow-up review found that a worker retry after an interrupted metadata write could insert a duplicate `lesson_videos` row. The worker now reuses an existing row for the same lesson/provider/object key, and the pending Course Studio migration adds a partial unique index for Cloudflare lesson media. The renderer self-test verifies the retry path.
- The curriculum prompt was aligned with the Pydantic contract: it explicitly requests both the required short catalogue description and full course description, uses only fields represented by the module schema, and states the 1–5 minute lesson estimate range. A regression test guards the required description fields.
- The Data Analytics pilot brief now follows the agreed Module 1 lesson sequence and includes the short-note guidance for careers, career motivation and the data analytics/data analysis comparison.
- These follow-up worker/schema/prompt changes are committed to `main`; the next full production CI run is pending.

- Human-produced lesson video uploads now read local MP4 metadata before requesting a signed R2 upload ticket and enforce a 1–300 second duration in both upload/finalisation request models. The atomic course-publication RPC also rejects ready video assets without a duration in that range.
