# Learner outcomes extension — phases 6–8

**Date:** 2 November 2026  
**Repository:** `Obikpe/Learnora-ME`  
**Scope:** Learnora ME learner outcomes and the supporting Learnora Teams workflows.

This document records the product owner's revised order for the next learner-outcome features. It supersedes the earlier proposed sequencing that placed track-completion feedback immediately after phases 1–5. That earlier feedback proposal is retained as backlog work; it is not silently deleted.

## Product decisions that remain binding

1. The official curriculum remains the published track → course → module → lesson structure. An AI-generated learning plan is optional and sits on top of that structure. AI output cannot create, remove, reorder or change official curriculum.
2. Learnora should measure demonstrated capability, not just course activity. A viewed lesson, AI-generated exercise or self-reported note is not verified competence.
3. Free launch remains intact. These phases must not add checkout, payment method, subscription, trial or expiry requirements. Existing Paystack, paid subscription, Pro and entitlement implementations remain untouched and reversible.
4. Phase 9 (learning companion/community) remains later scope.

## Phase 6 — Certificates and verification

### Existing foundation

The active schema already has `certificates` with a unique `certificate_number`, a course foreign key, learner foreign key, issue timestamp and JSON metadata. The table has RLS enabled and the backend service role is the only role with direct table privileges.

### Implemented

- Added authenticated `GET /api/credentials/me` to return issued certificates and courses whose full completion rules have been met but whose certificate has not yet been claimed.
- Added authenticated `POST /api/credentials/courses/{course_id}/issue`. It checks the same saved lesson, published-quiz and graded-assignment completion rules used by course progress before issuing a credential.
- Certificate numbers are deterministic HMAC-derived identifiers scoped to the learner and course. The existing unique certificate-number constraint provides idempotency and protects concurrent claim attempts.
- Added public `GET /api/credentials/verify/{certificate_number}`. It returns only the credential number, learner display name, course title, issuer and issue date; it does not disclose the learner's email or account ID.
- Added the learner certificate workspace, claim action, public verification page and browser print/save-to-PDF presentation.

### Boundaries

- The current credential is a **course-completion certificate**. Track-level credentials are not yet issued.
- Verification now distinguishes valid and revoked credentials. A new additive migration adds revoked_at, revoked_by and revocation_reason; an authorised Teams endpoint records revocation in the audit log, and the Teams certificate register exposes the action. The migration is in the repository and disposable-database CI path, but is not applied to the live Pheonix database.
- No payment or subscription condition is part of certificate eligibility.

## Phase 7 — Practice Lab and project submissions

### Existing foundation

The active schema already has `projects` and `project_submissions`. The backend project/skill management APIs were already registered; this checkpoint adds a dedicated Learnora Teams Practice Lab page and connects it to those APIs.

### Implemented

- Added internal staff APIs for skill catalogue management, project creation, editing, publication/unpublication, submission review and audit logging.
- Connected the existing Teams project workspace to the registered backend routes. Staff can associate a project with a global Learnora course, map it to catalogue skills, publish it and review submissions.
- Added learner discovery of published challenges. Course-linked challenges are visible only to learners with an active/completed enrolment in that published global Learnora course; standalone challenges remain open.
- Added the learner Practice Lab with a written project brief, submission explanation and HTTP/HTTPS repository, live-demo or supporting links.
- Added learner submission history and reviewer feedback.
- A staff approval requires at least 70%. The review flow prepares platform-generated evidence for the skills mapped to the project before changing the submission to approved; the mastery query counts it only after the approved state is saved. Returned work remains visible but does not count as verified mastery. If an approval is reversed, the status stops contributing immediately and derived evidence is cleaned up.
- Corrected the submission status filter to use the database's allowed values (`draft`, `submitted`, `reviewed`, `approved`, `returned`); the previous `under_review` value was not valid under the live constraint.
- Learners can add manual notes, but cannot self-assign a score or create platform-verified project/assessment evidence.

### Boundaries

- This Practice Lab is a structured challenge and submission/review workspace. It does **not** execute arbitrary Python/SQL code in a hosted sandbox and does not upload raw files; learners submit written work and links. A secure execution sandbox or file-upload workflow would be a separately designed capability, not something to fake with browser-side `eval` or an unsafe backend runner.
- Project submission URLs are restricted to HTTP/HTTPS.
- Course-linked projects are restricted to published global Learnora courses.

## Phase 8 — Skill mastery map and learner portfolio

### Implemented

- The learner skill map reads the central skill catalogue and calculates proficiency from approved project evidence only.
- Each evidence record counts only when its source submission belongs to the authenticated learner, has status `approved`, and the referenced skill is actually mapped to that project. This prevents a learner from attaching an arbitrary skill ID to an approved submission.
- Scores are averaged per skill. The current display uses `competent` for 70–84%, `advanced` for 85–100%, and `not_started` when there is no verified evidence.
- Manual notes, unreviewed work and returned submissions do not increase mastery.
- Added a private learner portfolio combining verified skills, approved projects, reviewer feedback, external work links and issued certificates. The learner can print/save the portfolio as a PDF.

### Boundaries

- The portfolio is private to the learner's authenticated workspace and can be exported as a PDF. A public hosted portfolio URL and public visibility controls require an explicit consent/settings data model; those have not been added to the existing schema or made public by default.
- The skill map currently uses reviewed project evidence. Automatic skill mapping from every quiz and assignment is not claimed; those assessment types need explicit skill-to-assessment relationships before their scores can contribute.

## Learnora Teams management

The existing Teams workspace now has backend support for the project and skill workflow. Staff with the existing `courses.view` and `content.manage` permissions can list skills/projects, create and edit skills, create project drafts, map skills, associate a global course, publish/unpublish projects, inspect submissions and record a decision/score/feedback. Review actions are written to the existing audit log.

The previously implemented course, track, module, lesson, resource, assessment and grading work remains the curriculum-authoring foundation. These additions do not replace it.

## Live schema verification — 2 November 2026

The read-only connection to the active Pheonix Supabase project is now working. The following relevant live objects were checked through PostgreSQL catalog queries:

- `certificates`, `projects`, `project_submissions`, `skills`, `skill_evidence` and `learner_skills` exist.
- Their columns match the fields used by the new APIs. The live `project_submissions_status_check` permits `draft`, `submitted`, `reviewed`, `approved` and `returned`. The live evidence-type check permits `quiz`, `assessment`, `assignment`, `project`, `simulation`, `certificate` and `manual`.
- `certificates.certificate_number` and `skills.name` have unique indexes.
- RLS is enabled on the relevant tables. The inspected table grants were limited to `service_role`; no direct `anon` or `authenticated` table grants were present.
- The relevant certificate, project, submission and skill tables currently contain zero rows. This means live learner/Teams workflow acceptance still requires controlled test records and an authorised test account.

### Existing phase 3 migration discrepancy

The migration ledger currently ends at `20261028171902`. The repository's `20261102090000_learner_learning_plans.sql` migration is not in the live ledger, and `public.learner_learning_plans` does not exist in the active database. Do not treat the optional plan workspace as production-operational until that additive migration has been separately reviewed, replayed and approved for the active project. No migration has been applied as part of phases 6–8.

## Verification and release status

- A combined contract test file was added at `backend-python/tests/test_learning_outcomes.py`.
- The new code has been committed to `main`.
- CI, browser-driven learner acceptance and staff acceptance have **not** been established by this implementation record. Do not label the features production-release verified solely because the code is committed.
- At the original implementation checkpoint, no production migration, environment change or deployment had been performed. The newer release-preparation checkpoint below records the later staging builds and the reversible Production free-access setting. Paid implementation remains preserved.

## Deferred items

- Phase 9 — learning companion and community.
- The earlier track-completion feedback/review proposal, including public-display consent and moderation.
- Track-level certificates.
- Hosted code execution, raw file uploads and public learner portfolio pages.
- Automatic mapping of quizzes/assignments to skills.

## Follow-up hardening — 2 November 2026

- The AI tutor is hidden on the learner course player while a quiz is opening or active, the quiz-specific tutor action is removed, and the AI page checks the backend active-session endpoint. The backend denies tutor requests for any learner with an unexpired quiz session and fails closed if the session lookup cannot be verified.
- The learner shell now checks the backend active-session list across tabs; the course player can recover a server-held session after a browser restart. An unsubmitted session cannot be deleted through the close endpoint: the backend requires a submitted attempt created after that session began before it releases the lock. This prevents a direct API call or a duplicated tab from restoring tutor access mid-assessment.
- Active quiz sessions are tab-scoped and expire after two hours if a browser is abandoned. A submitted quiz session is released when the learner closes its results view; an unsubmitted session remains locked and resumable if its tab is closed, preventing a second tab from releasing the tutor lock while the assessment is still in progress. The session table is service-role-only with RLS enabled; its migration and rollback are included in the disposable database workflow.
- Certificate revocation now has an additive schema migration, a staff-only API requiring the existing content.manage permission, audit logging, a Teams register, and public verification that reports revoked credentials as invalid. Public verification does not disclose the internal revocation note.
- Learner project history now distinguishes approved, returned, reviewed and awaiting-review states and displays reviewer feedback. Skill evidence remains derived only from an approved submission and a skill mapped to its source project.
- The combined contract tests cover certificate privacy/revocation, quiz tutor exclusion and the migration inventory. GitHub Actions were triggered by commits to main; the latest candidate is not yet evidenced as passing while its runs remain queued. Browser-driven learner/staff acceptance is still outstanding.
- Both new migrations remain unapplied to the active Pheonix project. This is deliberate: the existing migration policy requires successful disposable replay and a separate explicit production-migration approval. The free-access flag, Paystack, subscriptions, trials, entitlements and Pro logic were not changed.

## Release preparation checkpoint — 2 November 2026

The implementation checkpoint above is historical. The following release preparation is newer and supersedes the earlier statements about environment changes and deployments.

- Explicit Vercel staging builds from `Obikpe/Learnora-ME` completed successfully for all three active applications: Learnora ME (`frontend-v02`), Learnora Teams (`frontend-team`) and the FastAPI backend (`backend-python`). Learner and Teams Next.js builds completed compilation, type checking and static-page generation. The backend Python 3.12 build completed. The learner build includes the certificate, Practice Lab, skills and portfolio routes.
- Staging build references: learner `dpl_4mC59NuvVS3HadiU3pTWZfo1RDiT`; Teams `dpl_7hiqZUWwurpQSaAncjgCyYSzceEv`; backend `dpl_8JoHQYyighk6542J6AmazrJ9wxHs`. These are protected staging deployments, not production aliases.
- Vercel reported no grouped runtime-error clusters for the three existing production projects in the preceding 24 hours. This is an observation of the existing production deployments, not a claim that the new staging endpoints have completed authenticated browser acceptance.
- The production backend project now has the reversible `FREE_ACCESS_MODE=true` environment variable scoped to Production. It takes effect on the next production backend deployment; it does not change the currently running deployment by itself. The original Paystack, subscription, trial and Pro implementation remains preserved.
- The live Pheonix Supabase migration ledger was rechecked and still ends at `20261028171902`. The active database does not yet contain `learner_learning_plans`, `quiz_active_sessions`, or the certificate revocation columns. The four additive migrations dated 2 November therefore remain a hard production dependency for the new learning-plan, quiz-session-lock, certificate-revocation and project-integrity behaviours.
- No production database migration has been applied. Production deployment of the new backend and frontends is intentionally held until the additive migrations have been rehearsed against a disposable PostgreSQL/Supabase branch and separately approved for the active project.
- The general CI workflows were consolidated to one release-check job covering Python compile/lint/import, selected phase regression tests, additive migration/rollback rehearsal, backend HTTP startup and both active frontend builds. Duplicate backend/frontend workflows were removed; the expensive cohort database workflow now triggers only for cohort-specific changes. The final GitHub Actions run was still queued at this checkpoint, so no green CI result is claimed.
- The previous production Teams and backend deployments were built from older `Pheonix-Analytics` commits. The release-candidate staging deployments were explicitly built from `Learnora-ME`. Production will be deployed from the current repository and correct monorepo roots; automatic Git push linkage should be checked separately because Vercel project Git connections are not changed by a manual deployment.
- Production domains currently assigned to the Vercel projects are `learnora-me.vercel.app`, `teamslearnora.vercel.app` and `learnora-backend.vercel.app`. Both frontend Next.js configurations proxy `/api/*` to the backend domain; this same-origin proxy is retained.
- Production migration, browser-based learner/staff acceptance and the final production deployment remain unverified. Do not mark phases 6–8 as production-release complete until these gates pass.
