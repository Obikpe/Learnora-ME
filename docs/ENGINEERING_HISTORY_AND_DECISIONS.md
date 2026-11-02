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

- **Quiz tutor restriction:** the course player removes lesson-tutor entry points and hides the tutor navigation while a quiz is opening or active. The AI page checks the backend session endpoint, and the backend denies tutor requests while any unexpired quiz session exists. The lock is held through the results view and released when the learner closes the quiz. Abandoned sessions expire after two hours. The new quiz_active_sessions migration is service-role-only with RLS and a rollback script.
- **Certificate revocation:** added nullable revocation timestamp, staff actor and reason fields through an additive migration. An internal endpoint requires the existing content.manage permission, writes an audit event, and is exposed in a Teams certificate register. Public verification reports revoked certificates as invalid and does not expose internal revocation notes.
- **Project review and mastery:** approved evidence is prepared before the submission status changes to approved; mastery reads only evidence whose source submission is approved and whose skill is mapped to the source project. Returned work no longer contributes to mastery. Learner history distinguishes approved, returned, reviewed and awaiting-review states and shows feedback.
- **Tests and CI:** contract tests cover quiz tutor lock, certificate projection privacy/revocation and migration inventory. Both new migrations and rollback rehearsals are included in the disposable database workflow. GitHub Actions on the evolving main branch were still queued at the last status check; no success is claimed for the final candidate SHA until a run completes.
- **Live database and release boundary:** no production migration, data mutation, environment change, free-mode activation or deployment was performed. The quiz-session and certificate-revocation migrations remain pending the disposable replay gate and separate explicit approval for the active Pheonix database. Existing Paystack, subscriptions, trials, entitlements and Pro implementation are unchanged.

### Release preparation and deployment evidence — 2 November 2026

- Built the current `Learnora-ME` source explicitly into the existing Vercel projects using the monorepo roots `frontend-v02`, `frontend-team` and `backend-python`. All three staging deployments reached READY; the learner and Teams builds completed Next.js compile/typecheck/static generation, and the backend build completed under Python 3.12.
- Staging deployment IDs: learner `dpl_HWmkfWuybYhABMbXgRZ9DZEFCgm4`; Teams `dpl_7hiqZUWwurpQSaAncjgCyYSzceEv`; backend `dpl_DTamp1i4THKQbvSzP4HghZxtY8Vx`. No production alias was promoted.
- Added `FREE_ACCESS_MODE=true` to the backend Vercel Production environment only. It is reversible and applies on the next production deployment. Existing paid billing paths were not deleted or rewritten.
- The live Supabase ledger still ends at `20261028171902`; the four 2 November migrations remain unapplied. Catalog inspection confirms the quiz session table and certificate revocation columns are absent. Do not deploy the new backend to production until those dependencies have passed disposable replay and received separate production migration approval.
- Consolidated general CI to one workflow/job and narrowed the expensive cohort database workflow to cohort-specific paths. The latest general workflow remained queued; the queued state is not a pass.
- Existing production Teams/backend deployment metadata referenced `Pheonix-Analytics`; the new staging deployments explicitly reference `Learnora-ME`. Manual production deployment can use the current repository source, but future automatic Git deployment linkage still needs a deliberate Vercel Git connection check.
- Vercel showed no runtime error clusters for the existing production projects in the previous 24 hours. This is not a substitute for authenticated learner/staff acceptance on the new staging deployments.
