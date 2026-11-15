# Learner account lifecycle, notifications and marketing automation

**Status:** Product and engineering specification  
**Updated:** 16 November 2026  
**Scope:** Learnora ME individual learner accounts and shared Learnora notification services

This document records the intended account-recovery, notification-targeting and marketing-consent behaviour. It separates the account-deletion grace-period implementation from the broader automated notification engine, which remains a future build.

## 1. Learner account lifecycle

### 1.1 States

| State | Meaning | Sign-in |
|---|---|---|
| `active` | Normal learner account | Allowed |
| `deletion_pending` | Learner requested deletion; email confirmation is outstanding | Allowed until confirmation |
| `deactivation_pending` | Learner confirmed deletion; 30-day recovery period is running | Blocked |
| `deleted` | Recovery period ended and finalisation completed | Blocked; original email is released |

The 60-minute deletion-confirmation link is separate from the 30-day recovery period. The 30 days begin only after the learner opens the confirmation link.

### 1.2 Request and confirmation

1. The learner opens Account Settings and chooses a structured reason for leaving. An optional free-text explanation is available.
2. Learnora emails a one-time confirmation link. The account remains active while confirmation is outstanding.
3. The link expires after 60 minutes. A new request can be made after an earlier link expires.
4. Confirmation rechecks that the account is an individual learner and is not still owned or managed by an organisation/cohort.
5. Any active recurring Learnora subscription must be cancelled successfully before deactivation is committed.
6. The account changes to `deactivation_pending`, and `account_deactivation_until` is set to confirmation time + 30 days. The password, original email, learner progress and learning records remain in place during this period. The learner is signed out and cannot use the account while it is deactivated.

### 1.3 Reactivation and same-email sign-up

- During the 30-day period, the learner can enter the same email on the public registration page.
- The system must not create a second account or overwrite the original password, learner history, enrolments or marketing preferences.
- Instead, the backend creates a short-lived, single-use reactivation token and sends an activation link to the existing email address. The registration page routes to a clear "Reactivate your account" information page.
- The activation link is valid for 24 hours. Successful activation returns the existing account to `active`, clears the recovery deadline and deletion request data, and preserves learning history and the existing password. The learner then signs in normally.
- If the 24-hour link expires but the 30-day recovery period is still open, entering the email again issues a fresh link.
- At or after the 30-day deadline, the finalisation job must run before the email can be registered as a new account. If finalisation is delayed, registration must fail safely and retry rather than create a duplicate.

### 1.4 Final deletion and complete learner-data erasure

A daily Vercel cron invokes the protected account-finalisation endpoint. The endpoint calls a service-role-only database function that processes a bounded batch with row locking and `SKIP LOCKED`.

For each account whose 30-day recovery deadline has passed, finalisation must be atomic:

1. Insert or update one restricted `deleted_account_history` record containing only the original account identifier/email, account dates, deletion reason and deletion details required for the deletion history.
2. Delete the learner's account-linked records across learning, progress, sessions, onboarding, notes, skills, badges, recommendations, assessments, submissions, certificates, discussions, replies, AI conversations, AI usage, notifications, purchases, subscriptions, entitlements, feedback, creator/learner profile data, tokens, cohort membership/progress and other learner-owned tables.
3. Remove learner-specific audit/security entries and email-keyed records that would otherwise preserve a second copy of the learner's personal data.
4. Delete the row from `public.users` itself. Do not leave a disabled, anonymised or tombstone user row.
5. Preserve only the restricted `deleted_account_history` record. Shared catalogue and organisation resources are not deleted merely because the learner was recorded as their creator; user attribution is detached where the foreign key is configured to set null.

The entire operation runs inside one database transaction per batch function invocation. If a dependent record prevents deletion or any cleanup statement fails, the transaction must fail rather than report a successful deletion while leaving partial learner data behind. The function uses row locking and `SKIP LOCKED` so overlapping invocations do not finalise the same account twice.

The original email remains in the dedicated deletion-history table so Learnora can maintain its account-deletion history and prevent accidental account recreation from bypassing the recovery process. That history is restricted to authorised staff and is not a usable learner account. No learner learning history, profile, submissions, conversations or other account-linked records are retained in that history snapshot.

**Operational dependency:** the deployed backend needs a strong `CRON_SECRET` environment variable. The daily cron is configured in `backend-python/vercel.json`. The finaliser also has an explicit `ACCOUNT_DELETION_FINALIZER_ENABLED` gate which defaults to `false`; keep it false until the erasure migration is applied, the production schema has been checked against the cleanup inventory, and automated deletion tests pass. Monitor cron results and alert staff when a finalisation run fails.

### 1.5 Organisation-managed identities

The self-service deletion and reactivation flow is for independent individual learners only. Cohort and organisation-managed accounts must continue through the organisation release/ownership process. Do not silently convert a managed identity into an independent account.


### 1.6 Data-erasure boundary

The approved rule is complete erasure after the 30-day recovery period. During the recovery period, the learner's profile, password, enrolments, progress and all other learner records remain intact so reactivation restores the account as it was. At the deadline, the finaliser deletes the learner's entire account-linked record set and the `public.users` row. The only retained learner-specific record is the restricted `deleted_account_history` row.

The finalisation migration inventories learner-owned UUID references and restrictive foreign keys so legacy tables without foreign-key constraints are included. The cleanup must fail atomically if any dependent record prevents deletion. Do not describe the process as complete erasure until the migration is applied and the production database tests verify that no learner-linked rows remain outside the history table.

## 2. Deletion reasons and Learnora staff visibility

The deletion form uses a controlled reason:
- no longer needs Learnora;
- found another platform;
- missing courses/tracks;
- technical problems;
- cost/pricing;
- privacy/data concerns;
- other.

The optional details field is capped at 1,000 characters. Treat the text as potentially sensitive personal information: restrict access, escape it in the UI, do not put it into marketing segmentation, and define a retention period.

The audit trail must distinguish:
- `learner_registered` / `learner_created`;
- `learner_account_deletion_requested`;
- `learner_account_deactivated`;
- `learner_account_reactivated`;
- `learner_account_deleted`.

The Learnora admin Users view exposes current learners, accounts in the 30-day recovery period, completed deletions and their recorded reason. The activity stream retains the corresponding lifecycle audit events. Staff access remains governed by existing administrator permissions.

## 3. Email marketing consent and channel policy

### 3.1 Email marketing consent

The optional, unticked registration checkbox and Account Settings preference apply to **marketing email only**. Suggested wording:

> Yes, I would like to receive Learnora marketing emails about new learning tracks, course releases, learning opportunities, offers and discounts.

It must not be bundled with Terms of Use, Privacy Policy acceptance or account creation. Leaving it unticked must not block registration or reduce access to learning. Do not infer consent from account creation, course enrolment, browsing, search activity, silence or a preselected checkbox.

The existing `marketing_email_opt_in` field is the authoritative permission for promotional email. Keep the historical `marketing_in_app_opt_in` database field only for compatibility/migration purposes; it must not be used to suppress, hide or disable in-app notifications. In-app notifications are always available in the Learnora notification centre and learners cannot unsubscribe from that channel.

Store auditable email consent evidence using `marketing_email_opt_in`, `marketing_consent_at`, `marketing_consent_source` and `marketing_unsubscribed_at`.

### 3.2 Email unsubscribe and suppression

- Learners may withdraw consent for marketing email in Account Settings or through the unsubscribe link in a marketing email.
- Every marketing email must include a prominent, working unsubscribe link in its footer.
- The public unsubscribe action must work without sign-in, be idempotent and immediately set `marketing_email_opt_in=false`. It must not turn off in-app notifications, alter the notification inbox, or prevent future transactional/service messages.
- Each campaign email receives an opaque random token; only its hash is stored in a service-only token table. Unsubscribing consumes all outstanding tokens for that learner.
- Re-check email consent and suppression immediately before each marketing send, not only when a campaign audience is first built.
- Keep a minimal suppression record long enough to prevent accidental re-import or re-subscription. A later opt-in must be a new affirmative action with a new consent timestamp.
- Never include promotional content in essential account/security emails or disguise a promotion as a service notice.

### 3.3 Transactional, service and marketing classification

| Message | Default channel | Marketing email opt-in required? |
|---|---|---|
| Account verification and password reset | Email | No; essential account communication |
| Deletion confirmation and requested reactivation link | Email | No; account lifecycle communication |
| High-impact security alert | Email and in-app where applicable | No; essential security communication |
| Welcome after initial setup | In-app and email, once | No; onboarding/service communication |
| Important platform/service incident | In-app; email only when necessary | No, when genuinely required to provide or secure the service |
| Course/lesson activity, routine updates, comments and replies | In-app only | No email is sent |
| Upcoming important deadline | In-app; one email 24 hours before if still incomplete | No; learning-service reminder |
| Inactivity reminder | In-app; limited email reminder under section 4.6 | No; learning-service reminder |
| New courses, general programme launches, offers and promotions | In-app; marketing email only with consent | Yes for email |
| Interest-based promotional recommendations | In-app; marketing email only with consent | Yes for email |

Do not relabel a promotion as an important service notification to bypass email marketing consent. The purpose and content determine the category.

### 3.4 Approved automated email catalogue

The following is the approved product policy. Items marked **planned** are not represented as implemented.

| Email | Trigger and timing | Recipient | Consent / frequency rule | Current source status |
|---|---|---|---|---|
| Account verification | Immediately after registration when verification is required | New account owner | Transactional; verification token expiry applies | Implemented |
| Password reset | Only after the learner requests it | Account owner | Transactional; short-lived reset token | Implemented |
| Security alert | Immediately after a learner password is changed or reset | Affected account owner | Transactional; sent in-app and by email; no marketing opt-in required | Implemented for password change and password reset |
| Account deletion confirmation | After the learner explicitly requests deletion | Account owner | Transactional; confirmation link expires after 60 minutes | Implemented |
| Account reactivation link | Only after a deactivated learner explicitly requests it | Account owner | Transactional; link expires after 24 hours or the end of the 30-day recovery window, whichever comes first | Implemented |
| Welcome to Learnora ME | On the learner's first successful completion of initial account setup | New learner | One time per account; no retroactive welcome for existing completed profiles; send both in-app and email | Implemented in source; requires the new delivery migration and automation flag before production use |
| Upcoming deadline | First hourly automation run after a published assignment enters its 24-hour due window, if no submission exists | Affected learner with an active course enrolment | At most one email per assignment/deadline; in-app notification also created | Implemented for published assignments with `due_date`; quiz-specific deadlines are not represented in the current quiz schema |
| Learning inactivity | After 7 consecutive days without meaningful learning activity | Individual learner with completed onboarding | No repeat email within 30 days; suppresses a reminder if meaningful activity resumes before the send check | Implemented in source; requires the new delivery migration and automation flag before production use |
| Marketing campaign | Only when an authorised campaign is scheduled and approved | Eligible opted-in learners | Explicit email opt-in required; per-message unsubscribe link and consent recheck | Per-recipient consent-gated sender helper implemented; campaign authoring, audience selection, scheduling and admin UI remain future messaging-platform work |

Meaningful learning activity means completing a lesson, quiz or assessment. Merely signing in does not reset the inactivity clock. Weekly progress summaries are in-app only: Monday morning in the learner's recorded timezone, with a three-hour delivery window, and only when meaningful activity occurred in the previous Monday–Sunday period. No weekly summary email is sent.

### 3.5 Email exclusions

Do not send email for every lesson completion, quiz completion, comment, reply, routine course announcement, routine course update, certificate event, weekly progress summary or ordinary cohort activity. These belong in the in-app notification centre unless a separately approved critical-service reason applies.

## 4. Automated notification engine

Learnora should use event-driven notification routing rather than broadcasting every announcement to every learner.

### 4.1 Event and audience model

Every automated learner notification is created in the in-app notification centre. Email is a separate, selective delivery decision governed by sections 3.3–3.5. Manually composed messages are the exception: the future messaging platform lets the sender choose in-app, email or both.

| Event | Audience rule | In-app behaviour | Email behaviour |
|---|---|---|---|
| Registration / email verification | The account owner | Account/setup status as appropriate | Verification email only when required; not the post-setup welcome |
| Initial setup completed | The account owner | Create one welcome notification | Send one welcome email; both deliveries must be idempotent |
| Account deletion / reactivation | The account owner | Relevant account status notification where appropriate | Send only the requested transactional lifecycle email |
| Course enrolled or assigned | The enrolling learner, including user-backed cohort members | In-app confirmation | No routine email by default |
| Enrolled course materially updated | Current learners enrolled in that course | In-app notification | No automatic email by default; an authorised sender may choose email in the future messaging platform |
| New course/lesson published or materially updated | Relevant enrolled learners and matching eligible learners | In-app notification under the approved targeting rules | No automatic email; promotional campaigns require explicit email consent |
| Lesson completion, passed quiz, assignment submission, course completion and certificate issuance | The learner | In-app event notification; one per meaningful event (course completion/certificate are deduplicated) | No email |
| Discussion reply or accepted answer | Discussion author / reply author | In-app notification to the affected learner | No email |
| Cohort course or lesson assignment/completion | Affected user-backed cohort member | In-app notification | No email |
| Weekly learning summary | Learners with meaningful activity in the previous week | One in-app summary on Monday morning in the learner's timezone | Never email |
| Important deadline approaching | Learner with incomplete activity | In-app reminder | One email 24 hours before deadline if still incomplete |
| Learning inactivity | Learner with no meaningful activity for 7 days | In-app reminder | One email at the approved threshold; repeat no more than every 30 days |
| New offer or discount | Eligible audience | In-app promotional notification | Email only to opted-in learners |
| Platform-wide essential incident | Accounts materially affected | In-app notice | Email only when necessary to provide or secure the service |

Every event must resolve to an explicit recipient set. "All users" must never be the default audience.

### 4.2 Interest signals

Use a small, explainable interest model:
- explicit learner-selected interests from onboarding or preferences;
- repeated course/track searches;
- repeated visits to the same track/course detail page;
- course enrolments and saved learning plans.

Search interest should be derived from a controlled topic taxonomy (for example, web development, data analytics, cybersecurity), not an unrestricted dump of raw search text. A possible initial threshold is two or more distinct search/engagement events for a topic within 30 days, with recency decay. Enrolment is a stronger signal than a single search.

The signal should store the learner ID, topic ID, source, confidence/weight, first observed time and last observed time. Provide a way to inspect, correct or clear inferred interests. Do not use deletion-reason free text, private lesson content, assessment answers or sensitive data for targeting.

### 4.3 Routing rules

1. **Account-based:** route only to the relevant account.
2. **Enrolment-based:** route course updates only to learners with an active/current enrolment in that course.
3. **Interest-based:** route relevant catalogue updates only when the interest threshold is met. In-app delivery remains available; email delivery is promotional and requires active email marketing consent.
4. **Global marketing email:** route only to learners with active `marketing_email_opt_in` and no email suppression record. In-app notifications are not disabled by email unsubscribe.
5. **Managed accounts:** respect organisation/cohort tenant rules and any organisation-level communication settings. Do not expose one organisation's learner data or preferences to another.

### 4.4 Delivery architecture

The current implementation uses `learner_notification_deliveries` as a durable, service-role-only delivery ledger. Each recipient/event/channel pair is unique; the database claim function leases a delivery, recovers stale `sending` claims after 15 minutes and schedules failed attempts for retry after one hour. The hourly protected worker creates in-app notifications and sends eligible reminder emails. This is an initial durable delivery mechanism, not yet a general event bus or full campaign outbox.

- Use stable event keys and one delivery record per recipient/channel.
- Claim work atomically in Postgres to prevent overlapping cron invocations from sending duplicates.
- Re-check account status, email verification and marketing email consent immediately before campaign email delivery. Transactional emails use their own event-specific eligibility rules.
- Keep the `learnora_notifications` table as the in-app inbox source; do not store campaign state in it.
- Future campaign scheduling should add bounded backoff, delivery/bounce/complaint tracking, audience preview, cancellation and audit controls before bulk campaign use.

### 4.5 Email requirements

The approved email catalogue and send timing are defined in section 3.4. Every marketing email must:
- clearly identify Learnora and the commercial/marketing nature of the message;
- use a truthful subject and sender identity;
- include a working unsubscribe/preferences link at the bottom;
- support one-click unsubscribe headers where supported by the sending provider;
- record delivery, bounce, complaint and unsubscribe outcomes;
- stop subsequent marketing sends promptly after an unsubscribe or complaint.

Important transactional email templates must be separate from campaign templates. The email worker must not send to a deactivated/deleted account.

### 4.6 Reminder timing, deduplication and suppression

- Deadline email: the hourly worker sends once when a published assignment enters its 24-hour due window, only if the learner has an active enrolment and no submission exists at send time. Do not send a second reminder for the same assignment/deadline. Quiz-specific deadline reminders remain unavailable until quizzes have an explicit due-date field.
- Inactivity email: trigger after 7 consecutive days without a completed lesson, quiz or assessment, using `learner_learning_days` as the activity source. Login alone is not meaningful activity. The worker checks `last_inactivity_email_at` and will not repeat an inactivity email within 30 days.
- Weekly in-app summary: on Monday between 9:00 and 11:59 in the learner's stored timezone, summarise the previous Monday–Sunday activity. Do not create an empty weekly summary and never email this digest.
- Cancel/suppress a pending inactivity email if the learner completes meaningful learning activity before it is sent.
- Cancel/suppress a pending deadline email if the relevant activity is completed before it is sent.
- Welcome email and welcome in-app notification: one delivery per account after initial setup completes; registration or verification alone is not the welcome trigger.
- Use stable idempotency keys for each event/recipient/channel to prevent duplicate sends after retries.

### 4.7 Admin campaign controls

Learnora staff should be able to:
- create a draft campaign and choose a permitted audience rule;
- preview audience size and exclusion reasons before sending;
- preview and test-send the message;
- schedule, pause or cancel a campaign;
- inspect sent, delivered, bounced, complained and unsubscribed counts;
- audit who created, approved and sent each campaign.

Require an explicit send action and permission check. Do not let a campaign editor override consent or suppression rules.

## 5. Future instructor/admin message delivery

The future Learnora message platform must let an authorised instructor or administrator choose the delivery channel when composing a message:

- **In-app:** create a notification in the Learnora notification centre.
- **Email:** send to the selected recipients' registered email addresses, subject to account eligibility and the message's transactional/service/marketing classification.
- **Both:** deliver through both channels, subject to the same rules.

Audience selection should support appropriate learner, course, cohort and organisation scopes, with tenant isolation and permission checks. The sender must preview the audience and message before sending. The channel selector does not override email marketing consent, unsubscribe suppression, account status or organisation communication restrictions. Promotional email requires explicit email marketing consent; genuinely necessary service messages remain separately classified. In-app notifications remain available and cannot be unsubscribed from.

This is a future capability only; do not treat it as an existing messaging-platform feature.

## 6. Privacy, compliance and abuse safeguards

The platform is operated from Nigeria and should be designed conservatively around the Nigeria Data Protection Act 2023 and applicable NDPC guidance. Direct marketing should use affirmative, recorded opt-in consent; provide an easy withdrawal mechanism; and honour objections promptly. This engineering specification is not legal advice and does not guarantee legal compliance.

Before enabling campaigns, obtain qualified privacy/legal review of:
- the lawful basis and wording for each message category;
- the privacy notice, retention schedule and data-subject rights;
- profiling/interest inference and transparency;
- email service-provider processor terms and international transfers;
- suppression-list retention and deletion-history retention;
- marketing to minors and guardian consent requirements;
- applicable advertising/consumer-protection rules.

Security controls: opaque random, single-use unsubscribe tokens stored as hashes; no email addresses or account IDs in URLs; rate-limited public token endpoints; no raw tokens in logs; escape user-generated reason details; strict admin permissions; audit campaign changes; and test that unsubscribed/deactivated/deleted users are excluded.

## 7. Implementation status and release gates

### Implemented in the current source changes
- On phones and tablets only (up to 1023px), the notification preview width is constrained to the viewport; notification and profile menus close each other, close on outside interaction and close on Escape. Desktop menu behaviour and desktop preview width are unchanged.
- Notification preview remains a compact dropdown beneath the bell; selecting an item opens the full two-column notifications page.
- Signup and Account Settings marketing consent now controls email marketing only. Email unsubscribe changes only `marketing_email_opt_in`; it does not disable or hide in-app notifications.
- Password change and password reset create one-time in-app security alerts and send transactional security emails.
- The first successful completion of individual learner onboarding creates a one-time welcome notification and sends a welcome email. Existing completed profiles are not bulk-emailed; only failed/pending welcome deliveries are retried by the hourly worker.
- Published assignments with due dates generate one in-app reminder and one email within the 24-hour due window when the learner has an active enrolment and no submission.
- Individual learners with completed onboarding receive an in-app inactivity reminder after 7 days without meaningful activity and, subject to the 30-day cap, one email.
- A per-recipient marketing email delivery helper checks current opt-in, creates a per-message unsubscribe token and rechecks consent before sending.
- Account Settings retains deletion-reason capture; account deletion/recovery flows remain implemented.
- Account deletion backend is changed to a 30-day deactivation/recovery flow, including same-email reactivation-link issuance and a reactivation endpoint/page.
- Admin API/UI exposes learner account status and deletion events/reasons.
- A daily finalisation cron and protected endpoint are defined.

### Not yet released / must be completed before production use
- Apply `20261116120000_notification_email_automation.sql` to the active Pheonix Supabase project before deploying the new onboarding, delivery or reminder code. This migration has been committed but not applied.
- Set `LEARNORA_NOTIFICATION_AUTOMATION_ENABLED=true` only after that migration is applied and the worker is verified. It defaults to `false`. Configure `CRON_SECRET` so Vercel can authenticate the hourly worker.
- Both `20261109180000_learner_deletion_grace_and_marketing_consent.sql` and `20261109190000_erase_learner_records_after_recovery.sql` have been applied to the active Pheonix Supabase project and are recorded in migration history.
- Keep `ACCOUNT_DELETION_FINALIZER_ENABLED=false` until the full production erasure test suite and cleanup verification pass. The migrations being applied is necessary but not sufficient to enable automatic finalisation. Confirm `CRON_SECRET`, cron execution and failure alerting before enabling the finaliser.
- Run backend tests, frontend typecheck/build and browser acceptance on phone/tablet/desktop.
- Verify email delivery for deletion confirmation and reactivation links, and test all 30-day boundary cases.
- Run the new notification migration against the CI PostgreSQL baseline and add database assertions for delivery-claim concurrency, RLS/grants, retry leases and suppression states.
- The automation worker currently handles individual onboarding welcome messages, published assignment deadlines and individual learner inactivity. Extend deadline coverage to any future quiz/assessment deadline fields and cohort-specific assignment models when those data models expose authoritative due dates.
- Add marketing campaign authoring, audience selection, preview, scheduling, cancellation and audit UI/API in the future messaging platform. The per-recipient sender helper is present, but there is no campaign authoring/scheduling worker yet.
- Interest-signal capture and automated course recommendation campaigns remain future work. Course publish/update notifications currently remain in-app only.
- Review existing course-publish/update fan-out against the approved audience rules. The current service sends in-app notifications to active/completed course enrolments and learners whose completed onboarding profile matches the course; it has no email sender. Confirm the intended scope and avoid treating a general course launch as an automatic email.
- Review privacy notice and terms with qualified counsel before enabling marketing campaigns.
- Do not deploy backend/frontend changes or enable the deletion finaliser without the separately authorised release process.


## 8. Nigerian privacy references used for this design

This is an engineering interpretation for product planning, not legal advice. The current reference set is:
- **Nigeria Data Protection Act 2023:** sections 26(1)–(7) place the burden of proving consent on the controller, require affirmative rather than preselected consent, state that silence/inactivity is not consent, and require the right to withdraw to be explained. Section 27 requires clear privacy information including purposes, recipients, retention periods, rights and relevant profiling. Sections 35 and 36 cover withdrawal and objection, including an objection to direct marketing and related profiling.
- **NDPC General Application and Implementation Directive (GAID) 2025:** Article 18(1)(a) states that consent is required for any direct marketing activity.
- **ICLG, Data Protection Laws and Regulations 2026 — Nigeria:** its current country chapter explains the interaction between the NDPA direct-marketing objection right and the GAID opt-in requirement.

Primary references:
- [Nigeria Data Protection Act 2023 — Federal Government Gazette copy](https://www.nadpa-rapdp.org/sites/default/files/2023-07/Nigeria_Data_Protection_Act_2023_0.pdf)
- [NDPC General Application and Implementation Directive 2025](https://ndpc.gov.ng/wp-content/uploads/2025/07/NDP-ACT-GAID-2025-MARCH-20TH.pdf)
- [ICLG 2026 — Nigeria data protection](https://iclg.com/practice-areas/data-protection-laws-and-regulations/nigeria)

The controller identity, contact details, retention periods, lawful bases, provider contracts and whether Learnora meets any NDPC registration/DPO threshold must be assessed for the actual operating entity. A checkbox and unsubscribe link are necessary controls for marketing consent, but they do not by themselves establish full compliance or guarantee that the operator cannot be sued.
