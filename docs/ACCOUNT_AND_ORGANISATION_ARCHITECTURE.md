# Account, Organisation and Cohort Architecture

**Status:** Replacement architecture documented after source audit; implementation not yet changed.  
**Repository:** `Obikpe/Learnora-ME`  
**Audited branch:** `main`  
**Audit snapshot:** 4 November 2026  
**Scope:** Authentication identity, organisation-managed accounts, cohorts, tutors, course visibility, access control, WitStart retirement and account lifecycle.

---

## 1. Decisions and non-negotiable rules

1. **One email address represents one account identity and one account context at a time.** The same email must never authenticate as an individual learner in one flow and an organisation learner in another, nor as separate cohort accounts in different cohorts.
2. **Organisation-managed and independent Learnora accounts are mutually exclusive.** An organisation learner who wants to become an independent Learnora learner must first have their organisation-managed account closed/released through an authorised organisation process. Only after the release is complete may the email register as an individual account.
3. **An account belongs to one account class and, when organisation-managed, one organisation context.** Cohorts, tracks and tutor assignments are resource scopes inside that context; they are not separate login identities.
4. **No silent identity fallback.** A failed password for one account class must never cause the server to try another account table and authenticate the same email through a different identity.
5. **Organisation learners are not individual catalogue users.** They see only organisation-owned or organisation-assigned content and only courses assigned to their cohort/track or explicitly granted to their organisation account. They do not receive public catalogue discovery.
6. **Organisation access is enforced by the API and database policies**, not by frontend routing or hidden navigation.
7. **Cohort course configuration is track-first.** An organisation admin assigns courses to cohort tracks once. A learner assigned to a track inherits the active courses configured for that track. The current repeated per-learner course assignment workflow is to be removed from the normal path.
8. **A learner's track is fixed for the lifetime of that cohort.** A different track requires a new cohort membership/cohort, not an in-place reassignment.
9. **Organisation tutors are organisation-managed accounts.** They can create courses and view learner performance only within the organisation, cohort, track and course scopes assigned to them.
10. **Independent Learnora tutors remain a separate account class** and must not be granted organisation data or organisation course access.
11. **Platform administrators and internal staff remain separate privileged trust boundaries.** Removing organisation-specific legacy roles must not weaken platform administration.
12. **WitStart is retired from active product behaviour.** Do not delete, rewrite, migrate, or otherwise modify existing WitStart database rows or already-applied historical migrations.
13. Preserve the existing free-launch behaviour and reversible paid subscription/Paystack implementation. Do not remove billing code as part of account cleanup.

## 2. Account classes and identity boundary

The target model has one exclusive account class for a canonicalised email address:

| Account class | Purpose | Permitted scope |
|---|---|---|
| Individual learner | Self-registered Learnora learner | Public Learnora catalogue, personal enrolments and individual learning |
| Organisation-managed | Learner, organisation owner/admin, or organisation tutor provisioned/invited by one organisation | One organisation; assigned cohorts, tracks, courses and organisation workspaces |
| Independent tutor | Tutor using Learnora independently | Independent creator/tutor workspace and own creator resources |
| Platform administrator / internal staff | Platform operations | Explicit platform/internal permissions only |

An email cannot hold two of these account classes simultaneously. In particular:

- An organisation-managed learner cannot create or use an individual learner account with the same email.
- An organisation-managed tutor is not also an independent creator account.
- A cohort is not a separate account class. A cohort learner is an organisation-managed account with one or more cohort memberships within that same organisation.
- A user cannot have active organisation memberships in multiple organisations. The target is one active organisation boundary per email/account.
- Account class is resolved at registration/provisioning and stored as authoritative server-side state. It is not inferred from a frontend route, a client-provided role, a JWT claim alone, or the order in which tables happen to be queried.

### Canonical email

All account creation, invitation, lookup and release operations use a single normalisation function (trim whitespace, lowercase, validate syntax). The database must enforce uniqueness against the canonical email identity, including across individual, organisation-managed, independent-tutor and cohort-era records during migration. Case-insensitive application checks alone are not sufficient to prevent concurrent duplicate creation.

## 3. Authentication and registration

### 3.1 Individual registration

1. Validate and canonicalise email.
2. Check the authoritative identity registry and all legacy account sources covered by the compatibility guard.
3. If any active, pending, invited, suspended-but-retained, or otherwise reserved organisation-managed identity exists, reject individual registration with a safe explanation: the organisation must release the account first.
4. If an individual or independent-tutor identity already exists, do not create another account.
5. Create a pending individual learner identity and run the existing email verification flow. The existing free-launch and paid entitlement history remains intact.

The public registration endpoint must never create an individual account simply because it failed to find an email in one table.

### 3.2 Organisation provisioning and invitations

1. An organisation admin enters an email and selects the organisation role (learner, tutor/instructor, admin, or owner subject to existing permission constraints).
2. The backend checks the global identity boundary before issuing an invitation.
3. If the email already belongs to an individual learner, independent tutor, platform administrator, or another organisation, provisioning is rejected. The organisation must not silently take over that identity.
4. For a new email, create a pending organisation-managed identity reservation tied to exactly one organisation. The invitation is single-use, expiring, and bound to that email and organisation.
5. The recipient activates the organisation-managed account and establishes credentials. The email is reserved globally for that account class.
6. Re-inviting an existing organisation account within the same organisation updates the invitation or membership state; it does not create a second identity.

Organisation invitation is not equivalent to creating an individual Learnora account. The organisation controls the account's learning scope for as long as the organisation-managed identity remains active.

### 3.3 Cohort learner provisioning

- A cohort learner is provisioned under the organisation-managed identity for the organisation that owns the cohort.
- The cohort roster links to the organisation-managed account identity; it must not create a new login identity for each cohort.
- Cohort login should move from the separate username-only credential path to the single canonical email identity, while preserving secure activation and rate limiting.
- The same organisation-managed account can participate in cohort resources belonging to its one organisation, subject to membership rules. It cannot be re-created under a second cohort with a second username/password identity.
- Existing cohort records and progress must be reconciled without deleting or rewriting historical learning evidence.

### 3.4 Login resolution

The login endpoint performs one deterministic identity resolution:

1. Canonicalise the supplied email.
2. Resolve the unique account identity and its account class from the authoritative identity registry.
3. Verify the password only against that resolved account.
4. Verify account status, email verification/activation, organisation status and applicable cohort state.
5. Issue a token with immutable identity ID and account class; revalidate revocation and status on protected requests.
6. Return the single authorised workspace destination.

If no identity exists, return a generic invalid-credentials response. If an identity exists but the password is wrong, do not query a second account class as fallback. If duplicate legacy identities are detected, fail closed and log a security/repair event rather than selecting whichever table returns first.

Platform-admin/internal authentication remains a separately guarded flow and cannot be reached by learner account fallback.

## 4. Organisation account release and conversion to individual use

An organisation learner who wants independent Learnora access must use an explicit **organisation account release** lifecycle. The public individual registration endpoint cannot perform this conversion automatically.

### Required release sequence

1. A release is requested by the learner or initiated by an authorised organisation admin, according to the organisation's policy.
2. The backend verifies the actor's authority and the exact organisation/account relationship.
3. The organisation admin confirms release, or the configured organisation offboarding policy authorises it. The learner cannot bypass this by changing email case, using a second login route, or registering before release.
4. Revoke active sessions, refresh tokens, activation links and outstanding invitation tokens for the organisation identity.
5. Remove active cohort memberships and organisation entitlements; mark the organisation account as released/closed. Do not delete the organisation, cohort, audit or historical learning evidence records.
6. Preserve learner progress and assessment evidence according to the product's retention policy, detached from active organisation access. Historical organisation reports must retain their provenance and must not become visible to the new individual account unless a separately authorised transfer policy is defined.
7. Release the canonical email reservation only after the state transition has committed successfully and all active access paths are revoked.
8. The user may then register a new individual account and verify the email. The new identity receives no inherited organisation course access, organisation tutor permissions, organisation role, or organisation sessions.

**Atomicity:** The release operation must be transactional (or implemented through a durable state machine/outbox with a fail-closed intermediate state). There must be no interval in which both the organisation identity and a new individual identity can authenticate. If any required revocation or state update fails, keep the email reserved and the account inaccessible until recovery completes.

**Data retention:** "Delete organisation account" means close/release the operational identity and its active access. It does not mean cascading deletion of audit logs, cohort records, assessment evidence, certificates, billing records or organisation-owned content. Any true erasure request is a separate privacy workflow with its own legal and retention checks.

## 5. Organisation, cohort and tutor model

### 5.1 Organisation roles

Remove legacy product-specific administrator/learner roles. Use generic organisation roles:

- Owner
- Admin
- Tutor / Instructor
- Learner

Role names alone are insufficient for tutor access. Tutor permissions require resource assignments and organisation scoping.

### 5.2 Cohort and track configuration

1. Organisation admin creates a cohort.
2. Admin creates/selects organisation tracks and enables the tracks offered in the cohort.
3. Admin assigns published courses to each cohort track.
4. Admin provisions/invites learners and assigns exactly one active track per learner per cohort.
5. Learners automatically inherit all active courses assigned to their cohort track.
6. Admin updates track course configuration centrally; the learner's available course list updates from that configuration.
7. Track assignment is immutable after cohort participation begins. A learner changing programmes joins a new cohort or a new explicitly modelled cohort instance.

The normal learner workflow must not require admins to assign the same course individually to every learner. Individual exceptions should not be supported unless a later product decision explicitly requires them and the exception is auditable.

### 5.3 Organisation-owned courses

- An organisation tutor may create courses only inside their organisation.
- A newly created organisation course is private to that organisation by default.
- It is not added to the public Learnora catalogue and is not discoverable by other organisations.
- An organisation admin may publish/assign it within that organisation and select it for one or more cohort tracks.
- Every course read, lesson read, assessment, enrolment, search result, recommendation, AI tutor context and media URL must enforce ownership/assignment server-side.

### 5.4 Tutor assignment and performance visibility

- An organisation tutor must be an active tutor/instructor member of the same organisation.
- Admin assigns tutor to one or more cohort tracks and/or specific courses within those tracks.
- Tutor course authoring, learner roster, submissions, grades, progress, analytics and exports are restricted to the assigned resource scope.
- A tutor assigned to Track A cannot see Track B learners or reports merely because both tracks belong to the same organisation.
- A tutor cannot query another organisation by changing a path ID, query parameter, header or request body.
- Organisation admins retain organisation-wide oversight according to role permissions.
- Independent Learnora tutors see only their own creator workspace and explicitly authorised learner interactions.

## 6. Course discovery and access matrix

| Account class | Public catalogue discovery | Organisation catalogue | Cohort/track courses | Tutor workspace |
|---|---:|---:|---:|---:|
| Individual learner | Yes | No | No | No |
| Organisation learner | No | Own organisation only, assigned/visible courses | Assigned track only | No |
| Organisation tutor | No general public discovery | Own organisation only | Assigned track/course only | Assigned resources only |
| Organisation admin/owner | No learner catalogue access by default | Manage own organisation | Manage own cohorts/tracks | Oversight and assignment |
| Independent tutor | Public creator discovery as permitted | No | No | Own creator resources |
| Platform/internal admin | Explicit administrative interfaces only | Only with explicit platform permission | Only with explicit platform permission | Operational permissions only |

All rows are enforced in API services and database policies. Frontend redirects, conditional navigation and catalogue filtering are usability layers, not security controls.

## 7. Source audit: current implementation findings

The following is a source-level audit of the current `main` snapshot. It is not a live database audit. No database rows or live schema were queried or changed.

### 7.1 Authentication and identity

**Files inspected**
- `backend-python/routers/auth.py`
- `backend-python/routers/account_lifecycle.py`
- `backend-python/routers/permissions.py`
- `backend-python/routers/organisation_members.py`
- `backend-python/routers/cohort_learners.py`
- `backend-python/routers/internal_auth.py`

**Findings**
- `auth.py` still documents and supports learner roles `normal` and `witstart`, plus administrator role `witstart_admin`.
- `allowed_for()` still grants product-specific legacy permissions and redirect paths.
- The main `users` identity is separate from `cohort_accounts`; cohort JWTs are resolved in a separate branch of `get_current_user()`.
- Cohort login currently uses a username/password endpoint, while the main login uses email/password.
- Cohort learner provisioning checks email only inside the same cohort. That does not provide a global email uniqueness guarantee across cohorts, individual accounts or organisation identities.
- Organisation membership currently attaches a `public.users` user through `organisation_members`. This means an individual-style identity can also be treated as an organisation learner/member, contrary to the new exclusive account-context rule.
- Organisation membership lookup is case-insensitive and protected against LIKE wildcard matching, but table-local lookup is not a substitute for cross-account-class uniqueness.
- `organisation_members.py` currently adds an existing user by `user_id`; it does not implement the complete pending invitation/account reservation lifecycle required above.
- `account_lifecycle.py` contains checks against active organisation membership, but this does not yet constitute a complete release protocol with atomic email reservation, session revocation and controlled re-registration.
- Platform administrator and internal staff paths are distinct and must remain distinct.

### 7.2 Organisation and cohort management

**Files inspected**
- `backend-python/routers/organisations.py`
- `backend-python/routers/cohort_learners.py`
- `backend-python/routers/cohort_learning.py`
- `backend-python/services/cohort_membership.py`
- `backend-python/routers/learning_structure.py`

**Findings**
- The current cohort model already supports organisation-owned cohorts, track options, cohort membership, fixed learner track IDs and cohort-specific course assignments.
- Cohort learner accounts are currently stored in `cohort_accounts` and linked to `cohort_members` by `cohort_account_id`; they do not require a `public.users` or `organisation_members` row.
- This is a useful tenant-isolation foundation, but account creation per cohort conflicts with the new global one-email/one-account rule.
- The cohort learner provisioning path creates a separate username and activation flow for each cohort account.
- The cohort learning service already derives course access from the learner's assigned track and the cohort-track course mapping in some routes.
- The organisation dashboard currently describes and implements individual learner course/lesson-plan/tutor assignments after track-level course setup. This duplicates configuration and conflicts with the new track-inheritance rule.
- Tutor assignment currently checks that the tutor is an active organisation member, but resource-scoped tutor assignment must be enforced consistently across all reporting and content routes.
- `cohort_members` has both `user_id` and `cohort_account_id` pathways. Migration must converge to one canonical organisation-managed identity reference without losing historical records.

### 7.3 Course access, catalogue and content

**Files inspected**
- `backend-python/routers/course_access.py`
- `backend-python/routers/course_content.py`
- `backend-python/routers/courses.py`
- `backend-python/services/access.py`
- `backend-python/routers/creator.py`

**Findings**
- Organisation course grants use `course_access` and organisation IDs.
- `course_content.py` contains legacy role checks for `witstart` and separate cohort-account handling; the course-access logic needs consolidation around exclusive account class and explicit resource scope.
- `courses.py` checks organisation and cohort membership to restrict public course recommendations. This is currently a mixed-context check, not the target mutually exclusive identity model.
- Organisation-owned course visibility and course grants must be consistently applied to listing, detail, lesson, assessment, media, AI and search endpoints.
- Independent creator accounts are stored in `learnora_creator_accounts`; they are associated with the current Learnora user identity. This must not be treated as an organisation tutor capability.
- Tutor performance access needs an end-to-end scope audit, not just a check that the requester has an instructor role.

### 7.4 Frontend

**Files inspected**
- `frontend-v02/app/login/page.tsx`
- `frontend-v02/app/register/page.tsx`
- `frontend-v02/app/cohort-login/page.tsx`
- `frontend-v02/app/dashboard/page.tsx`
- `frontend-v02/app/dashboard/organisation/page.tsx`
- `frontend-v02/app/dashboard/cohort/page.tsx`
- `frontend-v02/components/dashboard/Sidebar.tsx`
- `frontend-v02/lib/api/auth.ts`
- `frontend-v02/lib/api/client.ts`
- Legacy `frontend/app/dashboard/admin/witstart_admin/page.tsx` and `frontend/app/dashboard/witstart/page.tsx` were located in the repository tree.

**Findings**
- The login page supports a separate cohort login route and then resolves organisation memberships from the normal user profile.
- The normal dashboard uses organisation membership and legacy role checks to infer assigned-only access.
- The organisation dashboard loads public course catalogue data and offers a per-learner course/lesson-plan/tutor assignment workflow.
- The sidebar/dashboard still include legacy role checks.
- A dedicated WitStart route exists in the active app tree, although the current frontend-v02 page is only a small placeholder. A separate older frontend contains legacy WitStart admin and learner routes.
- Frontend organisation context is stored in local storage and sent as an organisation header. This is acceptable only as a requested context selector where the server independently proves membership; it must not allow multiple active organisation identities under the new rule.

### 7.5 Tests

**Files inspected**
- `backend-python/tests/test_auth_email_lookup_security.py`
- `backend-python/tests/test_organisation_member_lifecycle.py`
- `backend-python/tests/test_cohort_login_security.py`
- `backend-python/tests/test_cohort_membership_guards.py`
- `backend-python/tests/test_course_access_guards.py`
- `backend-python/tests/test_instructor_assignment_workspace.py`
- `backend-python/tests/test_account_lifecycle.py`
- `backend-python/tests/test_frontend_security_contracts.py`

**Findings**
- Existing tests cover email lookup hardening, cohort login rate limits, membership lifecycle, course access guards and instructor assignment workspace.
- The instructor workspace tests currently model an instructor with organisation membership rows in more than one organisation, which must be changed under the one-organisation identity boundary.
- New regression coverage is required for cross-table email uniqueness, duplicate legacy identities, organisation invitation reservation, account release, release-vs-registration races, cohort reuse of one organisation identity, public catalogue denial, organisation course privacy and tutor track-level reporting boundaries.

### 7.6 Documentation and schema inventory

The audit located product/engineering documentation in `docs/`, migration plans and schema comparisons in `backend-python/migrations/`, a Supabase baseline, historical migration scripts and current migrations.

- Existing product and engineering docs contain historical product-specific account assumptions that must be reconciled with this architecture.
- Existing legacy migrations include the original organisation/identity bridge and product-specific pilot history.
- Historical migrations and already-applied migration files are immutable audit history for this cleanup. Do not edit them to make the repository appear as if the old model never existed.
- Current schema baselines and migration verification scripts must be inspected before designing any schema migration.
- The Supabase baseline and migration inventory are source artifacts, not permission to execute SQL or mutate live records.

### 7.7 Audit limits

- The repository tree was enumerated recursively on `main` (4,629 entries; GitHub reported the tree was not truncated).
- Core backend authentication, permissions, organisation, cohort, course access and creator files were inspected, along with the listed frontend entry points and targeted tests.
- This audit is not yet a complete line-by-line review of every one of the 4,629 repository entries. The full implementation cleanup must continue with a repository-wide literal/symbol search, then inspect every matching active source file and every affected test before code changes.
- No tests, builds, deployments, CI workflows, SQL migrations or database operations were run as part of this documentation pass.

### 7.8 Additional schema and lifecycle findings

The read-only source inspection was extended to the relevant Supabase schema baseline and migration files:

- `supabase/baselines/active-pheonix-public-schema.sql` records a separate `cohort_accounts` table. Its email is scoped by a unique `(cohort_id, email)` constraint, with only a non-unique lower-email lookup index. This permits the same canonical email in more than one cohort and does not provide a global identity reservation.
- The same baseline shows `cohort_members` can point to either `user_id` or `cohort_account_id`, and the learning evidence table `cohort_account_lesson_progress` is keyed to the cohort account. This is the historical split that the future migration must reconcile without losing progress.
- `supabase/migrations/20261021112845_cohort_account_track_assignment.sql` explicitly creates cohort-specific credentials and unique email only within each cohort. It also establishes track-scoped course mappings and immutable cohort track assignment.
- `supabase/migrations/20261021113310_allow_cohort_only_membership.sql` deliberately allows cohort-only identities, while the legacy-user path requires an active learner organisation membership. This is a valid historical compatibility rule but not the final one-identity model.
- `supabase/migrations/20261102130000_learner_account_deletion.sql` implements deletion for users whose role is `normal`. It blocks deletion of an active organisation owner, suspends active organisation memberships and team memberships, anonymises the email and clears credentials. It is **not** an organisation-account release workflow: it does not require an organisation release approval, does not cover `cohort_accounts`, and its function does not explicitly deactivate `cohort_members` rows for the user. This must be reconciled before the new release flow can safely reuse or replace it.
- The current baseline includes both `cohort_track_courses` (track-level configuration) and `cohort_member_course_assignments` / `cohort_member_lesson_assignments` (per-learner exceptions). The normal product flow should derive learner course access from the track mapping; any legacy individual assignment rows must be inventoried and preserved before the per-learner UI/path is retired.
- The baseline includes `learnora_creator_accounts`, creator ownership and finance tables, so independent creator identity and creator commercial data must be handled separately from organisation tutor membership.
- `supabase/legacy_migrations/002_learnora_v1_foundation.sql` and `003_learnora_identity_bridge.sql` document the historical organisation bridge and cohort membership for the former pilot. These files are historical and must remain untouched.
- `docs/PRODUCT_ENGINEERING_SPEC.md` currently describes cohort-specific identities as intentionally distinct from `public.users`; that statement is superseded by this architecture. The roadmap and engineering history also retain historical role and migration notes; update current-state guidance without erasing the audit trail.
- The legacy `backend-python-v0/` and `frontend/` trees still contain product-specific role and route implementations. The current `backend-python/` and `frontend-v02/` trees are the primary implementation surfaces identified for this work, but deployment/configuration references must be checked before deciding whether the older trees are inert, archival or still consumed by any workflow. Do not delete them based on directory naming alone.

These findings make the global email uniqueness and account-release work a schema-level prerequisite. An application-only pre-check cannot close races between individual registration and organisation/cohort provisioning.

## 8. Target data model and migration direction

The final schema must enforce a globally unique canonical email identity and one account class. The exact DDL is deferred until the current live schema and all relevant migration dependencies have been reconciled.

The likely target is a canonical account identity record with:
- immutable account ID;
- canonical email and verified-email state;
- exclusive account class;
- account lifecycle status (invited, pending activation, active, suspended, released/closed);
- credential reference/hash or provider identity;
- organisation ID for organisation-managed accounts only;
- timestamps and security/audit metadata.

Organisation membership/roles should be account attributes or scoped relationships under the single organisation, not an additional independent identity. Cohort membership should reference the canonical organisation account ID. A cohort account must not be created as a second identity for the same email.

Before implementation, inspect the live schema and baseline to determine whether this can be achieved by safely extending existing tables or requires a new identity registry. Do not assume a proposed table exists. Do not modify any existing WitStart rows. Use additive, reversible migrations with explicit compatibility and verification steps; never rewrite applied migration history.

## 9. Implementation sequence after this architecture

1. **Repository-wide audit completion:** search all active code, tests, docs, configuration and route trees for legacy product-specific roles, names, redirects, permissions and identity paths. Classify historical migration references separately.
2. **Schema reconciliation:** compare the current Supabase baseline, migration history, verification scripts and live schema read-only. Identify uniqueness constraints, foreign keys, RLS policies, token/session storage and all references to `users`, `cohort_accounts`, `organisation_members` and `cohort_members`.
3. **Identity guard:** implement one canonical email resolver and a database-enforced uniqueness/reservation strategy. Fail closed on duplicate legacy identities.
4. **Organisation invitation lifecycle:** implement invite, activation, re-invite, revoke, suspend, offboard and release states without creating individual learner identities.
5. **Cohort identity convergence:** make cohort memberships reference one organisation-managed account; move authentication to canonical email; preserve old account/progress data through a verified compatibility migration.
6. **Account release:** implement atomic release, session/token revocation, evidence retention and safe independent registration after release.
7. **Role and permission cleanup:** remove legacy product-specific role/permission branches from active application code; retain generic organisation roles and platform trust boundaries.
8. **Track-first cohort access:** make track course configuration the authoritative source of learner course access and remove the repeated individual assignment workflow.
9. **Organisation tutor scoping:** enforce organisation + assigned track/course constraints for course authoring, rosters, performance, reports and exports.
10. **Course visibility hardening:** verify organisation ownership/assignment on every catalogue, course, lesson, assessment, media, AI and search path.
11. **Frontend cleanup:** remove legacy routes and context inference; provide distinct, clear login/activation journeys and account-release messaging.
12. **Tests and static verification:** add focused regression tests and run a small, merged test selection. Do not trigger unnecessary GitHub Actions or Vercel deployments.

## 10. Explicit preservation and operational constraints

- Work on `main` as directed.
- Do not deploy to Vercel.
- Do not trigger deployments or CI workflows.
- Avoid broad test runs; merge related tests and use focused local/static checks.
- Do not execute SQL or change the live database without explicit authorisation.
- Do not delete, rewrite or mutate existing WitStart database records.
- Do not rewrite historical applied migrations. Historical references may remain in immutable migration history and audit records.
- Retain the shared cohort model and its security controls while converging account identity.
- Retain existing paid subscription, Paystack cancellation and free-launch implementation.
- Do not weaken platform-admin or internal-staff security boundaries.
- Do not claim implementation is complete based on documentation or static inspection alone.

---

**Current state:** Architecture documented. No application implementation, schema, database data, deployment or CI workflow has been changed by this pass.
