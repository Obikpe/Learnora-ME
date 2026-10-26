-- MANUAL ADMIN-ONLY REMEDIATION
-- Run only in a Supabase administrative session authorised to alter defaults
-- for role supabase_admin. The ordinary project connection role postgres is
-- not a member of supabase_admin in the active project and cannot execute this.
-- This is deliberately outside supabase/migrations/ so it is not auto-applied.
--
-- Goal: future public objects created by supabase_admin must not inherit browser
-- privileges. This does not change existing table grants; those are handled by
-- the already-applied 20261021220303_revoke_browser_table_grants migration.

BEGIN;

-- Apply the changes as the default-ACL owner. A superuser may SET ROLE here;
-- an ordinary postgres connection without membership cannot do so.
SET LOCAL ROLE supabase_admin;

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public
  REVOKE ALL PRIVILEGES ON TABLES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public
  REVOKE ALL PRIVILEGES ON SEQUENCES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin
  REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
-- Function EXECUTE defaults were granted globally, so revoke globally too;
-- a schema-specific REVOKE cannot cancel a global default grant.
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin
  REVOKE EXECUTE ON FUNCTIONS FROM anon, authenticated;

-- Fail the operation if browser-facing defaults remain for this managed owner.
DO $verify$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_default_acl d
    CROSS JOIN LATERAL aclexplode(d.defaclacl) acl
    LEFT JOIN pg_roles grantee ON grantee.oid = acl.grantee
    WHERE d.defaclrole = (SELECT oid FROM pg_roles WHERE rolname = 'supabase_admin')
      AND d.defaclnamespace IN (0, 'public'::regnamespace)
      AND (acl.grantee = 0 OR grantee.rolname IN ('anon', 'authenticated'))
  ) THEN
    RAISE NOTICE 'Remaining managed default ACLs: %', (
      SELECT string_agg(
        format('object_type=%s schema=%s grantee=%s privilege=%s',
          d.defaclobjtype, coalesce(n.nspname, '*'), coalesce(grantee.rolname, 'PUBLIC'), acl.privilege_type),
        '; ' ORDER BY d.defaclobjtype, n.nspname, grantee.rolname, acl.privilege_type
      )
      FROM pg_default_acl d
      CROSS JOIN LATERAL aclexplode(d.defaclacl) acl
      LEFT JOIN pg_roles grantee ON grantee.oid = acl.grantee
      LEFT JOIN pg_namespace n ON n.oid = d.defaclnamespace
      WHERE d.defaclrole = (SELECT oid FROM pg_roles WHERE rolname = 'supabase_admin')
        AND d.defaclnamespace IN (0, 'public'::regnamespace)
        AND (acl.grantee = 0 OR grantee.rolname IN ('anon', 'authenticated'))
    );
    RAISE EXCEPTION 'Browser-role default ACLs remain for supabase_admin; do not treat hardening as complete.';
  END IF;
END
$verify$;

COMMIT;
