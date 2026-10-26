# Security hardening runbook

This branch prepares code and migrations only. No production SQL, merge, or deployment is performed by CI.

## What this change hardens

- Shared PostgreSQL-backed authentication failure buckets and a shared API request limiter replace process-local limits in production.
- The cohort-login path already uses shared database counters and rejects wildcard username syntax with dummy-hash verification for unknown users.
- Browser-role privileges are revoked from current public tables, sequences, and functions again, with hardened default privileges for objects created by `postgres`.
- Creator sale record/release/refund actions use separate `creator_sales.*` permissions rather than the broad `courses.assign` permission.
- Production readiness details require `READINESS_PROBE_TOKEN`; public liveness remains available at `/api/health`.
- Verification and reset tokens are placed in URL fragments for new emails; the frontend clears the URL immediately and retains query-string fallback only for old emails.
- Browser sessions use Secure, HttpOnly, SameSite=Lax cookies delivered only to the explicit frontend-origin allowlist. Both Next.js frontends proxy `/api/*` through same-origin rewrites; session storage keeps only a non-secret `cookie-session` marker. Non-browser clients without an `Origin` header retain bearer-token compatibility.
- Cohort DOB values are encrypted at write time and excluded from organisation roster responses. A read-only live check on 26 October 2026 found zero plaintext DOB rows in `public.cohort_accounts`.

## Required migration sequence

Apply the timestamped migrations in order in a disposable staging project first:

1. `20261026100000_pin_cohort_assignment_function_search_paths.sql`
2. `20261026150000_shared_auth_rate_limits.sql`
3. `20261026151000_shared_api_rate_limit.sql`
4. `20261026152000_separate_creator_sales_permissions.sql`
5. `20261026153000_revoke_browser_privileges_and_defaults.sql`

Do not deploy the updated backend before the rate-limit migrations are applied. Production API requests fail closed with HTTP 503 if the shared limiter functions are missing. Configure `READINESS_PROBE_TOKEN` before deploying the protected readiness endpoint.

## Supabase role-default limitation

A read-only inspection of the connected project showed browser grants on 53 public tables for both `anon` and `authenticated`. It also showed unsafe table/sequence/function default ACLs for `supabase_admin`. The current connection is `postgres`, which is not a member of `supabase_admin`; it cannot modify that role's default privileges.

The migration revokes current objects and hardens defaults for `postgres`. The additional script at `supabase/operations/20261026153000_revoke_supabase_admin_default_privileges.sql` must be run in a separately authorised session authenticated as `supabase_admin`. Do not put it in the normal migration chain and do not attempt to bypass role membership.

### Verify effective browser access

Run after the migration and privileged default-ACL operation:

```sql
SELECT table_name, grantee, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'public'
  AND grantee IN ('anon', 'authenticated')
ORDER BY table_name, grantee, privilege_type;

SELECT c.relname AS object_name, r.rolname AS browser_role, p.privilege
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
CROSS JOIN (VALUES ('anon'), ('authenticated')) r(rolname)
CROSS JOIN (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'),
                   ('TRUNCATE'), ('REFERENCES'), ('TRIGGER')) p(privilege)
WHERE n.nspname = 'public'
  AND c.relkind IN ('r', 'p', 'v', 'm', 'f')
  AND has_table_privilege(r.rolname, c.oid, p.privilege);

SELECT pg_get_userbyid(d.defaclrole) AS owner_role,
       d.defaclobjtype,
       grantee.rolname AS grantee,
       acl.privilege_type
FROM pg_default_acl d
CROSS JOIN LATERAL aclexplode(d.defaclacl) acl
LEFT JOIN pg_roles grantee ON grantee.oid = acl.grantee
WHERE d.defaclnamespace IN (0, 'public'::regnamespace)
  AND (acl.grantee = 0 OR grantee.rolname IN ('anon', 'authenticated'))
ORDER BY owner_role, d.defaclobjtype, grantee.rolname, acl.privilege_type;
```

All three queries should return zero rows for browser table privileges/default grants. The last query must be run after the privileged `supabase_admin` operation.

## Creator finance permissions

The new permission keys are inserted without granting them automatically:

- `creator_sales.record`
- `creator_sales.release`
- `creator_sales.refund`

Before rollout, explicitly assign each permission to the approved finance role(s), using the existing permission administration process. Do not grant them to all instructors or to every role that has `courses.assign`.

Payout state changes already use the atomic `process_learnora_creator_payout` RPC. Validate both the payout state and ledger entry in staging, including a forced ledger-insert failure.

## Migration provenance and release blockers

Two earlier timestamped migrations remain catalog-reconstructed, and five earlier migration files have not been independently verified against original source artifacts. Do not label them verbatim recoveries. Recover original blobs/backups if possible; otherwise document the limitation and review semantic equivalence before production release.

The legacy schema fingerprint is intentionally report-only. Do not drop/remap legacy data just to make the replay match the catalog snapshot.

## Rollout order

1. Review this branch and the full security diff.
2. Run backend tests, cohort API lifecycle, database migration assertions, and both frontend builds in CI.
3. Apply migrations to disposable staging and verify browser grants/default ACLs.
4. Run the privileged `supabase_admin` default-ACL operation with the appropriate owner-approved access.
5. Run the DOB dry-run script; the current live count is zero, so no backfill is needed unless new plaintext rows are discovered.
6. Validate rate-limit behavior across multiple serverless instances, creator finance permission grants, and the readiness probe with the secret header.
7. Validate cookie login/logout from each production frontend domain and ensure Vercel rewrites target the intended backend; then resolve migration provenance before calling the security review complete.
8. Deploy only with explicit release approval and a rollback window. This branch does not authorise a production migration or deployment.
