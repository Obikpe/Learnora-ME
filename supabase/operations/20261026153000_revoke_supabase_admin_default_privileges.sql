-- OPERATOR ACTION — run only in a session authenticated as supabase_admin.
-- The normal project postgres role is not a member of supabase_admin, so the
-- active migration role cannot alter this role's default ACLs. Do not place this
-- file in supabase/migrations: it requires a privileged project-admin session.
-- Verify the result with the default-ACL query in docs/security-hardening-runbook.md.
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public
  REVOKE ALL PRIVILEGES ON TABLES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public
  REVOKE ALL PRIVILEGES ON SEQUENCES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin
  REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public
  REVOKE EXECUTE ON FUNCTIONS FROM anon, authenticated;
