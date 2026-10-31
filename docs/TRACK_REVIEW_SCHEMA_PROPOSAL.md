# Track completion reviews — schema proposal

**Status:** Proposed only — not migrated or deployed  
**Date:** 2026-10-31  
**Scope:** Learnora ME individual learner track reviews

## Why a dedicated table is required

The current `learnora_feedback` table is lesson-oriented and has no `track_id`, separate public-sharing consent, or moderation state. Reusing `lesson_id`, `organisation_id`, or overloading `feedback_type` / `message` to encode a track reference would create an unreliable relationship and weaken review controls. Do not do that.

## Proposed record

Create `learnora_track_reviews` with:

- `id uuid primary key`
- `track_id uuid not null references learnora_learning_paths(id)`
- `user_id uuid not null references users(id)`
- `rating smallint not null check (rating between 1 and 5)`
- `comment text null` with an application-enforced length limit
- `public_consent boolean not null default false`
- `moderation_status text not null default 'pending'` constrained to `pending`, `approved`, or `rejected`
- `moderated_by uuid null references users(id)`
- `moderated_at timestamptz null`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- unique `(track_id, user_id)` so one learner cannot create repeated public-rating rows for the same track

The API must only accept a review after the backend confirms the learner has completed every required course in that track. The rating/comment prompt must be optional and dismissible. The learner must actively choose public sharing; the default is private.

## Public display rules

A review may be displayed publicly only when both conditions are true:

1. `public_consent = true`
2. `moderation_status = 'approved'`

Do not publish the learner's email or other account identifiers. Public aggregate ratings must be calculated from approved, consented reviews only. Moderators must be able to approve/reject reviews and record who made the decision and when. A learner must be able to withdraw public consent; withdrawn reviews immediately stop appearing publicly.

Do not promise Google review stars or rich-result eligibility. A first-party course/track review is not automatically eligible for self-serving review snippets.

## Security

- Enable RLS.
- Do not grant direct anonymous or authenticated table writes.
- Keep writes behind the FastAPI service-role API with explicit learner ownership and track-completion checks.
- Public reads must use a narrow API query for approved, consented rows only.
- Staff moderation must require a dedicated review-moderation permission.
- Add indexes for `track_id`, `moderation_status`, and public-consent filtering.

## Required tests

- Reject a review before backend-confirmed track completion.
- Reject ratings outside 1–5 and overlong comments.
- Allow private feedback without public consent.
- Keep pending/rejected/consent-withdrawn reviews out of public results.
- Show only approved + consented reviews and aggregate only that subset.
- Enforce one review per learner per track.
- Verify moderator permission and moderation audit fields.
- Verify a learner cannot submit or edit another learner's review.

## Migration gate

Before creating a migration, confirm the live Pheonix schema with a working read-only connection, create the migration using the repository's Supabase migration workflow, test it in an approved disposable environment, and obtain explicit approval before applying it to the active production project. No migration has been created or applied for this proposal.
