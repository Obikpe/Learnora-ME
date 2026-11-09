# Learner account lifecycle, notifications and marketing automation

**Status:** Product and engineering specification  
**Updated:** 9 November 2026  
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

### 1.4 Final deletion

A daily Vercel cron invokes the protected account-finalisation endpoint. The endpoint calls a service-role-only database function that processes a bounded batch with row locking and `SKIP LOCKED`.

For each due account, the database function:
- inserts a restricted `deleted_account_history` record, including the original email, account dates, deletion reason and the minimum required account snapshot;
- anonymises the live user row and releases the original email for a future registration;
- clears credentials, verification and recovery tokens, marketing consent and other live account contact fields;
- disables retained organisation team/member links where applicable;
- records a `learner_account_deleted` audit event including the reason and finalisation date.

The historical record is not a second usable account. Its access must remain restricted to authorised staff/service roles and its retention period must be documented. The legal basis and retention period for keeping the original email and deletion reason require privacy review; do not retain them indefinitely by default.

**Operational dependency:** the deployed backend needs a strong `CRON_SECRET` environment variable. The daily cron is configured in `backend-python/vercel.json`; set the secret in the Vercel production environment before deploying. Monitor cron failures and alert staff when a finalisation run fails.

### 1.5 Organisation-managed identities

The self-service deletion and reactivation flow is for independent individual learners only. Cohort and organisation-managed accounts must continue through the organisation release/ownership process. Do not silently convert a managed identity into an independent account.

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

## 3. Marketing consent

### 3.1 Registration

The registration form presents a separate, optional, unticked checkbox:

> Yes, I would like to receive Learnora marketing emails about new learning tracks, course releases, offers and discounts.

It must not be bundled with Terms of Use, Privacy Policy acceptance or account creation. Leaving it unticked must not block registration or reduce access to learning.

Store an auditable consent record:
- `marketing_email_opt_in`;
- `marketing_consent_at`;
- `marketing_consent_source` (for example, `signup_form` or `account_settings`).

Do not infer consent from account creation, course enrolment, browsing, search activity, silence or a preselected checkbox.

### 3.2 Withdrawal and suppression

- Learners can change the preference in Account Settings.
- Every marketing email must include a prominent, working unsubscribe link in its footer.
- The unsubscribe action must work without requiring the learner to sign in, must be idempotent, and must update the central suppression state immediately. Each campaign email receives an opaque random token; only its hash is stored in a service-only token table. Unsubscribing consumes all outstanding tokens for that learner.
- Marketing delivery must check consent and suppression status at send time, not only when a campaign audience is first built.
- Keep a minimal suppression record long enough to prevent accidental re-import or re-subscription. A later opt-in must be a new affirmative action with a new consent timestamp.
- Do not include marketing content in essential account/security emails or enrolled-course service notices.

### 3.3 Transactional versus marketing messages

| Message | Channel | Marketing opt-in required? |
|---|---|---|
| Email verification, password reset, login/security alerts | Email | No; essential account communication |
| Deletion confirmation and reactivation links | Email | No; account lifecycle communication |
| Important account/service notices | In-app and, where needed, email | No, where genuinely necessary to provide or secure the service |
| Update to a course the learner is currently enrolled in | In-app; email where useful | No, when limited to the learner's existing enrolment/service |
| New track, general course launch, discounts, promotions | In-app and/or email | Yes; treat promotional delivery as marketing |
| Recommendations based on search/browsing interest | In-app and/or email | Yes; interest-based promotional targeting must not bypass consent |

Do not relabel a promotion as an "important notification" to avoid the marketing preference. The purpose and content determine the category.

## 4. Automated notification engine — future implementation

Learnora should use event-driven notification routing rather than broadcasting every announcement to every learner.

### 4.1 Event and audience model

| Event | Audience rule | Purpose |
|---|---|---|
| Account created / verified | The account owner | Transactional |
| Account deletion requested / deactivated / reactivated | The account owner | Transactional |
| Course enrolled | The enrolling learner | Service confirmation |
| Enrolled course updated | Learners with a current enrolment in that course | Learning-service update |
| Track/course published or materially updated | Learners with a relevant, sufficiently strong interest signal | Promotional/recommendation; marketing consent required |
| New offer or discount | Eligible, marketing-opted-in learners | Marketing |
| Platform-wide essential service incident | Accounts materially affected | Essential service notice |

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
3. **Interest-based:** route relevant catalogue updates only when the interest threshold is met. Treat this as marketing/personalised promotion and require opt-in for both email and promotional in-app delivery.
4. **Global marketing:** route only to learners with active marketing consent and no suppression record.
5. **Managed accounts:** respect organisation/cohort tenant rules and any organisation-level communication settings. Do not expose one organisation's learner data or preferences to another.

### 4.4 Delivery architecture

Use a durable outbox/queue:
- application services publish a typed event with a stable idempotency key;
- a recipient resolver calculates the audience from current enrolments, interest signals, account state and consent;
- delivery records are created per recipient/channel;
- a worker claims jobs with a lease, sends through the configured email provider or creates an in-app notification, and records outcome/provider ID;
- transient errors retry with bounded exponential backoff; permanent failures move to a dead-letter state;
- deduplicate event + recipient + channel so retries do not send duplicate messages;
- enforce per-user frequency caps and quiet hours for promotional messages;
- re-check account status, email verification, consent and unsubscribe suppression immediately before email send.

The current `learnora_notifications` table remains the in-app inbox source. The future engine should add event/outbox/delivery records rather than overloading the inbox table with campaign state.

### 4.5 Email requirements

Every marketing email must:
- clearly identify Learnora and the commercial/marketing nature of the message;
- use a truthful subject and sender identity;
- include a working unsubscribe/preferences link at the bottom;
- support one-click unsubscribe headers where supported by the sending provider;
- record delivery, bounce, complaint and unsubscribe outcomes;
- stop subsequent marketing sends promptly after an unsubscribe or complaint.

Important transactional email templates must be separate from campaign templates. The email worker must not send to a deactivated/deleted account.

### 4.6 Admin campaign controls

Learnora staff should be able to:
- create a draft campaign and choose a permitted audience rule;
- preview audience size and exclusion reasons before sending;
- preview and test-send the message;
- schedule, pause or cancel a campaign;
- inspect sent, delivered, bounced, complained and unsubscribed counts;
- audit who created, approved and sent each campaign.

Require an explicit send action and permission check. Do not let a campaign editor override consent or suppression rules.

## 5. Privacy, compliance and abuse safeguards

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

## 6. Implementation status and release gates

### Implemented in the current source changes
- Mobile/tablet navigation drawer is rendered through a body portal so the sticky header/backdrop filter cannot clip it.
- Notification preview is a constrained right-side drawer, with smaller text and the header left accessible so clicking the bell again closes it.
- Registration has an optional, unticked marketing email opt-in.
- Marketing consent fields are written on registration.
- Account Settings has a marketing preference control and deletion-reason capture.
- Account deletion backend is changed to a 30-day deactivation/recovery flow, including same-email reactivation-link issuance and a reactivation endpoint/page.
- Admin API/UI exposes learner account status and deletion events/reasons.
- A daily finalisation cron and protected endpoint are defined.

### Not yet released / must be completed before production use
- Apply the new migration `20261109180000_learner_deletion_grace_and_marketing_consent.sql` to the active Pheonix Supabase project before deploying the backend code. The migration has not been applied to production.
- Set a strong production `CRON_SECRET` in Vercel before deploying the backend; verify the daily cron is authorised and monitor its result.
- Run backend tests, frontend typecheck/build and browser acceptance on phone/tablet/desktop.
- Verify email delivery for deletion confirmation and reactivation links, and test all 30-day boundary cases.
- Implement and test the event/outbox notification engine, interest-signal capture, campaign worker and actual marketing email templates. The unsubscribe endpoint and page are in place, and the backend exposes a helper that creates a per-email opaque unsubscribe URL. No campaign sender currently consumes that helper.
- Review privacy notice and terms with qualified counsel before enabling marketing campaigns.
- Do not deploy or apply the migration without the separately authorised release process.
