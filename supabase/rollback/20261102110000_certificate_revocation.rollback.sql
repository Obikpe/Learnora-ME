DROP INDEX IF EXISTS public.certificates_revoked_at_idx;
ALTER TABLE public.certificates DROP COLUMN IF EXISTS revocation_reason, DROP COLUMN IF EXISTS revoked_by, DROP COLUMN IF EXISTS revoked_at;
