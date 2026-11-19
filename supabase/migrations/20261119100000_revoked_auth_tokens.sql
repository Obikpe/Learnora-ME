-- Server-side revocation for custom Learnora JWT sessions.
-- Store only a one-way fingerprint; never persist bearer token material.
BEGIN;
CREATE TABLE IF NOT EXISTS public.revoked_auth_tokens (
  token_hash text PRIMARY KEY CHECK (token_hash ~ '^[a-f0-9]{64}$'),
  expires_at timestamptz NOT NULL,
  revoked_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS revoked_auth_tokens_expires_at_idx ON public.revoked_auth_tokens (expires_at);
ALTER TABLE public.revoked_auth_tokens ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.revoked_auth_tokens FROM PUBLIC;
REVOKE ALL ON TABLE public.revoked_auth_tokens FROM anon, authenticated;
GRANT SELECT, INSERT, DELETE ON TABLE public.revoked_auth_tokens TO service_role;
COMMENT ON TABLE public.revoked_auth_tokens IS 'One-way fingerprints of revoked Learnora JWTs, retained only until each token expiry.';
COMMIT;
