# Learnora Free Launch → Paid Expansion Plan

**Decision date:** 31 October 2026  
**Status:** Approved product direction; implementation not yet started by this document update  
**Applies to:** Learnora ME, Learnora Teams, shared FastAPI backend, and the existing active Pheonix Supabase project  
**Relationship to existing plans:** This is a dated strategic addendum. It does not replace, erase, or retrospectively rewrite the original product specification, roadmap, security findings, migration history, or organisation/instructor plans.

## 1. Why this addendum exists

The original Learnora plan describes a broader commercial learning platform, including individual learners, creators/instructors, customer organisations, cohorts, subscriptions, payments, entitlements, and internal operations. Considerable product, backend, database, billing, and security work has already been completed toward that model.

The product owner has now chosen a staged launch strategy:

1. Make the learner-facing Learnora service temporarily free to use, without requiring a payment method, payment, subscription purchase, or trial-expiry date.
2. Concentrate implementation on two applications: **Learnora ME** (the learner experience) and **Learnora Teams** (internal course/content operations and platform oversight).
3. Make Teams sufficiently complete for staff to build and publish the catalogue: tracks, courses, modules, lessons, videos, and learning resources; and to inspect learner information and platform usage.
4. Make the learner journey work end to end against that same catalogue.
5. Invite learners to rate Learnora after completing a track, with optional written feedback and explicit consent before public display.
6. Once the free service has attracted real learners and earned trust, progressively introduce paid services, including paid courses and a Pro subscription.
7. Return to the broader organisation and instructor/creator workflows after the two launch-critical applications are operational.

This is a sequencing change, not a cancellation of the original commercial product vision.

## 2. Source-of-truth and preservation rules

- Keep the original sections of `PRODUCT_ENGINEERING_SPEC.md`, `ROADMAP.md`, and the migration/security records. Do not replace them with this plan.
- Treat this document as the current product sequencing addendum. The roadmap should link to it and state which execution order is current.
- Keep the original paid implementation, payment provider integration, subscription records, trial logic, entitlement logic, pricing concepts, and Pro planning. Do not delete them, rewrite history, or comment out large blocks of code as a substitute for a controlled feature switch.
- Record new decisions and actual implementation evidence in `ENGINEERING_HISTORY_AND_DECISIONS.md`.
- Keep deferred organisation and instructor work in the roadmap. Mark it deferred by sequencing, not removed.
- Work on the canonical repository `Obikpe/Learnora-ME`, on `main`, unless the product owner explicitly changes that instruction.
- Active applications: `frontend-v02/` (Learnora ME), `frontend-team/` (Learnora Teams), and `backend-python/` (shared FastAPI backend). Do not use the legacy `frontend/` as the target for new work.
- **Database target clarification (31 October 2026):** Learnora continues to use the already-active Pheonix Supabase project. Do not create or switch to a separate Learnora Supabase project. Existing engineering records identify the project reference as `gihfupzvdpyrmynqgukz`; confirm the configured target through safe, non-secret environment/project metadata before any operation. Never print or commit credentials.
- Repository documentation does not itself authorise a production migration, production data change, or deployment. Keep the existing explicit release-approval gates.

## 3. Temporary free-access phase

### 3.1 Intended learner experience

During the free-launch phase, an individual learner must be able to:

- Register and authenticate without entering card details or adding a payment method.
- Access the free-launch catalogue without purchasing a subscription.
- Enrol in eligible published tracks/courses without a payment checkout.
- Continue learning without a seven-day trial cutoff, subscription expiry, or payment-status lockout.
- Watch available lesson videos, read learning resources, complete supported learning activities, and retain progress.
- Return to the service without being asked to pay merely because an earlier trial/subscription date has elapsed.

The free phase must not silently delete or rewrite historical subscription, payment, trial, or entitlement records.

### 3.2 Reversible implementation; preserve the paid system

Implement a single, central, server-enforced free-access mode (working name: `FREE_ACCESS_MODE`). The final setting name and storage location must follow the existing configuration conventions and be documented in the environment examples.

When enabled:

- The backend grants the intended free-launch access to individual Learnora learners without requiring an active trial or paid subscription.
- Payment checkout and payment-method collection are not prerequisites for those learners.
- Trial and subscription expiry do not block the free-launch learner journey.
- Existing subscription/payment routes and records remain intact for later reactivation.
- The frontend reflects the actual backend access decision; hiding a paywall in the UI alone is not sufficient.
- The mode is centrally controlled and reversible, not implemented as scattered hard-coded exceptions.

When disabled for a future paid launch:

- Existing paid subscription, payment verification, trial, entitlement and expiry checks resume according to the original commercial rules.
- Pro/course pricing and entitlement rules can be introduced incrementally without reconstructing the billing foundation.

Do not make payment or subscription functions public merely to bypass billing. Do not weaken authentication, session security, staff permissions, database RLS, or audit controls.

### 3.3 Scope boundaries and safety

- Free access applies to the intended individual learner experience. It is not permission to bypass organisation tenant boundaries, cohort assignments, creator ownership, internal staff permissions, or protected administrative operations.
- Organisation and instructor/creator commercial workflows remain deferred for product implementation, but their existing data and permission boundaries must not be damaged by the free-mode change.
- Do not grant arbitrary access to unpublished, archived, private, or otherwise restricted content unless an explicit product rule authorises it.
- Email verification and account security requirements remain unless a separate approved decision changes them.
- No credit card, payment, paid membership, or trial-expiry requirement may block an individual learner from using the free-launch catalogue.
- Add backend tests for free access, expired legacy trials, absent payment records, paid-mode regression, role boundaries, and the ability to turn the mode off safely.
- Do not mass-update subscription statuses or expiry dates to simulate free access.

## 4. Immediate product scope: two applications

### 4.1 Learnora Teams — content and platform operations

Learnora Teams is the operational workspace for Learnora staff. The first goal is to make the content lifecycle dependable, not to finish every organisation or instructor feature.

Required capabilities:

1. **Tracks**
   - Create, edit, publish, unpublish/archive, and list tracks.
   - Set track title, slug, description, thumbnail/cover, level/category, and relevant metadata supported by the product.
   - Add courses to a track and define an explicit, editable order.
   - Remove/reorder courses without destroying course records or learner history.
   - Validate that only eligible courses can be attached and that duplicate/invalid links are rejected.
   - Support track publication and learner-facing visibility.

2. **Courses**
   - Create, edit, draft, publish, unpublish/archive, and preview Learnora-owned courses.
   - Manage course metadata, descriptions, thumbnails, level, estimated duration, and catalogue visibility.
   - Clearly distinguish course ownership and access type; do not let the central content workflow accidentally edit organisation-owned or creator-owned content.

3. **Modules and lessons**
   - Create, edit, reorder, publish, unpublish/archive modules and lessons.
   - Support the lesson types already represented by the backend, including video, article/text, practice, quiz, assignment, project, or mixed content where the current schema supports them.
   - Validate ordering, parent-child relationships, and publication dependencies.
   - Provide a useful preview of the learner-facing structure.

4. **Videos and learning resources**
   - Upload videos using the configured storage provider's correct signed-upload flow; verify upload completion and persist the resulting media record.
   - Support approved external video providers/URLs where already supported.
   - Attach, replace, and remove learning resources with appropriate metadata.
   - Show upload progress, validation errors, retry behaviour, and final processing/availability state.
   - Enforce file type/size constraints and private/public access rules. Never expose service-role credentials or private storage objects through public URLs without an intentional access policy.

5. **Learner and platform oversight**
   - Search and inspect learner accounts using role-appropriate, privacy-minimised fields.
   - View learner enrolments, course/track progress, completion, and relevant activity.
   - Provide platform-level statistics such as registrations, active learners, track/course enrolments, published content, completion rates, and lesson engagement where reliable underlying events exist.
   - Define each metric (time window, denominator, active definition, and source table/event) so dashboards do not display misleading counts.
   - Include loading, empty, error, permission-denied, and pagination states.

Organisation management, cohort administration, instructor management, creator applications, payouts, and customer tenant workflows remain part of the larger product plan but are not launch-critical scope for this phase. Preserve existing APIs, schema, and security boundaries while avoiding new feature expansion in those areas.

### 4.2 Learnora ME — learner experience

The learner application must consume the same published catalogue and learning structure managed through Teams.

Required end-to-end journey:

1. Register/sign in and reach the learner experience without a payment method or paid subscription.
2. Discover published tracks and courses with accurate descriptions and availability.
3. View track details, course sequence, modules, lessons, and learning requirements.
4. Enrol in a track or course under the free-launch rules.
5. Open lessons and access their videos/resources.
6. Complete supported activities and assessments.
7. Save and retrieve progress reliably across sessions/devices.
8. Resume learning from the correct course, module, or lesson.
9. Complete a course and then a track using explicit completion rules.
10. See a meaningful completion state and, where supported, a certificate/record that is backed by actual completion data.

Do not present a track as complete merely because a learner opened its final page. Completion rules must be explicit and consistently enforced by the backend.

### 4.3 Shared track/course model

Before adding tables or migrations, inspect the current `main` schema, active Supabase catalog, and existing track/path/course entities. Reuse the intended canonical model where it already exists; do not create a second track system or misuse cohort-specific track assignments.

The learner-facing model must support:

- A track containing an ordered set of courses.
- A course containing ordered modules.
- A module containing ordered lessons.
- Track/course enrolment and learner progress with stable identifiers.
- Historical completion records that remain meaningful if content is later edited or archived.
- Clear separation between general public Learnora tracks and cohort-specific track/course assignment rules.

If the current schema cannot represent the general public track-to-course relationship safely, propose a migration with constraints, indexes, RLS/permissions, rollback, and tests. Test it against a disposable database first. Production migration requires separate approval.

## 5. Track-completion ratings and learner feedback

After a learner genuinely completes a track, Learnora ME should offer a small, dismissible feedback prompt.

Requirements:

- Trigger only when the backend confirms track completion.
- Ask for a rating (for example, 1–5 stars).
- Allow an optional written comment.
- Allow the learner to skip or dismiss the prompt without blocking learning.
- Prevent duplicate submissions for the same learner/track unless an explicit edit policy permits updates.
- Record the track, learner, rating, comment, timestamps, and moderation/publication state.
- Ask separately for consent before showing the comment publicly; do not assume completion or submission implies consent.
- Provide internal moderation controls in Teams: review, approve, reject, hide, and record moderation actions.
- Publish only approved, consented reviews on a public testimonials/reviews page.
- Escape/sanitise displayed user content and provide abuse-reporting/removal handling.
- Use genuine review content and accurate aggregate calculations. Do not fabricate, incentivise undisclosed positive reviews, or mark up self-serving organisation reviews in a way that violates search-engine review-snippet policies.
- Make public reviews crawlable/indexable only after moderation and privacy checks. Search indexing is a goal, not a guarantee of rich-result stars.

This feedback feature is part of the free-launch trust-building strategy; it must not delay core course creation, publishing, enrolment, and learning workflows.

## 6. Later paid expansion — preserve and reactivate

The paid model remains an intended later stage, not a discarded project.

Potential staged commercial capabilities include:

- Selected paid courses while other courses/tracks remain free.
- Pro subscription with clearly defined benefits and access rules.
- Paid learning paths or premium content bundles if justified by usage.
- Existing payment provider integration and verification.
- Subscription lifecycle, renewals, cancellation, expiry, receipts, and entitlement enforcement.
- Organisation and instructor/creator commercial services from the original product plan.

Before charging users, define and document:

- Which content is free versus paid and who can change that classification.
- Whether existing learners retain access to content they already enrolled in or completed.
- Pro benefits, price, billing period, cancellation and renewal behaviour.
- Payment failure, refund, chargeback, grace-period and entitlement-revocation rules.
- How free-launch learners are treated when paid access is introduced.
- Clear notices before a previously free item becomes paid; do not retroactively surprise learners or remove earned completion records.
- Payment provider/webhook verification, idempotency, audit history, tax/consumer requirements applicable to the launch markets, and support/refund processes.
- Tests proving paid checks work again when free mode is disabled.

No pricing or paid launch date is set by this addendum. A later explicit product decision must approve the commercial rollout.

## 7. Revised execution sequence and acceptance gates

The sequence below governs immediate implementation. The original roadmap phases remain preserved as the wider engineering/security backlog; their unresolved security and release gates still apply wherever they are prerequisites for safe work.

| Order | Workstream | Acceptance evidence |
|---|---|---|
| 0 | Establish current baseline and protect the active Pheonix Supabase target | Confirm repository/main SHA, configured project identity without secrets, current schema/catalog, relevant CI state, and existing billing/access code. No production mutation. |
| 1 | Reversible free-access mode | Central server-side switch; no payment/card/trial-expiry barrier for individual free-launch learners; paid-mode regression tests; organisation/admin boundary tests. |
| 2 | Teams track/course content management | Staff can create/edit/order/publish tracks and courses using canonical relationships; changes appear correctly in learner catalogue. |
| 3 | Teams modules, lessons, video and resource management | Full create/edit/reorder/publish/upload/attach journey verified, including storage errors, retries, access rules and media playback. |
| 4 | Teams learner management and platform analytics | Search/detail views and metrics backed by defined, tested queries/events with privacy controls. |
| 5 | Learnora ME discovery and learning journey | Learner can discover, enrol, learn, resume, complete activities, and retain progress without payment/expiry interruption. |
| 6 | Track completion and feedback | Backend-confirmed completion triggers optional rating/comment; consent, moderation, duplicate prevention, public display and indexing rules verified. |
| 7 | Free-launch release readiness | Both frontends build; relevant backend/database/security suites pass on one SHA; browser E2E for critical journeys; storage and auth tested; rollback/recovery and monitoring documented. |
| 8 | Deferred original platform work | Resume organisation/cohort and instructor/creator workflows, plus remaining original security, privacy, finance, and operational roadmap items. |
| 9 | Paid expansion | Explicit commercial approval, staged free/paid catalogue, Pro rules, payment lifecycle and regression acceptance before enabling charges. |

### Definition of complete for the immediate phase

The free-launch foundation is not complete until all of the following are evidenced:

- Individual learner access is free without payment details, checkout, subscription purchase, or trial-expiry cutoff.
- Paid code and data remain preserved and can be re-enabled through the central mode.
- Teams can create and publish a track with ordered courses, modules and lessons.
- Teams can upload and manage videos/resources and the learner can access the published assets.
- Learners can discover, enrol, complete learning activities, resume, and have progress recorded.
- Track completion is calculated correctly.
- Teams can inspect learner information and trustworthy platform metrics.
- The post-completion feedback flow works with consent and moderation.
- No cross-tenant, creator ownership, staff permission, RLS, or private-media boundary has been weakened.
- Critical CI and browser acceptance evidence is recorded on the exact release candidate SHA.
- Production migrations and deployment have separate explicit authorisation.

## 8. What is deliberately deferred, not cancelled

The following remain in the original specification and roadmap:

- Customer organisation onboarding, workspaces, teams, cohorts, programmes, assignments and reporting.
- Instructor/tutor onboarding, creator accounts, course ownership, instructor tools, grading, payouts and creator sales.
- Organisation and creator commercial contracts/entitlements.
- Full subscription/Pro launch and paid-course catalogue rules.
- Remaining security, privacy, finance, migration-provenance, distributed rate-limit, deployment and recovery work.

Deferral means these do not lead the current implementation sequence. It does not authorise deleting their code, tables, migrations, documentation, or historical decisions.

## 9. Implementation reporting

For every workstream, update the roadmap and engineering history with:

- Date and exact `main` commit SHA.
- Files/routes/components/migrations changed.
- Behaviour completed and known gaps.
- Tests and CI run URLs/conclusions on that exact SHA.
- Whether database work was read-only, disposable, staging, or production.
- Confirmation that the active Pheonix Supabase target was not changed unless a separately approved operation explicitly says otherwise.
- Remaining risks and the next dependency.

Do not mark work complete because a UI exists or an API route returns success once. Verify the full workflow through the real application boundary and the appropriate database/storage fixture.


## 10. Implementation baseline and verified findings — 2026-10-31

### Reversible free-access foundation

The first code layer has been committed to `main`:

- A server-only `FREE_ACCESS_MODE` environment flag was added. It defaults to `false`; it must be deliberately enabled in the backend deployment environment before the free launch is live.
- The free entitlement is limited to verified individual learner accounts with role `normal`. Organisation/Witstart learners, cohort identities, prospects, creators, staff and administrators do not receive this individual free grant.
- In free mode, the learner access resolver bypasses trial expiry and paid-membership checks for eligible individual learners without updating their subscription rows, expiry dates, payment records or historical trial data. Inactive accounts remain inactive.
- Published, global Learnora-owned courses are eligible for free self-enrolment and content access. Tenant-scoped, organisation-owned and creator-owned content is not made free by this mode.
- The public catalogue can identify the temporary free mode. The learner course detail and subscription screens reflect the free individual-learner experience.
- The existing Paystack, subscription, trial, expiry, purchase and Pro implementation remains in place. Turning the flag off restores the original entitlement path.
- Regression tests were added for eligibility, expiry bypass, inactive-account denial, organisation boundary, unpublished/creator/tenant-scoped course denial and paid-mode fallback.

### Teams learner oversight and analytics

The first internal operations layer has also been added:

- A permission-protected, paginated individual learner list with email search and enrolment/lesson progress summaries.
- A permission-protected learner detail endpoint with enrolments, course labels and recent saved lesson progress. Password hashes and credentials are not selected.
- A platform analytics endpoint and Teams pages for learner oversight and metrics. The active-learner calculation currently samples up to 10,000 recent lesson-progress rows and exposes a cap warning; it is not yet a database-side aggregate.
- The existing Teams content manager already contains course, module, lesson, reorder and media/resource workflows. Those workflows still require end-to-end acceptance; their presence in the UI is not being treated as proof of completion.

### Track/course model — reuse the generic learning-path relationship, not cohort tables

The repository's checked-in baseline schema `supabase/baselines/active-pheonix-public-schema.sql` shows:

- `learnora_tracks` is the track-assignment model used with cohorts. `cohort_track_courses` links a track and course **through a required cohort_id**. That relation is cohort-scoped and is not used for the individual public catalogue.
- `learnora_learning_paths` and `learnora_learning_path_courses` provide the generic ordered course-sequence model. The path table permits both `owner_user_id` and `organisation_id` to be NULL, supports draft/published/archived states, and the course relation stores `order_index` and `required`.
- Global Learnora tracks therefore use this existing generic model with both owner and organisation IDs NULL. Personal learner paths and organisation paths remain separately scoped by their non-NULL owner/organisation values. This avoids creating a competing track table and avoids misusing the cohort-only join.
- Track enrolment creates the learner's ordinary course enrolments for the track's eligible courses. Track progress is derived from backend course completion for required courses; it does not invent a second lesson-progress store.
- The baseline `learnora_feedback` table has no dedicated track foreign key, consent field or moderation state. It is not sufficient by itself for the planned public track-review workflow; review storage still needs a dedicated, reviewed schema change before public review display.

The active Supabase project metadata was confirmed as Pheonix (`gihfupzvdpyrmynqgukz`), status `ACTIVE_HEALTHY`. Live SQL catalog introspection could not be completed because the read-only database connection returned a password-authentication failure for its read-only database user. The checked-in baseline is useful evidence, but it is not represented as a live-schema verification.

### Verification and release state

- No production database migration, data write, environment-variable change or deployment was performed.
- `FREE_ACCESS_MODE` remains off by default. The code is not live until the backend environment is configured and an authorised deployment is made.
- The new Python regression tests have been committed, but GitHub Actions jobs on the current workstream are failing before a runner is assigned: the jobs have no runner name and no executed steps, and downloadable logs are unavailable. This is an infrastructure/CI evidence blocker, not a verified code-test failure or a green test result.
- The Teams track/course workflow, track completion, consented/moderated reviews, full browser acceptance and production enablement remain open.



### Track implementation update — 2026-10-31

The global track MVP has now been implemented against the existing generic learning-path schema: Teams can create/manage global tracks, attach global Learnora courses, reorder the course sequence, publish/unpublish/archive tracks, and the learner app can discover tracks, enrol into their eligible courses and view backend-calculated required-course completion. Published tracks cannot have their course list reordered or changed until they are unpublished; courses linked to published global tracks cannot be unpublished or archived through the Teams course API. Track publication requires at least one required course and published course content.

This is code-only work against the checked-in baseline. Because live SQL introspection is still unavailable, confirm the live Pheonix schema before release. The track review/rating workflow remains blocked on a proper track-linked feedback model with separate public consent and moderation fields; no review data is being stored in an improvised field.


The proposed review schema and its consent, moderation, security and test gates are documented in [TRACK_REVIEW_SCHEMA_PROPOSAL.md](TRACK_REVIEW_SCHEMA_PROPOSAL.md). It is a proposal only; no migration or review table has been created.


The track manager now freezes a curriculum after course enrolments exist, preventing later edits from silently changing a learner's required sequence. Unpublished/archived tracks are removed from new discovery and enrolment, while learners with existing required-course enrolments can still retrieve their saved track progress. The Teams analytics view also reports published global tracks. These behaviours are covered by regression tests that are committed but currently blocked from execution by GitHub runner assignment failures.


### Implementation progress update — 2026-11-01

- The free-launch entitlement resolver now checks active organisation membership before applying individual learner access. If the membership lookup fails while free mode is enabled, authentication fails closed with a temporary service error rather than treating the learner as an individual. The free flag remains server-side and default-off; billing records are not rewritten.
- Global track management now uses the canonical global learning-path records and their course links. Track enrolments carry a per-track source marker, curriculum freezing is scoped to that track's enrolments, and archived tracks reject curriculum edits. Required/optional course handling and learner progress continuity have regression coverage.
- Track progress for an unpublished/archived track now requires an enrolment explicitly originating from that track; unrelated self-enrolments no longer expose unpublished track progress. Archived course summaries retain the lesson history path while still invoking module assessment-lock checks.
- Track enrolment now scopes existing records to individual/global enrolments and reactivates withdrawn records rather than attempting a duplicate insert. Suspended or invited records fail closed instead of being silently reactivated.
- Public catalogue free labels and analytics are scoped to global Learnora courses/tracks. Additional regression tests cover tenant isolation, independent enrolments, archived-track visibility and enrolment lifecycle.
- The optional post-completion review and public moderation flow is not yet implemented. It requires an additive review table, RLS/grants, authenticated completion-gated APIs, staff moderation and learner UI. No migration was applied or deployed; live schema verification is still blocked.
- CI was triggered on the latest commits, but GitHub reports failed jobs with no executed steps/logs (runner allocation unavailable). These are not passing tests and do not establish code failures. Local test execution was also unavailable in this session because the runtime could not resolve GitHub.
- The active Pheonix Supabase project remains the intended database. A read-only live-schema request failed with password authentication for the read-only database user. No production database, environment variable or deployment was changed.



## 11. Learner journey expansion — 2 November 2026

The immediate learner experience has been expanded into five implementation phases, recorded in [LEARNER_JOURNEY_PHASES_1_5.md](LEARNER_JOURNEY_PHASES_1_5.md):

1. Confirm and preserve the canonical global track → course → module → lesson architecture.
2. Improve discovery using actual published track/course relationships.
3. Offer an optional AI-assisted personalised learning plan based on onboarding preferences and the published catalogue. The plan is stored separately and cannot alter track curriculum.
4. Let Teams configure quizzes and assignments, grade assignment submissions, and monitor learner performance. Course completion now includes published assessment outcomes as well as lesson completion.
5. Give the AI tutor verified course/lesson/optional quiz context, current lesson progress and recent attempts, without sending answer keys.

### Free-launch safeguards

- No changes were made to the central `FREE_ACCESS_MODE`, Paystack, checkout, subscription, trial, expiry, entitlement, or Pro implementation.
- No payment method, paid subscription, checkout or trial-expiry requirement was introduced for the individual learner experience.
- The AI plan uses the existing AI provider/quota service and remains optional.
- The new plan-storage migration is additive, backend-only, RLS-enabled, and explicitly grants the server role only. It has **not** been applied to the active Supabase project. It must be tested on a disposable/staging database before deployment.
- No production data mutation, environment change or deployment was performed.

### Current acceptance state

The implementation and regression tests are committed to `main`, but CI runs must complete successfully on the exact final SHA. Browser/mobile journeys, AI provider/fallback behaviour, Teams grading/performance views and disposable/staging migration verification remain required. The free-launch flag remains default-off until separately configured and deployed. The existing paid implementation and its reactivation path remain preserved.
