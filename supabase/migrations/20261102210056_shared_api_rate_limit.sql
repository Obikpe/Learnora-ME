-- Shared API request throttling for serverless deployments.
-- Bucket keys are SHA-256 digests; raw client IP addresses are not stored.
BEGIN;

CREATE OR REPLACE FUNCTION public.consume_api_rate_limit(
  p_bucket_key text,
  p_max_requests integer,
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
  next_attempts integer;
BEGIN
  IF p_bucket_key !~ '^[0-9a-f]{64}$'
     OR p_max_requests < 1
     OR p_window_seconds < 1 THEN
    RAISE EXCEPTION 'Invalid API rate-limit parameters';
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
    next_attempts := 1;
    UPDATE public.auth_rate_limit_buckets
    SET attempts = next_attempts,
        window_started_at = v_now,
        blocked_until = NULL,
        updated_at = v_now
    WHERE bucket_key = p_bucket_key;
    RETURN false;
  END IF;

  next_attempts := bucket.attempts + 1;
  UPDATE public.auth_rate_limit_buckets
  SET attempts = next_attempts,
      blocked_until = CASE WHEN next_attempts > p_max_requests
        THEN v_now + pg_catalog.make_interval(secs => p_window_seconds)
        ELSE blocked_until END,
      updated_at = v_now
  WHERE bucket_key = p_bucket_key;

  RETURN next_attempts > p_max_requests;
END;
$function$;

REVOKE ALL ON FUNCTION public.consume_api_rate_limit(text, integer, integer) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.consume_api_rate_limit(text, integer, integer) TO service_role;

COMMIT;
