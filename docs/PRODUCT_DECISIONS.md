# Learnora Product Decision Register

**Status:** CURRENT — authoritative record of explicit product-owner decisions  
**Last reviewed:** 21 November 2026  
**Repository:** `Obikpe/Learnora-ME`  
**Applies to:** Learnora ME, Learnora Teams, cohorts, corporate organisations and independent tutors

This register records explicit product-owner decisions. It does not turn proposals, code observations, historical implementation notes or assumptions into approved product requirements. Where a detail is not settled here or in a current approved domain specification, it remains unresolved and must not be invented during implementation.

## 1. Authority and use

This is the authoritative register for explicit cross-product decisions. Domain specifications remain authoritative for detailed workflows within their scope, provided they do not contradict a decision recorded here.

When a decision changes, add a dated entry identifying the previous rule, the replacement, affected documents and compatibility implications. Update the affected specifications and roadmap in the same documentation workstream. Do not silently rewrite historical records.

Decision status:
- **APPROVED:** explicitly confirmed by the product owner.
- **UNRESOLVED:** required detail is missing or sources conflict; implementation must stop at that boundary.
- **SUPERSEDED:** replaced by a later numbered decision; retain the history and link to the replacement.

## 2. Approved product decisions

### PD-001 — Product implementation sequence

**Status:** APPROVED  
**Confirmed:** 21 November 2026

The implementation sequence is:

1. Complete only the normal individual learner experience in Learnora ME.
2. Build the separate Learnora Teams website, including its internal course/content production workflows.
3. Return to normal Learnora ME to implement the corporate organisation experience.
4. Build independent tutor functionality separately.

This sequence governs implementation priority. It does not cancel deferred product capabilities or authorise deletion of their code, schemas, permissions, migrations, accounts or historical records.

Cohort functionality and existing cohort accounts, access rules, assignments, progress and historical data must be preserved during the individual learner phase. Do not build corporate organisation, independent tutor or Teams workflows as part of the current individual learner implementation. Shared changes are permitted only when necessary for the individual learner work, security, compatibility or regression prevention.

**Supersedes:** Older roadmap sequencing that places organisation/cohort completion before the individual learner journey, and older implementation ordering that treats creator/tutor work as part of the immediate learner release.

### PD-002 — Learnora ME and Learnora Teams are separate products

**Status:** APPROVED  
**Confirmed:** 21 November 2026

- **Learnora ME** is the customer-facing learning website. In the current phase, its priority is the normal individual learner experience.
- **Learnora Teams** is a separate website and workspace for authorised internal teams to manage course/content production and related internal operations.
- Learnora Teams is not the corporate organisation portal.
- The existence of internal staff routes or Course Studio functionality inside Learnora ME is an implementation detail and does not redefine the intended product boundary.
- Do not merge the cohort, corporate organisation, independent tutor and internal staff contexts into one generic workspace.

### PD-003 — AI course production belongs to Learnora Teams

**Status:** APPROVED  
**Confirmed:** 21 November 2026

The intended product responsibility is:

- Learnora Teams owns authorised AI-assisted course and lesson creation, curriculum/lesson production workflows, production review, acceptance and publishing.
- Learnora Teams users can also upload their own human-produced lesson videos and other permitted lesson assets.
- Normal Learnora ME is the learner-facing delivery website. It renders and serves accepted/published course content and associated media through the approved backend and storage/delivery architecture.
- Normal learner-facing Learnora ME is not the intended AI course-authoring or AI video-production workspace.

Existing Course Studio functionality currently placed in Learnora ME must be treated as a transitional implementation state. Do not assume that its current location is the final architecture or move it without first documenting dependencies and an approved transition plan.

This decision does not authorise a storage migration, provider change, production migration, deployment or destructive content operation.

### PD-004 — Cohorts and corporate organisations are distinct domain models

**Status:** APPROVED  
**Confirmed:** 21 November 2026

A cohort is not merely a corporate organisation with a different label. Cohorts and corporate organisations may both have teams, members and learning resources, but their team structures, responsibilities, tutor relationships, assignments, dashboards, permissions and operating workflows are distinct.

A cohort has its own teams. Cohort teams can include tutors assigned to specific tracks created by that cohort, alongside learners and other cohort-specific operations. Tutor access must be scoped to the cohort/team and the specific track, course or other resources assigned to that tutor.

Do not model cohorts as simply:
- an organisation with a roster;
- a list of learners and courses;
- a corporate team with a different name; or
- a single track assignment without the cohort's team and tutor operating model.

The exact cohort team taxonomy, membership rules, operational responsibilities and permission matrix are not yet fully settled in this register. See the unresolved items below. Do not invent them. Earlier assistant-generated suggestions about permanent teams, time-bound cohorts, simultaneous team/cohort memberships, 70% progression gates or specific contract-capacity rules are proposals only unless independently confirmed by the product owner; do not treat them as approved requirements.

Corporate organisation teams and workflows must be documented independently. The existence of cohort teams does not define the corporate organisation team model, and vice versa.

### PD-005 — Preserve existing cohort data and access during individual learner work

**Status:** APPROVED  
**Confirmed:** 21 November 2026

During the current individual learner phase:
- Preserve existing cohort accounts and identity/access paths unless a narrowly scoped compatibility or security correction is required.
- Preserve cohort membership, team relationships, tutor assignments, track/course/lesson assignments, progress, assessment evidence and historical records.
- Do not silently convert cohort identities to individual learner identities.
- Do not delete cohort functionality because its broader workflow is deferred.
- Any necessary shared change must include explicit regression protection for cohort access and data.

This is a preservation requirement, not approval of any particular long-term cohort identity schema.

### PD-006 — Customer authoring permissions are separate from internal AI production

**Status:** APPROVED  
**Confirmed:** 21 November 2026

Internal Learnora Teams AI production permission does not automatically extend to:
- corporate organisation owners, administrators or teams;
- cohort tutors;
- independent tutors; or
- ordinary learners.

Any later customer-facing course authoring capability must be specified separately for its relevant product context, with its own roles, resource ownership, review/publication authority and permission rules. AI production access is not implied for every organisation; any selected-organisation AI build capability requires an explicit product-owner decision and permission model. External/independent tutors do not receive AI course-building access.

### PD-007 — Historical examples are not evidence of current customer access

**Status:** APPROVED  
**Confirmed:** 21 November 2026

WitStart was used as an example of a cohort context. It is not evidence that an active customer organisation currently exists or that a current user has a live organisation entitlement.

Preserve historical WitStart records and migration history. Do not infer live product access from a legacy role constant, route, migration, table row mentioned in an old audit or historical engineering note. Current live state requires current, read-only evidence from the relevant system.

### PD-008 — Documentation governs implementation

**Status:** APPROVED  
**Confirmed:** 21 November 2026

The repository documentation is the source of truth used for product and engineering implementation. It must be accurate, internally consistent and explicit about:
- approved product decisions;
- current versus intended architecture;
- implementation status and verification evidence;
- deferred capabilities;
- historical decisions;
- unresolved requirements; and
- migration, compatibility and release constraints.

Do not infer requirements from route names, code structure, schema names or isolated historical notes. If the documentation is unclear or contradictory, reconcile it or ask the product owner before implementing the affected behaviour.

### PD-009 — No unapproved production operations

**Status:** APPROVED  
**Confirmed:** 21 November 2026

Documentation work does not authorise application implementation, production deployments, live database mutations, migration application, storage changes, secret/configuration changes or destructive data operations. Each requires the product owner's separate explicit approval.

### PD-010 — Customer operating-model scope must be defined before implementation

**Status:** APPROVED — scope and modelling requirement only; detailed relationships remain unresolved  
**Confirmed:** 20 October 2026

The customer-side architecture must explicitly define and distinguish corporate organisations, learning cohorts, teams and instructor-led programmes. The operating-model work must account for cohort-based, employee and other organisation contexts, and for organisation owners/administrators, employees, team managers, cohort managers, tutors, programme managers and learners. Learnora internal administrators and internal staff are a separate product/trust boundary and are not customer organisation roles.

These actor categories and domain concepts define the scope that the architecture must address. They do not, by themselves, approve a final hierarchy, role inheritance model, team/cohort duration rule, simultaneous memberships, tutor assignment cardinality, contract entitlement model or progression threshold. Those relationships must be specified and approved before implementation.

## 3. Unresolved decisions and documentation conflicts

The following items are deliberately unresolved. They are not implementation permission.

| ID | Topic | What must be resolved |
|---|---|---|
| UR-001 | Cohort team model | The user has confirmed that cohorts have their own teams and that cohort teams can include tutors assigned to specific tracks created by that cohort, alongside learners and other cohort-specific operations. Still define team types/purposes, membership, managers, tutor-to-track/course assignment rules, learner relationships, operations, dashboards and permissions. |
| UR-002 | Corporate organisation model | Define distinct configurable contexts for cohort-based, employee and other organisations, and model organisations, teams, cohorts and instructor-led programmes. Account for owners/admins, employees, team managers, cohort managers, tutors, programme managers and learners. Resolve their relationships, contracts/entitlements, tutor relationships, workflows, dashboards and permissions. Do not reduce the model to a member/course mapping. |
| UR-003 | Account identity | Reconcile the historical cohort-specific login/account model with later global identity proposals. PD-005 requires preservation; it does not approve a conversion or a new identity schema. |
| UR-004 | Cohort versus organisation tutor lifecycle | Specify separately how tutors join, are assigned, gain access, are removed and retain/relinquish access in each context. |
| UR-005 | Independent tutor model | Define the independent tutor product context and lifecycle separately from cohort tutors and organisation tutors. |
| UR-006 | Customer authoring | Define what selected corporate organisations may author, whether any AI capability is allowed, and the distinct non-AI authoring/upload/review/publishing rules for tutors and cohort teams. |
| UR-007 | Transitional Course Studio | Define the eventual transition from the current Learnora ME Course Studio prototype to Learnora Teams, including shared APIs, data ownership, media upload, review and publishing. Do not move code until dependencies and acceptance criteria are documented. |
| UR-008 | Roadmap alignment | Rewrite older roadmap/phase sequencing so it follows PD-001 while preserving security, migration and release gates that remain prerequisites to safe individual learner delivery. |
| UR-009 | Current implementation versus live state | Revalidate dated code/schema/CI/deployment claims before presenting them as current. Historical audit snapshots must retain their dates and limitations. |

## 4. Required document alignment

The following documents must be reviewed against this register. This is a reconciliation list, not a claim that they have already been corrected.

- `docs/README.md` — authority, status and reading rules.
- `docs/PRODUCT_ENGINEERING_SPEC.md` — product boundaries, personas, cohort identity, current phase and deferred scope.
- `docs/ACCOUNT_AND_ORGANISATION_ARCHITECTURE.md` — account/identity proposals, cohort and organisation separation, tutor scope and preservation.
- `docs/AI_COURSE_PRODUCTION_AND_MEDIA_ARCHITECTURE.md` — Teams ownership, transitional Course Studio placement and delivery boundary.
- `docs/ROADMAP.md` — current sequence, release gates and deferred work.
- `docs/LEARNER_JOURNEY_PHASES_1_5.md` and `docs/LEARNER_OUTCOMES_PHASES_6_8.md` — scope and sequence, without erasing historical phase records.
- `docs/ENGINEERING_HISTORY_AND_DECISIONS.md` — preserve chronology; label superseded product directions rather than rewriting history.

## 5. Implementation rule

Before implementing any affected feature:

1. Read this register and the complete current domain specification.
2. Check the unresolved register.
3. Distinguish approved target behaviour from current code and verified live state.
4. Preserve existing cohort and historical data unless a separately approved migration says otherwise.
5. Stop and request clarification when a required domain rule remains unresolved.
