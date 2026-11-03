# Learnora ME and Learnora Teams — Product Engineering Roadmap

**Last reviewed:** 26 October 2026  
**Branch policy:** all documentation and implementation work requested for this effort goes directly to `main`; do not create or switch to another branch.  
**Release policy:** documentation commits do not authorise production migrations, deployments, or destructive data changes.

This roadmap records priorities, dependencies, and exit criteria. It is not a claim that unfinished items have already shipped.

## Guiding sequence

1. Close security risks that could expose tenant data or corrupt financial/learning state.
2. Reconcile migration history, actual schema grants and the test environment.
3. Prove customer organisation and cohort workflows end-to-end.
4. Complete learner/creator learning journeys in Learnora ME.
5. Complete and validate internal operational journeys in Learnora Teams.
6. Establish release, monitoring, recovery and documentation practices.

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

## P2 — Organisation and cohort workflow completion

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

## P3 — Learnora ME learner and creator experience

### P3.1 Public discovery and conversion

- Audit every public route and ensure the navigation and metadata are correct.
- Use accurate course/tutor records and honest claims.
- Make registration, sign-in, verification, reset and activation resilient.
- Test responsive layout, keyboard access, form validation and errors.

### P3.2 Learning experience

- Course/module/lesson progression.
- Notes, quizzes, attempts and progress persistence.
- Clear completion versus verified-skill distinction.
- AI learning assistance behind permissions and quota.
- Resume/re-entry behaviour and unavailable-content states.

### P3.3 Creator/tutor workflows

- Application and status display.
- Approval/permission transitions.
- Creator dashboard and content management.
- Course publication state and ownership.
- Course-level learner submission access and grading.
- Grade revision policy and audit trail.

**Acceptance:** browser-level journey tests use a disposable account and fixtures; API denial tests verify direct endpoint access cannot bypass UI restrictions.

## P4 — Learnora Teams internal operations

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

## P5 — Privacy, finance and operational hardening

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