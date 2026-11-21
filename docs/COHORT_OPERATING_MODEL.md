# Cohort Operating Model and Lifecycle

**Status:** Approved product behaviours with explicitly unresolved domain and implementation details  
**Confirmed:** 21 November 2026  
**Authority:** [PRODUCT_DECISIONS.md](PRODUCT_DECISIONS.md), especially PD-004, PD-011 and PD-012  
**Scope:** Cohort management, track/tutor assignments, learner access and the relationship between cohort and parent-organisation lifecycles.

This document defines the cohort-specific behaviour that has been explicitly confirmed. It does not turn unspecified team structures, permissions, identity mechanics or data-erasure details into assumptions.

## 1. Cohort and parent organisation

A cohort is a managed learning programme under a customer organisation. The organisation is the continuing customer-level record; an individual cohort is a distinct programme instance with its own configured tracks, learners and tutor assignments.

- The customer organisation is classified as a cohort-type organisation when it is created.
- It has an active manager and a formal management team under the shared management model.
- The manager creates any additional cohort teams and appoints administrators with role-specific responsibilities.
- The cohort coordinator manages learner placement into the cohort's configured tracks and tutor assignment to those tracks.
- A cohort can end while its parent organisation continues to exist.
- A later cohort for the same organisation is a new cohort identity. Do not reuse the ended cohort as though it were still active.

A cohort must not be modelled as a corporate organisation with a different label. Its track configuration, learner placement and tutor assignment workflow are cohort-specific.

## 2. Track and learner model

The cohort's enabled tracks and course configuration are established for that cohort. Each learner is assigned to a track by the coordinator. The existing approved cohort rule remains that a learner has one fixed track for the lifetime of that cohort; a different track requires a new cohort membership/cohort context rather than an in-place change.

The exact learner grouping/team structure around each track is not yet approved. Do not assume that a track is itself a formal team, or that every track must have a separately named team, until that distinction is confirmed.

## 3. Tutor coverage and assignment cardinality

### 3.1 Minimum coverage

Every learning track in a cohort must have at least one tutor assigned. An active cohort track without a tutor does not satisfy the required operating model.

### 3.2 One tutor across multiple tracks

A tutor may be assigned to more than one track. This is optional, not an automatic assignment.

When a coordinator attempts to assign a tutor to another track and that tutor already has an assignment, the system must:

1. Display a warning that the tutor is already assigned.
2. Identify the course associated with the existing assignment, as specified by the product owner.
3. Ask the coordinator to confirm the additional track assignment.
4. Make the additional assignment only after explicit confirmation.

The warning is not a prohibition. It is a deliberate confirmation step.

### 3.3 Multiple tutors on one track

A track may have more than one tutor. When a coordinator attempts to assign another tutor to a track that already has a tutor, the system must:

1. Display a warning that a tutor is already assigned.
2. Ask the coordinator to confirm that they want to add another tutor to the track.
3. Add the additional tutor only after explicit confirmation.

This warning is also a confirmation step, not a hard limit of one tutor per track.

### 3.4 Assignment scope and unresolved detail

Tutor access must remain restricted to the relevant cohort, track, courses and responsibilities assigned to that tutor. An assignment to one track must not grant access to every track or all cohort administration.

The precise warning copy, how the course is selected/displayed where several course assignments exist, whether the coordinator can select multiple tutors in one operation, and the full assignment/reassignment/removal audit workflow remain to be specified. Do not silently replace the required confirmation with a hard validation error or automatic assignment.

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
