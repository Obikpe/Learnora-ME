# Learner journey implementation — phases 1–5

**Implementation date:** 2 November 2026  
**Working branch:** `main` only  
**Scope:** Learnora ME learner journey and Learnora Teams internal content operations  
**Product rule:** Learnora should help a learner become capable of doing something with what they have learned—not merely accumulate course completions.

This document records the implementation work for the five requested phases. It is additive to the original product specification, roadmap, and free-launch plan. It does not cancel later certificate, Practice Lab, skill-map, portfolio, community, organisation, instructor, creator, or paid-expansion work.

## 1. Canonical learning architecture

The current repository and checked-in schema use the following relationships:

```text
Global published track
  learnora_learning_paths
        |
        | ordered membership (order_index, required)
        v
  learnora_learning_path_courses
        |
        v
  learnora_courses
        |
        v
  course_modules
        |
        v
  learnora_lessons

Course/module/lesson assessments:
  quizzes -> quiz_questions -> quiz_attempts
  assignments -> assignment_submissions
```

Rules:

- Global learner tracks are rows in `learnora_learning_paths` with `owner_user_id IS NULL` and `organisation_id IS NULL`.
- The ordered course membership is `learnora_learning_path_courses`; its `order_index` and `required` values are authoritative.
- `learnora_tracks` and `cohort_track_courses` remain cohort-specific. They are not repurposed for the public individual catalogue.
- A course contains ordered `course_modules`; modules contain ordered `learnora_lessons`.
- Quizzes belong to a course and may be attached to a module and/or lesson. Questions and attempts remain in their existing tables.
- Assignments belong to a course and may be attached to a lesson. Learner submissions and staff grades remain in `assignment_submissions`.
- Track progress is derived from the required course records. A learner-specific plan is not a new curriculum and cannot mutate a published track.

The canonical model is established by the checked-in schema baseline and existing track/content APIs. The active Pheonix live SQL catalogue has not been re-verified in this work because the previously documented read-only database connection failure remains a release constraint.

## 2. Phase status

| Phase | Implementation | Remaining acceptance |
|---|---|---|
| 1. Architecture and relationships | Canonical track → course → module → lesson and assessment relationships retained; publication validation strengthened | Live Pheonix SQL catalogue revalidation remains blocked by the read-only database authentication failure; repository/CI schema checks pass |
| 2. Discovery and track browsing | Public course payloads expose real published track membership; course catalogue filters by track; track catalogue supports search and level filters | Browser/mobile acceptance |
| 3. Optional AI learning plans | Profile-based plan generation, saved versions, weekly course schedule, validated AI guidance and rule-based fallback; individual-learner access boundary | Disposable PostgreSQL migration/RLS/grant/rollback checks pass in CI; active Supabase migration and provider/browser acceptance remain |
| 4. Assessments, grading and completion | Teams quiz settings and question editing, assignment configuration/editing, answer validation, grading audit events, learner performance, and assessment-aware completion | Automated regression/build checks pass; browser-driven learner/Teams acceptance and immutable grade-revision history remain |
| 5. Contextual AI tutor | Verified course/lesson/assessment context, lesson progress, recent quiz attempts and assignment feedback; answer keys excluded and assessment-to-lesson scope enforced | Provider-level, browser and privacy acceptance remain |

A route or component existing is not treated as production acceptance. CI and live-schema evidence must be recorded separately.

## 3. Phase 2 — catalogue discovery and track browsing

The public course endpoint now includes a `tracks` collection derived from `learnora_learning_paths` and `learnora_learning_path_courses`. It only attaches published global Learnora tracks to global Learnora courses; tenant and creator courses do not inherit a global track label.

The Learnora ME course catalogue filters using those actual relationships rather than a free-text `settings.track` label. The track catalogue adds search across track names/descriptions/course names and a course-level filter. Existing public track detail and enrolment routes remain the source for the structured journey.

## 4. Phase 3 — optional personalised learning plans

The AI plan is an optional layer on top of a selected published track (or a flexible set of published global courses). It does not create, delete, reorder, publish, or otherwise modify catalogue content.

Inputs come from the learner's saved onboarding profile: goal, experience level, interests, and weekly study time. The backend uses the real published course IDs, titles, levels, required/optional flags, and estimated hours to construct a bounded weekly schedule. The AI provider is asked for strict JSON week-by-week focus, practice, and reflection guidance. That output is validated against the fixed schedule before it is stored. If the provider is unavailable or the structure is invalid, the plan uses clearly labelled rule-based guidance instead.

The plan is saved as a versioned record in `learner_learning_plans`; generating a replacement archives the previous active plan. Learners can view, regenerate, and archive their plan. Course and track completion still comes from backend learning/assessment records, never from the plan.

**Database dependency:** `supabase/migrations/20261102090000_learner_learning_plans.sql` creates the new table with an owner FK, track FK, bounded weekly-time constraint, JSONB plan data, active/archive status, index, RLS enabled, and an explicit `service_role` grant. `anon` and `authenticated` receive no direct table grants. A rollback file is in `supabase/rollback/`.

The migration is replayed by the Cohort Learning Access CI workflow against a disposable PostgreSQL database restored from the checked-in catalog schema. Assertions verify table creation, RLS, browser-role denial, service-role privileges and the checked-in rollback (inside a transaction). That replay passed on implementation checkpoint `8e21f264744a1a49d26d0f81b3272f1c5d72f24a`. It has **not** been applied to the active Pheonix Supabase project. The active project's read-only SQL connection still fails password authentication, and no staging branch is available. Apply it to the active project only through a separately approved release process.

## 5. Phase 4 — assessment authoring, grading and completion

Learnora Teams now has an Assessments workspace and permission-protected APIs to:

- list course modules, quizzes and assignments;
- create draft quizzes attached to a course/module/lesson;
- configure passing score (70–100%) and maximum attempts;
- add, edit and remove supported auto-graded multiple-choice and true/false questions while the quiz is a draft;
- edit draft quiz title, description, passing threshold and attempt limit;
- validate correct answers against configured options before publishing;
- publish/unpublish quizzes;
- create, edit and publish course/lesson assignments, including instructions, lesson association, maximum score and optional due date; published assignment settings must be unpublished before editing;
- review learner assignment submissions and save score, feedback, grader identity and grading time;
- inspect per-course learner lesson progress, quiz attempts and assignment grading.

Module unlocking checks every published quiz in each earlier module against that quiz's configured threshold; an earlier module with no published quiz does not deadlock progression. Course completion requires all learner-visible published lessons to be completed, every published quiz to have a passing attempt at its configured threshold, and every published assignment's latest submission to be graded at 70% or above of its configured maximum score. The course progress percentage counts lesson and published-assessment completion units. Track completion continues to use required-course completion, so assessment gates flow through to track progress.

A published assessment is treated as required for completion. Unpublished drafts do not block completion. A course with no published assessments retains lesson-only completion. Assignment grading is currently based on the latest submission. Each staff grading action is recorded in `audit_logs`; a separate immutable grade-revision history and learner resubmission workflow remain future work.

## 6. Phase 5 — contextual AI tutor

The learner course player now sends course and current lesson IDs when the learner opens the tutor, and can also attach a quiz ID from the quiz card.

The backend does not trust client-supplied lesson content. It verifies:
- the learner has an active/completed enrolment in the course;
- the lesson belongs to the supplied course and is published;
- the module is unlocked for that learner;
- any attached assessment is published and belongs to that course.

It then loads course/module/lesson metadata, bounded lesson text, saved learner lesson progress, assessment questions/options without answer keys, recent quiz outcomes, and recent assignment outcomes/staff feedback. An attached quiz must belong to the active lesson or its module. Course material and staff feedback are treated as untrusted reference data. The contextual tutor is started in a fresh conversation to avoid mixing an unrelated saved conversation into a lesson handoff. The AI is instructed not to reveal or infer answer keys and to coach reasoning rather than simply disclose solutions. The tutor must also be completely hidden and inaccessible during active quizzes; this is a mandatory UI/backend policy and browser-acceptance gate, not merely a prompt instruction.

**Quiz visibility rule (mandatory): the AI tutor must not be visible, launchable, or otherwise accessible anywhere in an active quiz-taking experience.** Hide/remove the tutor entry point, floating launcher, chat panel, contextual handoff and keyboard/accessibility entry points for the entire quiz attempt, including question navigation, review and submission states. Do not rely on the model prompt or omission of answer keys as the control. The learner may use the tutor from ordinary lesson/course learning surfaces outside an active quiz; returning to the quiz must not preserve an accessible tutor overlay or allow a tutor request to be submitted against the quiz. Enforce this in the UI and, where requests can be made independently of the UI, in the backend request policy. Browser acceptance must verify that no tutor affordance or tutor response can be reached during an active quiz.

General tutor use remains available without a course context. The contextual path is optional and does not alter enrolments, progress, curriculum, or assessments.

## 7. Next milestone and Phase 6 sequence

The next milestone is deliberately limited to two release-readiness workstreams:

1. **Live Supabase verification:** regain a working read-only connection to the active Pheonix project, verify the live SQL catalogue, migration ledger, RLS and grants against the checked-in baseline, reconcile the additive learning-plan migration, and document an approved, reversible migration plan. Do not apply a production migration or mutate production data without separate explicit approval.
2. **Browser-based acceptance:** exercise learner discovery/enrolment, course and track progress, optional learning-plan generation and fallback, quiz/assignment completion, Teams assessment authoring/grading/performance, and contextual tutor behaviour. Specifically verify the tutor is completely unavailable throughout every active quiz state. Record browser evidence and defects on the exact candidate SHA; production builds alone are insufficient.

Once those two workstreams pass and any separately required migration approval is obtained, proceed directly to **Phase 6 — track completion and learner feedback**: completion-gated, dismissible feedback; optional rating/comment; explicit consent before public display; staff moderation; duplicate prevention; and privacy-safe public rendering. Do not insert unrelated feature phases between this acceptance milestone and Phase 6.

## 8. Free-launch and paid-system protection

No free-access resolver, Paystack integration, checkout, subscription, trial, expiry, entitlement, Pro, or payment-history code was removed or rewritten for these phases. The central `FREE_ACCESS_MODE` remains server-side and default-off. These features do not introduce a payment method, paid subscription, checkout, or trial-expiry requirement for the individual learner journey.

The optional AI plan uses the existing AI provider/quota service; it does not grant organisation, staff, creator, or administrative access. Existing authentication, course access, tenant scope, private media, and internal staff permission boundaries remain in force.

## 9. Verification and known limitations

- Regression coverage now includes assessment completion thresholds/latest assignment submissions, module unlocking (configured thresholds and no-quiz modules), individual-only onboarding/plan access, quiz/assignment publication/edit guards, and learning-plan scheduling.
- All five GitHub Actions workflows passed on implementation checkpoint `8e21f264744a1a49d26d0f81b3272f1c5d72f24a`: [backend regression tests](https://github.com/Obikpe/Learnora-ME/actions/runs/41438366731), [backend verification](https://github.com/Obikpe/Learnora-ME/actions/runs/41438366705), [all three frontend production builds](https://github.com/Obikpe/Learnora-ME/actions/runs/41438366775), [quality checks](https://github.com/Obikpe/Learnora-ME/actions/runs/41438366744), and [cohort-learning plus disposable database migration tests](https://github.com/Obikpe/Learnora-ME/actions/runs/41438366779).
- The disposable PostgreSQL workflow applied `20261102090000_learner_learning_plans.sql`, verified RLS and role grants, and executed the rollback inside a transaction. This does not constitute a migration of the live Pheonix project.
- The live Pheonix SQL catalogue remains unverified because the read-only database connection fails password authentication. No staging Supabase branch was available. No live migration, production data mutation, Vercel environment change, or deployment was performed.
- Full browser/mobile acceptance of discovery, course completion, Teams assessment workflows, AI tutor context, and the plan generation/fallback path remains outstanding. The CI frontend builds are production builds, not browser-driven acceptance tests.
- The AI plan's week allocation is deterministic from published course estimates; the AI personalises each week's focus, practice and reflection. The AI cannot alter the underlying curriculum or invent courses.
- Teams now exposes in-place editing for draft quiz settings/questions and draft assignment settings. Published assessments must be unpublished before editing.
- Each staff grading action is recorded in `audit_logs`; a separate immutable grade-revision history and learner resubmission workflow remain future work.

The five phases are implementation-complete and automated-CI-verified on the checkpoint above. Do not treat that as production-release approval: live schema verification, browser/mobile acceptance, and the separately approved live migration/deployment remain release gates.
