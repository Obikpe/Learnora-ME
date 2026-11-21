ALTER TABLE public.certificates ADD COLUMN IF NOT EXISTS revoked_at timestamptz NULL, ADD COLUMN IF NOT EXISTS revoked_by uuid NULL REFERENCES public.users(id) ON DELETE SET NULL, ADD COLUMN IF NOT EXISTS revocation_reason text NULL;
CREATE INDEX IF NOT EXISTS certificates_revoked_at_idx ON public.certificates (revoked_at) WHERE revoked_at IS NOT NULL;
