# AI Course Production and Curriculum Architecture Audit

**Status:** Architecture decision and implementation baseline  
**Reviewed:** 21 November 2026  
**Repository:** `Obikpe/Learnora-ME`, branch `main`  
**Applications:** Learnora ME (`frontend-v02/`), Learnora Teams (`frontend-team/`), FastAPI (`backend-python/`), Supabase (`supabase/`)

## 1. Why this document exists

This document records the current-state audit and the approved direction for introducing AI-assisted course production into Learnora ME. It supplements, and does not replace, the Product Engineering Specification, Roadmap, Account and Organisation Architecture, learner journey documents, or migration reconciliation records.

The implementation must be based on the active application roots. The legacy `frontend/`, `backend-node/`, and `backend-python-v0/` are historical/legacy surfaces and must not be used as the implementation target without a separately documented migration decision.

## 2. System map confirmed in the repository

| System | Active location | Responsibility |
|---|---|---|
| Learnora ME | `frontend-v02/` | Public discovery, individual learner experience, creator workflows, customer organisation and cohort experience |
| Learnora Teams | `frontend-team/` | Separate internal workforce website for Learnora staff, platform administration and internal content operations |
| Shared API | `backend-python/` | FastAPI authentication, authorisation, business logic, course content, AI, media, progress and internal operations |
| Data and storage | `supabase/` plus active Pheonix project | PostgreSQL, migrations, RLS, database functions, private storage buckets and application records |
| Engineering documentation | `docs/` | Product specification, roadmap, engineering decisions, security, migration and learner journey records |

Learnora Teams is not the customer organisation portal. Customer organisation owners, managers, tutors and learners continue to use Learnora ME. Learnora Teams is a distinct website and must remain a distinct trust boundary and deployment surface. This phase integrates the course-production capability into the shared backend and the existing Learnora ME/Teams architecture; it does not redesign or rebuild the Teams website. The Teams website build is a later phase after the Learnora ME integration is stable.

## 3. Curriculum model — preserve the four levels

The canonical hierarchy is:

`Track → Course → Module → Lesson`

- **Track:** an ordered learning pathway that groups courses. The global public catalogue uses `learnora_learning_paths` and `learnora_learning_path_courses`. Cohort-specific tracks remain separately represented by `learnora_tracks` and `cohort_track_courses`.
- **Course:** a standalone learning product that can be discovered and enrolled in independently when its publication and access rules permit. A course may also be included in one or more tracks. For example, an Excel course can stand alone, while a broader Data Analytics course can also teach Excel in one of its own modules.
- **Module:** an ordered section inside one course.
- **Lesson:** the smallest learner-facing instructional unit inside a module. A lesson can combine a video, concise written reinforcement, resources, practice and assessment links.

A track is not a course, and a course is not a module. Do not flatten these levels, create a second global track model, or make course existence dependent on track membership. A course can exist outside a track.

Example catalogue direction (illustrative, not a seed instruction):
- Track: Data Analytics
  - Course: Introduction to Data Analytics
  - Course: Excel for Data Analytics
  - Course: SQL for Data Analytics
  - Course: Data Visualisation
- Standalone course: Excel Fundamentals (may also be included in an appropriate track)
- Track: Front-end Web Development
  - Course: HTML and CSS
  - Course: JavaScript
  - Course: Responsive Interfaces

The same course may be reusable in a track where curriculum and access rules allow it. Track order and required-course settings remain authoritative for track progression.

## 4. Existing course and lesson capabilities found

### 4.1 Curriculum management already exists

The active Teams content operations UI is in `frontend-team/components/ContentManager.tsx` and its content APIs are in `frontend-team/lib/content.ts`. It already manages courses, ordered modules, ordered lessons, lesson type, duration, lesson content, media and resources. Backend routes are in `backend-python/routers/internal_content.py`, with course/module/lesson logic in `backend-python/routers/course_content.py`.

The existing Teams content workspace is therefore the foundation to extend, not a reason to invent a parallel course-management subsystem.

### 4.2 Lesson media and learner playback already exist

The current learner player is `frontend-v02/components/course/CourseWorkspace.tsx`. It loads the lesson workspace from `/progress/lessons/{lesson_id}/workspace`, receives lesson text, video metadata and resources, renders a native HTML video element for signed media, and supports YouTube and Vimeo embeds. It also renders lesson text through `RichContent`, provides learner-owned notes, and supports lesson progress, quizzes, assignments and projects.

The current player is not text-only and is already structurally capable of displaying video plus written lesson content. However, it has material limitations to address before treating it as ready for AI-produced courses:
- It selects only the first video (`media.videos?.[0]`) for display. Multiple videos attached to one lesson are not presented as a sequence or playlist.
- Playback is currently based on a signed URL or YouTube/Vimeo embed. A new video-rendering provider must integrate through stable media metadata and a secure playback resolver rather than hardcoded public file URLs.
- The learner's personal notes are separate from the authored lesson's short teaching notes. Keep those concepts separate.
- The existing learner progress tracker records lesson/video interaction in the player, but overall session-time accounting is not the same as verified video watch-time. Do not claim a learner watched the full video merely because the lesson is open.
- The current UI should be refined to make the intended lesson flow clear: video (when pedagogically appropriate), short authored note, practical activity/resources, then knowledge check.

### 4.3 Existing media storage is Supabase Storage today

The backend currently creates signed upload URLs for the private `learnora-course-media` and `learnora-resources` buckets in `backend-python/routers/internal_content.py`. Learner progress/workspace routes create signed playback URLs from Supabase Storage. The `lesson_videos` and `lesson_resources` records store media metadata and references. A provider-neutral media metadata API also exists in `backend-python/routers/media.py`.

Therefore Cloudflare R2 is a proposed future storage option, not an implemented integration. Do not change the storage provider as part of the first AI authoring increment. First make the existing provider abstraction and signed playback path reliable, then compare the operational cost and security of R2 against the existing Supabase private buckets before selecting a migration. No production bucket migration or new provider credential is authorised by this document.

## 5. Existing AI architecture — extend, do not replace

The active shared gateway is `backend-python/services/ai_gateway.py`; profile resolution and operations are supported by `backend-python/services/ai_profiles.py`, `backend-python/routers/ai_profiles.py`, and AI routes. The gateway resolves a named profile to provider/model settings and has a fallback attempt structure. The current provider request implementation explicitly supports OpenRouter; other provider keys are not yet implemented in `_attempt`.

Course production must use this gateway for LLM tasks. Do not hardcode an LLM model inside course-generation features, and do not rebuild the gateway. The new course-production engine should be a feature/service layer above the gateway, with a dedicated profile key and independently configurable prompt/schema/version controls. The provider used for script/content generation must be independent of the video rendering and speech-generation components.

The gateway's current fallback mechanism is a single configured fallback model, not a general multi-provider orchestration engine. Documentation and UI must describe the actual supported provider behaviour, not overstate provider interchangeability.

## 6. Target AI Course Production workflow

The initial capability is for authorised Learnora ME internal team members only. It is not a feature for independent creators, tutors, customer organisations or organisation staff. The backend must enforce this boundary using the existing internal staff authentication and permission model. Hiding a button in the frontend is not authorisation.

Proposed workflow:
1. An authorised Learnora Teams staff member enters a course brief, target audience, prerequisites, level, learning outcomes and a structured outline.
2. AI reviews the outline, identifies missing prerequisites or sequencing problems, and proposes a course/module/lesson structure for staff confirmation.
3. AI generates each lesson package: teaching script, concise written reinforcement, examples, practice activity, knowledge check, references/source notes where required, and a media plan.
4. A video-production worker renders suitable lessons into a video using a chosen renderer, voice/narration engine and deterministic visual templates. Software lessons should use real screen capture or reproducible demonstrations; technical diagrams and equations should use deterministic rendering. Do not rely on generative video for exact code, equations, labels or instructional text.
5. Generated assets are attached to lesson media records using provider-neutral metadata and stable asset identifiers.
6. Course remains a draft while content and media are generated.
7. Staff review and approve curriculum, lesson content, video, resources and assessments.
8. Only an authorised publication action makes the course and its learner-visible content available in the catalogue/track.

The first release should prioritise reliable structured text/course generation and a production-ready lesson package. Automated video rendering should be added as a separate pipeline with job tracking, retry handling, output validation and human review. Do not make the entire authoring workflow fail because video generation is unavailable; allow a lesson to be text/practice-first when video adds little value.

## 7. Lesson pedagogy and content contract

Videos are the primary teaching medium where they improve learning, but not every lesson requires a video. Use concise lessons:
- Simple concept: typically 1–2 minutes.
- Concept with worked example: typically 2–3 minutes.
- More involved explanation or demonstration: typically 3–5 minutes.
- Five minutes is a ceiling guideline, not a target. Split a longer topic into multiple lessons.

AI must produce a full teaching script with clear explanations, examples and demonstrations. The script is not the short written note. The authored note is a brief reinforcement item: definition, key terms, short comparison, formula, checklist or takeaways. Avoid long essay-style lesson notes when a video is the main teaching medium.

A lesson package should support:
- instructional objective and prerequisites;
- lesson format (narrated visual, practical demonstration, text/practice-first, or mixed);
- teaching script and estimated duration;
- video asset(s), captions/transcript and thumbnail where applicable;
- concise written reinforcement;
- examples and practical activity/instructions;
- knowledge-check items or links to existing quiz/assignment mechanisms;
- resources and source/reference metadata;
- review status, version and generation provenance.

Use the existing `learnora_lessons` and `course_modules` relationships and existing quiz/assignment structures where possible. Do not introduce duplicate quiz, assessment or lesson tables without a schema-level reason.

## 8. Video-production architecture

Keep three concerns separate:
1. **LLM content generation:** outline interpretation, curriculum sequencing, scripts, notes, activities, assessment drafts, storyboards and structured production instructions. This calls the existing AI gateway.
2. **Media production:** deterministic visual composition, screen recordings, narration/TTS, captions, audio mixing, rendering and encoding. This is an asynchronous worker pipeline and must not be coupled to the LLM provider.
3. **Media delivery:** storage, access checks, signed playback URLs, CDN/cache policy and browser playback. This is separate from generation and must reuse the existing course access boundary.

A zero/low-cost first renderer can use HTML/CSS/SVG templates, deterministic diagrams, real screen recordings, an open-source TTS engine where licensing and voice quality are verified, and FFmpeg for assembly. Manim Community may be used for mathematics and technical animations. These are candidate tools, not yet installed or adopted dependencies. Rendering still consumes compute; "open source" does not mean zero operating cost.

The initial implementation must not assume the current Vercel request process can run long renders. Use a job/worker model and persist state such as queued, generating, rendering, validating, ready and failed. Record retry count, timestamps, output metadata and safe error details. Never store expiring signed URLs as durable asset identity.

## 9. Media identity and storage decision

The existing lesson media tables are the current integration point. Before adding a new `media_assets` table, inspect the actual live schema and current table constraints to determine whether `lesson_videos` can safely represent generated renditions and asset versions. Prefer additive extension/reuse over parallel media registries.

A durable media reference should identify the provider, bucket/container, object key, MIME type, byte size, duration, checksum, visibility, status and version/rendition. Lesson-to-media relationship must be stable and unique. Signed URLs are generated at playback time after backend course-access validation and must not be persisted as the canonical media location.

Current storage provider remains Supabase Storage. Cloudflare R2 is a cost/egress candidate to evaluate separately. A decision to move to R2 requires a tested private-access/signing design, cost estimate, migration plan, lifecycle/retention policy and rollback. No production storage migration is part of this initial phase.

## 10. Course catalogue and initial content direction

The platform must support both standalone courses and courses grouped into tracks. Examples of future catalogue breadth include a standalone Excel course, a broader Data Analytics course that includes Excel in its own curriculum, and a Front-end Web Development course/track. Avoid making the whole catalogue a single monolithic Data Analytics course.

The existing published "Introduction to Data Analytics" test course was seeded as a mock/test introduction. It must be replaced by the real AI-produced course once the generation workflow can create, review and publish its replacement. Do not delete it prematurely: first confirm its current production record, track links, enrolments, learner progress and references. If it has no learner history, archive/delete only through an approved, verified data operation; if learners have progress, preserve history and replace it without destructive deletion. Remove mock/test labelling and test content only after the replacement is ready and the access/track links are reconciled.

## 11. Security, quality and release requirements

- Course authoring/generation endpoints are internal-staff-only and require an explicit permission such as a dedicated course-production capability; existing generic course-view permissions are insufficient.
- Individual creators and customer organisations must be denied server-side, including direct API requests.
- Generated content is untrusted draft output. Validate structure, length, lesson count, quiz payloads, URLs and media metadata before persistence.
- Do not auto-publish AI output. Human review and explicit publication are mandatory.
- Keep provider secrets server-side; never expose service-role or video-provider credentials in either frontend.
- Keep AI usage accounting/quota and generation job accounting separate enough to prevent retries from duplicating charges or content.
- Add audit events for who initiated, edited, approved and published each generated course.
- Protect media playback using the same course/lesson access checks as text content. A signed URL must not become a public bypass.
- Test cross-role denial (internal staff allowed only with permission; creator/org/learner denied generation), course access, draft invisibility, publication readiness, video playback, missing media, failed generation and retry/idempotency.
- Do not apply production migrations, alter live records, change storage provider or deploy without the appropriate separate approval and release verification.

## 12. Initial audit findings and known gaps

| Area | Confirmed current state | Gap / next action |
|---|---|---|
| Product separation | Two active websites: ME and Teams | Keep Teams as later website-build phase; shared API integration only now |
| Curriculum | Global track → ordered courses → modules → lessons exists | Preserve semantics; make standalone course creation first-class in authoring flow |
| AI gateway | Named profile and provider/model configuration exists | Existing request executor currently supports OpenRouter only; add a course-generation profile through gateway |
| Teams content operations | Manual course/module/lesson and media management exists | Extend content operations with AI-assisted outline and lesson-package generation |
| Lesson player | Video + text + resources + learner notes + assessments already supported | Only first attached video is rendered; improve multi-asset lesson presentation and concise note layout |
| Video storage | Private Supabase buckets and signed upload/playback flows exist | Keep provider stable initially; evaluate R2 later rather than assuming it is integrated |
| Video production | No automated rendering worker confirmed in the audited active paths | Design and implement as a separate asynchronous pipeline |
| Course review | Draft/published content and publishability checks exist | Add generation provenance and explicit human approval state |
| Mock course | A published Introduction to Data Analytics seed is documented | Verify current live state and learner history before archive/replace |
| Brand | Landing page currently passes `hideBrand` to `PublicNav` | Remove the flag so Learnora ME brand appears in the landing-page top navigation |

## 13. Audit boundaries and outstanding verification

This audit inspected the root system map, the active product and roadmap documentation, canonical learner journey and account/organisation architecture, current learner player, Teams content management components, active course/media/AI routes and gateway, and migration/storage evidence. It is a targeted architecture audit of the relevant active paths, not a claim that every file among the repository's 4,700+ tracked paths has been line-by-line reviewed.

Still required before schema or production-media implementation:
- Read the current live `lesson_videos`, `lesson_resources`, `learnora_lessons`, `course_modules`, `learnora_courses`, track/link and permission table definitions from the active Pheonix project.
- Reconcile the exact production migration ledger before adding a migration; the repository documents timestamp/version mismatches and a pending migration. Do not run `supabase db push` until reconciled.
- Verify current Vercel project/environment routing and whether the active deployment uses the current main commit; repository code alone does not prove deployment state.
- Verify current test-course enrolments and progress before changing seeded data.
- Verify current video file-size limits, storage quota and actual bucket policies before choosing a rendering/upload format.



## 14. Learnora ME placement and internal staff authentication boundary

The two active websites proxy API requests to the same FastAPI backend, but they do not use the same browser session identity:
- Learnora ME's normal learner/admin application session uses the public authentication cookie/session flow.
- Internal staff authentication uses the domain-separated staff JWT and the separate `learnora_team_token` HttpOnly cookie through `/api/internal/auth/login`, `/api/internal/auth/me` and `/api/internal/auth/logout`.

The ME admin dashboard's `account_type === "admin"` check is not a substitute for internal staff authorisation. A normal learner, creator, organisation owner, or public-site administrator must not gain course-production access merely by reaching a hidden route or possessing an ME session.

To place the first Course Studio inside the Learnora ME website while keeping the Learnora Teams website build deferred:
1. Add a dedicated Learnora ME route for internal staff sign-in and Course Studio.
2. Authenticate that route against the existing internal staff endpoints and the separate staff cookie.
3. Require the existing internal `content.manage` permission on every course-generation endpoint (and consider a narrower `content.generate` permission when the permission catalogue/migration ledger is safely reconciled).
4. Do not accept the learner cookie or client-supplied role as proof of staff authority.
5. Keep all generation logic in the shared backend. The later Learnora Teams website should reuse these APIs rather than create a second generation engine.

The current `frontend-team/` remains a separate internal application with its own login and content operations. This phase does not redesign it or move its existing pages into Learnora ME; it temporarily makes the new AI Course Studio reachable inside Learnora ME through the proper staff identity boundary.


## 15. Live Pheonix database verification — 21 November 2026

The active Supabase project was checked read-only:
- Project: **Pheonix**, reference `gihfupzvdpyrmynqgukz`, status `ACTIVE_HEALTHY`, PostgreSQL 17.11, region `eu-west-3`.
- The live migration ledger contains **56** versions.
- The repository contains **57** SQL files under `supabase/migrations/`.
- There are **12 live migration versions without a same-version repository source file**, including the live `20261118214152_public_course_catalogue_rpc` while the repository has `20261118141100_public_course_catalogue_rpc.sql`.
- There are **13 repository-only migration filenames**: 12 are stale timestamp versions corresponding to live migrations, and `20261026153000_revoke_browser_privileges_and_defaults.sql` remains an unapplied candidate. The repository and live ledger are not version-aligned.
- **Do not run `supabase db push` or apply a new production migration until this discrepancy is reconciled.** The live migration ledger is the authority for applied versions; a semantically similar SQL file with a different timestamp is not a matching migration source.

### Live curriculum and media schema

The live schema confirms:
- `learnora_courses` has global/organisation/creator ownership, publication status, descriptions, `settings jsonb` and estimated hours.
- `learnora_learning_paths` and `learnora_learning_path_courses` are the global track and ordered course-link tables.
- `course_modules` and `learnora_lessons` already represent ordered modules and lessons. `learnora_lessons.content` is plain text/Markdown; there are no dedicated columns for a private production script, storyboard or AI-generation provenance.
- `lesson_videos` supports multiple rows per lesson, provider values including Supabase, Cloudflare, Mux, Bunny, Vimeo and YouTube, storage path/external ID, duration, size, MIME type, privacy, processing status and transcript text.
- `lesson_resources` stores resource metadata and storage/external references.
- The current database has no lesson-video records for the test Introduction to Data Analytics lesson.

The schema is therefore sufficient for current learner-facing text, video metadata, resources and playback, but not yet a durable AI production workspace. A production script/storyboard should not be placed in learner-visible `learnora_lessons.content`, nor hidden in an oversized course settings JSON object. Add a reviewed production-draft/job model in a migration after migration reconciliation.

### Live AI profile and permission findings

- The live `content_generation` AI profile exists, is enabled, and is configured as `openrouter/free` with a stored default maximum of 2,000 output tokens.
- The active gateway can override output tokens per call, but the model/provider's actual response limits and output validity still need runtime verification.
- The internal permission `content.manage` exists. In the live staff-role permission mapping it is currently assigned only to `super_admin`.
- The `learning_curriculum` staff role exists but does not currently have `content.manage`. Therefore the first generation API is restricted to super-admin staff until a dedicated course-generation permission is safely added and assigned to the curriculum role. Do not bypass the permission system with a hardcoded role check.
- The current generation endpoint uses the existing `content_generation` profile and requires internal staff `content.manage`. It produces validated draft proposals only; it does not create or publish course records yet.

### Test course — preserve history when replacing

A read-only live query confirmed that the test course is not an empty disposable record:
- Course: **Introduction to Data Analytics**, published and Learnora-owned.
- It is linked to the published **Data Analytics** track.
- It currently has one published module and one published article lesson, **What Is Data Analytics?**
- The lesson is marked as 35 minutes and contains 10,655 characters of written content.
- It has **2 enrolments and 2 lesson-progress records**, and no attached videos.

Do not hard-delete this course or its lesson. When the real AI-produced course is ready, retire the test version from new discovery while preserving those enrolments and progress records. The existing track curriculum may be frozen by its enrolment history, so the replacement may require a successor track/version and a reviewed transition plan rather than editing the current track in place. Verify the current learner access and track-lock behaviour before any retirement operation.

