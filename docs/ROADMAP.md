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
| Browser token storage | Current `main` clears the legacy `phx_token` from `localStorage` and stores the bearer token in `sessionStorage`. Verification/reset links use URL fragments for new emails and retain query fallback for existing emails. | Interim mitigation only; JavaScript can still read sessionStorage. HttpOnly cookies remain unmerged in PR #13. |
| Shared API/auth throttling | Current `main` still uses process-local normal-auth failure counters and SlowAPI's default in-process limiter. | Open; database-backed implementation is in draft PR #13. |
| Security hardening draft | PR #13 has successful recorded CI runs for commit `0b54f1cda55c7de548005cfcb515ad8c0c02ff2b`. Separately, current `main` candidate `92c3900e5186a0e05fa8f2010a05716320412a48` passed backend regression, backend verification, both frontend builds, cohort-learning tests, and quality checks on the same SHA. | PR #13 remains unmerged; passing CI does not establish that its live migrations have been applied. |
| Creator sales mutation authorization | Recording, releasing, and refunding creator sales now requires `creator_payouts.process` (or the existing super-admin bypass), rather than the broad `courses.assign` permission. | Temporary restriction; dedicated creator-sales permissions and atomic ledger operations remain pending. |
| Database migration sequence | PR #13 adds migrations required by its shared limiter, permission, and grant changes. Its own notes state that these must precede backend deployment. | Blocked on reviewed staging/migration sequence and explicit production approval. |
| Managed `supabase_admin` default ACL | Draft security work records that the connected database role cannot remediate these managed-role defaults. An operator-only SQL script exists on the draft branch. | Blocked on an authorised Supabase administrator and post-change catalog verification. |
| Migration provenance and identity lineage | The reconciliation below still records reconstructed historical sources, legacy successor mappings, and the Witstart identity-set mismatch. | Open; no speculative data repair is authorised. |
| API error disclosure | Course-content and internal video-upload failures now return generic client errors and log only exception types rather than raw database/storage messages. | Implemented with regression coverage. |
| Readiness endpoint | Public readiness output now reveals only `ready`/`not_ready`, not internal configuration/database checks; a token-protected readiness endpoint remains in PR #13. | Partially mitigated; protected probe still pending. |
| Trusted proxy/IP handling | `_get_client_ip` trusts `X-Real-IP` only when running on Vercel and ignores client-supplied proxy headers elsewhere. | Implemented with regression coverage; shared rate-limit storage remains open. |
| Browser-driven product acceptance | CI evidence covers builds and API/database tests, not every complete browser journey across both applications. | Open. |

Do not merge the draft security PR solely because its recorded checks passed: first compare its current head and migration set to `main`, verify the complete required workflow set on one exact candidate SHA, and establish a safe deployment/migration order. Production database changes, data repair, and deployment remain separate approval gates.
