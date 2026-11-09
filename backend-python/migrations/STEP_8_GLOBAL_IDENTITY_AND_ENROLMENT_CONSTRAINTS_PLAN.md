# Step 8 — Global identity and individual enrolment constraints

**Status:** Design only; this is not an executable migration.  
**Prepared:** 9 November 2026.  
**Execution boundary:** Do not run SQL, apply migrations, alter live rows, or deploy this design without explicit approval and a fresh live-schema/data review.

## 1. Purpose

The application now checks email identities across users, admins and cohort_accounts, rejects duplicate case-insensitive matches within the individual/admin tables, and blocks managed emails from individual registration. These checks fail closed during ordinary requests, but they are not atomic across simultaneous requests.

The current account tables are separate identity sources. Two requests can both pass an application lookup before either inserts its row. A database-enforced reservation is required for a race-safe one-email/one-account guarantee.

The current enrolment schema also has a unique constraint on (user_id, course_id, organisation_id). Individual enrolments have organisation_id NULL; ordinary PostgreSQL unique constraints treat NULL values as distinct. That constraint therefore does not prevent concurrent duplicate personal enrolments.

## 2. Required invariants

1. One canonical email belongs to at most one active Learnora identity across individual users, managed learner users, cohort accounts and platform administrators.
2. An organisation-managed learner remains a managed identity when membership is suspended or removed from an active cohort. They do not become an individual learner merely because an assignment ended.
3. An organisation-managed identity can become an individual identity only after an authorised release/deletion process has completed. Existing account history remains available for legitimate audit and reporting.
4. A deleted identity's original email is historical evidence, not an active reservation. Reuse is permitted only after the account deletion transaction has completed successfully.
5. A cohort account cannot coexist with an individual or administrator account using the same canonical email.
6. A personal enrolment is unique for a (user_id, course_id) pair where both organisation_id and cohort_id are NULL.
7. Organisation/cohort enrolments remain scoped and are not converted into personal enrolments by these constraints.

## 3. Proposed identity registry

Proposed table: public.learnora_identity_emails.

| Column | Purpose |
|---|---|
| normalized_email | Primary key; canonical lower-case, trimmed email |
| identity_type | learner_user, cohort_account, or platform_admin |
| identity_id | UUID of the owning row in its source table; no polymorphic foreign key |
| account_context | individual, managed, cohort, or platform |
| status | active, deletion_pending, or released |
| created_at, updated_at | Audit timestamps |
| released_at, released_by | Explicit release audit fields |
| metadata | Restricted operational metadata; never passwords or tokens |

The primary key on normalized_email is the global uniqueness constraint. Registry access must be service-role-only; no browser role should read or mutate it directly.

The final SQL must define one canonical normalisation function and ensure Python and PostgreSQL use equivalent normalisation. Do not assume lower(trim(email)) is identical to Python's full Unicode strip().lower() without testing the accepted email character set.

### 3.1 Ownership rules

- Individual registration reserves individual + learner_user in the same database transaction that creates the users row.
- Cohort provisioning reserves cohort + cohort_account in the same transaction that creates the cohort account.
- Administrator provisioning reserves platform + platform_admin in the same transaction that creates the administrator.
- When an existing user is attached to an organisation or cohort, the registry context becomes managed. Suspension or removal of an active assignment does not release it.
- The registry must not infer that an account is individual solely because no active membership row is currently returned.
- The existing account deletion transaction must anonymise the users.email value, preserve the original email in the restricted deletion-history table, and release the registry reservation atomically.
- A future organisation release workflow must be explicit, authorised, audited, and must preserve learner history. It must not simply delete an organisation_members row.

## 4. Transactional account operations

The final migration should introduce narrowly scoped database functions or equivalent transactions for:

1. Create individual learner: reserve canonical email, create the user row and initial verification token record. A uniqueness conflict returns a safe conflict result.
2. Create cohort learner: reserve canonical email, create the cohort account and cohort membership. Reject an existing individual/admin identity and any other cohort account.
3. Create administrator: reserve canonical email and create the administrator row.
4. Attach managed membership: change an existing learner registry context to managed; do not create a second identity.
5. Release/delete managed identity: require an authorised organisation workflow, preserve learning/audit history, revoke sessions and tokens, anonymise credentials, and release the canonical email only after all required checks succeed.

Do not implement these as independent client-side pre-checks followed by separate inserts. The uniqueness decision and account creation must be in one transaction.

## 5. Existing-data preflight — read only

Before writing a migration, generate a report for:

- Case-insensitive duplicates in users.email.
- Case-insensitive duplicates in admins.email.
- Case-insensitive duplicates in cohort_accounts.email.
- Cross-table collisions between all three sources.
- Users with retained organisation memberships, including suspended memberships.
- Users with retained cohort memberships whose cohort or organisation cannot be resolved.
- Accounts with account_status = deletion_pending or deleted.
- Existing rows in deleted_account_history; these are historical and must not be backfilled as active reservations.
- Multiple personal enrolment rows for the same user_id and course_id where organisation_id IS NULL and cohort_id IS NULL.

Do not automatically merge, delete, anonymise, or select a winner for any conflict. Each conflict needs a documented owner and resolution decision before registry backfill.

## 6. Personal enrolment uniqueness

After the duplicate preflight and any approved remediation, add a partial unique index equivalent to:

    CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS
      learnora_personal_enrolments_user_course_uidx
    ON public.learnora_enrolments (user_id, course_id)
    WHERE organisation_id IS NULL
      AND cohort_id IS NULL;

This is a design sketch, not approved executable SQL. Confirm PostgreSQL version, Supabase migration execution rules, duplicate counts, existing index names, and whether concurrent index creation is supported in the chosen migration workflow before preparing the final migration.

The application should still handle a uniqueness conflict as an idempotent re-enrolment result: re-read the personal row, return active/completed rows, reactivate a withdrawn personal row only when permitted, and reject invited/suspended or ambiguous records.

## 7. Rollout order

1. Take a fresh schema snapshot and read-only data inventory from the active Supabase project.
2. Review and resolve every identity collision with the account owner; do not merge by email alone.
3. Produce a reviewed SQL migration and rollback plan.
4. Create the registry and backfill only conflict-free identities.
5. Add transactional registration/provisioning functions and update backend callers.
6. Add managed-context transitions for organisation/cohort membership operations.
7. Add the partial personal-enrolment unique index after duplicate remediation.
8. Run focused database assertions and mocked application tests.
9. Verify signup, verification, login, recovery, cohort provisioning, account deletion/release, personal enrolment, withdrawal/reactivation, and progress access.
10. Remove redundant application-only reservation logic only after database enforcement is proven in the live environment.

## 8. Current interim protections

Until this step is explicitly approved and implemented:

- Keep the current application-level checks and fail-closed responses.
- Keep retained organisation/cohort memberships as identity reservations.
- Keep the final account-deletion confirmation recheck.
- Reject ambiguous duplicate user/admin rows.
- Reject duplicate personal enrolment rows rather than selecting an arbitrary record.
- Do not claim the system has race-safe global email or personal-enrolment uniqueness.
- Do not apply this design to the live Supabase project.
