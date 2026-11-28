# Learnora Product Decision Register

**Status:** CURRENT — authoritative record of explicit product-owner decisions  
**Last reviewed:** 28 November 2026  
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

### PD-011 — Shared organisation management and invitation-based account activation

**Status:** APPROVED
**Confirmed:** 21 November 2026

When a customer organisation request is processed and an organisation is created, its type must be established as either a **cohort** or a **corporate organisation**. The two types share a top-level management pattern but retain distinct operating models, team structures and administrator responsibilities.

Both organisation types have:
- An active **manager** who coordinates the organisation's overall operation.
- A formal **management team**. The manager belongs to and leads this team.
- Other teams created under that organisation by the manager.
- Administrators appointed by the manager, each with a defined role and responsibilities.

The manager has organisation-wide management access to everything that the specific organisation is entitled to access, including its teams. This does not grant access to other organisations or internal Learnora staff capabilities. The manager establishes the organisation's teams and appoints its administrators.

Administrators do not automatically inherit the manager's full access. Their permissions and responsibilities follow their assigned roles. For example:
- In a **cohort**, the coordinator is responsible for placing learners into the cohort's configured tracks and assigning tutors to those tracks. Other cohort administration duties are assigned according to each administrator's role.
- In a **corporate organisation**, the coordinator onboards the organisation's learners/employees into the relevant learning teams. Other corporate administration duties are assigned according to each administrator's role.

The management team is a real organisation team, not merely a label for a collection of unrelated platform functions. Learner support, assessment/quality, programme operations and reporting do not need separate teams by default; the manager, coordinator or an administrator may take responsibility for those functions.

#### Organisation onboarding and account activation

Managers, coordinators and administrators may initiate onboarding and create an invitation/provisioning record for an intended person, including the intended organisation, team or learning context and assigned role. They must not create the person's completed login credentials or set the person's password on their behalf.

For every organisation type:
1. An authorised manager or administrator initiates the person's onboarding and supplies the relevant organisation and role details.
2. The system sends an invitation email to the intended person's email address. The email identifies the relevant organisation and communicates the role/context for which the person is being onboarded.
3. The email contains an activation link.
4. The intended person follows the link and is taken to the account activation flow, where they create their own password and complete account activation.
5. The invitation/activation link expires **48 hours** after it is issued.

The organisation-side action is therefore an invitation/onboarding action, not full account creation. The invited person must personally complete activation. This rule applies to managers, coordinators, administrators, tutors, learners/employees and other organisation users; no organisation role may bypass the person's own activation step.

The invitation flow must be designed so that an expired or invalid link cannot activate an account. The exact resend, revoke, duplicate-invitation and expired-invitation recovery behaviour remains to be specified before implementation. Invitation tokens must be treated as sensitive, single-purpose credentials and must not expose passwords or reusable secrets in email content.

This decision establishes intended product behaviour. It does not approve a database migration, live account provisioning, email-provider/configuration change or deployment.

### PD-010 — Customer operating-model scope must be defined before implementation

**Status:** APPROVED — scope and modelling requirement only; detailed relationships remain unresolved  
**Confirmed:** 20 October 2026

The customer-side architecture must explicitly define and distinguish corporate organisations, learning cohorts, teams and instructor-led programmes. The operating-model work must account for cohort-based, employee and other organisation contexts, and for organisation owners/administrators, employees, team managers, cohort managers, tutors, programme managers and learners. Learnora internal administrators and internal staff are a separate product/trust boundary and are not customer organisation roles.

These actor categories and domain concepts define the scope that the architecture must address. They do not, by themselves, approve a final hierarchy, role inheritance model, team/cohort duration rule, simultaneous memberships, tutor assignment cardinality, contract entitlement model or progression threshold. Those relationships must be specified and approved before implementation.


### PD-012 — Cohort tutor assignment, organisation-managed account deletion and contract-end lifecycle

**Status:** APPROVED for the product behaviours below; technical erasure, audit and retention controls remain to be specified  
**Confirmed:** 21 November 2026; identity and deletion clarification: 21 November 2026

#### Cohort track tutor assignments

- Every learning track configured for a cohort must have at least one tutor assigned.
- A tutor may be assigned to more than one track. This is permitted but not compulsory.
- If a coordinator attempts to assign a tutor to another track while that tutor is already assigned, the system must first display a warning identifying the course/assignment already held by that tutor and require explicit confirmation before making the additional assignment.
- A track may have more than one tutor. If a coordinator attempts to assign another tutor to a track that already has a tutor, the system must display a warning and require explicit confirmation before adding the additional tutor.
- These warnings are confirmation gates, not prohibitions. The assignment must not proceed until the coordinator confirms.
- Tutor access remains scoped to the relevant cohort, assigned track(s), courses and responsibilities.

#### Exclusive email identity across individual and organisation-managed accounts

- An email address already associated with an organisation-managed account (including a cohort account) cannot be used to register or operate a normal individual Learnora learner account.
- An email address already associated with a normal individual Learnora learner account cannot be used to create or activate an organisation/cohort-managed account.
- The same email must not hold both account contexts simultaneously. This is a two-way exclusivity rule, not merely a restriction on individual registration.
- The rule applies to tutors and other organisation-managed users as well as organisation/cohort learners.
- When an organisation/cohort-managed account is deleted following access revocation, its identity and associated account data are deleted. The email is no longer reserved by that deleted account and may be used for a new account, subject to the normal registration/invitation checks. No automatic conversion or transfer of the deleted account's data occurs.

#### Cohort access revocation and account deletion

A cohort coordinator may revoke a learner's or tutor's access to Learnora. For an organisation/cohort-managed learner or tutor, revoking that person's access means deleting that managed account and its associated learner/tutor data, not merely disabling a cohort membership while retaining the account and data. The account and data are not retained as an identifiable dormant record.

This deletion applies to the organisation/cohort-managed account context. It must not delete shared platform resources merely because the person interacted with them. The exact dependent-record inventory, deletion transaction, security/audit evidence that may be retained without retaining the person's learning data, failure handling and any legally required exceptions must be specified before implementation. The organisation/cohort must not retain a learner roster or personal learning history as a workaround for deletion.

#### Cohort end and organisation contract end

- A cohort ending does not mean its parent organisation ends or should be deleted. The same organisation may start another cohort under a new cohort identity.
- When an organisation's contract ends, the organisation record itself must remain.
- At the contract-end point, retain an aggregate count of the learners associated with that organisation at that time. Retain the organisation record and this count, not the learner identities, roster, team membership or associated learner data covered by this rule.
- The organisation's Learnora access must be denied if no new contract is signed.
- A later contract may allow the organisation to operate again and create a new cohort, but it does not revive the deleted cohort's learner accounts or restore deleted learner/team data.

The retained count is a numeric organisation-level aggregate; it must not be possible to reconstruct an identifiable learner roster from it. The exact technical deletion sequence, backup/log/processor expiry, narrowly required legal or financial retention exceptions, and non-personal security audit design remain to be specified. These details do not weaken the approved requirement to delete organisation-managed learner data and preserve only the organisation record and learner count at contract end.

This decision does not authorise production deletion, anonymisation, account changes, database operations, migrations or deployment.
## 3. Unresolved decisions and documentation conflicts

The following items are deliberately unresolved. They are not implementation permission.

| ID | Topic | What must be resolved |
|---|---|---|
| UR-001 | Cohort operating/team model | The cohort has a management team led by its active manager. The manager creates other cohort teams and appoints role-scoped administrators. The coordinator places learners into configured tracks and assigns tutors. Every track requires at least one tutor; multiple tutors per track and one tutor across multiple tracks are allowed only after the specified confirmation warnings. The formal relationship between tracks, teaching groups/teams and learner groups, the complete team taxonomy, membership rules, dashboards and detailed permissions remain unresolved. Do not create separate support, assessment, operations or reporting teams by default. |
| UR-002 | Corporate organisation model | Corporate organisations have an active manager and management team. The manager creates other teams and appoints role-scoped administrators. The corporate coordinator onboards learners/employees into the relevant learning teams. Corporate team taxonomy, team managers, cohort-based/employee/other contexts, programmes, tutor relationships, contracts/entitlements, dashboards and detailed permissions still require specification. |
| UR-003 | Exclusive email identity and activation | The target rule is one mutually exclusive email identity: an email used by an individual learner cannot be used by an organisation/cohort-managed account, and vice versa. Deleting an organisation/cohort-managed account releases that email for a new registration/invitation; no account data is transferred. The canonical identity registry, race-safe uniqueness, legacy conflict reconciliation, organisation-membership cardinality (including whether one managed identity may belong to more than one customer organisation), and migration plan remain unresolved. Preserve existing records until an approved migration/transition plan exists. |
| UR-004 | Invitation and account-deletion mechanics | Specify invitation resend/revoke/duplicate/recovery; tutor joining and assignment lifecycle; the dependent-record inventory and atomic deletion process for organisation/cohort-managed learner/tutor accounts; security audit evidence that may remain without retaining learner data; backup/log/processor expiry; and legally required exceptions. The product outcome is settled: revocation deletes the managed account and its associated data. |
| UR-005 | Independent tutor model | Define the independent tutor product context and lifecycle separately from cohort tutors and organisation tutors. |
| UR-006 | Customer authoring | Define what selected corporate organisations may author, whether any AI capability is allowed, and the distinct non-AI authoring/upload/review/publishing rules for tutors and cohort teams. |
| UR-007 | Transitional Course Studio | Define the eventual transition from the current Learnora ME Course Studio prototype to Learnora Teams, including shared APIs, data ownership, media upload, review and publishing. Do not move code until dependencies and acceptance criteria are documented. |

| UR-009 | Current implementation versus live state | Revalidate dated code/schema/CI/deployment claims before presenting them as current. Historical audit snapshots must retain their dates and limitations. |
| UR-010 | Contract-end data lifecycle | Implement the approved outcome safely: retain the organisation record and numeric learner count at contract end; delete the covered learner identities, roster, team membership and associated learner data; deny access without a renewed contract. Specify atomic erasure, backup/log/processor expiry, narrow legal/financial exceptions and non-identifying security audit retention. A later cohort is a new cohort and does not restore deleted data. |

## 4. Documentation alignment status — 28 November 2026

The following documents have been checked against the approved decisions in this register. This is documentation status only; it is not evidence that the corresponding code, database or live product behaviour has been implemented.

| Document | Alignment status |
|---|---|
| `docs/README.md` | Updated with current product boundaries, sequence and a status register that separates documented decisions from unresolved specifications and live-state evidence. |
| `docs/PRODUCT_ENGINEERING_SPEC.md` | Updated to remove the obsolete claim that cohort learner records are retained after cohort closure and to distinguish approved email exclusivity/deletion outcomes from unresolved identity architecture. |
| `docs/ACCOUNT_AND_ORGANISATION_ARCHITECTURE.md` | Updated to replace the account-release implementation sequence with the current product sequence and approved deletion outcomes. Historical source observations and proposals remain labelled as historical. |
| `docs/COHORT_OPERATING_MODEL.md` | Records approved cohort track/tutor rules, account deletion on revocation, contract-end aggregate retention and the remaining technical/domain questions. |
| `docs/ROADMAP.md` | Current sequence follows PD-001. Historical launch ordering and the former account-release wording are labelled as superseded; the current product outcome is managed-account deletion. |
| `docs/LEARNER_JOURNEY_PHASES_1_5.md` | Historical implementation record explicitly states that it does not override the current individual learner → Teams → corporate organisation → independent tutor sequence. |
| `docs/AI_COURSE_PRODUCTION_AND_MEDIA_ARCHITECTURE.md` | Retains the separate Teams production and learner-delivery boundary, including Teams video uploads. Existing Course Studio placement remains transitional; migration/transition is not authorised. |
| `docs/FREE_LAUNCH_AND_PAID_EXPANSION_PLAN.md` | Its 31 October sequence is explicitly historical; free-access and paid-system preservation requirements remain subject to PD-001 and later decisions. |
| `docs/ENGINEERING_HISTORY_AND_DECISIONS.md` | Historical chronology is preserved. The older cohort-closure retention proposal is now explicitly marked superseded by PD-012. |

### Still open before the affected future features can be implemented

- Cohort team taxonomy and the exact relationship between tracks, teaching groups/teams and learner groups.
- Complete corporate organisation team taxonomy, operating workflows and permission matrix.
- Invitation resend, revoke, duplicate-invitation and expired-link recovery behaviour.
- Canonical identity architecture, race-safe uniqueness, legacy identity conflict/migration plan and whether one organisation-managed identity may belong to more than one customer organisation.
- Complete managed-account deletion inventory, atomicity/failure handling, sessions/tokens/invitations, non-identifying audit evidence, backup/log/cache/export/processor expiry and narrowly required legal/financial exceptions.
- Contract renewal/reactivation/grace-period and manager-visibility rules.
- Tutor assignment warning copy and detailed bulk/reassignment/removal audit behaviour.
- Current live Supabase/Vercel state and historical security/migration findings requiring separate evidence-based verification.

Do not resolve these by inventing defaults. Keep them unresolved until the product owner or the appropriate technical/legal review supplies the missing decision.


## 5. Implementation rule

Before implementing any affected feature:

1. Read this register and the complete current domain specification.
2. Check the unresolved register.
3. Distinguish approved target behaviour from current code and verified live state.
4. Preserve existing cohort and historical data unless a separately approved migration says otherwise.
5. Stop and request clarification when a required domain rule remains unresolved.
