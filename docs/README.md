# Learnora Documentation Guide

**Status:** Product documentation governance and reading guide  
**Applies to:** The complete Learnora product and its application, service, data and operational boundaries  
**Last reviewed:** 21 November 2026

## 1. Why this guide exists

The documentation in this directory is the product and engineering source of truth. Implementation work must follow the documented product decisions, scope, workflows, permissions, data boundaries and acceptance criteria.

A reader must not have to infer product architecture from route names, legacy code, database table names, old implementation notes or isolated conversations. Where the documentation is unclear or contradictory, the conflict must be resolved in writing before the affected feature is implemented.

This guide establishes how the documents relate to one another. It does not silently rewrite or erase historical decisions.

## 2. Authority and precedence

Use the following precedence when documents disagree:

1. **Latest explicit product-owner decision** recorded in [PRODUCT_DECISIONS.md](PRODUCT_DECISIONS.md). This is the cross-product decision register; domain specifications define detailed workflows within those approved boundaries.
2. **Current product and system architecture specifications** for the relevant domain.
3. **Approved feature/workflow specifications and acceptance criteria.**
4. **Current implementation and operational runbooks**, which describe how an approved design is implemented or operated.
5. **Roadmaps and sequencing plans**, which determine when approved work is scheduled, not what the product means.
6. **Engineering history, audit reports and superseded proposals**, which provide evidence and historical context but do not independently authorise a new product direction.

A newer document does not automatically override an older one merely because its timestamp is later. The newer document must explicitly identify the decision it changes, the previous rule it supersedes, the reason, the effective scope and any migration or compatibility implications.

If two sources at the same authority level conflict and no explicit supersession is recorded, mark the issue **UNRESOLVED**. Do not choose whichever interpretation is easiest to implement.

## 3. Product boundaries that must remain distinct

The following are distinct product concepts and must not be collapsed into one another:

- **Learnora ME:** the customer-facing learning platform. Its immediate implementation priority is the normal individual learner journey.
- **Learnora Teams:** a separate internal/workforce application. Course authoring operations, AI production orchestration, review, acceptance and publishing belong here in the intended product architecture.
- **Individual learner:** a self-managed learner account using the individual learner experience and the public/global catalogue according to the applicable access rules.
- **Cohort:** a managed learning environment with its own cohort-defined tracks, teams, learners and tutor assignments. Cohort teams can include tutors assigned to specific tracks created by that cohort. Cohort learner and tutor operations are not interchangeable with corporate organisation operations.
- **Corporate organisation:** a managed customer environment with its own organisational structure, teams, responsibilities, programmes and operational workflows. Do not reduce it to a generic list of members and courses.
- **Independent tutor:** a separate future account/workspace and creator workflow. It is not the same as a tutor assigned to a cohort team or corporate organisation.
- **Platform staff and administrators:** internal privileged roles with a separate trust boundary from customer accounts.

A cohort and a corporate organisation may both have teams, members, learning resources and oversight responsibilities. That surface similarity does not make their internal structures, team responsibilities, tutor relationships, assignment rules, dashboards or workflows identical.

A tutor's access must be explicitly scoped to the relevant managed environment and assigned resources. Membership in one team or assignment to one track must not imply unrestricted access to all tracks, courses, learners or administrative operations.

## 4. Current implementation sequence

The currently approved delivery sequence is:

1. Complete the **normal individual learner experience in Learnora ME**.
2. Build the separate **Learnora Teams** application and its internal course/content operations.
3. Return to **Learnora ME** to implement the corporate organisation experience.
4. Implement **independent tutor** functionality as a separate product context.

Cohort structures, existing cohort accounts, access rules, learning records and progress must be understood and preserved while the current individual learner work is completed. The sequence above is not permission to delete cohort functionality or historical records.

Do not implement deferred corporate organisation, independent tutor or Teams workflows during the individual learner phase merely because they are described in architecture documents. Shared code may be changed only when required for the individual learner journey, security, compatibility or prevention of regressions, and the reason must be documented.

## 5. AI content production and learner delivery

The intended responsibility boundary is:

- Learnora Teams owns AI-assisted course and lesson creation, production orchestration, review, acceptance and publishing.
- Learnora Teams can also manage and upload its own lesson videos and other approved learning assets.
- Normal Learnora ME is the learner-facing delivery application. It renders and serves accepted course content and associated media made available through the approved backend, Supabase and Cloudflare delivery architecture.
- Learner-facing Learnora ME must not be treated as the authoring or AI video-production environment.

Any temporary or historical placement of Course Studio functionality in Learnora ME must be labelled as an implementation state, not mistaken for the intended product boundary.

Later customer-facing authoring permissions for corporate organisation teams and independent tutors must be documented as separate capabilities with their own rules. AI production access is not implied for every tutor or organisation; it must follow an explicit product-owner decision and permission model.

## 6. Account, identity and access rules

Account identity, authentication, tenant context, membership, team membership, cohort membership, tutor assignment and resource access are related but distinct concepts.

Documentation must state explicitly:

- Which principal is signing in.
- Which account class/context that identity belongs to.
- Whether the account is individual, cohort-managed, corporate-organisation-managed, independent tutor or internal staff.
- Which managed environment the account belongs to, where applicable.
- Which teams and resources the account is assigned to.
- Which actions are permitted within each scope.
- How context is resolved and how ambiguity or conflicting memberships are handled.
- How existing accounts, progress and historical records are preserved during any future identity-model transition.

Do not infer an active customer organisation, cohort or access grant from the existence of a route, role constant, migration, schema table or historical record. Source-code capability, documented intended behaviour and verified live account/data state are different kinds of evidence and must be reported separately.

## 7. Document status labels

Every substantive specification should identify its status:

- **APPROVED:** the product owner has approved this rule or design.
- **CURRENT:** the rule is in force for the present implementation.
- **PLANNED:** approved or intended future work, not yet implemented.
- **DEFERRED:** intentionally postponed; not cancelled.
- **HISTORICAL:** retained to explain a past decision or implementation.
- **SUPERSEDED:** replaced by a named newer decision or specification.
- **PROPOSED:** a recommendation awaiting product-owner approval.
- **UNRESOLVED:** conflicting or missing information that must be clarified before implementation.

Do not describe planned, proposed or historical behaviour as live functionality. Do not describe a code path as an active user entitlement without evidence.

## 8. Required structure for feature specifications

Each substantial feature specification should cover, as applicable:

1. Purpose and intended outcome.
2. Product/application ownership.
3. In-scope and out-of-scope work.
4. Actors and account contexts.
5. Domain concepts and terminology.
6. User journeys and operational workflows.
7. Roles, permissions and resource scopes.
8. Data ownership, relationships and lifecycle.
9. API/service responsibilities and integration boundaries.
10. UI behaviour, including desktop and mobile.
11. Loading, empty, validation, error and permission-denied states.
12. Security, privacy and audit requirements.
13. Notifications and communication rules.
14. Acceptance criteria and test scenarios.
15. Dependencies, migration/compatibility concerns and release gates.
16. Status, owner decision date and references to related documents.

A specification must distinguish required behaviour from implementation suggestions. It must not invent database schema, active organisations, user assignments, metrics or production state.

## 9. How to record decisions and changes

When a product decision changes:

1. Record the decision in the product decision register.
2. State the previous rule and the new rule.
3. Explain why it changed and which product contexts it affects.
4. Identify documents that must be updated.
5. Identify code, schema, migration, data and compatibility implications without assuming those changes are authorised.
6. Update affected specifications and roadmap sequencing.
7. Mark obsolete guidance as superseded and link to the replacement; do not leave contradictory instructions appearing equally current.

Engineering history must remain historical. Do not rewrite historical entries to make the past appear consistent with a later decision.

## 10. Initial documentation reconciliation register

The following issues were identified during the documentation review on 21 November 2026. They must be resolved in the relevant specifications before implementation relies on the affected areas:

| Topic | Reconciliation required |
|---|---|
| Cohort and corporate organisation models | Document both complete operating models separately, including their team structures, tutor relationships, track ownership, assignments, dashboards and workflows. |
| Cohort teams | Specify cohort team types/responsibilities, membership, tutor inclusion, track assignment, learner relationships and permission boundaries. |
| Account identity | Reconcile historical cohort-specific login handling with the newer organisation-managed identity proposal without silently changing existing accounts or records. |
| Learnora Teams boundary | Make Teams the authoritative home of internal AI/content production, review, acceptance and publishing; identify any temporary or legacy Learnora ME implementation. |
| Delivery sequence | Align older roadmap and learner-journey documents with the currently approved individual learner → Teams → corporate organisation → independent tutor sequence. |
| Customer authoring | Separately specify future corporate-team authoring, cohort tutor capabilities and independent tutor capabilities. Do not assume they share permissions or AI access. |
| WitStart | Treat it as a historical example/context unless current product-owner-approved evidence says otherwise. Preserve historical records and migrations; do not imply an active product organisation or grant. |
| Live state vs intended design | Clearly label repository code observations, documented target architecture and verified live Supabase/Vercel state as separate evidence categories. |
| Conflicting audit reports | Reconcile overlapping scalability and security reports, retaining dated findings and recording which observations remain current. |
| Database/migration status | Maintain a single current migration reconciliation record and do not treat old audit snapshots as current live state. |

This register is a work queue, not a claim that the listed architecture has already been fully specified or implemented.

## 11. Reading and implementation rule

Before changing a feature, the implementer must:

1. Read this guide.
2. Read [PRODUCT_DECISIONS.md](PRODUCT_DECISIONS.md), the authoritative cross-product decision register.
3. Read the complete specification for the relevant product context.
4. Read the applicable workflow, security, data and operational documents.
5. Check the reconciliation register for unresolved conflicts.
6. Inspect code and tests only after the intended behaviour is clear.
7. Record any newly discovered mismatch between documentation and implementation.

If a required decision is unresolved, stop at that boundary and ask for clarification rather than guessing.

## 12. Document inventory

The documents in this directory are grouped by purpose:

- **Product governance and decisions:** this guide and [PRODUCT_DECISIONS.md](PRODUCT_DECISIONS.md).
- **Product architecture and requirements:** account/organisation architecture, product engineering specification, AI course production/media architecture.
- **Learner experience:** learner journey phases, learner outcomes, public catalogue/SEO, learner notifications/marketing automation.
- **Delivery and commercial strategy:** free launch/paid expansion, roadmap, initial pilot course production briefs.
- **Security and reliability:** backend security hardening, security/reliability review, shared rate-limit rollout, scalability audits.
- **Data and operations:** active Pheonix migration reconciliation, R2 video bucket setup, Gmail API setup, track review schema proposal.
- **Design research:** Learnora UI/UX research and design decisions.
- **Engineering history:** engineering history and decisions.

This inventory is an orientation aid. The status and authority rules above determine which document controls when content overlaps.
