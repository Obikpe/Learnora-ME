# Account, Organisation and Cohort Architecture

**Status:** Historical source audit and proposed architecture; target identity decisions remain partly unresolved.  
**Repository:** `Obikpe/Learnora-ME`  
**Audited branch:** `main`  
**Audit snapshot:** 4 November 2026; later implementation notes are individually dated below.  
**Scope:** Authentication identity, organisation-managed accounts, cohorts, tutors, course visibility, access control, WitStart retirement and account lifecycle.

---

## Immediate implementation scope — 4 November 2026

The account and tenant architecture above is the long-term contract, not a request to finish the entire multi-tenant product in this pass.

**The current implementation priority is the normal individual Learnora learner journey in Learnora ME (`frontend-v02/`).** The product must become usable end-to-end for an individual learner first:

1. Registration, email verification, resend verification, sign-in, sign-out, password recovery/reset and change-password.
2. Reliable HttpOnly-cookie session establishment, revalidation, expiry handling and safe redirects.
3. Learner onboarding and profile data.
4. Public published-course and global-track discovery, detail, enrolment and course access.
5. The My Learning dashboard: actual enrolled courses, resume/continue learning, course and track progress, learning time/streak, activity, evidence, projects, skills and certificates.
6. Lesson content/media, notes, quizzes, assignments, submissions and completion rules already in scope.
7. Correct loading, empty, retry and error states; responsive desktop/mobile behaviour.

### Explicitly deferred

Do not attempt to complete the organisation portal, organisation invitations, organisation-managed account revocation/deletion UI, organisation admin/cohort management, track-scoped tutor workspaces, independent tutor onboarding/creator tools, creator finance/payouts, or the full cross-identity migration now. Keep their existing code/schema and the documented future architecture intact; do not delete or weaken their boundaries.

For this pass, make only the compatibility and security changes needed to ensure that normal individual learner registration/sign-in cannot accidentally create or authenticate a second identity where a reserved organisation/cohort identity already exists. Preserve existing cohort accounts and progress. Do not convert or migrate historical cohort identities as part of the individual learner release.

Learnora Teams is not the focus of this learner-flow implementation. Its internal staff/platform-admin trust boundary must remain unaffected.

### Delivery rule

Implement the individual learner path as one coherent vertical slice across backend authentication, account provisioning guards, individual course/progress access and the Learnora ME frontend. Review cohort/organisation/creator paths where they share those services, but change them only when required to prevent a regression or preserve a future-safe contract. Do not build the deferred workflows merely because the architecture describes them.

## 1. Earlier proposed identity and access rules — target model not yet approved

**Authority warning:** Sections 1–3 below retain earlier proposed identity and access architecture and must be read only where consistent with current approved decisions. They are not, by themselves, the final target model. Section 4 has been replaced with the current approved organisation/cohort account revocation and deletion rule. [PRODUCT_DECISIONS.md](PRODUCT_DECISIONS.md) governs cross-product decisions. The two-way email exclusivity rule is approved; the canonical identity registry, legacy conflict reconciliation and migration design remain unresolved. Cohorts must not be reduced to a generic organisation resource scope; their separate domain model remains governed by the cohort specifications. Do not implement identity convergence or migration without an approved preservation and transition plan.

## 1.1 Identity and access invariants — historical proposal, subject to current approved decisions

1. **One email address represents one account identity and one account context at a time.** The same email must never authenticate as an individual learner in one flow and an organisation learner in another, nor as separate cohort accounts in different cohorts.
2. **Organisation-managed and individual Learnora accounts are mutually exclusive by email.** An email associated with an organisation/cohort-managed account cannot be used for an individual learner account, and an email associated with an individual learner account cannot be used for an organisation/cohort-managed account. Under the current approved lifecycle, revoking organisation/cohort access deletes the managed account and its associated data; after deletion, the email is no longer reserved by that account and may be used through the normal registration/invitation checks.
3. **An email has one mutually exclusive account context at a time.** Cohorts, tracks and tutor assignments are resource scopes inside the organisation-managed context; they are not separate login identities. An individual learner identity and an organisation/cohort-managed identity must never coexist for the same email.
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

## 2. Earlier proposed account classes and identity boundary

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

All account creation, invitation, lookup and account-deletion operations use a single normalisation function (trim whitespace, lowercase, validate syntax). The database must enforce uniqueness against the canonical email identity, including across individual, organisation-managed, independent-tutor and cohort-era records during migration. Case-insensitive application checks alone are not sufficient to prevent concurrent duplicate creation.

## 3. Earlier proposed authentication and registration model

### 3.1 Individual registration

1. Validate and canonicalise email.
2. Check the authoritative identity registry and all legacy account sources covered by the compatibility guard.
3. If any active, pending, invited, suspended-but-retained, or otherwise reserved organisation-managed identity exists, reject individual registration with a safe explanation: the organisation-managed account must first be deleted through the authorised organisation access-revocation process.
4. If an individual or independent-tutor identity already exists, do not create another account.
5. Create a pending individual learner identity and run the existing email verification flow. The existing free-launch and paid entitlement history remains intact.

The public registration endpoint must never create an individual account simply because it failed to find an email in one table.

### 3.2 Organisation provisioning and invitations

1. An organisation admin enters an email and selects the organisation role (learner, tutor/instructor, admin, or owner subject to existing permission constraints).
2. The backend checks the global identity boundary before issuing an invitation.
3. If the email already belongs to an individual learner, independent tutor, platform administrator, or another organisation, provisioning is rejected. The organisation must not silently take over that identity. The reverse restriction also applies: an email already associated with an organisation/cohort-managed identity cannot register as an individual learner.
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

## 4. Organisation-managed account revocation and deletion — current approved rule

**Authority:** PD-012 in [PRODUCT_DECISIONS.md](PRODUCT_DECISIONS.md), clarified 21 November 2026. This section replaces the earlier account-release proposal in this document.

An organisation/cohort-managed learner or tutor whose access is revoked has their managed account deleted together with its associated learner/tutor data. Revocation is not merely a membership suspension, soft deactivation or account release that preserves personal learning history.

The email identity is exclusive across account contexts:
- An email already associated with an organisation/cohort-managed account cannot be used for an individual Learnora learner account.
- An email already associated with an individual learner account cannot be used for an organisation/cohort-managed account.
- Once the organisation/cohort-managed account is deleted, that account no longer reserves the email. The email may then be used for a new account through the ordinary registration/invitation checks.
- No account data, progress, role, entitlement or history is transferred to the new account.

The deletion must remove the managed identity's associated learner/tutor data and revoke sessions, tokens, invitations and other access paths. Shared platform or organisation-owned resources must not be deleted merely because the person interacted with them; personal attribution may need to be detached. The precise dependent-record inventory, atomic deletion and failure handling, non-identifying security audit evidence, backup/log/processor expiry and any narrowly required legal/financial exceptions must be specified before implementation.

The earlier proposal to preserve organisation learner progress and assessment evidence, close/release the account while retaining that data, and then allow the email to register individually is **superseded**. Do not implement that earlier proposal.

The separate 30-day recovery and erasure rule documented for individual learner self-service deletion applies to individual learner accounts only. It must not be assumed to apply to organisation/cohort-managed account revocation.

## 5. Organisation, cohort and tutor model — incomplete domain specification

The following sections contain an earlier organisation-centred model and source audit. They do not fully specify the cohort product. Cohorts have their own teams; those teams can include tutors assigned to tracks created by that cohort, as well as learners and other cohort-specific operations. Cohort and corporate organisation team structures, responsibilities, tutor relationships, dashboards, assignments and permissions must be documented separately. The detailed cohort team model remains unresolved under UR-001. Do not assume that the organisation admin/team workflow below is the cohort workflow.

### 5.1 Organisation roles

Remove legacy product-specific administrator/learner roles. Use generic organisation roles:

- Owner
- Admin
- Tutor / Instructor
- Learner

Role names alone are insufficient for tutor access. Tutor permissions require resource assignments and organisation scoping.

### 5.2 Earlier proposed organisation-owned cohort and track configuration

The following sequence is retained as an earlier proposal for an organisation-owned cohort arrangement. It is not a complete or approved definition of every cohort context; confirm the cohort's actual owner, teams and operating model before relying on it.

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
- The instructor workspace tests currently model an instructor with organisation membership rows in more than one organisation. Whether one organisation-managed identity may belong to more than one customer organisation is not settled by the approved two-way email exclusivity rule; do not change this behaviour or enforce a one-organisation limit solely on the basis of the earlier proposal in Sections 1–3. Resolve the organisation-membership cardinality before that future workflow is implemented.
- New regression coverage is required for two-way email identity exclusivity, duplicate legacy identity handling, organisation invitation reservation, managed-account deletion and delete/re-registration races, cohort identity compatibility, public catalogue denial, organisation course privacy and tutor track-level reporting boundaries.

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

- `supabase/baselines/active-pheonix-public-schema.sql` records a separate `cohort_accounts` table. Its email is scoped by a unique `(cohort_id, email)` constraint, with only a non-unique lower-email lookup index. The schema therefore permits the same canonical email in more than one cohort. This is a historical schema capability, not an approved product rule: whether one managed identity may participate in more than one cohort or customer organisation remains unresolved. The separate approved rule is that an individual learner email and an organisation/cohort-managed email cannot coexist across those two account contexts.
- The same baseline shows `cohort_members` can point to either `user_id` or `cohort_account_id`, and the learning evidence table `cohort_account_lesson_progress` is keyed to the cohort account. This is the historical split that the future migration must reconcile without losing progress.
- `supabase/migrations/20261021112845_cohort_account_track_assignment.sql` explicitly creates cohort-specific credentials and unique email only within each cohort. It also establishes track-scoped course mappings and immutable cohort track assignment.
- `supabase/migrations/20261021113310_allow_cohort_only_membership.sql` deliberately allows cohort-only identities, while the legacy-user path requires an active learner organisation membership. This is a valid historical compatibility rule but not the final one-identity model.
- `supabase/migrations/20261102130000_learner_account_deletion.sql` is a historical implementation observation for individual accounts whose role was `normal`. It blocks deletion of an active organisation owner, suspends active organisation memberships and team memberships, anonymises the email and clears credentials. It does not implement the currently approved organisation/cohort-managed account deletion outcome and does not cover `cohort_accounts`. Do not reuse its retention or anonymisation behaviour as the managed-account target. The approved target is deletion of the managed account and associated data on access revocation; the exact dependent-record inventory and safe erasure design remain unresolved.
- The current baseline includes both `cohort_track_courses` (track-level configuration) and `cohort_member_course_assignments` / `cohort_member_lesson_assignments` (per-learner exceptions). The normal product flow should derive learner course access from the track mapping; any legacy individual assignment rows must be inventoried and preserved before the per-learner UI/path is retired.
- The baseline includes `learnora_creator_accounts`, creator ownership and finance tables, so independent creator identity and creator commercial data must be handled separately from organisation tutor membership.
- `supabase/legacy_migrations/002_learnora_v1_foundation.sql` and `003_learnora_identity_bridge.sql` document the historical organisation bridge and cohort membership for the former pilot. These files are historical and must remain untouched.
- `docs/PRODUCT_ENGINEERING_SPEC.md` currently describes cohort-specific identities as intentionally distinct from `public.users`; that statement is superseded by this architecture. The roadmap and engineering history also retain historical role and migration notes; update current-state guidance without erasing the audit trail.
- The legacy `backend-python-v0/` and `frontend/` trees still contain product-specific role and route implementations. The current `backend-python/` and `frontend-v02/` trees are the primary implementation surfaces identified for this work, but deployment/configuration references must be checked before deciding whether the older trees are inert, archival or still consumed by any workflow. Do not delete them based on directory naming alone.

These findings show that the approved two-way email exclusivity rule cannot be guaranteed safely by application-only pre-checks under concurrent registration and organisation/cohort provisioning. The global uniqueness mechanism, legacy-conflict reconciliation and migration design remain unresolved. Managed-account access revocation must result in deletion, not account release with retained learning history. No schema or production change is authorised by this audit.

### 7.9 Active versus legacy application surfaces and remaining source work

The repository README and root Vercel configuration identify the active implementation surfaces:
- `frontend-v02/` is Learnora ME.
- `frontend-team/` is Learnora Teams.
- `backend-python/` is the FastAPI backend.
- Root `vercel.json` routes `/api/*` to `backend-python/main.py` and has deployment automation disabled.
- `backend-python-v0/` and `frontend/` are legacy trees, not the documented source of truth for current application work. They still contain legacy role implementations and must not be mistaken for active routes; retain them unless a separate archival/removal decision is made.
- `frontend-team/` is an active application and must be included in any permission/auth contract review even though its current login page does not contain the retired product-specific learner role.

Additional source findings:
- `backend-python/routers/public_directory.py` explicitly filters public courses by ownership and organisation public-catalogue settings. It must remain a separate public discovery path and must never expose private organisation-owned courses through public track or course results.
- `backend-python/services/free_access.py` intentionally limits free-launch eligibility to individual learners. Preserve that boundary; organisation/cohort accounts, creators, tutors and staff must not become eligible merely because their role strings are normalised during this work.
- `backend-python/routers/creator_finance.py` and `creator.py` use creator account ownership and payout permissions. These are independent-tutor/creator surfaces and must not be merged into organisation tutor membership.
- `backend-python/routers/organisation_teams.py` and the Teams UI use organisation membership and team-member relationships. They must enforce the approved two-way email exclusivity between individual learner and organisation/cohort-managed account contexts. Whether one managed identity may belong to more than one customer organisation remains unresolved; do not impose a one-organisation limit based on the earlier proposal.
- The active organisation dashboard currently fetches public catalogue data for organisation configuration and exposes organisation-wide course assignment plus per-learner course/lesson/tutor assignment. Both need redesign: private organisation-created content must be selectable inside the tenant, and track configuration must supply the normal learner course list.
- `backend-python/routers/course_content.py` has legacy role fallback branches and a distinct cohort-account branch. This is a high-risk consolidation point because multiple course, lesson and content endpoints call its shared access guard.
- The active permissions module still includes legacy role constants alongside platform and organisation roles. The empty `backend-python/routers/learnora_permissions.py` is not an implementation of the permission system.
- The current instructor assignment workspace filters assignments by tutor ID and derives organisation IDs from memberships, while the test fixture permits the same identity to have memberships in two organisations. Before this future workflow is implemented, the product owner must decide whether one managed identity may belong to multiple customer organisations. Regardless of that decision, every tutor query and report must enforce the relevant organisation context and the tutor's assigned track/course scope; do not assume the cardinality rule.

**Remaining before implementation:** the current pass has inspected the identity-critical backend, organisation/cohort/course services, active frontend login/registration and organisation/cohort dashboards, Teams entry points, targeted security tests, relevant migration DDL and the schema baseline. It has not yet inspected every one of the 462 identity-/organisation-/cohort-/course-related source, test, configuration and document paths identified by the repository-tree filter. Continue that targeted inventory (including all auth callers, course/content/media/AI/report routes and affected tests), then reconcile the live schema read-only. The GitHub code-search endpoint was unavailable in this connector context, so no claim of a successful repository-wide text search is made.

## 8. Approved identity and managed-account lifecycle outcomes; technical model unresolved

The approved product outcomes are:

- A normal individual learner email and an organisation/cohort-managed account email are mutually exclusive in both directions. The rule also covers organisation-managed tutors and other organisation-managed users.
- Revoking an organisation/cohort-managed learner's or tutor's access means deleting that managed account and its associated data. It is not suspension, soft deactivation or release while preserving personal learning history.
- After deletion, the deleted account no longer reserves the email. The email may be used for a new account through ordinary registration/invitation checks. No deleted account data, progress, entitlement or history is transferred.
- At organisation contract end, retain the organisation record and numeric learner count at that time; delete the covered learner identities, roster, team membership and associated learner data. Deny organisation access if no new contract is signed.

These are product outcomes, not a decision about the technical identity architecture. The following remain unresolved and must not be assumed:
- Whether to introduce a canonical identity registry or enforce exclusivity through another database design.
- Canonical email normalisation details and race-safe cross-account uniqueness enforcement.
- How duplicate/conflicting legacy identities and existing cohort-specific accounts are reconciled.
- How existing memberships, progress, assessments and other historical records are handled during any approved transition; no migration may silently transfer deleted managed-account data to a new individual account.
- Exact deletion dependencies, atomicity, failure/retry handling, session/token/invitation revocation, non-identifying audit evidence, backup/log/cache/export/processor expiry and narrow legal/financial retention exceptions.

Preserve existing records until a separately approved transition plan exists. Do not modify WitStart records or applied migration history. Do not infer that a proposed identity table or lifecycle status exists in the current schema. Any future migration must be additive where feasible, evidence-backed, tested on disposable data and separately authorised before production use.

## 9. Current product sequence and deferred implementation boundary

The current approved product implementation sequence is governed by PD-001:

1. Complete only the normal individual learner experience in Learnora ME.
2. Build the separate Learnora Teams website, including internal course/content production, review, acceptance, publishing and Teams-owned lesson-video uploads.
3. Return to Learnora ME to implement the corporate organisation experience.
4. Build independent tutor functionality separately.

During the current individual learner phase, preserve existing cohort functionality, accounts, access paths, assignments, progress and historical records. Do not implement deferred Teams, corporate organisation or independent tutor workflows as part of the individual learner phase. Shared changes are limited to what is necessary for individual learner work, security, compatibility or regression prevention.

Cohort and corporate organisation workflows remain distinct. The approved cohort requirements include a fixed learner track per cohort, at least one tutor per track, confirmation warnings for additional tutor/track assignments, two-way email exclusivity, managed-account deletion on access revocation, and aggregate-only learner retention at organisation contract end. The cohort team taxonomy and detailed technical identity/deletion design remain unresolved in the linked domain specifications.

No implementation sequence for the deferred identity, invitation, cohort or corporate workflows is authorised by this architecture document. Before those phases begin, complete the relevant source/live-schema review, resolve the documented product and technical questions, prepare a compatibility/deletion design and obtain separate implementation approval. Do not implement an account-release workflow that preserves managed learner history.

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

## 11. Implementation update — 9 November 2026

This section supersedes earlier status statements above where they described the learner implementation as not yet started. It records the current code changes; it does not claim the launch workflow is complete.

### 11.1 Implemented in the active codebase

- `backend-python/routers/auth.py` now has a fail-closed lookup for reserved `cohort_accounts` email identities. Individual registration rejects an email reserved by an organisation/cohort account, and individual login does not fall through to the `users` table when the email belongs only to a managed cohort account.
- The authenticated-user resolver checks the separate admin, individual-user and cohort-account identity sources for conflicting records. Conflicts return HTTP 409 and are security-logged rather than silently selecting one account.
- Cohort-token resolution verifies that the token's cohort account is the sole managed account for its canonical email and that no individual or administrator identity shares that email.
- Individual and administrator email lookups now fetch up to two case-insensitive matches and return HTTP 409 with a security event when duplicate rows exist within either table, rather than selecting an arbitrary first match.
- Verification resend and password-recovery flows now resolve individual, administrator and cohort identities before sending tokens. Conflicting or managed-only identities receive the same generic response without an individual/admin reset email. Password-reset tokens are claimed with a conditional unused-and-unexpired update before the password change, preventing concurrent submissions from reusing one token.
- Organisation-context resolution checks both direct organisation memberships and retained legacy cohort memberships. Multiple organisation or incompatible role contexts fail closed for learner authentication. It also rejects unresolved/orphaned cohort references instead of treating them as an individual account with no organisation context.
- `backend-python/routers/cohort_learners.py` blocks cohort provisioning when an individual/admin identity or another cohort's managed account already uses the email. Existing same-cohort inactive records can be considered for controlled re-provisioning; active duplicates are rejected.
- The individual login page verifies the newly established session with `/auth/me` before routing. Failed verification clears the local session marker. The frontend continues to use the HttpOnly cookie rather than persisting the JWT in browser storage.
- The `/auth/me` endpoint now fails with HTTP 503 if it cannot resolve organisation memberships, instead of silently returning an empty membership list. This prevents transient database failures from making a managed account appear to have no organisation context.
- The individual course page no longer presents a misleading “Switch to individual learning” link for an organisation-managed identity. The historical copy says the organisation must release the managed account before an individual account can be created; that wording is superseded. The approved product rule is that the managed account must first be deleted through the authorised access-revocation process.
- Single-course self-enrolment now queries only personal rows (`organisation_id IS NULL` and `cohort_id IS NULL`), returns existing active/completed enrolments, reactivates a withdrawn personal enrolment in place, and rejects ambiguous duplicate or suspended/invited records instead of attempting a conflicting insert.
- Learner progress/content access now checks course, module and lesson publication state. Draft courses, draft modules and draft lessons are not served by the shared lesson-content resolver; lesson content, workspace, notes, media and progress endpoints use that resolver. Quiz/assignment module checks also validate that the current module and its course remain published or reviewable as archived.
- The AI tutor's lesson-context path now calls the same scope-aware enrolment resolver as progress/content APIs instead of querying `learnora_enrolments` directly. This closes a path where a personal enrolment could otherwise be mistaken for an organisation learner's assignment.
- The shared course-content API now hides draft courses, modules and lessons from learner contexts while retaining draft visibility for authorised course-management roles. Learner module/lesson endpoints validate current publication state before returning lesson content; list and full-structure endpoints omit unpublished rows.
- The onboarding page now redirects cohort and organisation-managed identities to their own workspace rather than sending a backend 403 to the login page. Only a normal individual learner can complete individual onboarding.
- The API client attaches HTTP status codes to thrown errors. The dashboard preserves previously loaded learning data on transient refresh failures, distinguishes unavailable data from a genuinely empty learning state, and redirects on unauthorised responses.
- The dashboard learning-session tracker declares its browser interval handle as `number`, matching the DOM `window.setInterval()` return type in this project's combined DOM/Node TypeScript environment. This fixes the TypeScript error reported by Vercel at `components/dashboard/LearningSessionTracker.tsx:120`. The correction is committed on `main` as `e51f5b60`.

### 11.2 Verification status and known limitations

- The two Vercel build logs supplied on 9 November 2026 both reported successful Next.js compilation, then failed during TypeScript validation on the same timer type mismatch. The source fix is committed as `e51f5b60`; a subsequent production build has not yet been run or observed. Do not treat the build as verified until a fresh build passes.
- Added focused mocked regression tests for literal reserved-email matching, fail-closed reserved-identity lookup, fail-closed current-user membership resolution, duplicate user/admin email rows, and unresolved cohort identity context. Added source-contract checks for conflict-aware verification/password recovery and single-use reset-token claims; none have been executed. Added an account-lifecycle contract check for the final managed-identity recheck; none have been executed. These tests have been committed but have **not** been executed. Added source-contract regression checks for individual enrolment scope, withdrawn-enrolment reactivation and fail-closed duplicate handling; none of these tests have been executed. Added source-contract checks for course/lesson publication visibility across progress and course-content endpoints, plus the AI tutor's use of the shared enrolment resolver; none have been executed. No fresh production build, browser journey, deployment, CI workflow, SQL migration or live database operation was run.
- Email uniqueness remains an application-level guard across separate identity tables. It is not race-safe against simultaneous individual registration and managed-account provisioning. The global canonical email registry/unique constraint and its backfill/conflict-resolution procedure remain a future additive migration; do not apply it without explicit approval and a reviewed live-schema/data plan.
- The current schema baseline also has a unique constraint on `learnora_enrolments(user_id, course_id, organisation_id)`. Because individual rows use `organisation_id = NULL` (and PostgreSQL treats NULL values as distinct for ordinary unique constraints), this does not prevent concurrent duplicate individual enrolments. The new route handles existing duplicates by failing closed, but race-safe prevention needs a reviewed partial unique index over `(user_id, course_id)` for rows where both `organisation_id` and `cohort_id` are NULL, after a read-only duplicate preflight. Do not apply that migration without approval. The complete read-only design and rollout sequence are in [STEP_8_GLOBAL_IDENTITY_AND_ENROLMENT_CONSTRAINTS_PLAN.md](../backend-python/migrations/STEP_8_GLOBAL_IDENTITY_AND_ENROLMENT_CONSTRAINTS_PLAN.md).
- The code audit at this date described an organisation-controlled release workflow as not implemented; that historical implementation observation does not define the current product target. The approved target is now account deletion on organisation/cohort access revocation, with associated managed learner/tutor data deleted and the email reservation ending with that identity. The older release-and-preserve-history proposal is superseded by PD-012. Any existing self-deletion guard or release-related code must be reconciled against this target only in a separately authorised implementation pass; do not alter existing records during documentation work.
- Existing legacy `witstart` role compatibility remains in active auth/session code pending the full audit of historical rows and the separate cohort login path. Historical records and migration history must remain untouched; remove active product-specific role handling only after a safe compatibility transition is designed.
- The full learner vertical slice is still being audited: registration/verification/recovery, login/session revocation, public catalogue visibility, enrolment, course/lesson content, assessment, progress, evidence and completion must each be reconciled across backend and frontend before launch readiness can be claimed.

### 11.3 Operational boundary

Continue on `main`. Do not deploy, trigger CI, execute SQL, apply migrations, alter live records, or mutate legacy WitStart data. Use focused regression tests and source-level checks; report runtime/browser/database verification gaps explicitly.



## Learner account deletion and recovery addendum — 9 November 2026

Individual learner self-service deletion uses a 60-minute email confirmation followed by a 30-day `deactivation_pending` recovery period. The learner can reactivate the same account through a one-time email link during that period. The original email, password and learning history are retained during recovery; a same-email registration attempt issues a reactivation link rather than creating a second account. After the recovery deadline, a protected scheduled finaliser creates a restricted deletion-history record and anonymises the live account. Organisation/cohort identity and ownership safeguards remain unchanged.

The implementation details, deletion-reason audit trail, staff visibility, marketing consent and future notification engine are documented in [LEARNER_NOTIFICATIONS_AND_MARKETING_AUTOMATION.md](LEARNER_NOTIFICATIONS_AND_MARKETING_AUTOMATION.md). The associated database migration is additive and must be applied before deploying backend code that reads its new columns. It has not been applied to production.

## Account deletion decision — 30-day recovery, then complete learner erasure

The approved product rule is:

- Confirmed deletion starts a 30-day deactivation and recovery window. No learner data is erased during this period.
- Reactivation during the window restores the existing account with its password, enrolments, progress, notes, submissions and other learner records intact.
- At the end of the 30 days, the finalisation process deletes the learner's `public.users` row and all account-linked learner records, including learning/progress data, notes, assessments, submissions, certificates, discussions, AI conversations/usage, notifications, activity records, account tokens, membership links and learner-owned commercial/profile rows.
- The only learner-specific record retained is the restricted `public.deleted_account_history` row. It contains the deletion-history fields and reason; it is not a reusable learner account.
- The finaliser must fail atomically if a dependent learner record cannot be deleted. It must never report completion after partial cleanup.
- Shared platform catalogue and organisation resources are not deleted solely because a learner created or was assigned as their actor; the learner attribution is detached where appropriate.

The implementation is represented by migrations `20261109180000_learner_deletion_grace_and_marketing_consent.sql` and `20261109190000_erase_learner_records_after_recovery.sql`. They remain unapplied to production until separately authorised. Keep `ACCOUNT_DELETION_FINALIZER_ENABLED=false` until migrations, schema checks and deletion tests are complete. The Terms and Privacy Policy wording will be reviewed and updated in a separate documentation/legal-review pass after the feature set is complete.


---

## 12. Approved organisation management and invitation model — 21 November 2026

**Authority:** This addendum records the product owner's approved shared management and onboarding rules. It supplements the earlier architecture audit and proposed identity model. Where older proposed rules conflict with this addendum or [PRODUCT_DECISIONS.md](PRODUCT_DECISIONS.md), the approved decision register and this addendum take precedence. It does not authorise implementation or migration.

### 12.1 Organisation type is established at creation

When a customer organisation request is processed and the organisation is created, its type must be established as one of:

- **Cohort**
- **Corporate organisation**

This classification determines the organisation's operating model, team responsibilities, administrator duties and learning workflows. A cohort is not simply a corporate organisation with a different label. The two types share the management pattern below but retain distinct team and operational models.

### 12.2 Shared management structure

Every cohort and corporate organisation has:

1. An **active manager** responsible for coordinating the organisation as a whole.
2. A formal **management team**, led by that manager.
3. Other teams created under the organisation by the manager.
4. Administrators appointed by the manager, each with an assigned role and defined responsibilities.

The manager has organisation-wide management access to everything that the specific organisation is entitled to access, including its teams. This scope does not extend to other organisations or privileged Learnora internal staff capabilities.

The manager establishes the organisation's other teams and appoints its administrators. The management team is a real team within the organisation, not simply a generic label for unrelated functions.

Administrators receive permissions appropriate to their assigned roles. Appointment as an administrator does not automatically grant the manager's full organisation-wide access.

The manager, coordinator or another administrator may take responsibility for functions such as learner support, assessment and quality, programme operations and reporting. These functions do not need to become separate teams by default. Create a separate team only where there is an actual distinct working group with members and defined responsibilities.

### 12.3 Organisation-specific coordinator responsibilities

The shared management structure does not make cohort and corporate coordinator workflows interchangeable.

**Cohort coordinator**

The cohort coordinator is responsible for:
- Adding/onboarding learners into the cohort's configured learning tracks.
- Assigning tutors to the relevant tracks.
- Carrying out other cohort coordination tasks permitted by the coordinator's assigned role.

The cohort's configured tracks and the cohort-specific tutor/learner relationships remain part of the cohort domain model. A coordinator's authority must not be interpreted as unrestricted access beyond the cohort and assigned responsibilities.

**Corporate organisation coordinator**

The corporate coordinator is responsible for:
- Onboarding the organisation's learners/employees into the relevant learning teams.
- Carrying out other corporate coordination tasks permitted by the coordinator's assigned role.

Corporate team structures and learning workflows must be specified independently of cohort tracks and tutor assignment rules.

### 12.4 Invitation-based onboarding and self-service password creation

Organisation managers, coordinators and authorised administrators can initiate onboarding for another person. They do not complete that person's account activation and must not create or set that person's password.

The required flow applies to both cohorts and corporate organisations:

1. An authorised organisation manager or administrator initiates onboarding for the intended person.
2. The onboarding record identifies the organisation and the intended role. Where relevant, it also identifies the team, cohort, track or other learning context for which access is being requested.
3. The system sends an invitation email to the intended person's email address. The email includes the relevant organisation information and details of the role or context for which the person is being onboarded.
4. The email contains an activation link.
5. The intended person follows the link and is redirected to the account activation flow.
6. The intended person creates their own password and completes the activation process.
7. The activation link expires **48 hours after issuance**.

The organisation-side action is an invitation/onboarding action, not the creation of a fully activated account. A manager or administrator cannot bypass the invited person's own activation step. This applies to all organisation users, including administrators, coordinators, tutors, learners and employees.

The invitation must be bound to the intended recipient and the specified organisation/role context. An expired, invalid or already-consumed link must not activate an account. Email content must not contain a password or reusable credential.

### 12.5 Invitation lifecycle details still requiring specification

The following behaviours have not yet been decided and must not be invented during implementation:

- Whether and how an authorised administrator can resend an invitation.
- Whether a new invitation invalidates any previously issued link.
- Whether an invitation can be revoked, and which roles may revoke it.
- How duplicate invitations or an already-existing account are handled.
- What the user sees after following an expired link and how a fresh invitation is requested.
- Whether the intended person's email can be changed after an invitation has been issued.
- The exact activation-token storage, hashing, single-use enforcement, audit and rate-limit design.

These are specification gaps, not permission to choose convenient defaults. The 48-hour expiry and recipient-completed password creation are approved requirements.

### 12.6 Access and security boundaries

- The manager's broad access is confined to the specific organisation and its entitled resources.
- Administrators operate under their assigned roles and permissions.
- Coordinators perform the onboarding and learning-structure duties assigned to their organisation type and role.
- Invitation initiation does not mean the invited person is already an active authenticated user.
- Only the intended recipient completes account activation and chooses their password.
- Invitation links are time-limited credentials and must be protected against disclosure, replay and use by a different recipient.
- Organisation roles do not confer Learnora internal staff or platform-administrator privileges.
- Cohort and corporate team membership, tutor assignments and learning-resource access remain scoped to their respective organisation and assigned responsibilities.

### 12.7 Implementation and preservation boundary

This addendum documents approved target behaviour only. The organisation portal and invitation workflows remain deferred according to the approved product implementation sequence. Do not implement them during the current individual learner phase.

Do not infer that the current database schema, legacy cohort login flow or existing invitation code already satisfies this target model. Before implementation, reconcile current source and live schema read-only, define compatibility with existing cohort accounts and progress, specify the unresolved invitation lifecycle, and obtain the required implementation authorisation. No account conversion, migration, email-provider change, live database mutation or deployment is authorised by this documentation decision.


### 12.8 Cohort tutor coverage, assignment confirmations and managed-account deletion

The cohort-specific operating model is detailed in [COHORT_OPERATING_MODEL.md](COHORT_OPERATING_MODEL.md) and governed by PD-012 in [PRODUCT_DECISIONS.md](PRODUCT_DECISIONS.md).

- Every learning track in a cohort must have at least one tutor.
- A tutor may be assigned to more than one track. If the coordinator attempts an additional track assignment for a tutor who already has an assignment, the system must warn the coordinator, identify the existing course/assignment and require explicit confirmation before proceeding.
- A track may have more than one tutor. If the coordinator attempts to add another tutor to a track that already has a tutor, the system must warn and require explicit confirmation before proceeding.
- These warnings are confirmation gates, not assignment prohibitions.
- Tutor access remains scoped to the cohort, assigned track(s), courses and responsibilities.

A cohort coordinator may revoke a learner's or tutor's access. Revocation of an organisation/cohort-managed learner or tutor means deleting that managed account and its associated learner/tutor data. It is not merely removing a membership or disabling access while retaining the person's account and learning history.

The email identity is mutually exclusive: an email used by an organisation/cohort-managed account cannot be used by an individual learner account, and an email used by an individual learner account cannot be used by an organisation/cohort-managed account. Once the managed account is deleted, its email reservation ends and the email may be used for a new account through normal checks. No deleted data is transferred. The earlier account-release proposal that preserved learner history is superseded by PD-012.

### 12.9 Cohort, organisation and contract-end data lifecycle

A cohort ending and a parent organisation's contract ending are distinct events:

- An ended cohort does not cause its parent organisation record to be deleted.
- The same organisation may start a later cohort under a new cohort identity.
- When an organisation contract ends, the organisation record remains.
- At the contract-end point, retain the numeric count of learners associated with that organisation at that time.
- Delete the covered organisation/cohort-managed learner accounts and associated learner/team data. Do not retain an identifiable learner roster, dormant learner accounts or personal learning histories as a substitute.
- If no new contract has been signed, the organisation's Learnora access must be denied.
- A later contract may permit a new cohort under a new cohort ID; it does not restore deleted accounts or data from the previous cohort.

The retained count is an organisation-level aggregate, not a retained roster. Technical erasure, atomicity, backup/log/processor expiry, narrow legal/financial exceptions and non-identifying security audit requirements must be specified before implementation. Those technical details do not reopen the approved outcome. See [COHORT_OPERATING_MODEL.md](COHORT_OPERATING_MODEL.md). These organisation/cohort workflows remain deferred under the approved implementation sequence.
