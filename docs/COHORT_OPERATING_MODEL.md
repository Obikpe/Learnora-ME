# Cohort Operating Model and Lifecycle

**Status:** Approved product behaviours with explicitly unresolved domain and implementation details  
**Confirmed:** 21 November 2026  
**Authority:** [PRODUCT_DECISIONS.md](PRODUCT_DECISIONS.md), especially PD-004, PD-011 and PD-012  
**Scope:** Cohort management, track/tutor assignments, learner access and the relationship between cohort and parent-organisation lifecycles.

This document defines the cohort-specific behaviour that has been explicitly confirmed. It does not turn unspecified team structures, permissions, identity mechanics or data-erasure details into assumptions.

## 1. Cohort and parent organisation

A cohort is a managed learning programme under a customer organisation. The organisation is the continuing customer-level record; an individual cohort is a distinct programme instance with its own configured tracks, learners, teams and tutor assignments.

- The customer organisation is classified as a cohort-type organisation when it is created.
- It has an active management account and a formal management team under the shared management model.
- The management account has oversight of the entire cohort and all its tracks, subject to the organisation's entitlements.
- The manager creates additional cohort teams and appoints administrators with role-specific responsibilities.
- The cohort coordinator manages learner placement into tracks and sends track-specific tutor invitations.
- Cohort teams are working groups with members and responsibilities. A track is a separate learning/teaching structure, not a team.
- Members of cohort teams may be assigned to one or more tracks according to their responsibilities. A team membership alone does not grant access to every track.
- A cohort can end while its parent organisation continues to exist.
- A later cohort for the same organisation is a new cohort identity. Do not reuse the ended cohort as though it were still active.

A cohort must not be modelled as a corporate organisation with a different label. Its track configuration, learner placement and tutor invitation/assignment workflow are cohort-specific.

## 2. Track and learner model

The cohort's enabled tracks and course configuration are established for that cohort. Each learner is assigned to one track by the coordinator. The learner remains on that fixed track for the lifetime of that cohort; a different track requires a new cohort membership/cohort context rather than an in-place change.

Tracks and teams are distinct:

- A track represents a defined learning/teaching path with its configured courses and assigned learners.
- A team represents a working group of people with cohort responsibilities.
- A team member may be assigned to a track or multiple tracks where appropriate.
- Being a member of a team does not, by itself, grant access to all cohort tracks or learners.
- A track must not be created, displayed or permissioned as though it were a team.

The management account can oversee all cohort tracks. Other members' access is based on their explicit track assignments and role responsibilities.

## 3. Tutor invitations, coverage and assignment scope

### 3.1 Minimum tutor coverage

Every learning track in a cohort must have at least one tutor assigned. An active cohort track without a tutor does not satisfy the required operating model.

### 3.2 Track-specific invitation flow

Tutor onboarding for cohort teaching follows an invitation-link model similar to Google Classroom:

1. The coordinator selects the tutor and the specific track they are being invited to teach.
2. Management initiates an invitation for that track. The tutor receives an invitation link and completes the required account activation themselves; management does not create the tutor's password or completed login credentials.
3. The invitation identifies the cohort and the track teaching context. It is an invitation to teach that track, not an invitation to see the entire cohort. The invitation link expires 48 hours after issue, consistent with the shared organisation invitation rule in PD-011.
4. If the tutor is already actively assigned to another track, management must see a warning before sending the additional track invitation. The warning identifies the existing track/course assignment and asks management to confirm that it intends to invite the tutor to teach another track.
5. If the selected track already has an assigned tutor, management must see a warning before sending an invitation to another tutor for that track. The warning asks management to confirm that it intends to add a co-tutor.
6. If both conditions apply, the confirmation must make both relevant existing assignment facts clear before the invitation is sent.
7. The invitation is sent only after the authorised management user explicitly confirms. The warning is a confirmation gate, not a prohibition.

A tutor may teach multiple tracks, but each additional track requires its own explicit invitation/assignment. A track may have multiple tutors, including co-tutors, but each additional tutor must be explicitly invited and confirmed through the warning flow.

### 3.3 Tutor visibility and access boundary

A tutor can access only the track or tracks to which that tutor has an active assignment, and only the courses, learners and teaching resources within those assigned tracks and permitted responsibilities.

In particular:

- A tutor assigned to Track A must not see the roster, identities, profiles, progress, submissions, assessment results, reports or other learner information belonging to Track B.
- A tutor assigned to more than one track may see the learners and learning information in each of those specifically assigned tracks, but no others.
- Team membership does not expand a tutor's track visibility.
- A tutor must not gain cohort-wide learner search, reporting or export access merely because they are a cohort team member or have been invited to teach one track.
- The management account retains oversight across all tracks and may access cohort-wide management information within its authorised responsibilities.

These restrictions must be enforced by the backend for every relevant list, detail, search, report, export and learner-data endpoint, not only by hiding items in the user interface.

### 3.4 Assignment confirmation and unresolved detail

The precise warning copy, how existing course/track assignments are displayed when several exist, whether a coordinator can issue multiple invitations in one operation, and the detailed assignment/reassignment/removal audit workflow remain to be specified. Do not silently replace the required confirmation with a hard validation error or automatic assignment.

## 4. Revoking access and deleting organisation-managed accounts

A cohort coordinator may revoke a learner's or tutor's access to Learnora. For an organisation/cohort-managed learner or tutor, revoking access means deleting that person's managed account and its associated learner/tutor data. It is not merely a suspension or removal from the current cohort roster while retaining the person's account and learning data.

The email identity is mutually exclusive across account contexts:
- If an email is associated with an organisation/cohort-managed account, it cannot be used for a normal individual Learnora learner account.
- If an email is associated with a normal individual learner account, it cannot be used for an organisation/cohort-managed account.
- The same email cannot hold both contexts at once.
- Once the organisation/cohort-managed account has been deleted, that account no longer reserves the email. The email may be used for a new account through the ordinary registration/invitation process. No deleted account data is transferred to the new account.

The deletion applies to the managed account and its associated learner/tutor data. Do not retain an identifiable dormant account, learner roster, personal learning history or assessment record as a workaround. Shared platform resources must not be deleted solely because the person interacted with them.

The exact dependent-record inventory, atomic deletion/failure handling, security evidence that may be retained without retaining learner data, backup/log/third-party processor expiry and any legally required exceptions must be specified before implementation. Existing records must be preserved until a separately approved transition and migration plan is ready; this product decision is not authorisation to delete current production data.

## 5. Cohort end versus organisation contract end

These are different lifecycle events.

### 5.1 A cohort ends

When a cohort ends:
- That cohort's active learning programme ends.
- The parent organisation record remains.
- A future cohort may be created under the same organisation with a new cohort ID.
- Do not delete the organisation merely because one cohort has ended.

A later cohort is a new cohort identity. It does not automatically revive learner accounts or restore learner/team data deleted under the organisation contract-end process.

### 5.2 The organisation contract ends

When the organisation's contract ends:
- The organisation record must remain.
- At the contract-end point, retain the numeric count of learners associated with that organisation at that time.
- Delete the covered organisation/cohort-managed learner accounts and their associated learner data, including identifiable learner roster and team-membership data covered by this rule.
- Do not retain an identifiable learner roster, dormant learner accounts or personal learning histories as a substitute for deletion.
- Deny the organisation's Learnora access if no new contract is signed.
- A later contract may permit the organisation to operate again and create a new cohort under a new cohort ID. It does not restore the deleted learner accounts or data.

The retained learner count is an organisation-level aggregate only. It is not a retained list of learners and must not allow the organisation's former learner identities to be reconstructed.

## 6. Data lifecycle and privacy constraints

The approved contract-end outcome is to retain the organisation record and the learner count captured at contract end, while deleting the covered organisation/cohort-managed learner accounts and associated learner/team data.

Before implementation, specify the technical controls needed to carry out that approved outcome safely:
- The complete inventory of account-linked learner and tutor records to delete, including progress, assessment evidence, certificates, submissions, notes, reports, notifications, AI conversations, team membership and personal uploads where they are within the organisation-managed account data.
- Which shared platform or organisation-owned resources must remain, with the person's attribution detached where appropriate rather than deleting the shared resource.
- How the numeric learner count is calculated and retained without retaining learner identities or a reconstructable roster.
- The narrow security, legal, accounting or financial records that may need separate retention, and how those records avoid preserving the learner's learning history or a usable account.
- Atomic deletion, retries, failure handling and proof that no active access path survives completion.
- Backup, log, cache, export and third-party processor deletion/expiry.
- How the process handles invitations, sessions, tokens and any pending activation.
- Who authorises contract-end processing and how completion/failure is audited without retaining unnecessary personal data.

These are implementation and compliance details; they do not reopen the product decision about the outcome. Do not use a broad "legal retention exception" to retain the learner roster or personal learning data without a specific reviewed basis. Obtain privacy/legal review before destructive implementation. This document is a product requirement, not legal advice or authorisation to erase production data.

## 7. Access state after contract end

The organisation record remains available as a retained customer record, but its learning access is denied when there is no renewed contract. The exact states, renewal grace period (if any), manager visibility, billing status, reactivation rules and access restoration workflow are unresolved. Do not invent a grace period or automatically restore previous cohort access.

## 8. Implementation boundary

These rules are future product requirements. The current approved implementation sequence still places the normal individual learner experience first, then Learnora Teams, then corporate organisation experience, with independent tutor functionality separately scoped. Cohort-specific requirements must be preserved and documented, but this document does not authorise implementation during the current individual learner phase.

No application code, database schema, migrations, live records, storage, account state, email configuration, CI or deployment may be changed on the basis of this document alone.
