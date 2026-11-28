# Learnora ME and Learnora Teams — Product Engineering Roadmap

**Last reviewed:** 28 November 2026  
**Branch policy:** all documentation and implementation work requested for this effort goes directly to `main`; do not create or switch to another branch.  
**Release policy:** documentation commits do not authorise production migrations, deployments, or destructive data changes.

This roadmap records priorities, dependencies and exit criteria. It is not a claim that unfinished items have already shipped. Cross-cutting security, data-integrity, migration-provenance and release checks remain mandatory gates for safe individual learner delivery; they do not authorise reordering the product sequence or building deferred customer workflows.

## Current approved product sequence

The product sequence below is governed by [PRODUCT_DECISIONS.md](PRODUCT_DECISIONS.md):

1. Complete the normal individual learner experience in Learnora ME.
2. Build the separate Learnora Teams website, including internal course/content production workflows.
3. Return to Learnora ME for the corporate organisation experience.
4. Build independent tutor functionality separately.

Preserve existing cohort functionality, accounts, access rules, assignments, progress and historical data throughout the current individual learner phase. Cohort and corporate organisation workflows are distinct; neither is to be flattened into the other. Security and migration work in P0/P1 is performed only as necessary to protect data and make the individual learner release safe. Organisation/cohort completion, creator/tutor workflows and the full Teams website must not be pulled into the current individual learner scope.

## Cross-cutting release gates

P0 security containment and P1 migration/schema provenance work remain release-safety requirements where relevant to the individual learner journey. A gate may block release, but it does not change the product implementation sequence above.

## Status definitions

- **Done (evidence-backed):** code/docs and a successful relevant test or verification are available.
- **In progress:** some implementation exists but acceptance evidence is incomplete.
- **Blocked:** a dependency, environment, mapping or approval is required.
- **Planned:** not yet implemented or verified.
- **Needs revalidation:** older documentation/test evidence exists but must be repeated on current `main`.

## P0 — Security containment and CI trust

### P0.1 Cohort login correctness and enumeration resistance

**Scope:** `backend-python/routers/cohort_learners.py`, cohort login tests.

- Use exact username matching, never `ilike` or wildcard matching.
- Validate username syntax before querying; return the same generic 401 response for malformed, unknown and incorrect credentials.
- Perform password verification against a precomputed dummy hash for unknown accounts.
- Add username and client-IP failure buckets; ensure five failed attempts lock the sixth attempt under the documented policy.
- Add regression tests for `%`, `a%`, `_`, malformed names, unknown-user timing path and lockout behaviour.
- Keep per-process counters labelled as temporary only; production serverless protection needs a shared store (Supabase/Redis) and abuse monitoring.
- Verify proxy/client-IP trust assumptions from actual deployment configuration before relying on forwarded headers.

**Acceptance:** targeted tests and full backend suite pass on main; no wildcard can match a real account; response body/status is indistinguishable for invalid credentials.

### P0.2 Database browser-grant review and safe revocation

**Scope:** Supabase grants, migration history, cohort CI workflow.

1. Read-only inventory of `information_schema.role_table_grants` for `anon` and `authenticated`.
2. Inspect default ACLs in `pg_default_acl` by object-creating role and schema.
3. Confirm all clients use the FastAPI backend for protected tables; explicitly identify any legitimate public browser reads before revoking.
4. Test grant revocation in a disposable database restored from the catalog-derived current schema and separately on the replayed legacy chain.
5. Make CI fail if prohibited grants remain on backend-only tables or if newly created tables inherit broad grants unexpectedly.
6. Prepare an exact, separate rollback SQL artefact that reflects the actual previous ACLs. Do not guess grants.
7. Add a timestamped migration only after the source chain/ledger is reconciled and staging tests pass.
8. Deploy only after separate explicit approval, staging verification and a quiet-window/rollback plan.

**Acceptance:** table-by-table grant inventory approved; owner-specific defaults verified; backend API journey passes after revocation; direct browser access is denied where intended; rollback has been tested. No blanket revoke from all shared learning tables without proving the intended public access contract.

### P0.3 Merge-independent security findings onto the release baseline

Earlier audit and cohort work had separate branches/PRs; PRs #7–#10 were later merged on 21 October according to GitHub metadata. Do not assume every source-branch change survived. Compare current `main` against each finding and regression test.

- Course-content access guards.
- Atomic AI quota reservation.
- Module unlock checks.
- Team membership and tenant-scope guards.
- Cohort membership, activation, archive and lifecycle enforcement.
- Tests for cross-tenant access, revoked memberships, scoped course assignments and capacity.
- Finance atomicity and role separation.
- Instructor grading scope and audit history.

**Acceptance:** current-main code and tests explicitly cover each issue; no reliance on branch names or PR titles alone.

### P0.4 CI reliability and release signal

- Prevent unnecessary cancellation of required quality checks; use concurrency settings that preserve required evidence.
- Treat a cancelled run as not passed.
- Run all workflows on the same exact main SHA and retain links/results in the engineering history.
- Ensure grant/security assertions execute against the replayed schema as well as the catalog-derived fixture where relevant.

**Acceptance:** every required workflow concludes success on the exact candidate commit.

## P1 — Migration provenance and schema truth

### P1.1 Migration source provenance

Known historic uncertainty:
- `20261008100924_add_learnora_ai_profiles.sql` and `20261011051442_learner_onboarding_profiles.sql` were reconstructed from the live catalog, not verified byte-for-byte originals.
- Five timestamped SQL files dated 20 October exist and replay, but their original source blobs/paths were not independently verified in the earlier investigation.
- Historical migrations 001–015 contain data changes and must not be blindly replayed or marked applied based on object names alone.

Actions:
- Search Git history, prior trusted archives and original author/deployment artefacts.
- Compare source SQL to current catalog definitions and seed data.
- Mark each file as verified original, reconstructed, equivalent but provenance unknown, superseded, or unresolved.
- Do not call a reconstructed file an original recovery.
- Do not fabricate migration-ledger rows or re-run identity/permission seed migrations without record-level review.

**Acceptance:** provenance matrix complete with evidence and owner sign-off; unknowns remain explicit.

### P1.2 Full schema comparison

Compare columns/types/defaults, constraints, indexes, sequences, views, functions/bodies/configuration, triggers, RLS enabled/forced states, policies, owners, grants and default privileges. Distinguish catalog-derived current state from historical replay.

The previous reconciliation recorded differences including missing/extra columns, constraints, indexes, triggers, RLS states, one policy and a view. Those counts are a historical snapshot and must be recomputed from a single pinned schema snapshot before being used as current status.

**Acceptance:** machine-readable diff, reviewed classification for every difference, no automatic destructive correction.

### P1.3 Identity and seed lineage

- Resolve the Witstart role/membership set mismatch using explicit identity evidence.
- Compare AI permission mappings and quota values by key and value, not only row counts.
- Map legacy tracks/enrolments/progress/community/project objects to intended successors.
- Preserve both sides of unresolved identity conflicts until an authorised mapping decision is recorded.

**Acceptance:** no unresolved identity or seed mismatch is silently repaired; each transformation has a testable mapping and reconciliation report.

### P1.4 Schema grants and RLS guard

- Add negative CI assertions for browser-role grants on backend-only tables.
- Assert RLS and policy expectations table by table.
- Check `SECURITY DEFINER` function execute grants and pinned search paths.
- Cover default privileges for every relevant object owner.
- Keep public/anon-readable product content intentionally allowlisted and documented.

**Acceptance:** a test fixture with a forbidden grant fails; an approved allowlisted public read still works; API lifecycle tests pass with the intended ACLs.

## P2 — DEFERRED: Corporate organisation and cohort workflow completion

**Delivery status:** Deferred until after the normal individual learner experience and the Learnora Teams website, in accordance with PD-001. Preserve existing cohort behaviour and data; do not implement this work during the current individual learner phase.

### P2.1 Organisation lifecycle

- Organisation creation/request, activation and owner/manager membership.
- Organisation/team member management with active membership validation.
- Team creation, manager assignment, role validation and deactivation.
- Programmes and ordered programme-course relations.
- Contract entitlements and capacity constraints.
- Clear permission/error states and audit events for sensitive actions.

### P2.2 Cohort lifecycle

- Create/edit cohort and select its track/programme.
- Assign eligible courses and define capacity.
- Provision learners, validate membership, and handle duplicates safely.
- Assign tutors and learner access without widening scope.
- Activate/deactivate cohort-specific accounts.
- Progress, assessment gates and completion.
- Archive/close cohort; preserve required user history and deactivate relevant active state.
- Verify reactivation and capacity boundaries under concurrent requests.

**Acceptance:** authenticated end-to-end journey passes against disposable PostgreSQL/PostgREST; tests cover success, invalid state, cross-tenant operations, revoked membership, capacity race and archive/restore.

### P2.3 Course access invariants

- Separate organisation-wide grants from individual/team/cohort scoped grants.
- Require current active membership and a matching assignment for scoped access.
- Ensure stale enrolment records cannot preserve access after membership revocation.
- Validate module unlock prerequisites and assessment requirements.
- Enforce course-level instructor assignment before submission reads or grading.

**Acceptance:** tests prove allowed access and denial for every scope and revocation case.

## P3 — CURRENT PRIORITY: Normal individual learner experience in Learnora ME

**Scope restriction:** This phase is the normal individual learner journey only. Creator, tutor, cohort-management and corporate organisation workflows are not included merely because they share the Learnora ME application.

### P3.1 Public discovery and conversion

- Audit every public route and ensure the navigation and metadata are correct.
- Use accurate course records and honest claims.
- Make registration, sign-in, verification, reset and activation resilient.
- Test responsive layout, keyboard access, form validation and errors.

### P3.2 Learning experience

- Course/module/lesson progression.
- Notes, quizzes, attempts and progress persistence.
- Clear completion versus verified-skill distinction.
- AI learning assistance behind permissions and quota.
- Resume/re-entry behaviour and unavailable-content states.

### P3.3 Deferred creator and independent-tutor workflows

The following capabilities are not part of the current individual learner phase. Preserve their existing code and data, and schedule them only within the separately approved future tutor/creator product work:

- Application and status display.
- Approval/permission transitions.
- Creator dashboard and content management.
- Course publication state and ownership.
- Course-level learner submission access and grading.
- Grade revision policy and audit trail.

Do not treat the existence of these routes or APIs as permission to build or expose them during P3. Independent tutor functionality follows the product sequence in PD-001; cohort and corporate organisation tutor capabilities remain separately scoped.

## P4 — NEXT PRODUCT PHASE: Learnora Teams internal operations

**Delivery status:** Follows completion and acceptance of the normal individual learner experience. AI/content production ownership belongs to Teams; the Course Studio currently placed in Learnora ME is transitional.

### P4.1 Internal access boundary

- Verify session guard plus backend platform-staff permissions.
- Separate internal roles from customer organisation roles.
- Require explicit confirmation for high-impact mutations.
- Audit privileged actions and ensure errors do not leak sensitive values.

### P4.2 Operations surfaces

Review each existing section in `frontend-team/app/` and its `lib/api.ts`, `lib/content.ts`, and `lib/operations.ts` implementations:
- Super Admin overview.
- Organisations and internal organisation operations.
- Course/content operations.
- Creator operations.
- AI operations.
- Notifications.
- General section routes and session handling.

For each, document the API endpoint, required role, data source, empty/loading/error states, mutation confirmation, and audit event. Do not treat a visible page as proof of a functional workflow.

**Acceptance:** each action has a tested API contract, role denial test, successful operation test, and audit evidence where sensitive.

## P5 — Cross-cutting privacy, finance and operational hardening

Apply only the work required to protect the current individual learner phase and the relevant platform trust boundaries. Organisation- and tutor-specific items remain deferred with their respective product phases.

- Remove DOB from organisation responses unless the use case and role justify it; establish field-level privacy and retention.
- Review encryption for sensitive dates/identifiers and migrate safely where required.
- Make payout state and ledger insertion atomic (single DB transaction/RPC) with idempotency.
- Separate permission to edit user data from permission to execute creator payouts.
- Restrict CORS to explicit trusted origins; do not allow arbitrary preview origins with credentials.
- Add CSP and security headers after validating frontend/backend compatibility.
- Protect or disable public `/docs` and `/redoc` in production.
- Replace in-memory rate limiting with shared storage for serverless deployments.
- Verify Vercel forwarded-IP behaviour and trust only the configured proxy.
- Avoid activation tokens in query strings where a safer one-time exchange flow is possible.
- Make readiness output minimal and safe.
- Pin function/trigger search paths and parameterise query construction, including PostgREST `.or_()` filters.

**Acceptance:** threat-focused tests, deployment header checks, payout failure-injection tests, and documented privacy decisions.

## P6 — Release and recovery readiness

- Verify which Supabase project the deployed backend actually uses without exposing secret values.
- Maintain local development instructions and environment-variable examples.
- Run both frontend production builds and all backend suites on the same candidate SHA.
- Test restore/recovery using disposable data.
- Produce release notes with schema changes, API changes, migration steps, rollback steps and known risks.
- Keep staging, production and local test configuration separate.
- Only perform production migrations or deployment after explicit release authorisation.

**Acceptance:** clean CI, staging sign-off, verified target, rollback plan and recorded release decision.

## Suggested execution order

| Order | Work | Dependency | Release gate |
|---|---|---|---|
| 1 | Cohort login wildcard/timing regression tests | Current backend code | P0 |
| 2 | CI grant assertions and owner-specific default ACL inventory | Disposable DB fixture | P0 |
| 3 | Confirm main contains all audit hardening; fix gaps and tests | Source/PR comparison | P0 |
| 4 | Grant-revocation migration proposal plus tested rollback | Schema and client inventory | P0/P1 |
| 5 | Provenance and schema diff | Trusted snapshot and migration files | P1 |
| 6 | Identity/seed lineage | Reviewed user mapping | P1 |
| 7 | Organisation/cohort E2E and concurrency tests | Disposable test database | P2 |
| 8 | Learnora ME learner/creator journey verification | Stable API contracts | P3 |
| 9 | Learnora Teams workflow/permission verification | Stable internal API contracts | P4 |
| 10 | Privacy, finance and browser hardening | Security tests | P5 |
| 11 | Release readiness | All prior gates | P6 |

## Roadmap maintenance

For each completed item, record: date, commit SHA on `main`, files changed, test command/run URL, result, live-vs-disposable scope, and any residual limitation in `docs/ENGINEERING_HISTORY_AND_DECISIONS.md`. Never mark an item done based solely on a branch name, PR title, or old test run.


## Execution snapshot — 26 October 2026

This snapshot records what has been verified from repository metadata; it is not a release approval.

| Area | Current evidence | Status |
| --- | --- | --- |
| Active local setup | Root scripts and docs target `frontend-v02/`, `frontend-team/`, and `backend-python/`. Local frontends default to `http://localhost:8000` in development; `.env.example` uses `APP_ENV=development` and local frontend origins. Regression tests cover these contracts. | Implemented; root-script and frontend builds pass in CI. |
| Browser sessions | Current `main` uses HttpOnly cookies with `SameSite=Lax` through same-origin `/api` proxies. JavaScript stores only a non-secret session marker; legacy localStorage/sessionStorage bearer tokens are cleared. New verification/reset links use URL fragments and old query-string links remain supported. | Source implementation passes all five workflows on `5ef2cc1`; no Vercel deployment exists for that candidate. Coordinated deployment and browser acceptance remain pending. |
| Shared API/auth throttling | Current `main` still uses process-local normal-auth failure counters and SlowAPI's default in-process limiter. | Open; database-backed implementation is in draft PR #13. |
| Security hardening draft | PR #13 has successful recorded CI runs for commit `0b54f1cda55c7de548005cfcb515ad8c0c02ff2b`. Current `main` candidate `0cc35c58913ed198e7a9f2c15f91203b398b8221` independently passed backend regression, backend verification, both frontend builds, cohort-learning tests, and quality checks on the same SHA. | PR #13 remains unmerged; its shared limiter/permission migrations are not applied. The cookie-auth source changes on main are not deployed. |
| Creator sales mutation authorization | Recording, releasing, and refunding creator sales now requires `creator_payouts.process` (or the existing super-admin bypass), rather than the broad `courses.assign` permission. | Temporary restriction; dedicated creator-sales permissions and atomic ledger operations remain pending. |
| Database migration sequence | PR #13 adds migrations required by its shared limiter, permission, and grant changes. Its own notes state that these must precede backend deployment. | Blocked on reviewed staging/migration sequence and explicit production approval. |
| Managed `supabase_admin` default ACL | Draft security work records that the connected database role cannot remediate these managed-role defaults. An operator-only SQL script exists on the draft branch. | Blocked on an authorised Supabase administrator and post-change catalog verification. |
| Migration provenance and identity lineage | The reconciliation below still records reconstructed historical sources, legacy successor mappings, and the Witstart identity-set mismatch. | Open; no speculative data repair is authorised. |
| API error disclosure | Course-content and internal video-upload failures now return generic client errors and log only exception types rather than raw database/storage messages. | Implemented with regression coverage. |
| Readiness endpoint | Public readiness output now reveals only `ready`/`not_ready`, not internal configuration/database checks; a token-protected readiness endpoint remains in PR #13. | Partially mitigated; protected probe still pending. |
| Trusted proxy/IP handling | Auth failure buckets and the global SlowAPI limiter trust `X-Real-IP` only when `VERCEL=1`; otherwise they use the ASGI peer address and ignore client-supplied proxy headers. | Implemented with regression coverage; shared rate-limit storage remains open. |
| Browser-driven product acceptance | CI evidence covers builds and API/database tests, not every complete browser journey across both applications. | Open. |

Do not merge the draft security PR solely because its recorded checks passed: first compare its current head and migration set to `main`, verify the complete required workflow set on one exact candidate SHA, and establish a safe deployment/migration order. Production database changes, data repair, and deployment remain separate approval gates.


---

## Strategic execution addendum — 31 October 2026: free launch before paid expansion

**This section changes the immediate execution order; it does not replace the original P0–P6 roadmap above.** The original priorities, acceptance criteria, organisation/cohort work, instructor/creator scope, security findings, and release requirements remain preserved. See [Free Launch → Paid Expansion Plan](FREE_LAUNCH_AND_PAID_EXPANSION_PLAN.md) for the full decision record and detailed acceptance criteria.

### Product direction

Learnora will first launch a usable free learner experience to build a real learner base and collect genuine, moderated feedback. Paid services and Pro subscription are a later stage. The existing paid system is retained; it is not cancelled or to be reconstructed later.

**Database clarification:** Learnora continues to use the already-active Pheonix Supabase project. Do not create or switch to a separate Learnora project. Existing records identify project reference `gihfupzvdpyrmynqgukz`; confirm configured target safely without exposing secrets before any operation. No production migration or deployment is authorised by this documentation update.

### Current implementation focus

Only these two product applications lead feature implementation now:

1. **Learnora Teams (`frontend-team/`)** — internal content and platform operations: tracks, ordered track-course relationships, courses, modules, lessons, video/resource uploads, publishing, learner information, and reliable platform analytics.
2. **Learnora ME (`frontend-v02/`)** — free learner discovery, track/course enrolment, lessons/media, assessments/activities supported by the product, progress/resume, and accurate course/track completion.

Both use the existing shared FastAPI backend (`backend-python/`) and active Pheonix Supabase project. The legacy `frontend/` is not the target.

### Revised execution order

| Order | Workstream | Exit evidence |
|---|---|---|
| 0 | Verify current main baseline, active Pheonix Supabase target, schema and billing/access implementation | Exact SHA and project identity recorded; no production mutation |
| 1 | Add central, reversible server-side free-access mode | Individual learner can use free catalogue without payment method, checkout, paid subscription or trial expiry; paid checks remain intact and regression-tested when mode is off |
| 2 | Complete Teams tracks and course catalogue management | Staff can create/edit/order/publish tracks and courses using canonical schema relationships |
| 3 | Complete Teams curriculum and media management | Modules/lessons, signed video uploads, resources, publication and playback verified end to end |
| 4 | Complete Teams learner oversight and analytics | Privacy-safe learner views and metrics with documented definitions and tested data sources |
| 5 | Complete Learnora ME learning journey | Discovery → enrolment → course/module/lesson → supported activities → progress/resume → completion |
| 6 | Add track-completion rating and optional review | Backend-confirmed completion, optional 1–5 rating/comment, separate publication consent, moderation and safe public display |
| 7 | Free-launch release acceptance | Both app builds, relevant backend/database/security tests, browser E2E, storage/auth checks, recovery plan and explicit release approval |
| 8 | Resume deferred original platform work | Organisation/cohort and instructor/creator workflows, plus remaining original security/finance/privacy/release items |
| 9 | Paid expansion | Separate product approval, free/paid catalogue rules, Pro benefits/pricing, payment lifecycle, learner transition policy and paid-mode regression acceptance |

### Reversible free mode — mandatory constraints

- Use one central server-enforced mode/configuration; do not scatter UI-only paywall bypasses.
- When enabled, individual free-launch learners must not be blocked by missing payment records, trial status, subscription expiry or card details.
- Preserve all subscription, payment, Paystack, trial, expiry, pricing, entitlement and Pro implementation/data.
- When disabled, the original paid enforcement must resume and pass regression tests.
- Keep authentication, email verification, staff permissions, tenant isolation, RLS, creator ownership and protected/private media controls intact.
- Do not mass-edit historical subscription records or turn payment routes into unauthenticated endpoints.
- Free access does not grant cross-organisation or administrative access and does not make unpublished/private content public.

### Deferred scope — retained, not removed

Organisation onboarding/workspaces, teams/cohorts/programmes, instructor/tutor/creator onboarding and tools, creator sales/payouts, organisation contracts/entitlements and the wider original commercial model remain in the original roadmap. They are deferred by sequencing only. Their existing schema, code, security boundaries and documentation must not be deleted or weakened.

### Track completion and public feedback

The learner may be invited to rate Learnora after the backend confirms completion of a track. The prompt must be dismissible; written comment is optional. Public display requires separate consent and moderation. Keep reviews genuine and searchable where appropriate; do not promise Google star-rich-results for self-serving reviews of Learnora itself. This feature must not delay the core Teams content workflow or learner journey.

### Active plan maintenance

For current work, use the sequence in this addendum and the detailed acceptance criteria in `FREE_LAUNCH_AND_PAID_EXPANSION_PLAN.md`. The original P0–P6 items remain applicable safety/release gates and the broader backlog; do not interpret this revised sequence as permission to ignore a security issue that directly affects the feature being changed. Record actual completion evidence in the engineering history with the exact main SHA and test results. Production SQL, production data changes and deployment continue to require separate explicit approval.


## 2026-10-31 implementation status update

The first learner/free-launch and Teams operations code layers are now present on `main`:

- Reversible server-side `FREE_ACCESS_MODE` access enforcement for verified individual role-`normal` learners, with billing history preserved and organisation/cohort/admin/creator access boundaries unchanged.
- Learner-facing catalogue and subscription messaging for the free-launch mode.
- Teams individual learner list/detail and first platform analytics endpoints/pages.
- Global track management using the existing generic `learnora_learning_paths` and ordered `learnora_learning_path_courses` model; public track discovery, course enrolment and backend-derived required-course completion are implemented.
- Progress calculations now use published learner-visible modules and lessons.

Do not mark this release-ready. Remaining acceptance gates: restore GitHub Actions runner execution and obtain passing test/build evidence; verify the checked-in schema against live Pheonix using a working read-only database connection; finish full browser/end-to-end learner and Teams acceptance; design and implement track-linked reviews with separate public consent and moderation; obtain separate approval for backend environment configuration and deployment. No production migration or deployment has been performed. The free mode remains off by default.


### Release verification constraints recorded — 2026-10-31

- Latest main commit at this check: `41735ba6cdedcc810420693a0cd77aa4d6ce48da`.
- All five GitHub Actions workflows triggered for this commit failed before executing a step: every job had zero steps and no assigned runner name. This is a runner-allocation/infrastructure failure, not evidence that the tests or builds passed or failed on the code. Automated acceptance remains unverified.
- Repository Vercel configuration has Git deployment disabled. The latest Learnora ME deployment predates the current main commit; no deployment was performed. The backend Vercel project is still linked to the older `Pheonix-Analytics` repository while the learner frontend project is linked to `Learnora-ME`; deployment linkage/root configuration must be reconciled before release.
- `FREE_ACCESS_MODE` remains default-off in code and has not been enabled in Vercel or production. No production database migration, data change, environment-variable change or deployment was made.
- The read-only SQL connection to the active Pheonix Supabase project remains unavailable, so checked-in baseline schema is not treated as live-schema verification.


### Implementation progress — 2026-11-01

The first free-access and global-track hardening changes are committed on `main`. The free-launch resolver now checks active organisation membership before granting individual access and fails closed if that check cannot be completed while the flag is on. Track curriculum lock state is scoped to per-track enrolments; track progress for unpublished tracks requires that track's enrolment source. Withdrawn individual enrolments can be reactivated safely; invited/suspended enrolments are not. Archived-track curriculum edits are rejected, and archived course progress retains assessment-lock checks. Regression tests were added for these paths.

Still outstanding before the planned free launch: run the backend/frontend regression suites on a functioning runner; verify the live Pheonix schema and storage bucket; implement the completion-gated learner review + explicit public-consent + moderation workflow; complete end-to-end acceptance of Teams content/media workflows and learner course/assessment/resume flows; reconcile the backend Vercel project repository linkage. The free-access environment flag remains off and no production migration/deployment was performed.



## Learner journey extension — phases 1–5 (2 November 2026)

This is an additive extension to the 31 October free-launch sequence. It does not replace the original P0–P6 roadmap, deferred organisation/instructor/creator work, or paid-expansion plan. See [Learner Journey Phases 1–5](LEARNER_JOURNEY_PHASES_1_5.md) for the architecture and implementation record.

| Phase | Work | Implementation status | Remaining gate |
|---|---|---|---|
| 1 | Confirm track/course/module/lesson architecture | Canonical global track model remains `learnora_learning_paths` → `learnora_learning_path_courses` → `learnora_courses` → `course_modules` → `learnora_lessons`; cohort track tables remain separate | Live Pheonix SQL catalogue revalidation remains blocked by read-only DB authentication; automated regression passes |
| 2 | Improve course discovery and track browsing | Public course payloads now include real published global track memberships; catalogue filters by actual track; track browse supports search and level filters | Browser/mobile acceptance |
| 3 | Optional AI onboarding and personalised plans | Optional individual-learner plan API/workspace; published track/course IDs are authoritative; validated AI weekly guidance and rule-based fallback; plan never changes curriculum | Disposable PostgreSQL migration/RLS/grant/rollback replay passed in CI; live Supabase migration and provider/browser acceptance remain |
| 4 | Assessments, grading and completion | Teams quiz settings/question editing, assignment editing and due dates, answer validation, grading audit events, learner performance, and assessment-aware course completion; configured quiz thresholds also govern module unlocking | Automated CI passed; browser E2E and immutable grade-revision history remain |
| 5 | Contextual AI tutor | Tutor receives verified course/lesson/assessment context, progress, recent quiz attempts and assignment feedback; answer keys excluded and assessment scope checked | Provider, browser and privacy acceptance |

### Completion rules introduced

- Published lessons count toward course completion; drafts and archived content do not count as current learner work.
- Every published quiz must have a passing attempt at its configured threshold.
- Every published assignment must have a latest submission graded at 70% or above of its maximum score.
- Published assessments are required; unpublished drafts do not block completion. Courses with no published assessments retain lesson-only completion.
- Module unlocking requires passing every published quiz in each earlier module at its configured threshold; an earlier module with no published quiz does not deadlock progression.
- Track completion continues to derive from required course completion; no separate learner-plan completion state is introduced.

### Free-launch protection

These additions do not change the central `FREE_ACCESS_MODE`, Paystack, checkout, subscription, trial, expiry, entitlement, or Pro implementation. The free flag remains server-side and default-off until separately configured and deployed. The new learning-plan table is backend-only with RLS enabled and an explicit `service_role` grant. Its migration and rollback passed against the disposable PostgreSQL database in CI; it has not been applied to the active Pheonix project. No production migration, data change, environment change, or deployment was performed for this work.

### Verification status

Implementation code checkpoint: `8e21f264744a1a49d26d0f81b3272f1c5d72f24a`. All five workflows passed on this exact candidate: [backend regression tests](https://github.com/Obikpe/Learnora-ME/actions/runs/41438366731), [backend verification](https://github.com/Obikpe/Learnora-ME/actions/runs/41438366705), [frontend production builds](https://github.com/Obikpe/Learnora-ME/actions/runs/41438366775), [quality checks](https://github.com/Obikpe/Learnora-ME/actions/runs/41438366744), and [cohort-learning/disposable migration tests](https://github.com/Obikpe/Learnora-ME/actions/runs/41438366779). The live Pheonix schema and production migration remain unverified/unapplied because the read-only database connection fails authentication and no staging Supabase branch is available. Browser/mobile E2E and provider/fallback acceptance remain required. Do not treat CI success as production-release approval.


## Next milestone after learner journey phases 1–5 — 2 November 2026

Do not begin unrelated feature work yet. The next milestone is restricted to:

1. **Live Supabase verification:** restore read-only access to the active Pheonix Supabase project; verify live catalogue/schema, migration ledger, RLS and grants against the repository baseline; reconcile the learning-plan migration; and prepare a tested, reversible migration plan. No production migration or data mutation without separate explicit approval.
2. **Browser-based acceptance:** verify learner discovery/enrolment, track/course progress, optional AI plan and fallback, assessment flows, Teams authoring/grading/performance, and contextual tutoring. The AI tutor must be completely hidden and inaccessible during every active quiz state (including navigation, review and submission), with no floating launcher, chat panel, keyboard/accessibility route or contextual tutor request available. Prompt-level instructions are not an adequate substitute for UI and backend enforcement.

The product-level learner-outcomes sequence is now defined in [Learner Outcomes Product Phases 6–8](LEARNER_OUTCOMES_PHASES_6_8.md): Phase 6 certificates and verification, Phase 7 Practice Lab and project submissions, and Phase 8 skill mastery map and learner portfolio. This user-confirmed sequence supersedes the older phase numbering for the next learner-outcome work. The earlier track-completion feedback proposal remains backlog work and is not a prerequisite or a renumbering of these phases.

The active Pheonix schema and migration ledger have now been rechecked read-only for the certificate, project, submission, skill and evidence tables. The relevant tables exist with RLS enabled and service-role-only direct grants. Follow-up hardening adds two additive migrations: quiz_active_sessions for backend-enforced tutor exclusion during quizzes, and certificate revocation fields. Both have rollback scripts and are included in disposable-database CI; neither has been applied to the live project. The historical learner-learning-plans migration discrepancy remains separate and must not be silently applied. Browser/mobile acceptance and passing CI remain release gates. Production migration/deployment remains separately authorised.

## Revised learner-outcomes priority — 2 November 2026

The product owner has confirmed a revised feature order after learner journey phases 1–5. This new order takes priority over the earlier proposed immediate Phase 6 track-feedback milestone below; that feedback proposal is retained as deferred backlog work.

1. **Phase 6 — Certificates and verification**
2. **Phase 7 — Practice Lab and project submissions**
3. **Phase 8 — Skill mastery map and learner portfolio**
4. **Phase 9 — Learning companion and community (later)**

Implementation details and acceptance boundaries are recorded in [Learner Outcomes Phases 6–8](LEARNER_OUTCOMES_PHASES_6_8.md). The official curriculum remains fixed; optional AI learning plans cannot modify it. Free-launch and paid-system protection remain mandatory.

### Live database revalidation — 2 November 2026

The read-only connection to the active Pheonix Supabase project is now available. Relevant certificate, project, submission and skill table columns, constraints, indexes, RLS and grants were checked. RLS is enabled and the inspected tables grant direct access only to `service_role`; no `anon` or `authenticated` grants were found. The certificate-number and skill-name uniqueness constraints required by the new APIs are present.

The active migration ledger still does not include `20261102090000_learner_learning_plans`, and `public.learner_learning_plans` is absent. That pre-existing Phase 3 release dependency remains unapplied. No production migration, data mutation, environment change, free-mode activation or deployment was performed.

The new Phase 6–8 code is committed on `main`; staging builds are now successful, but browser acceptance, final CI success, production migration approval and production deployment remain outstanding. Do not mark production release readiness until those gates have evidence.


### Phase 6–8 implementation follow-up — 2 November 2026

The learner-outcomes follow-up adds an auditable certificate revocation workflow and strengthens the quiz tutor lock across the frontend and backend. Teams has a credential register; public verification reports revoked credentials as invalid without disclosing internal revocation notes. Learner project history distinguishes approved and returned work, and only approved evidence mapped to the source project contributes to skill mastery. The two new schema migrations remain unapplied pending disposable replay and the separately required production approval. Automated workflow runs on the evolving main branch were still queued at the last status check; do not report them as passing until the final SHA completes. Phase 9 and the earlier track-review/consent proposal remain deferred.

### Release readiness recheck — 2 November 2026

The learner, Teams and backend applications have successful Vercel staging builds from the canonical `Learnora-ME` repository. The staging builds verify framework compilation, frontend type checking/static generation and backend Python packaging, but not authenticated end-to-end workflows.

The production backend's reversible `FREE_ACCESS_MODE=true` setting is prepared and will take effect on the next production deployment. The live Supabase database still lacks the four additive 2 November migrations required by the current learner-outcomes code. Those migrations must be replayed in a disposable database, reviewed and explicitly approved before applying them to the active Pheonix project.

General CI has been consolidated to one release workflow; the final run remains queued and is not yet evidence of success. Production deployment and browser acceptance are not yet complete. The older Teams/backend production deployments reference the former `Pheonix-Analytics` repository; release deployments must use `Obikpe/Learnora-ME` with the correct monorepo root directories. Preserve the existing production domains and same-origin API proxy.


## Learner experience repair and account lifecycle — 2 November 2026

The following source changes have been committed to `main` in `Learnora-ME`; they are implementation work, not production release evidence.

- Learner track navigation now has a dedicated `/dashboard/tracks` workspace for a learner's enrolled global tracks. The existing `/tracks` and `/courses` routes remain public discovery/catalogue pages. The progress API includes enrolment source markers so the workspace can resolve the exact track and display course-level progress.
- Removed the profile-editing implementation explanation and identified internal notes from the learner dashboard, evidence and course catalogue surfaces.
- Shared frontend API errors no longer expose internal request URLs or raw server error details for 5xx responses.
- Added light as the default interface theme, a persisted light/dark switch to public and dashboard navigation, improved light-theme contrast, and styled scrollbars.
- Added Support links to `learnorame@gmail.com` in public and authenticated navigation.
- Added email-confirmed individual learner account deletion. The confirmation link is single-use and expires after 60 minutes. Active recurring Paystack subscriptions must be confirmed cancelled before account deletion can finish. Organisation ownership must be transferred first.
- Account deletion stores a restricted snapshot in `deleted_account_history`, then anonymises authentication fields and marks the original user row as a deleted tombstone. This preserves foreign-key-linked learning and financial history rather than cascading away learner records. Password and verification/reset tokens are cleared. The history table is not browser-readable.
- Added regression-contract tests and updated the migration inventory for the pending 2 November migrations.

**Release dependencies and limitations**

- The live Pheonix database has not received the 2 November migrations. The certificate-revocation migration is required for `/api/credentials/me`; the quiz-session migration is required for the learner shell to safely establish whether the AI tutor should be hidden during an active quiz; the learning-plan and project-integrity migrations are also pending. The new account-deletion migration must be applied before its API can be deployed.
- No production SQL migration, production data mutation, environment change, or deployment was performed as part of this work.
- Vercel team access for `obikpes-projects` remains blocked by a 403 at the time of this entry. The production learner project source/root/deployment could not yet be revalidated. The current repository already contains `/courses`, public `/tracks`, and the new personal `/dashboard/tracks` route; production must be deployed from the intended `Learnora-ME` source with root `frontend-v02`.
- CI was not triggered to conserve the monthly Actions allowance. The added/updated tests have not been executed; browser acceptance and build verification remain required before release.


**Follow-up implementation checks — 2 November 2026:** The learner credentials endpoint now retries with the pre-revocation certificate column set when the additive revocation columns are not yet present, so Portfolio and Certificates can continue loading while the revocation migration awaits approval. Added the learner-specific `/dashboard/tracks` route and changed the sidebar to use it; public `/tracks` and `/courses` remain catalogue routes. Removed the remaining identified developer-facing notes from the AI, certificate, admin, team and landing-page surfaces. The new migration and frontend changes remain unbuilt/unreleased pending the production migration and Vercel access gates.


**Account-deletion migration review:** The production schema was checked before finalising the migration. Organisation-owner accounts are blocked from self-service deletion until ownership is transferred; active organisation memberships are suspended (the valid status in the live schema), team memberships are deactivated, and manager assignments are cleared. The retained user tombstone has its password, verification/reset tokens, email, display name, trial dates and access dates cleared or anonymised. The original email/name and a limited account snapshot remain in the service-role-only history table. The migration has not been applied to production.


**Migration ledger reconciliation note:** A read-only check of the live `supabase_migrations.schema_migrations` table found two additional applied versions, `20261102210054` (`shared_auth_rate_limits`) and `20261102210056` (`shared_api_rate_limit`), which do not currently have matching timestamped files in `supabase/migrations`. The repository also contains earlier files with related names. These entries must be reconciled against their recorded SQL before using a bulk migration push; they have not been replayed or modified during this work.

## Quiz-page-scoped AI tutor access — 3 November 2026

Corrected the quiz/tutor boundary to match the product requirement: the AI tutor is hidden and unavailable only while the learner is actively viewing the quiz/test interface. An unfinished or active quiz session in another tab, or a session left open after navigating away from the quiz interface, must not globally hide or disable the tutor. The dashboard sidebar now relies on the current page's explicit `hideTutor` state rather than querying all active quiz sessions. The AI page no longer blocks access based on the learner's global active-session list. The course player hides the tutor only while its quiz interface is open or opening; an orphaned session no longer hides the tutor once the learner is outside that interface. The backend no longer rejects tutor requests merely because any quiz session exists; requests carrying an assessment ID remain explicitly blocked. Updated the quiz/tutor regression contract. No build, tests, browser checks, CI, or production deployment were run.
- Quiz-session recovery in the course player now matches the current browser tab's client session ID only. An active quiz in another tab no longer creates a false 'unfinished quiz in this tab' state.

## Live catalogue seed: Introduction to Data Analytics — 3 November 2026

Seeded and verified the first published global Learnora learning track and course in the production Supabase project. This is data-only; no schema or application code was changed.

- Track: **Data Analytics** (`data-analytics`), ID `63715469-8b41-4972-b686-830fe55327e8`, published, global (no owner or organisation).
- Course: **Introduction to Data Analytics** (`introduction-to-data-analytics`), ID `e89cdf59-f4ad-4453-ab14-73e372fbce7e`, published, global Learnora-owned, beginner level, free for individual learners, linked as the required first course in the track.
- Module: **Foundations of Data Analytics**, ID `546aa84c-70d4-47aa-8371-6a3464599e32`, published.
- Lesson: **What Is Data Analytics?**, ID `9f051008-29e4-48b5-b1c2-c0b45954b812`, published, article, preview enabled, 35 minutes, approximately 10.6k characters of lesson content.
- The lesson covers data vs information vs insight, organisational uses, descriptive/diagnostic/predictive/prescriptive analytics, the analytics workflow, analyst responsibilities, an applied example, key points and reflection questions.

Read-only verification confirmed the track-course relationship, published statuses, exactly one module and one lesson for this new course, and one published global course/track in the catalogue. The existing 201 draft courses and the pre-existing Data Analytics Foundations course/module/lesson were left untouched. The public discovery API source exposes `GET /api/public/courses`, `GET /api/public/courses/{course_id}`, `GET /api/public/courses/{course_id}/structure`, `GET /api/public/tracks` and `GET /api/public/tracks/{track_id}`; these routes are registered in `backend-python/main.py`. A live HTTP request to the deployed Vercel API could not be completed from this environment, so production browser/API availability is not claimed as independently tested.


## Learner dashboard redesign — implementation in progress (3 November 2026)

- Dashboard activity tracking schema and backend endpoints are present on `main`; the learning-time/streak migrations have now been applied to the active Pheonix Supabase project.
- Learner session tracking uses visible-page heartbeats and a five-minute recent-interaction window. Meaningful learning days are recorded for first-time lesson completion, passed quizzes and assignment submissions; cohort lesson completion is recorded through the cohort progress API. Sign-ins alone never extend a streak.
- Dashboard summary includes learning time, current and longest streaks, and recent meaningful learning days. The cohort dashboard now displays the same activity metrics. The tracker is mounted for cohort routes as well as the standard learner shell, and existing `witstart` learner-role accounts are eligible for tracking.
- Active sessions are reused across tabs and protected by a partial unique index. Heartbeat/end accounting is atomic in service-role-only database functions, caps each counted interval at 60 seconds, and uses wall-clock timestamps. Hiding a tab pauses its contribution rather than ending a session shared by another active tab.
- WitStart learner accounts and cohort memberships remain intact. No account, membership, enrolment, or historical learning record was deleted or migrated.
- Remaining acceptance work: run local frontend/backend checks and browser acceptance when the local development environment is available. Do not trigger GitHub Actions or Vercel deployments without explicit instruction.


## Learning time and streak tracking integration — 3 November 2026

### Database
- Applied migration 20261103155243_learner_learning_sessions_and_streaks to the active Pheonix Supabase project (gihfupzvdpyrmynqgukz). It creates learning_sessions and learner_learning_days, with RLS enabled, no browser-role table grants, and service-role-only access.
- Applied migrations 20261103155546_atomic_learner_learning_session_accounting, 20261103155555_fix_atomic_learner_session_elapsed_accounting, and 20261103160004_use_wall_clock_for_learner_session_elapsed_time. These add one-active-session-per-learner uniqueness, serialized session creation, atomic heartbeat/end operations and wall-clock elapsed-time calculation.
- Database smoke checks ran inside rolled-back transactions: duplicate starts reused one session; active heartbeats counted elapsed seconds; inactive heartbeats/end did not count time; learning-day upserts combined activity types and incremented the daily activity count. No test rows were retained.
- Existing activity tables were empty immediately after the initial migration. The new tracker begins collecting data from qualifying activity after integration; historical time is not fabricated or backfilled.

### Application integration
- backend-python/routers/progress.py now calls the atomic session RPCs using the authenticated learner identity and account type. A learner cannot submit another learner's ID to read or update a session.
- frontend-v02/components/dashboard/LearningSessionTracker.tsx starts/reuses a session, sends 30-second heartbeats, stops counting when the page is hidden or interaction has been idle for five minutes, and pauses rather than ending a session when one tab is hidden. Existing normal, witstart and cohort learner identities are supported; admin/privileged organisation roles are excluded.
- The standard My Learning dashboard already reads /progress/learning-summary; the cohort dashboard now reads the same authenticated summary and shows total active learning time, current streak, longest streak and recent learning activity.
- Live learning-summary and session endpoints are excluded from the frontend API response cache so dashboard refreshes do not show stale activity.
- Existing backend event hooks record first-time individual/cohort lesson completion, passed individual quizzes and individual assignment submissions. Cohort lesson completion is recorded through the scoped cohort progress route. The current cohort learner UI exposes assigned lessons; it does not currently expose cohort quiz or assignment submission routes.

### Preservation and release boundaries
- Rechecked WitStart membership records after migration: 25 cohort membership rows and 24 linked public.users accounts remain. No WitStart account, membership, enrolment or historical record was deleted.
- Migration SQL and rollback artefacts are committed under supabase/migrations/ and supabase/rollback/ with the live ledger versions. The rollback for the two function-correction migrations is intentionally a no-op rather than restoring a known-bad elapsed-time implementation.
- No Vercel deployment, GitHub Actions workflow or CI run was triggered. Frontend builds, Python tests and browser acceptance have not been run in this environment; a focused backend route test file was added but remains unexecuted. Production runtime behaviour is therefore not claimed as fully browser-verified.

## Authentication loading and assigned-learner redirect correction — 3 November 2026

- Removed the full-page skeleton replacement from the standard learner login screen. The login form now remains visible while authentication runs; the submit button carries the inline “Signing in…” state and authentication errors remain on the form.
- Applied the same no-full-page-skeleton behaviour to cohort username login and added an inline submit state. Registration already used inline button feedback and did not have a login-style skeleton replacement, so its existing dashboard skeleton behaviour is unchanged.
- Hardened the standard login redirect: a `next` path is honoured only after `/auth/me` has successfully resolved and the account is an individual normal learner with no cohort or organisation assignment. Organisation/cohort/WitStart-linked learners ignore course-originated `next` paths and are sent to their normal dashboard entry instead. This prevents the sign-in callback itself from returning an assigned learner to a public course/enrolment intent.
- This is a frontend redirect safeguard, not a replacement for backend course-enrolment and course-content permission checks. Direct URL/API access must continue to be enforced server-side.
- No cohort or organisation dashboard pages were changed in this step. The agreed shared-dashboard implementation remains the next workstream: reuse the individual learner Shell, Sidebar, Topbar and dashboard experience, while filtering destinations and data to assigned cohort/organisation learning only.
- No deployment, GitHub Actions run or CI test was triggered. Browser/build verification remains outstanding.
- The public course detail page also treats a learner with cohort, organisation or WitStart assignment metadata as ineligible for individual self-enrolment, including when a free-course enrol intent is present. This is a client-side eligibility guard only; backend enrolment and content endpoints remain the authoritative access boundary and must be verified before the assigned-learner access work is considered complete.

## Assigned-learner backend access audit — 3 November 2026

The backend access audit identified and corrected several paths that could otherwise let assigned learners inherit individual course access.

- Public course and public track self-enrolment now share a server-side individual-account guard. It requires a global normal learner account and checks active organisation-learner and cohort memberships in the database; it does not rely only on JWT organisation claims. This closes the explicit-free-course path that previously bypassed the free-launch-only identity check.
- Generic course-content access no longer treats a personal enrolment with a null organisation as permission to read a course while the request is operating in an organisation context. The learner must instead have the organisation's active assigned-course grant or a valid active organisation-scoped assignment.
- The shared progress access resolver now rejects active cohort-account identities from generic individual progress routes. For organisation learners, it requires an active learner membership plus a matching active organisation-scoped assignment or an active organisation-wide assigned course grant and current organisation entitlement. It rejects unscoped personal enrolments when the account is operating as an organisation learner.
- The learner's /api/progress/me course list is filtered through the same access resolver. The common enrolment guard also protects lesson content/workspace, media signing, notes, progress writes, course activities, quizzes, quiz attempts, assignments and submissions because those routes use that resolver.
- Dedicated cohort learner routes remain separately scoped: the authenticated cohort account and active cohort membership are resolved server-side, each course must have an active learner-specific course assignment, and lesson content/progress requires an active lesson assignment tied to that course assignment. Cohort learner IDs and requested course/lesson IDs are not accepted as substitutes for those checks.
- The public catalogue endpoints intentionally continue to expose only published public course metadata and course structure (titles/descriptions and lesson metadata); they do not return lesson body content, videos, resources or assessment questions. Authenticated content and media routes enforce the assigned-access checks above.

**Preservation and verification boundary:** Existing individual free-launch access, paid billing records, organisation-wide assigned-course grants, scoped cohort/team/individual assignments, and existing WitStart cohort membership records were not deleted or migrated. The changes were committed directly to main. No GitHub Actions, CI, build, test suite, browser acceptance or Vercel deployment was triggered. The backend source was re-fetched after each write for targeted inspection, but runtime behaviour still requires focused automated tests and authenticated API/browser acceptance before release. Do not mark this access boundary fully release-verified yet.

## Shared cohort and organisation learner dashboard — 3 November 2026

The cohort learner experience now uses the same Learnora ME dashboard shell as individual learners rather than a separate visual layout.

- Cohort overview, assigned-course and lesson pages now use the shared Shell, Sidebar and Topbar. They use the existing theme tokens, responsive navigation, account controls and headset support link.
- Cohort content remains assignment-driven: the dashboard lists only courses returned by the authenticated cohort learner endpoint; course and lesson pages call the learner-specific assignment APIs. No public course catalogue or self-enrolment controls are rendered.
- The cohort layout remains the single owner of LearningSessionTracker so session accounting persists across nested cohort routes. Shared Shell instances on cohort pages disable their own tracker mount to prevent duplicate tracking.
- Organisation learners continue through the standard individual learner dashboard and shared components. Their active learner membership marks the account as assigned-only: public course discovery, course search, learning-track discovery, recommendations and the AI course-discovery assistant are not rendered.
- Public course and track catalogue pages, public track detail pages, dashboard track pages and direct unassigned course-detail routes redirect assigned learners to their appropriate dashboard. A course-detail route is retained only when the authenticated learner has an active scoped enrolment/assignment verified by the backend.
- Practice projects now use the central scope-aware enrolment resolver. Organisation/cohort learners see course-linked projects only when their course assignment is active; course-less public practice projects remain individual-learner-only. Submission endpoints enforce the same rule.
- When an organisation adds or reactivates a learner after organisation-wide courses have already been assigned, the membership API now creates the learner's organisation-scoped enrolment rows for those active assigned-course grants. This prevents newly added learners from being incorrectly treated as having no assigned courses.
- Legacy organisation membership role "member" is treated as assigned-only alongside "learner" in the relevant access checks; it does not inherit individual free enrolment or unscoped course-content access.
- Existing individual learner discovery and self-enrolment remain available. No organisation, cohort, course assignment, enrolment, billing or learner records were deleted or migrated.

**Verification boundary:** Source files were re-fetched after edits and checked for the expected route guards, shared shell usage, responsive navigation restrictions and single cohort tracker mount. No build, test suite, GitHub Actions/CI or Vercel deployment was run. Browser-level mobile and desktop acceptance, and focused backend regression tests for individual, organisation and both cohort account models, remain outstanding.

## Assigned-learning access verification follow-up — 4 November 2026

A second source-level audit found and corrected two cohort-scope gaps.

- Generic course-content endpoints now reject the newer dedicated `account_type="cohort"` identity. Those accounts must use the cohort-learning endpoints, which validate the active cohort account, active cohort membership, exact assigned course, exact assigned lesson and course/lesson relationship.
- Legacy WitStart learners represented by `public.users` plus `cohort_members.user_id` retain their existing cohort-assignment workflow. Authentication now resolves their organisation from the active cohort when they have no duplicate `organisation_members` row. Progress and course-content checks require an active `cohort_course_assignments` record for that learner's cohort; an organisation-wide grant alone cannot substitute for it.
- Legacy cohort progress resolves the organisation through the active cohort and can therefore continue to load its existing organisation-scoped `learnora_enrolments`. The helper still validates the cohort and course assignment before returning progress.
- The shared learner dashboard now suppresses public recommendations for WitStart, dedicated cohort, organisation-scoped and active organisation learner/member identities. Course and track discovery redirects also recognise organisation context and the legacy member role.
- Organisation-wide assigned-course synchronisation now runs for both current `learner` and legacy `member` membership roles.
- Added regression coverage for individual free-launch content and enrolment, individual global progress, organisation self-enrolment denial, both cohort account models, legacy cohort course-assignment isolation, and the newer cohort lesson assignment boundary.

**Verification result:** Current `main` source was re-fetched after the changes. Automated source assertions passed for the individual enrolment/content path, both cohort models, organisation membership restrictions, direct course/track route guards, and the cohort-specific lesson endpoints. The new/updated Python unit tests have been committed but were not executed in this session. No GitHub Actions/CI, deployment, or production data mutation was performed. Therefore this is a source-level verification, not a runtime or browser acceptance sign-off.

## Individual learner launch priority — 4 November 2026

This is the immediate execution focus and supersedes any interpretation that all Learnora Teams, organisation, cohort, independent tutor or creator workflows must be completed before Learnora ME can serve normal individual learners.

### Primary outcome

Make the normal individual learner journey reliable end to end in `frontend-v02/`:

- Register with a canonical email, verify the address and recover/resend verification.
- Sign in only after email verification; establish and verify the HttpOnly browser session before redirecting.
- Sign out cleanly; handle expired/revoked/invalid sessions without leaving stale authenticated dashboard state.
- Complete optional learner onboarding and load the learner's real profile.
- Discover published global Learnora courses/tracks, view details, enrol and enter course workspaces.
- See actual enrolments, resume learning, track progress, lesson completion, learning time/streak, activity, evidence, projects, skills and certificates in My Learning.
- Complete lessons, media, notes, quizzes, assignments and submissions with server-verified access and correct completion rules.
- Provide clear loading, empty, retry and error states on mobile and desktop.

### Work order

1. Complete the source inventory and access-path reconciliation for authentication, registration, account lifecycle, course discovery/enrolment, progress, content/media, AI, evidence, credentials and the dashboard.
2. Correct backend email identity checks, login resolution and session-state handling without changing existing learner records.
3. Add safe provisioning guards for the approved two-way exclusivity rule: individual registration cannot use an email already associated with an organisation/cohort-managed account, and organisation/cohort onboarding cannot use an email already associated with an individual learner. Whether one managed identity may belong to multiple customer organisations or cohorts is not decided here. Historical conflicts must fail closed for the affected path; do not auto-merge, delete or migrate existing records.
4. Verify the normal learner access path from public catalogue through enrolment, course content, progress, assessment and completion. Keep organisation/cohort-specific access checks intact.
5. Correct Learnora ME login/registration/verification/recovery flows and the authenticated learner dashboard together.
6. Add focused regression coverage for the affected identity, session, course and dashboard contracts. Avoid broad CI runs; no GitHub Actions or Vercel deployment unless separately authorised.
7. Record remaining runtime/browser/live-schema acceptance gaps honestly.

### Deferred, retained architecture

Organisation account invitations and the approved managed-account deletion/revocation workflow, organisation/cohort administration, tutor resource assignment and analytics, independent tutor onboarding/creator workspaces, creator finance, and the unresolved technical identity architecture/migration remain future work. Preserve their existing source, schema, data and trust boundaries. Do not build these workflows in the individual learner launch pass.

The approved identity rule is two-way email exclusivity between normal individual learner accounts and organisation/cohort-managed accounts, including managed tutors. It does not yet decide whether one managed identity may belong to multiple customer organisations or cohorts. Because the repository schema has separate `users`, `admins` and `cohort_accounts` identity sources and existing cohort records must be preserved until an approved transition plan exists, application guards are only an interim measure. A race-safe implementation requires a separately reviewed uniqueness design and legacy-conflict plan; do not claim that guarantee until it is safely implemented and verified.

## Individual learner implementation status — 9 November 2026

The implementation pass has moved beyond the initial inventory. The following changes are committed on `main`:

- Authentication now checks all three email identity sources, rejects duplicate user/admin rows instead of selecting an arbitrary match, fails closed when organisation membership resolution is unavailable, and rejects unresolved retained cohort references.
- Registration, login, cohort provisioning, verification resend and password recovery apply the reserved-identity checks. Password-reset token use is conditionally claimed before the password update so concurrent submissions cannot both reuse one token.
- Account deletion requires an individual identity and rechecks retained organisation/cohort context at confirmation time. An account that became managed after the deletion email was sent cannot be deleted through the stale confirmation link.
- Individual course self-enrolment is scoped to personal rows, reactivates a withdrawn personal enrolment in place, and rejects ambiguous duplicates or non-reactivatable statuses.
- Progress, lesson content, notes, workspace, media and AI lesson-context paths now use the central scope-aware enrolment checks. Draft courses/modules/lessons are hidden from learner contexts while authorised course-management roles retain draft visibility.
- The historical course-detail copy says an organisation-managed identity must be released before individual registration. That wording is superseded: the approved product rule is that the managed account must first be deleted through the authorised access-revocation process. Individual onboarding redirects cohort and organisation-managed identities to the appropriate workspace.
- The reported Vercel TypeScript error in the learning-session tracker was fixed by declaring the browser interval handle as `number`, matching `window.setInterval()`'s DOM return type in the combined DOM/Node type environment. The timer cleanup also explicitly checks for null. The correction is committed as `e51f5b60`; a post-fix production build is still pending.
- Focused regression tests were added or updated for duplicate email identities, auth recovery, deletion confirmation, enrolment reactivation, progress/content visibility, AI lesson scope and publication-state fixtures.
- A design-only Step 8 plan documents the future global identity registry and personal-enrolment partial unique index. It is not an executable migration and has not been applied.

### Remaining release gates

1. Run the focused Python test suite from `backend-python/` and fix all failures. Tests added in this pass have not been executed.
2. Run a fresh frontend production build after the timer fix. The supplied Vercel log is from commit `325d9b1`; the timer correction is later on `main`. No post-fix Vercel build has been observed.
3. Complete an authenticated browser walkthrough of signup, verification, login, dashboard, catalogue, individual enrolment, lesson content, progress, assessment, evidence and certificates.
4. Review the active Supabase schema and duplicate report before preparing any executable identity/enrolment migration. No SQL or live data changes are authorised in this pass.
5. Do not mark the individual learner launch as ready until the test, build and runtime/browser gates pass.

No deployment, CI run, SQL migration or live database mutation was performed for this implementation update.



## AI-assisted course production milestone — 21 November 2026

**Priority:** P1 — required to seed a credible catalogue before the planned learner outreach. This work must not bypass existing security, migration and release gates.

### Product and architecture decisions
- Preserve the canonical Track → Course → Module → Lesson hierarchy. Tracks group ordered courses; courses can exist independently and can also belong to tracks.
- Introduce AI course production as an internal Learnora ME capability for authorised Learnora Teams staff only. Independent creators, tutors and customer organisations must be denied by backend policy.
- Keep the Learnora Teams website separate. This phase integrates the capability into the shared backend and Learnora ME; the separate Teams website build follows once the Learnora ME integration is stable.
- Extend the existing named-profile AI gateway; do not replace it. The active gateway currently executes OpenRouter requests, so provider support must be described and tested accurately.
- Use a staged workflow: outline review → curriculum proposal → lesson packages → optional media jobs → staff review → explicit publication.
- The lesson player already supports video and written content, but currently displays only the first attached video. Improve it for multiple media assets and short authored notes, while keeping learner-owned notes distinct.
- Retain Supabase private Storage and its signed upload/playback path for the first increment. Evaluate Cloudflare R2 separately; do not migrate storage by assumption.
- Video rendering is a separate asynchronous worker concern, not a synchronous Vercel request and not coupled to the LLM provider.

### Delivery sequence
1. Complete the current-state audit and update the engineering documents.
2. Restore the Learnora ME brand in the landing-page top navigation (the root page currently passes `hideBrand` to `PublicNav`).
3. Verify live schema, permissions, migration ledger and test-course history; do not run unreviewed migrations or destructive data changes.
4. Implement the backend course-production service and internal-staff-only draft-generation API using the existing AI gateway.
5. Extend the existing Teams content workflow with outline input, structured curriculum preview/editing and lesson-package generation.
6. Adapt the Learnora ME lesson player for video + concise authored notes + resources/practice, including multiple videos where needed.
7. Add asynchronous video-rendering jobs, storage integration and secure playback only after the content-generation foundation is verified.
8. Generate, review and publish initial real courses (including Excel, Data Analytics and Front-end Web Development catalogue directions). Replace the test Introduction to Data Analytics course only after verifying enrolment/progress and preserving any learner history.
9. Run backend, frontend, permission, publication and browser/mobile acceptance checks. Deployment remains a separate explicit step.

### Acceptance gates
- Internal team member with the specific generation permission can create and edit drafts.
- Learner, creator, tutor and organisation identities cannot call generation APIs directly.
- Generated hierarchy persists in the canonical tables without duplicate course/module/lesson models.
- Draft courses and lessons do not appear in public discovery or learner progress/completion counts.
- Staff approval is required before publication.
- Video and text can coexist in a lesson; a lesson without video remains valid; multiple videos do not silently disappear from the player.
- Media access is re-authorised at playback time; durable records store asset identity, not expiring signed URLs.
- Test-course replacement preserves learner history and track relationships.
- No production migration, storage migration or deployment is performed without separate verification and approval.


### Progress update — 21 November 2026

- [x] Read the active product, roadmap, account/organisation, learner journey and migration reconciliation documents; inspect active Learnora ME, Learnora Teams and FastAPI paths.
- [x] Add the AI Course Production and Media Architecture Audit and link it from the README and Product Engineering Specification.
- [x] Record the current Pheonix schema, live migration ledger discrepancy, AI profile, staff permission mapping and test-course enrolment/progress evidence.
- [x] Restore Learnora ME branding in the landing-page top navigation.
- [x] Add the first internal Course Studio entry point inside Learnora ME, with a separate staff sign-in route and backend permission checks.
- [x] Add validated AI curriculum and lesson-package proposal endpoints using the existing `content_generation` profile.
- [x] Clarify the authored lesson note in the learner player; confirm the existing video playback path is already present.
- [ ] Add the dedicated `content.generate` permission for the learning-curriculum role after migration reconciliation.
- [ ] Add durable private course-generation drafts and atomic draft-to-course persistence; keep generated teaching scripts out of learner-visible lesson content.
- [ ] Add the review/edit/approve/publish workflow and ensure draft courses remain invisible to learners.
- [ ] Implement the asynchronous video/TTS/caption/rendering pipeline and secure playback validation.
- [ ] Generate the initial real course catalogue, then retire the test Introduction to Data Analytics course without deleting its completed enrolments or progress.
- [ ] Complete CI, browser/mobile acceptance and a separate deployment approval.

**Important:** the current Course Studio is a proposal-generation prototype, not yet an end-to-end publisher. The next engineering gate is the private draft/persistence schema and migration reconciliation, not a video-provider migration. The Teams website itself remains a separate later build.


### Migration readiness update — 21 November 2026

- [x] Reconcile all 56 active Pheonix migration version identifiers with the repository's active migration source filenames.
- [x] Move the unapproved browser-privilege/default-ACL migration out of the active migration directory while preserving it for separate review.
- [x] Update the disposable migration rehearsal to apply the selected migrations in live timestamp order.
- [ ] Design and rehearse the new private course-generation draft schema; do not apply it to live Pheonix until separately approved.


### Persistent Course Studio update — 21 November 2026

- [x] Add versioned private course-generation job and lesson-production-package schema source, with RLS and service-role-only access.
- [x] Add a service-role-only atomic RPC that creates draft courses, modules, lessons and unpublished knowledge-check quizzes from approved packages.
- [x] Add the dedicated `content.generate` permission mapping for curriculum staff and super admins in the pending migration.
- [x] Persist generated curriculum and lesson packages; add explicit staff approval before course draft creation.
- [x] Add optional global-track targeting and saved-draft restoration.
- [x] Add migration assertions and rollback rehearsal to CI.
- [x] Complete CI migration rehearsal and resolve the Course Studio schema/rollback checks.
- [ ] Obtain approval and apply the migration to live Pheonix.
- [x] Add the private video render queue, claim/complete/stale-recovery RPCs, Kokoro/FFmpeg worker source, and R2 signed-playback source.
- [x] Add a sequential Course Studio action to generate all missing lesson packages.
- [x] Prepare the first Data Analytics, Excel Fundamentals and Front-end Web Development production briefs.
- [x] Pass full CI for backend tests, Course Studio migration/rollback rehearsal, Kokoro/FFmpeg MP4 smoke test, and both website builds (commit `e776c2613f`).
- [ ] Configure private R2, CORS, Vercel backend environment and GitHub Actions worker secrets; then run the actual queued render workflow.
- [ ] Deploy the verified renderer/playback integration and run an end-to-end test lesson.
- [x] Link a generated course to its selected global track during atomic publication, after rechecking track enrolment locks.
- [x] Add a final publish action restricted to the existing `content.manage` permission; generation-only staff cannot publish.
- [x] Add staff-only video previews so reviewers can watch rendered lessons before publication; block publication unless the backend can read every rendered R2 object and sign learner playback URLs.
- [x] Let staff select AI or human video production per lesson; human-produced videos upload to the same private R2 bucket through a staff-only signed PUT flow and are required before publication.
- [x] Allow authorised Course Studio staff to create a draft global track and publish it after its linked course passes validation.
- [x] Add an atomic, permission-gated publication action that checks completed video jobs, ready media and valid knowledge checks before publishing the course hierarchy.
- [ ] Complete real course review and publication after the video worker is configured and the migration is approved.
- [ ] Generate the initial real course catalogue and retire the test course from discovery without deleting its two certificates or learner history.


### Current execution update — 21 November 2026

- The current Learnora ME root navigation renders the `Logo` component by default, and the dashboard navigation also renders the Learnora ME wordmark. The previously reported missing brand text is not present in the current `main` source inspected for this pass. No unnecessary logo rewrite was made.
- The learner lesson workspace is already video-capable: it renders signed native video, YouTube/Vimeo embeds, authored lesson content and learner-owned notes separately. It displays one primary video per lesson; the first AI renderer also produces one primary video per lesson.
- The cohort learner lesson route previously displayed text only. The cohort lesson API now returns only ready media after the existing course/lesson assignment checks, and the cohort page plays the primary signed video before its concise notes. Video position and percentage are saved to the existing cohort progress record. A regression test covers the authorised media response; the latest CI run is pending.
- The standard individual learner player now resumes native MP4 playback from its existing saved lesson position; no progress schema change was needed.
- The Course Studio remains an internal-staff-only route inside Learnora ME, separate from normal learner/creator/organisation navigation and permissions. The separate `frontend-team/` application remains a later website build, not part of this integration. The current Course Studio also includes only the small track create/publish controls needed to prepare the first catalogue; the full Teams track/content management workspace remains separate.
- The selected global track is linked only during final publication, after the database rechecks the track's enrolment lock. Authorised super-admin staff can create a new draft global track from Course Studio and publish it once its linked course is ready. Standalone courses remain supported.
- The batch action now generates missing lesson packages sequentially and stops on the first failed request.
- The video worker configuration uses dedicated R2 worker credentials and the actual `lesson_videos` schema. The backend R2 token is separate and bucket-scoped; it needs object read access for playback/verification and write access for authorised human-video uploads.
- The latest scheduled renderer workflow completed without errors but skipped its render steps because the required Supabase and R2 GitHub Actions secrets are not configured. This is a configuration check, not an end-to-end rendering result.
- The Course Studio video-status refresh now guards a missing job ID. The full Learnora production checks and the Cohort Learning Access Tests both passed on commit `e776c2613f`.
- After that passing checkpoint, the curriculum prompt was aligned with the required `short_description`/`course_description` schema, the lesson player was enabled to return approved YouTube/Vimeo embeds, and the renderer now reuses existing media rows on retry with a partial unique R2 object index. The renderer self-test covers retry idempotency; a new full CI run is pending for these latest changes.
- Human-produced MP4 uploads now read and enforce a 1–300 second duration before issuing the R2 upload ticket; the finalisation API and course-publication RPC enforce the same five-minute ceiling.
- The Data Analytics pilot brief now includes the agreed Module 1 lesson topics and short-note guidance for careers, career motivation and the data analytics/data analysis comparison.
- No learner-facing developer comments, implementation notes, or debug text have been added.
- No deployment, live Supabase migration, live R2 bucket creation, or production secret change has been performed.

**Next work:** complete migration/CI and worker verification, review the full draft-to-publication path, finish the real course briefs and content QA, and prepare the mock-course retirement as a separate non-destructive operation. The existing Introduction to Data Analytics test course has 2 completed enrolments, 2 lesson-progress records and 2 certificates; it must be archived/replaced only after the new course and track transition are ready. Do not hard-delete it.


### Publication and renderer verification update — 21 November 2026

- [x] Add a service-role-only atomic `publish_course_from_generation_job` RPC. It keeps the course unpublished until all required lesson packages are ready, all video render jobs are complete, all video lessons have ready private assets, and all module knowledge checks have valid questions and answers.
- [x] Add a separate Course Studio Publish action. It requires the existing `content.manage` permission; staff who only have `content.generate` can generate and prepare drafts but cannot publish.
- [x] Add a database assertion that exercises draft creation, track linking, video-job completion and idempotent publication in one transaction.
- [x] Add a self-contained renderer smoke test that downloads checksum-verified Kokoro model files, synthesises narration, renders captions and produces an MP4 with FFmpeg. The CI workflow now runs this test without Supabase or R2 production credentials.
- [x] Prepare initial production briefs for Data Analytics, Excel Fundamentals and Front-end Web Development in `docs/INITIAL_PILOT_COURSE_PRODUCTION_BRIEFS.md`.
- [ ] Confirm the latest CI run passes with the renderer smoke test and atomic publication assertion.
- [ ] Configure private R2 and GitHub worker secrets after the repository-side pipeline passes.
- [ ] Apply the pending migration and deploy only after explicit user approval.

### Verified CI checkpoint — 21 November 2026

- On commit `3fd30fd0`, GitHub Actions completed the Kokoro/FFmpeg real-render smoke test, additive migration-and-rollback rehearsal, backend compilation/import checks, complete backend test suite, learner frontend build and Teams frontend build successfully.
- Subsequent commits add the table visual renderer, generic-editor publication guard, enrolment-lock recheck hardening and UTC-ordered migration filename. The latest full CI run for those final changes is pending; do not treat the earlier checkpoint as verification of the newest commit.

### Permission and publication hardening — 21 November 2026

- [x] Correct curriculum proposal generation to use `content.generate`, matching the Course Studio access check and the curriculum staff permission mapping.
- [x] Prevent the legacy generic course editor from publishing an AI-generated course unless the Course Studio publication RPC has completed.
- [x] Filter archived tracks from Course Studio selection and validate track availability before saving the course draft.
- [x] Recheck all linked track enrolment locks during final publication so a course cannot silently change a learner's locked track sequence.
- [x] Require 2–4 knowledge-check questions in every generated lesson package and preserve the existing assessment unlock rules.


## Deferred: Learnora Teams website

- [ ] When the separate Teams website rebuild resumes, connect its media manager to the same private R2 upload and preview flow for new Course Studio courses; preserve the legacy Supabase media path for existing courses.
