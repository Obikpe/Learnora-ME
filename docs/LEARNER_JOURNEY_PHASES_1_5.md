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
| 1. Architecture and relationships | Canonical track → course → module → lesson and assessment relationships retained; publication validation strengthened | Live schema comparison and full regression run |
| 2. Discovery and track browsing | Public course payloads expose real published track membership; course catalogue filters by track; track catalogue supports search and level filters | Browser/mobile acceptance |
| 3. Optional AI learning plans | Profile-based plan generation, saved versions, weekly course schedule, AI-generated weekly guidance and fallback; learner workspace and dashboard entry | Apply additive plan migration in a disposable/staging database; verify provider/fallback and browser journey |
| 4. Assessments, grading and completion | Teams quiz/assignment authoring, answer validation, assignment grading, learner performance view, assessment-aware course completion | Test suite and end-to-end learner/Teams acceptance |
| 5. Contextual AI tutor | Verified course/lesson/assessment context, learner progress and recent attempts; answer keys excluded | Provider-level tests, browser acceptance and privacy review |

A route or component existing is not treated as production acceptance. CI and live-schema evidence must be recorded separately.

## 3. Phase 2 — catalogue discovery and track browsing

The public course endpoint now includes a `tracks` collection derived from `learnora_learning_paths` and `learnora_learning_path_courses`. It only attaches published global Learnora tracks to global Learnora courses; tenant and creator courses do not inherit a global track label.

The Learnora ME course catalogue filters using those actual relationships rather than a free-text `settings.track` label. The track catalogue adds search across track names/descriptions/course names and a course-level filter. Existing public track detail and enrolment routes remain the source for the structured journey.

## 4. Phase 3 — optional personalised learning plans

The AI plan is an optional layer on top of a selected published track (or a flexible set of published global courses). It does not create, delete, reorder, publish, or otherwise modify catalogue content.

Inputs come from the learner's saved onboarding profile: goal, experience level, interests, and weekly study time. The backend uses the real published course IDs, titles, levels, required/optional flags, and estimated hours to construct a bounded weekly schedule. The AI provider is asked for strict JSON week-by-week focus, practice, and reflection guidance. That output is validated against the fixed schedule before it is stored. If the provider is unavailable or the structure is invalid, the plan uses clearly labelled rule-based guidance instead.

The plan is saved as a versioned record in `learner_learning_plans`; generating a replacement archives the previous active plan. Learners can view, regenerate, and archive their plan. Course and track completion still comes from backend learning/assessment records, never from the plan.

**Database dependency:** `supabase/migrations/20261102090000_learner_learning_plans.sql` creates the new table with an owner FK, track FK, bounded weekly-time constraint, JSONB plan data, active/archive status, index, RLS enabled, and an explicit `service_role` grant. `anon` and `authenticated` receive no direct table grants. A rollback file is in `supabase/rollback/`.

This migration has **not** been applied to the active Supabase project or to staging. The plan API cannot be enabled in a deployed environment until the migration has been tested against a disposable/staging database and applied through the approved release process. Supabase's Data API default-grant changes mean the explicit server-role grant is intentional; the table remains backend-only.

## 5. Phase 4 — assessment authoring, grading and completion

Learnora Teams now has an Assessments workspace and permission-protected APIs to:

- list course modules, quizzes and assignments;
- create draft quizzes attached to a course/module/lesson;
- configure passing score (70–100%) and maximum attempts;
- add/remove supported auto-graded multiple-choice and true/false questions;
- validate correct answers against configured options before publishing;
- publish/unpublish quizzes;
- create and publish course/lesson assignments;
- review learner assignment submissions and save score, feedback, grader identity and grading time;
- inspect per-course learner lesson progress, quiz attempts and assignment grading.

Existing module unlocking remains assessment-aware. Course completion now requires all learner-visible published lessons to be completed, every published quiz to have a passing attempt at its configured threshold, and every published assignment's latest submission to be graded at 70% or above of its configured maximum score. The course progress percentage counts lesson and published-assessment completion units. Track completion continues to use required-course completion, so assessment gates flow through to track progress.

A published assessment is treated as required for completion. Unpublished drafts do not block completion. A course with no published assessments retains lesson-only completion. Assignment grading is currently a single latest-submission grade; each staff grading action is recorded in `audit_logs`, but a separate immutable grade-revision history and resubmission workflow are not introduced here.

## 6. Phase 5 — contextual AI tutor

The learner course player now sends course and current lesson IDs when the learner opens the tutor, and can also attach a quiz ID from the quiz card.

The backend does not trust client-supplied lesson content. It verifies:
- the learner has an active/completed enrolment in the course;
- the lesson belongs to the supplied course and is published;
- the module is unlocked for that learner;
- any attached assessment is published and belongs to that course.

It then loads the course/module/lesson metadata, lesson text (bounded), saved learner lesson progress, assessment questions/options without answer keys, and the learner's recent quiz outcomes. The contextual tutor is started in a fresh conversation to avoid mixing an unrelated saved conversation into a lesson handoff. The AI is instructed not to reveal or infer answer keys and to coach reasoning rather than simply disclose solutions.

General tutor use remains available without a course context. The contextual path is optional and does not alter enrolments, progress, curriculum, or assessments.

## 7. Free-launch and paid-system protection

No free-access resolver, Paystack integration, checkout, subscription, trial, expiry, entitlement, Pro, or payment-history code was removed or rewritten for these phases. The central `FREE_ACCESS_MODE` remains server-side and default-off. These features do not introduce a payment method, paid subscription, checkout, or trial-expiry requirement for the individual learner journey.

The optional AI plan uses the existing AI provider/quota service; it does not grant organisation, staff, creator, or administrative access. Existing authentication, course access, tenant scope, private media, and internal staff permission boundaries remain in force.

## 8. Verification and known limitations

- New backend regression files cover assessment authoring constraints and assessment-based course completion; learning-plan scheduling tests were added. Existing publication-readiness fixtures were updated to include answerable quiz questions.
- GitHub Actions workflows were queued for the implementation commit `5e6527009fb07e160696869e0864ceb207fd9310` at the time of the latest check. The latest code-checkpoint workflows were still queued, not passing evidence: [backend regression tests](https://github.com/Obikpe/Learnora-ME/actions/runs/41416399989), [backend verification](https://github.com/Obikpe/Learnora-ME/actions/runs/41416400119), [frontend builds](https://github.com/Obikpe/Learnora-ME/actions/runs/41416399968), [quality checks](https://github.com/Obikpe/Learnora-ME/actions/runs/41416400031), and [cohort-learning tests](https://github.com/Obikpe/Learnora-ME/actions/runs/41416400015). Their queued state is not a pass. The exact final documentation/code SHA must have all required workflows completed successfully before this work is marked evidence-backed.
- No local Python suite or frontend production build has been run in this environment.
- No live Supabase migration, data mutation, Vercel environment change, or deployment was performed.
- The new learning-plan migration requires disposable/staging replay and explicit release approval before deployment.
- Full browser/mobile acceptance of discovery, course completion, Teams assessment workflows, AI tutor context, and the plan generation/fallback path remains outstanding.
- The current AI plan's week allocation is deterministic from published course estimates; the AI personalises each week's focus, practice and reflection. This is deliberate: the AI cannot alter the underlying curriculum or invent courses.
- The Teams question editor supports creating/removing questions; existing question edits can be done through the protected API after unpublishing, but an in-place edit form is not yet exposed in the UI.
- Assignment grades record `graded_by` and `graded_at`, but a separate immutable grade-change audit stream is not yet implemented.

Do not mark the five phases release-complete until the remaining acceptance evidence above is recorded on the exact candidate SHA.
