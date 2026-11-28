# Learnora Product Engineering Specification

**Status:** Engineering source of truth (living document)  
**Last reviewed:** 28 November 2026  
**Repository:** `Obikpe/Learnora-ME`  
**Default and requested working branch:** `main`  
**Products covered:** Learnora ME and Learnora Teams  
**Implementation roots:** `frontend-v02/`, `frontend-team/`, `backend-python/`, `supabase/`

This document describes product intent, repository structure, architecture, workflows, security expectations and rebuild procedure. Cross-product decisions and implementation order are governed by [PRODUCT_DECISIONS.md](PRODUCT_DECISIONS.md); this specification defines domain detail within those decisions. It distinguishes implemented behaviour from intended behaviour and known gaps. Where repository evidence does not establish a detail, it is marked **needs verification** rather than invented.

## 1. Product overview

Learnora is a learning and skills-development platform built around a journey from discovering a skill to learning, practising, building, demonstrating competence with appropriate evidence, showcasing that evidence, and connecting to opportunities. Completion is not the same as verified competence; unreviewed evidence must be labelled unverified. Marketing must not fabricate course counts, learner outcomes, testimonials, organisation metrics, or portfolio evidence.

The platform has two distinct web applications backed by a shared Python API and Supabase data platform:

- **Learnora ME** is the customer-facing learning website: public discovery and learner delivery, with customer organisation workflows planned for a later phase.
- **Learnora Teams** is the separate internal workforce website and the intended home of authorised internal course/content production, AI orchestration, review, acceptance and publishing. It is not the customer organisation portal.

The current Course Studio prototype's placement inside Learnora ME is transitional implementation history, not the target product boundary. See [AI_COURSE_PRODUCTION_AND_MEDIA_ARCHITECTURE.md](AI_COURSE_PRODUCTION_AND_MEDIA_ARCHITECTURE.md) and PD-003 in the decision register.

### Product principles

1. Use actual API records for operational metrics and public claims.
2. Tenant boundaries are enforced by backend scope checks and database constraints, not merely by hiding UI controls.
3. A cohort learner is assigned exactly one fixed track for that cohort; the learner cannot change track during that cohort. The cohort's track, team and tutor operating model remains distinct from corporate organisation workflows.
4. Email identity is mutually exclusive between normal individual learner accounts and organisation/cohort-managed accounts in both directions. Revoking access to an organisation/cohort-managed learner or tutor account means deleting that managed account and its associated data; the email becomes available for a new account only after deletion. A cohort ending does not itself delete the parent organisation. At organisation contract end, retain the organisation record and the numeric learner count at that time, and delete the covered learner identities, roster, team membership and associated learner data. See PD-012 and `COHORT_OPERATING_MODEL.md`; technical erasure and audit controls remain unresolved.
5. Cohort teams and corporate organisation teams are distinct domain models. Team/cohort-scoped access must not silently become organisation-wide access.
6. Loading, empty, validation, error, success, and permission-denied states are first-class UI states.
7. Avoid paid dependencies when the existing stack is sufficient; do not add a design/component library without a clear need.
8. No destructive schema/data action is justified solely to make migration history or a schema diff look clean.

## 2. Repository map and ownership

| Path | Responsibility | Notes |
|---|---|---|
| `frontend-v02/` | Learnora ME customer-facing Next.js application | Active customer UI: public pages, learner/creator flows, organisation portal/workspace, cohort flows |
| `frontend-team/` | Learnora Teams internal Next.js application | Super Admin and internal operations |
| `backend-python/` | FastAPI backend, business rules, API routes, services, tests | Shared application API; check router registration in `main.py` |
| `supabase/migrations/` | Timestamped/active SQL migration files and current schema baseline assets | Never blindly replay legacy SQL against a live project |
| `supabase/legacy_migrations/` | Archived historical migration chain | Historical analysis only; not a queue of pending active migrations |
| `supabase/baselines/` | Disposable catalog-derived schema fixture and comparison assets, where present | Staging fixture, not a replacement for verified migration history |
| `backend-python/tests/` | Python unit, regression, API and migration-inventory tests | DB fixtures/assertions are under `tests/db/` |
| `backend-python/migrations/` | Migration planning, verification SQL, reconciliation reports | Some files are planning/evidence artefacts rather than migrations to execute |
| `docs/` | Product, UX, migration, security and release documentation | Keep the decisions and status here current |
| `.github/workflows/` | CI checks for backend, frontend, quality, and cohort lifecycle | A cancelled workflow is not a passing check |
| `frontend/` | Legacy frontend | Historical/legacy surface; do not silently substitute it for the active ME frontend |

**Important separation:** Learnora ME is implemented under `frontend-v02/`, and Learnora Teams under `frontend-team/`. Do not confuse Teams with the organisation workspace. The legacy `frontend/` is not the target for new ME work.

## 3. Technology and runtime architecture

### Frontend applications

Both active frontends use Next.js/React and the repository's existing styling stack (Tailwind and Lucide where already used). Keep their dependencies and deployment roots independent. Review each `package.json`, `vercel.json`, and environment example before changing build or deployment behaviour.

- Learnora ME: `frontend-v02/app/`, `frontend-v02/components/`, `frontend-v02/lib/`.
- Learnora Teams: `frontend-team/app/`, `frontend-team/components/`, `frontend-team/lib/`.

The UI must call the FastAPI API for protected operations. Do not put Supabase service-role secrets in browser code. Avoid direct browser database access for backend-only records.

### Backend

- Entry point: `backend-python/main.py`.
- HTTP API: routers in `backend-python/routers/`.
- Shared business logic: `backend-python/services/`.
- Data validation: Pydantic models and route validation.
- Tests: `backend-python/tests/`.
- Dependencies: `backend-python/requirements.txt` and `pyproject.toml`.
- Vercel routing/configuration: `backend-python/vercel.json`.

The backend is the authority for authentication, organisation/tenant scoping, cohort membership, course-content access, grading, AI quota reservations, finance operations, and internal staff privileges. Inspect route inclusion and dependency wiring in `main.py` before adding a router.

### Database and storage

Supabase provides PostgreSQL, database functions/triggers, and related platform services. The active Pheonix project reference recorded in repository engineering notes is `gihfupzvdpyrmynqgukz`. This reference identifies the intended project but does **not** prove the currently deployed Vercel backend points to it; deployment environment values have not been independently verified.

Reuse existing tables and relationships. Do not create parallel models without proving the existing model cannot represent the requirement. Do not run migrations against production as part of ordinary local development or CI.

### External integrations

Payment providers and email/notification integrations appear in the repository history and README. Treat provider status, production credentials, webhook configuration, and live payment behaviour as **environment-specific and requiring verification**. Never place real keys in source control. Use CI-only dummy values in tests.

## 4. User groups and product boundaries

### Learnora ME personas

- **Public visitor:** discovers learning tracks, courses, tutors, platform information, policies, and organisation options.
- **Individual learner:** registers/authenticates, discovers/enrols in available learning, views lessons, tracks progress, attempts quizzes, takes notes, and accesses eligible AI/learning support.
- **Tutor/creator applicant:** submits an application; approval and account capabilities must follow the backend's status/permission checks.
- **Approved tutor/creator:** manages permitted creator/course work, content and submissions within granted ownership and roles.
- **Organisation owner/manager:** accesses only the organisation(s) they are authorised to manage; manages teams, cohorts, learner memberships, programmes, courses, tutors, contracts/entitlements, and progress according to grants.
- **Organisation team manager/member:** accesses only permitted team operations and assigned learning.
- **Cohort learner:** uses the cohort's own access and learning context, sees only assigned learning, and follows the cohort's fixed track and lifecycle.
- **Cohort tutor/team member:** participates in a cohort team and may be assigned to specific tracks created by that cohort; access is limited to the cohort/team/resources assigned. Detailed cohort team types, responsibilities and permissions remain unresolved.

### Learnora Teams personas

- **Platform Super Admin:** operates internal platform controls according to explicit platform-admin authority.
- **Internal staff/team member:** can access only the internal operational sections and actions permitted to their staff membership and role.

Internal platform administration and customer organisation administration are separate trust boundaries. Do not grant platform-admin powers because a user is an organisation owner, or vice versa.

## 5. Functional scope and workflows

### 5.1 Public discovery and learning

Current routes and components should be inspected directly under `frontend-v02/app/`; the route tree includes public course/tutor/organisation discovery, informational/legal pages, login/registration, and learner dashboards. Preserve existing working routes and navigation when redesigning individual pages.

Target user journey:

1. Visitor lands on the site and understands the learning proposition.
2. Visitor browses real courses/tracks and tutor information.
3. Visitor registers or signs in.
4. Learner enrols only where course visibility, publication, entitlement and access rules permit.
5. Learner opens a course, module and lesson; the backend validates current access at request time.
6. Progress, quiz attempts, notes and other permitted learning records are persisted.
7. Evidence/portfolio is presented with a clear distinction between self-reported, submitted, reviewed and verified evidence.

A route existing in the tree does not by itself prove that its full journey has been browser-tested. Verify each end-to-end flow.

### 5.2 Future independent tutor/creator lifecycle — deferred

Independent tutor functionality is a separate future product context under PD-001, not part of the current individual learner phase. It must not be conflated with cohort tutors or corporate organisation tutors.

The customer app includes an application-to-teach flow and creator dashboard. The intended lifecycle is application → review/approval → authorised creator workspace → course/content creation or management → publication according to permissions → learner engagement and grading where allowed. Do not infer creator approval from the existence of a user account.

Course ownership, organisation affiliation, and instructor assignment must be checked server-side. Creator/finance operations require separation of duties and auditable state transitions.

### 5.3 Corporate organisation onboarding and workspaces — deferred

Corporate organisation workflows belong to Learnora ME but are deferred until after the individual learner experience and Learnora Teams website. This section records an earlier proposed organisation workflow, not a complete specification of the cohort domain. Cohorts have their own teams and tutor/track relationships; do not assume that the corporate organisation team model or this organisation lifecycle describes cohort operations. See PD-004 and UR-001/UR-002 in [PRODUCT_DECISIONS.md](PRODUCT_DECISIONS.md).

The eventual corporate organisation scope includes organisation owners/managers, teams, programmes, tutors, learners, course access, contracts/entitlements, AI use, and progression.

Approved management pattern:

1. A customer organisation request is processed and the organisation is created with its type established as either **cohort** or **corporate organisation**. These types share top-level management but have distinct team structures and workflows.
2. Each organisation has an active manager and a formal management team led by that manager.
3. The manager creates other teams and appoints administrators with defined, role-scoped responsibilities. Administrators do not inherit the manager's full access automatically.
4. In a corporate organisation, the coordinator onboards learners/employees into the relevant learning teams. In a cohort, the coordinator places learners into the cohort's configured tracks and assigns tutors to those tracks.
5. The intended person completes their own account activation and creates their own password through the invitation flow; the activation link expires 48 hours after issue.
6. The manager's access is limited to the organisation's entitlements and does not grant access to another organisation or internal Learnora staff capabilities.

The complete corporate team taxonomy, team-manager roles, course/programme assignment model, tutor responsibilities, dashboard/analytics scope, contracts/entitlements and detailed permissions remain unresolved. Do not fill these gaps by importing the cohort track/tutor model into corporate organisations or by treating a corporate organisation as a cohort.

A scoped team/cohort entitlement is not an organisation-wide grant. A learner who loses active membership or assignment must lose the corresponding content access even if a stale enrolment row remains. Cohort end and organisation contract end are distinct lifecycle events; follow PD-012 and `COHORT_OPERATING_MODEL.md` for the approved account deletion and contract-end retention outcomes.

### 5.4 Cohort account and login — current implementation and approved product constraints

**Current repository behaviour (historical source observation):** cohort learner identities are stored separately from `public.users`, with the cohort login implementation in `backend-python/routers/cohort_learners.py`. Relevant tests include `test_cohort_login_security.py`, `test_cohort_learner_workflow.py`, `test_cohort_archive_lifecycle.py`, and `test_cohort_api_lifecycle.py`. This describes the repository snapshot, not proof of current live database state.

**Approved product behaviour:** an email address cannot be used simultaneously by a normal individual learner account and an organisation/cohort-managed account; the restriction applies in both directions and includes managed tutors. Revoking an organisation/cohort-managed learner's or tutor's access deletes that managed account and its associated data. After deletion, the email is no longer reserved and may be used for a new account through the ordinary registration/invitation checks; no deleted data is transferred. A cohort learner remains on one fixed track for that cohort.

**Still unresolved:** the canonical identity registry (if any), race-safe global uniqueness mechanism, reconciliation of existing duplicate/legacy identities, and the safe migration/transition design. Preserve existing cohort accounts and historical data until a separately approved transition plan exists. Do not infer that the approved product-level exclusivity rule settles the technical identity architecture or authorises a migration.

Cohorts have their own teams. Cohort teams can include tutors assigned to tracks created by that cohort, alongside learners and other cohort-specific operations. Their exact types, responsibilities, membership rules, dashboard behaviour and permission matrix remain to be specified. Do not substitute the corporate organisation team model for this missing cohort detail.

Security requirements:

- Username matching must be exact, never wildcard-based.
- Reject malformed usernames before database lookup but return the same public authentication failure as an incorrect password.
- Perform dummy password-hash verification for unknown usernames to reduce account-enumeration timing differences.
- Rate-limit by both username and client IP; process-local counters alone are not sufficient for multi-instance/serverless production.
- Recheck account/cohort status and membership against the database on authenticated requests.
- Activation tokens must be hashed, single-use, short-lived, and not exposed unnecessarily through URLs/logs/referrers.
- Passwords must be stored using the existing secure password-hashing helper; never log credentials or token values.

Current status of each item must be verified against main code and tests before claiming complete.

### 5.5 Learning content and course access

The backend contains access, course content, course, learning structure, progress, grading, and evidence routers. Enforce access in the backend for every read and write, not only in dashboard route guards.

Access decisions should combine:
- current user identity and account state;
- active organisation membership, if relevant;
- course publication and ownership;
- explicit organisation-wide assignment versus scoped entitlement;
- active team/cohort membership and matching assignment;
- contract/entitlement and capacity state;
- module unlock prerequisites;
- applicable course/module/lesson progress or assessment gates.

Any instructor access to learner submissions must be constrained to courses/modules the instructor is authorised to teach, not merely to all courses in the same organisation. Grade changes need an audit record and a clear policy for revisions.

### 5.6 AI features and quota

AI-related code includes `routers/ai.py`, `routers/ai_profiles.py`, `services/ai.py`, `services/ai_gateway.py`, `services/ai_profiles.py`, and quota-related database objects such as `learnora_ai_limits` and `ai_usage_logs`.

Requirements:
- Resolve AI profile/provider access from server-side policy.
- Check role, entitlement and applicable quota before calling a provider.
- Reserve quota atomically to prevent concurrent requests from exceeding limits.
- Define unlimited monthly quota only where the stored contract explicitly permits a NULL monthly limit; daily limits remain independently enforced.
- Log usage without storing unnecessary secrets or sensitive prompt content.
- Handle provider errors/retries without double charging or duplicate side effects.
- Never expose provider secrets to the browser.

### 5.7 Learnora Teams internal operations

The internal application is rooted at `frontend-team/`. Its current route/component tree includes areas for super-admin, organisations, courses/content, creators, AI operations, notifications, and general section routing. Components include `Shell`, `Sidebar`, `SessionGuard`, `OrganisationWorkspace`, `ContentManager`, `ContentWorkspace`, `LivePanel`, and API/operations helpers under `lib/`.

Treat these screens as an internal control plane:
- verify staff session and server-side role before every protected action;
- separate read-only inspection from mutations;
- use explicit confirmations for high-impact actions;
- record audit events for privileged operations;
- display accurate loading/error/empty states;
- avoid exposing secrets or unnecessary personal data;
- do not confuse internal organisation management tools with the customer-facing organisation portal in Learnora ME.

Exact per-role permissions and every control's current API implementation must be confirmed in the current code before changing them.

## 6. Data model and invariants

The existing schema already contains (names are taken from engineering notes; verify columns and constraints against the current catalog before writing SQL):

| Domain | Existing structures |
|---|---|
| Users and tenant membership | `users`, `organisations`, `organisation_members` |
| Teams | `organisation_teams`, `organisation_team_members` |
| Cohorts | `cohorts`, `cohort_members`, `learnora_cohort_lifecycle`, `learnora_cohort_lifecycle_events` |
| Programmes | `learnora_programmes`, `learnora_programme_courses` |
| Course assignment/access | `cohort_course_assignments`, `course_access`, `learnora_access_entitlements`, `learnora_enrolments`, team course assignments |
| Contracts | `learnora_contracts`, `learnora_contract_entitlements`, `learnora_contract_versions`, `learnora_contract_clauses` |
| Capacity | `learnora_capacity_reservations` |
| AI usage | `learnora_ai_limits`, `ai_usage_logs` |
| Learning and assessment | `quizzes`, `quiz_attempts`, `course_modules`, `learnora_lessons`, progress/notes tables |

Core invariants:
1. Every tenant-owned relationship must be consistent with the same organisation. Foreign keys that prove only entity existence are not enough.
2. Team members and team managers must have active membership in the team's organisation.
3. Cohort members must have active learner membership in the cohort's organisation.
4. Cohort/programme and team/cohort course assignments must point to an allowed course/programme in the same tenant scope.
5. A learner's track does not change during a cohort.
6. Capacity reservation and AI quota reservation must be atomic under concurrent requests.
7. Organisation-wide course grants and scoped assignments are different access types.
8. Cohort closure changes active state/access without destroying historical records needed for audit/statistics.
9. User identity mapping must be explicit; matching aggregate row counts do not prove record-level correctness.
10. Schema changes must be migration-backed, reviewed and tested on a disposable database first.

## 7. Security architecture and requirements

### Authentication and sessions

The repository has historical docs that describe an HttpOnly/JWT security target, while a later review identified a frontend session token in `localStorage` (`phx_token`) with a 24-hour lifetime. This is a documented inconsistency and must not be papered over: inspect current main code and decide/implement the supported session design. Preferred target is an HttpOnly, Secure, appropriately SameSite cookie with short access lifetime and a deliberate refresh/session revocation strategy, subject to the deployed architecture and CSRF controls.

Unknown-user and wrong-password responses should be indistinguishable in body/status and as close as practical in timing. Password reset, email verification and activation flows must use single-use, expiring, hashed tokens.

### Authorization and database grants

The API must use server-side scope checks. Browser roles `anon` and `authenticated` must not have broad table grants on backend-only tables. A prior security review identified overly broad default/table grants and a mismatch between the locked-down test fixture and the live grant model. Before a grant migration is approved:
1. inventory table grants and per-owner default privileges read-only;
2. confirm no browser/mobile/scripts depend on direct table access;
3. test the revocation against a disposable replay and the authenticated API journey;
4. ensure CI fails when forbidden grants appear in the replayed schema;
5. prepare an exact rollback script outside the active migration directory;
6. apply to production only after separately approved staging verification and quiet-window plan.

Default privileges are scoped to the role that creates future objects. Check every relevant owner (including `postgres` and `supabase_admin` where applicable); a single `ALTER DEFAULT PRIVILEGES` statement does not necessarily cover all owners.

Do not assume RLS alone neutralises excessive grants. Test grants, RLS flags, policies, functions, views, and service-role paths together.

### Additional API/browser hardening

Track and remediate:
- shared/distributed login rate limits for serverless instances;
- trusted-proxy handling for client IP and verification of Vercel header behaviour;
- CSP and standard security headers;
- minimising personal data, especially learner date of birth and data returned to organisations;
- payout/ledger atomicity and separation of finance duties;
- instructor/course-level grading scope and grade-change audit logs;
- restrictive, explicit CORS origin allowlists (avoid broad preview-domain trust with credentials);
- disabling or protecting production API documentation endpoints;
- pinning `search_path` for security-sensitive functions/triggers;
- avoiding activation tokens in URL query strings where a safer flow is feasible;
- sanitising query/filter construction, especially any interpolated `.or_()` expression;
- ensuring readiness endpoints disclose no sensitive operational information.

### Privacy

Store and return only data needed for a clear purpose. DOB is sensitive personal information and should not be returned to an organisation unless there is a justified, documented requirement. Where it must be retained, consider encryption at rest at application level, strict field-level access and retention rules. Establish jurisdictional/legal requirements with qualified review; this document is engineering guidance, not legal advice.

## 8. UI and design system

Design direction documented in `docs/learnora-ui-ux-research.md`:
- dark graphite surfaces with warm gold accent;
- deliberate typography and generous whitespace;
- high-contrast functional controls;
- retain the existing top-navigation structure unless usability evidence justifies change;
- page-specific layouts for marketing, learning, tutor discovery, organisation onboarding and internal operations;
- use different relevant imagery for different story sections;
- keep motion subordinate to comprehension;
- mobile-responsive layouts and keyboard/semantic accessibility;
- use existing Next.js/React/Tailwind/Lucide stack;
- research actual shipped flows (where available) rather than copying isolated inspiration shots;
- do not claim a Figma/Mobbin review occurred unless the integration was actually connected and used.

Every key flow needs loading, empty, validation, error, success, disabled and permission-denied states. Avoid fabricated statistics or generic repeated card layouts where a purpose-built composition is clearer.

## 9. Local rebuild and developer setup

These instructions are a starting point; exact environment variables and commands must be checked against current config files.

### Prerequisites

- Node.js version compatible with both frontend package files.
- Python version compatible with `backend-python/pyproject.toml` and requirements.
- PostgreSQL/Supabase disposable database for integration tests that require SQL.
- Git and access to the repository.
- Provider/test credentials only where the relevant feature requires them.

### Get the code

```bash
git clone https://github.com/Obikpe/Pheonix-Analytics.git
cd Pheonix-Analytics
git switch main
```

### Learnora ME

```bash
cd frontend-v02
npm ci
npm run dev
```

Read `frontend-v02/package.json` for the authoritative scripts. Copy `.env.example` to a local-only environment file and populate only the values actually required by the frontend. Never commit the local environment file.

### Learnora Teams

```bash
cd frontend-team
npm ci
npm run dev
```

Read `frontend-team/package.json` for exact scripts and environment variable names.

### FastAPI backend

```bash
cd backend-python
python -m venv .venv
# Activate the virtual environment for your operating system.
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Use `.env.example` as the source of variable names. Keep service-role secrets server-side and local. Do not copy production credentials into a development environment.

### Tests

From `backend-python/`, inspect the configured pytest/test scripts and run the unit/regression suites. The cohort integration workflow requires disposable PostgreSQL and a local PostgREST/API setup; use `.github/workflows/cohort-learning-tests.yml` as the authoritative CI procedure. Run frontend production builds from each frontend directory. A cancelled workflow is not a pass.

Never use a live production database as a test fixture for lifecycle, auth, quota, payout, or cohort mutations.

## 10. CI and release workflow

The repository has workflows for backend verification/tests, frontend builds, quality checks, and cohort lifecycle tests. Read their current definitions rather than relying on historic run summaries.

Minimum release gate:
- all relevant workflows finish with conclusion `success`;
- no workflow remains cancelled/skipped without an explained, approved reason;
- auth, tenant isolation, cohort lifecycle, course access, quota, finance and migration tests pass;
- schema grants/RLS/policies/functions/triggers are reviewed;
- frontend builds pass for both active apps;
- migrations run against a disposable database and have a documented rollback;
- staging smoke test covers critical user journeys;
- deployment target and environment mapping are verified;
- no production deploy or live SQL change occurs without explicit release authorisation.

## 11. Definition of done

A feature is not done merely because a route or component exists. It is done when:
1. Product behaviour and roles are documented.
2. UI works on mobile and desktop with complete interaction states.
3. Backend enforces authentication, tenant scope and business invariants.
4. Data schema and migration are reviewed, replayable on disposable PostgreSQL, and safe to roll back where applicable.
5. Tests cover normal, invalid, cross-tenant, revoked-access, concurrency and failure paths as relevant.
6. CI completes successfully on the exact commit.
7. Telemetry/audit events are added for sensitive operations.
8. Documentation and environment examples are updated.
9. Any known limitation is explicitly recorded and not represented as complete.
10. Production rollout is separately authorised and verified.

## 12. Source-of-truth files

- `docs/ROADMAP.md` — prioritised implementation roadmap and acceptance gates.
- `docs/ENGINEERING_HISTORY_AND_DECISIONS.md` — action log, decisions, security findings and migration provenance.
- `docs/learnora-ui-ux-research.md` — UI/UX design decisions and research constraints.
- `backend-python/migrations/STEP_4_ORGANISATION_DATA_MODEL_PLAN.md` — organisation data model and migration planning.
- `backend-python/migrations/STEP_7_FINAL_GAP_REGISTER.md` — historical audit and release findings; verify dates/branch references before relying on old status.
- `backend-python/migrations/STEP_7_REPOSITORY_MIGRATION_COMPARISON.md` — repository migration comparison.
- `backend-python/migrations/STEP_7_SCHEMA_DATA_COMPARISON_RESULTS.md` — recorded live inventory/data-lineage findings.
- `docs/active-pheonix-migration-reconciliation.md` — current-schema baseline versus legacy replay reconciliation.

When these sources disagree, inspect the current `main` code and active database catalog, record the discrepancy, and update the documentation rather than silently choosing whichever claim looks newer.


---

## 13. Staged launch direction — free learner launch, then paid expansion (31 October 2026)

This is a dated product-direction addendum to the original specification. Sections 1–12 above remain intact as the original product and engineering plan. This section records the 31 October 2026 launch strategy and how it coexists with the original commercial model. Its application sequencing is historical and is superseded by PD-001 in [PRODUCT_DECISIONS.md](PRODUCT_DECISIONS.md). The free-access and paid-system preservation rules remain relevant. The detailed historical plan is in [FREE_LAUNCH_AND_PAID_EXPANSION_PLAN.md](FREE_LAUNCH_AND_PAID_EXPANSION_PLAN.md).

### 13.1 Launch strategy

Learnora will first make the individual learner experience free, with no card/payment-method requirement, checkout, paid subscription requirement, or trial-expiry cutoff. The aim is to launch the learning experience, attract learners, gather genuine feedback, and establish trust before introducing paid courses and Pro.

The existing subscription, payment-provider, trial, expiry, entitlement, and Pro work is retained. This strategy does not authorise deletion or replacement of those systems.

### 13.2 Temporary free-access behaviour

A central, reversible, server-enforced free-access mode will grant the intended individual learner access while the free launch is active. The backend—not merely the frontend—must enforce the mode. With the mode enabled, an individual learner must not be blocked by absent payment records, expired trials, or subscription expiry. With the mode disabled, the original paid checks must resume.

Free mode must not weaken authentication, staff permissions, tenant isolation, RLS, creator ownership, unpublished/private content controls, or media access. It must not grant organisation or administrative privileges. Do not rewrite historical subscription/payment records to simulate free access.

### 13.3 Historical immediate application scope — superseded 21 November 2026

The following records the earlier 31 October sequence in which Teams content operations were prioritised before the learner journey. It is retained as history and must not be used as the current delivery order. Under PD-001, complete the normal individual learner experience first, then build the separate Learnora Teams website.

- **Learnora Teams (frontend-team/):** content operations for tracks, ordered track-course relationships, courses, modules, lessons, video/resource upload and publishing; learner lookup/progress views; trustworthy platform analytics.
- **Learnora ME (frontend-v02/):** free catalogue discovery, track/course enrolment, lesson/media consumption, supported assessments/activities, progress persistence/resume, and accurate course/track completion.
- **Shared services:** existing FastAPI backend (backend-python/) and the already-active Pheonix Supabase project. Do not create or switch to a separate Learnora Supabase project. Existing records identify the Pheonix project reference as gihfupzvdpyrmynqgukz; verify the configured target safely before any operation and never expose credentials.
- **Legacy app:** frontend/ remains outside the current implementation target.

Track/course relationships must be inspected in the current main schema and active Supabase catalog before adding tables. Reuse the canonical model if available. Do not create a competing track system or reuse cohort-only track assignment structures as a public catalogue model.

### 13.4 Track-completion feedback

After backend-confirmed track completion, offer a dismissible 1–5 rating prompt with an optional comment. Submission must not be required to continue learning. Public display requires separate learner consent and moderation. Prevent duplicate submissions or define an explicit edit policy; sanitise user-generated content and provide a removal/reporting path. Public reviews may be indexed after moderation/privacy checks, but search rich-result stars are not guaranteed and self-serving review markup must follow search-engine policies.

### 13.5 Deferred capabilities

Customer organisation workflows, cohorts/programmes, instructor/tutor/creator onboarding and tools, creator sales/payouts, and the full paid commercial model remain part of the original specification. They are deferred in implementation order, not cancelled. Preserve their code, data, migrations, permission boundaries and original documentation.

### 13.6 Paid expansion

A later separately approved stage may introduce paid courses and Pro subscriptions. Before charging, define free-versus-paid catalogue rules, Pro benefits and pricing, renewals/cancellation/refunds/failures, entitlements, existing free-launch learner treatment, and clear notice before any previously free content becomes paid. Preserve earned completion/progress records. Prove the paid path works when free mode is disabled before enabling charges.

### 13.7 Acceptance and release

The immediate free-launch acceptance criteria and execution order are maintained in docs/ROADMAP.md and docs/FREE_LAUNCH_AND_PAID_EXPANSION_PLAN.md. A screen or route alone is not evidence of a complete workflow. Verify Teams content creation through learner consumption, progress and completion, including backend authorization and storage. Production migrations, production data changes and deployments remain separate explicit approval gates.



---

## 14. Learner journey extension — architecture, plans, assessments and contextual tutoring (2 November 2026)

This addendum records the five-phase learner journey extension. The original sections 1–13 remain intact. See [LEARNER_JOURNEY_PHASES_1_5.md](LEARNER_JOURNEY_PHASES_1_5.md) for implementation details, tests and outstanding acceptance evidence.

### 14.1 Canonical curriculum relationships

The global catalogue uses the existing generic learning-path model:

`learnora_learning_paths` → `learnora_learning_path_courses` (ordered by `order_index`, with `required`) → `learnora_courses` → `course_modules` → `learnora_lessons`.

The cohort-specific `learnora_tracks` / `cohort_track_courses` relationship remains separate. Do not introduce another global track table or encode learner plans as track curriculum.

### 14.2 Optional AI learning plan

An individual learner may optionally generate a plan from their saved onboarding profile and a published global track, or from the published global course catalogue. The schedule references only existing course IDs and follows the track's existing order. The AI may personalise weekly focus, practice and reflection prompts, but it may not create or reorder courses, modules or lessons. A rule-based fallback is clearly identified when structured AI output is unavailable or invalid.

Plan state is stored separately in `learner_learning_plans`; plan completion is not course completion. The table is backend-only, RLS-enabled, and grants only the server role. The migration and rollback pass the disposable PostgreSQL CI replay with RLS/grant assertions; the live Pheonix project remains unapplied and its SQL catalogue remains unverified because the read-only DB connection fails authentication.

### 14.3 Assessment and course completion policy

Teams staff with the relevant internal permissions can configure and publish supported auto-graded multiple-choice and true/false quizzes, edit draft quiz settings/questions, and create/edit/publish manually graded assignments with lesson association and optional due dates. Published assessment settings must be unpublished before editing. Correct-answer keys are not returned to learner-facing quiz APIs or contextual AI prompts. Assignment grades store the grader and timestamp, and every grading action is written to `audit_logs`.

Course completion requires:
- all learner-visible published lessons completed;
- a passing attempt for every published quiz, using that quiz's configured threshold; and
- the latest submission for every published assignment graded at 70% or above of its maximum score.

All published assessments are treated as required for course completion. Unpublished drafts do not affect learner completion. A course without published assessments retains lesson-only completion. Earlier-module unlocking checks published quizzes against their configured thresholds; modules without a published quiz do not deadlock progression. Track completion remains derived from required course completion.

A separate immutable grade-revision history and learner resubmission workflow remain future work.

### 14.4 Contextual AI tutor

The learner player may attach course, lesson and optional assessment identifiers to a tutor request. The backend revalidates enrolment, course/lesson membership, publication state, module unlock state, and that an attached quiz belongs to the active lesson/module. It loads lesson content, saved lesson progress, question/options without answer keys, recent quiz outcomes, and recent assignment outcomes/staff feedback. Course content and feedback are untrusted reference data. Contextual handoffs start a fresh conversation; general tutor conversations remain supported.

### 14.5 Learnora Teams responsibilities

Teams continues to manage the canonical global tracks, ordered course relationships, courses, modules, lessons, video/resources and publication. The new assessment workspace adds quiz and assignment authoring, grading and course-level learner performance inspection. Internal staff permissions remain enforced by the backend for every route.

### 14.6 Free-launch compatibility and release gates

No payment, Paystack, subscription, trial, expiry, entitlement or Pro implementation is removed or rewritten by this extension. The existing server-side free-access mode remains default-off until separately configured and deployed. The plan feature does not require payment details or a paid subscription.

The learning-plan migration is additive; its disposable PostgreSQL CI replay, RLS/grant assertions and transactional rollback passed on checkpoint `8e21f264744a1a49d26d0f81b3272f1c5d72f24a`. It has not been applied to the active Supabase project. All five CI workflows (backend tests, backend verification, three frontend builds, quality checks, and cohort/disposable migration tests) passed on that exact checkpoint. Live Pheonix SQL revalidation remains blocked by read-only DB authentication; browser/mobile acceptance, provider/fallback acceptance, and separately approved live migration/deployment remain release gates. No production deployment or migration was authorised.


### 14.7 Quiz integrity — AI tutor availability

The AI tutor is not available inside any active quiz. The tutor launcher, chat interface, contextual tutor action and any equivalent keyboard/accessibility entry point must be absent or disabled for the full quiz lifecycle: answering, moving between questions, reviewing and submitting. A learner must not be able to open the tutor overlay or send a tutor request while an attempt is active. This is an application access-control rule, not a prompt-only instruction. Backend tutor endpoints must reject quiz-context requests during an active attempt, even if called outside the normal UI. The tutor remains available on ordinary lesson/course learning surfaces outside an active quiz. Browser tests must verify both visible UI absence and request-level denial.

### 14.8 Immediate acceptance milestone and Phase 6

The next milestone is limited to live Pheonix Supabase schema/migration/RLS/grant verification and browser-based acceptance of the phase 1–5 learner/Teams workflows, including the quiz tutor-visibility restriction above. Once both are accepted and any live migration has separate approval, proceed directly to Phase 6: track completion feedback, optional rating/comment, explicit public consent, moderation, duplicate prevention and privacy-safe display. No unrelated feature phase is to be inserted.


## Learner dashboard activity tracking (3 November 2026)

The learner dashboard uses lesson-weighted progress across active enrolments. Session time and meaningful learning-day streaks are separate metrics.

- `learning_sessions` stores authenticated browser sessions, last heartbeat, active seconds, timezone and closure status. The frontend sends a heartbeat every 30 seconds and only counts time while the page is visible and recent learner interaction has occurred (five-minute inactivity threshold). A stale session is reconciled on the next start; page exit/logout attempts a keepalive close.
- `learner_learning_days` stores one unique row per learner account type and local activity date. A server-side RPC upserts only first-time lesson completions, passed quizzes and submitted assignments. Login, dashboard views and course opens do not qualify.
- Individual and cohort account types are separate in both tables because cohort identities are held outside `public.users`.
- Streak is calculated from consecutive activity dates. If today has no qualifying event yet, the displayed streak remains anchored to yesterday. Longest streak is derived from the full stored history.
- Time is conservative: hidden tabs and sessions without recent interaction do not accrue time. It is not a measure of video playback duration.
- The SQL migration `supabase/migrations/20261103120000_learner_learning_sessions_and_streaks.sql` is prepared but must be applied and verified separately before persisted values are available. Historical days are not backfilled because the previous records do not consistently retain the learner timezone or equivalent cohort completion timestamps; streak history begins with verified events after migration. No production migration is executed by a GitHub commit.
- The browser timezone is validated against IANA timezone data. Invalid or missing timezone values fall back to `Africa/Lagos`.
- Learning-time and streak values are not fabricated. If tracking is unavailable, the UI indicates that rather than inventing a number.


## 15. Learner account recovery and communications

The current learner account recovery, deletion-reason capture, 30-day recovery period, marketing-consent requirements and planned event-driven notification architecture are specified in [LEARNER_NOTIFICATIONS_AND_MARKETING_AUTOMATION.md](LEARNER_NOTIFICATIONS_AND_MARKETING_AUTOMATION.md). That document is the detailed source of truth for message classification, audience targeting, consent, unsubscribe, delivery and release gates.

## Account deletion decision — 30-day recovery, then complete learner erasure

The approved product rule is:

- Confirmed deletion starts a 30-day deactivation and recovery window. No learner data is erased during this period.
- Reactivation during the window restores the existing account with its password, enrolments, progress, notes, submissions and other learner records intact.
- At the end of the 30 days, the finalisation process deletes the learner's `public.users` row and all account-linked learner records, including learning/progress data, notes, assessments, submissions, certificates, discussions, AI conversations/usage, notifications, activity records, account tokens, membership links and learner-owned commercial/profile rows.
- The only learner-specific record retained is the restricted `public.deleted_account_history` row. It contains the deletion-history fields and reason; it is not a reusable learner account.
- The finaliser must fail atomically if a dependent learner record cannot be deleted. It must never report completion after partial cleanup.
- Shared platform catalogue and organisation resources are not deleted solely because a learner created or was assigned as their actor; the learner attribution is detached where appropriate.

The implementation is represented by migrations `20261109180000_learner_deletion_grace_and_marketing_consent.sql` and `20261109190000_erase_learner_records_after_recovery.sql`. They remain unapplied to production until separately authorised. Keep `ACCOUNT_DELETION_FINALIZER_ENABLED=false` until migrations, schema checks and deletion tests are complete. The Terms and Privacy Policy wording will be reviewed and updated in a separate documentation/legal-review pass after the feature set is complete.


## AI course production and lesson media addendum — 21 November 2026

See [AI Course Production and Media Architecture Audit](AI_COURSE_PRODUCTION_AND_MEDIA_ARCHITECTURE.md) for the current-state audit, workflow, security model and implementation requirements.

The canonical curriculum remains **Track → Course → Module → Lesson**. A track groups ordered courses; courses remain independently discoverable/enrollable where permitted and may also be included in one or more tracks. A course may include Excel in its own modules while a separate standalone Excel course also exists. Do not collapse courses into tracks or modules.

AI course production is an internal Learnora ME capability operated by authorised Learnora Teams staff. It is not available to independent creators, tutors or customer organisations. The feature must be enforced by backend internal-staff permissions. The separate Learnora Teams website remains a distinct application and is not being rebuilt in this phase; the current integration is a backend and product capability, with a later Teams website build after Learnora ME integration is stable.

The existing `services/ai_gateway.py` is the LLM integration point and must be extended through a named course-production profile rather than replaced. The individual learner workspace supports signed video playback, YouTube/Vimeo embeds, lesson text, resources and learner notes; native MP4 playback now resumes from the saved lesson position. The cohort learner lesson endpoint and page also support authorised ready-video playback, with video position saved to the existing cohort progress record and restored on return. Both learner surfaces present the primary lesson video before the concise authored note. The active Teams content manager already supports manual curriculum and media management; AI generation and automated rendering are new capabilities, not existing completed features.

Human-uploaded course videos and resources continue to use the existing private Supabase Storage workflow. The new AI renderer stores its finished MP4s in a separate private Cloudflare R2 bucket and records the provider/object key in the existing `lesson_videos` table. For new Course Studio courses, human-produced and AI-rendered MP4s both use private Cloudflare R2. Older manual media remains in private Supabase Storage. The learner backend checks course access and returns a temporary signed playback URL for either provider. The R2 worker, storage configuration and playback code are in repository source, but the bucket, credentials and production environment are not configured. The new Course Studio migration is pending and has not been applied to live Pheonix.

The Course Studio is currently available as a staff-only route inside Learnora ME at `/team-studio`; the separate `frontend-team/` application remains a distinct website and its broader rebuild is deferred until this integration is stable. When the Learnora Teams website is resumed, its media manager must use the same private R2 upload/preview flow for new Course Studio courses while preserving the existing Supabase media path for legacy courses. Curriculum and lesson generation require `content.generate`; track creation and final course/track publication require `content.manage`. AI-generated courses remain drafts until the final atomic Course Studio publication action confirms every required lesson package, rendered video, media asset and knowledge check is ready. Track linking occurs during publication, after the backend rechecks the track's enrolment lock. Course Studio lets staff choose AI or human video production per lesson. AI videos are rendered in the worker; human videos can be uploaded from Course Studio through a short-lived private R2 upload URL. The learner player displays the primary lesson video with the concise authored note below it.

The first pilot production briefs are Data Analytics, Excel Fundamentals and Front-end Web Development. Data Analytics is the first priority; Excel is both a module within Data Analytics and a separate standalone course; Front-end Web Development has its own track. The test Introduction to Data Analytics course is to be archived and unlinked only after the real replacement has been reviewed and published. Preserve its existing enrolments, progress and certificates; do not hard-delete learner history.


The cohort learner video correction is implemented in `backend-python/routers/cohort_learning.py` and `frontend-v02/app/dashboard/cohort/courses/[courseId]/lessons/[lessonId]/page.tsx`. It reuses the existing cohort assignment checks and media signer; the video asset is returned only after the learner is authorised for that course and lesson. Regression coverage is in `backend-python/tests/test_cohort_learning_access.py`. This source change is not deployed. Legacy Supabase media signing uses the verified private `learnora-course-media` video bucket and `learnora-resources` resource bucket. New Course Studio MP4s use private Cloudflare R2. The existing `lesson_videos` schema has no bucket-name column, so the backend selects the appropriate legacy bucket by asset type rather than storing a signed URL or inventing a schema field.

The individual learner video player now seeks to the saved `last_position_seconds` value when MP4 metadata is loaded, using the existing `learnora_lesson_progress` record. No new progress schema was introduced.
