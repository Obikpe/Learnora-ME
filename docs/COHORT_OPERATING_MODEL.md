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

## 4. Revoking access and account deletion

A cohort coordinator may:
- Revoke a learner's access to the Learnora site.
- Revoke a tutor's access to the Learnora site.
- Delete the learner's or tutor's account.

Access revocation and account deletion are separate operations. Revoking access must not be assumed to erase the account or learning data. Conversely, account deletion must not be treated as merely hiding the user from the cohort roster.

**Unresolved before implementation:** what account is deleted (the cohort-specific access/account record or the person's wider Learnora identity), whether the person has memberships in other cohorts/organisations or an individual account, the effect on learning evidence and audit history, who can restore access, confirmation requirements, and the exact erasure/anonymisation rules. The earlier individual learner 30-day deletion workflow must not be assumed to apply to organisation-managed cohort members without an explicit decision.

## 5. Cohort end versus organisation contract end

These are different lifecycle events.

### 5.1 A cohort ends

When a cohort ends:
- That cohort's active learning programme ends.
- The parent organisation record remains.
- A future cohort may be created under the same organisation with a new cohort ID.
- Do not delete the organisation merely because one cohort has ended.

The precise retention/erasure timing for cohort-specific data when a cohort ends independently of a contract ending remains to be specified.

### 5.2 The organisation contract ends

When the organisation's contract ends:
- The organisation record must remain.
- The organisation's access to Learnora must be denied if no new contract has been signed.
- The learner/team data covered by the product owner's retention rule must not be retained after contract end.
- The system must retain the count of learners associated with that organisation at the contract-end point.
- The organisation may enter a later contract and create a new cohort; the continuing organisation record must support this without reviving the previous cohort.

The learner count is an organisation-level historical count, not a retained learner roster. The product owner has not yet specified the exact counting rule (for example, whether it counts all learners ever associated with the organisation or the active learner population at the contract-end point); do not choose one without confirmation.

## 6. Data lifecycle and privacy constraints

The approved outcome is to retain the organisation record and a learner count at contract end, while not retaining the covered learner and team data. The implementation must not quietly preserve identifiable learner/team records in an archive or merely remove them from the user interface.

Before implementation, specify:
- Which learner and team fields/records are erased, anonymised or retained as strictly necessary exceptions.
- Whether team definitions, team membership, assignments, tutor records, progress, assessment evidence, certificates, reports and uploaded materials are included in the erasure scope.
- How the learner count is calculated, verified and retained without retaining the learner roster.
- Treatment of audit/security records, invoices, payment records, legal holds and other records that may have independent retention requirements.
- Backup, log, cache, export and third-party processor deletion/expiry.
- Whether a renewed contract restores any former data (no such restoration is currently approved) or starts a new cohort with new learner/team records.
- How the contract-end process interacts with individual identities, other organisation memberships and account deletion.
- Who authorises contract-end processing and how completion/failure is audited.

Do not infer that the count alone is sufficient to satisfy all legal, accounting or security retention duties. Obtain the required privacy/legal review before implementing destructive erasure. This document is a product requirement, not legal advice or authorisation to erase production data.

## 7. Access state after contract end

The organisation record remains available as a retained customer record, but its learning access is denied when there is no renewed contract. The exact states, renewal grace period (if any), manager visibility, billing status, reactivation rules and access restoration workflow are unresolved. Do not invent a grace period or automatically restore previous cohort access.

## 8. Implementation boundary

These rules are future product requirements. The current approved implementation sequence still places the normal individual learner experience first, then Learnora Teams, then corporate organisation experience, with independent tutor functionality separately scoped. Cohort-specific requirements must be preserved and documented, but this document does not authorise implementation during the current individual learner phase.

No application code, database schema, migrations, live records, storage, account state, email configuration, CI or deployment may be changed on the basis of this document alone.
