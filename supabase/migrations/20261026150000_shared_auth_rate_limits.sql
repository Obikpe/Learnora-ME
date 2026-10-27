-- Shared, database-backed authentication throttling for serverless instances.
-- Keys are SHA-256 digests of application-defined bucket identifiers; raw usernames
-- and IP addresses are never persisted in this table.
BEGIN;

CREATE TABLE IF NOT EXISTS public.auth_rate_limit_buckets (
  bucket_key text PRIMARY KEY CHECK (bucket_key ~ '^[0-9a-f]{64}$'),
  attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
  window_started_at timestamptz NOT NULL DEFAULT pg_catalog.clock_timestamp(),
  blocked_until timestamptz,
  updated_at timestamptz NOT NULL DEFAULT pg_catalog.clock_timestamp()
);

ALTER TABLE public.auth_rate_limit_buckets ENABLE ROW LEVEL SECURITY;
REVOKE ALL PRIVILEGES ON TABLE public.auth_rate_limit_buckets FROM PUBLIC, anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.auth_rate_limit_buckets TO service_role;

CREATE OR REPLACE FUNCTION public.check_auth_rate_limit(
  p_bucket_key text,
  p_max_attempts integer,
  p_window_seconds integer
)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
DECLARE
  bucket public.auth_rate_limit_buckets%ROWTYPE;
  v_now timestamptz := pg_catalog.clock_timestamp();
BEGIN
  IF p_bucket_key !~ '^[0-9a-f]{64}$'
     OR p_max_attempts < 1
     OR p_window_seconds < 1 THEN
    RAISE EXCEPTION 'Invalid rate-limit parameters';
  END IF;

  INSERT INTO public.auth_rate_limit_buckets (bucket_key)
  VALUES (p_bucket_key)
  ON CONFLICT (bucket_key) DO NOTHING;

  SELECT * INTO bucket
  FROM public.auth_rate_limit_buckets
  WHERE bucket_key = p_bucket_key
  FOR UPDATE;

  IF bucket.blocked_until IS NOT NULL AND bucket.blocked_until > v_now THEN
    RETURN true;
  END IF;

  IF bucket.window_started_at <= v_now - pg_catalog.make_interval(secs => p_window_seconds) THEN
    UPDATE public.auth_rate_limit_buckets
    SET attempts = 0,
        window_started_at = v_now,
        blocked_until = NULL,
        updated_at = v_now
    WHERE bucket_key = p_bucket_key;
    RETURN false;
  END IF;

  RETURN bucket.attempts >= p_max_attempts;
END;
$function$;

CREATE OR REPLACE FUNCTION public.record_auth_rate_failure(
  p_bucket_key text,
  p_max_attempts integer,
  p_window_seconds integer
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
DECLARE
  bucket public.auth_rate_limit_buckets%ROWTYPE;
  v_now timestamptz := pg_catalog.clock_timestamp();
  next_attempts integer;
BEGIN
  IF p_bucket_key !~ '^[0-9a-f]{64}$'
     OR p_max_attempts < 1
     OR p_window_seconds < 1 THEN
    RAISE EXCEPTION 'Invalid rate-limit parameters';
  END IF;

  INSERT INTO public.auth_rate_limit_buckets (bucket_key)
  VALUES (p_bucket_key)
  ON CONFLICT (bucket_key) DO NOTHING;

  SELECT * INTO bucket
  FROM public.auth_rate_limit_buckets
  WHERE bucket_key = p_bucket_key
  FOR UPDATE;

  IF bucket.window_started_at <= v_now - pg_catalog.make_interval(secs => p_window_seconds) THEN
    next_attempts := 1;
    UPDATE public.auth_rate_limit_buckets
    SET attempts = next_attempts,
        window_started_at = v_now,
        blocked_until = CASE WHEN next_attempts >= p_max_attempts
          THEN v_now + pg_catalog.make_interval(secs => p_window_seconds) ELSE NULL END,
        updated_at = v_now
    WHERE bucket_key = p_bucket_key;
  ELSE
    next_attempts := bucket.attempts + 1;
    UPDATE public.auth_rate_limit_buckets
    SET attempts = next_attempts,
        blocked_until = CASE WHEN next_attempts >= p_max_attempts
          THEN v_now + pg_catalog.make_interval(secs => p_window_seconds)
          ELSE blocked_until END,
        updated_at = v_now
    WHERE bucket_key = p_bucket_key;
  END IF;
END;
$function$;

CREATE OR REPLACE FUNCTION public.clear_auth_rate_limit(p_bucket_key text)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
BEGIN
  IF p_bucket_key !~ '^[0-9a-f]{64}$' THEN
    RAISE EXCEPTION 'Invalid rate-limit key';
  END IF;
  DELETE FROM public.auth_rate_limit_buckets WHERE bucket_key = p_bucket_key;
END;
$function$;

REVOKE ALL ON FUNCTION public.check_auth_rate_limit(text, integer, integer) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.record_auth_rate_failure(text, integer, integer) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.clear_auth_rate_limit(text) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.check_auth_rate_limit(text, integer, integer) TO service_role;
GRANT EXECUTE ON FUNCTION public.record_auth_rate_failure(text, integer, integer) TO service_role;
GRANT EXECUTE ON FUNCTION public.clear_auth_rate_limit(text) TO service_role;

COMMIT;
