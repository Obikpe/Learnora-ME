-- Disposable-only behavioral checks for shared rate-limit RPCs.
BEGIN;

SELECT public.clear_auth_rate_limit(repeat('a', 64));
DO $check_auth$
BEGIN
  IF public.check_auth_rate_limit(repeat('a', 64), 2, 60) THEN
    RAISE EXCEPTION 'A fresh authentication bucket must not be limited';
  END IF;
  PERFORM public.record_auth_rate_failure(repeat('a', 64), 2, 60);
  IF public.check_auth_rate_limit(repeat('a', 64), 2, 60) THEN
    RAISE EXCEPTION 'One failed attempt must not exceed a two-attempt threshold';
  END IF;
  PERFORM public.record_auth_rate_failure(repeat('a', 64), 2, 60);
  IF NOT public.check_auth_rate_limit(repeat('a', 64), 2, 60) THEN
    RAISE EXCEPTION 'The authentication bucket must lock after the threshold';
  END IF;
END
$check_auth$;

SELECT public.clear_auth_rate_limit(repeat('b', 64));
DO $check_api$
BEGIN
  IF public.consume_api_rate_limit(repeat('b', 64), 2, 60) THEN
    RAISE EXCEPTION 'The first API request must be allowed';
  END IF;
  IF public.consume_api_rate_limit(repeat('b', 64), 2, 60) THEN
    RAISE EXCEPTION 'The second API request must be allowed';
  END IF;
  IF NOT public.consume_api_rate_limit(repeat('b', 64), 2, 60) THEN
    RAISE EXCEPTION 'The third API request must be limited';
  END IF;
END
$check_api$;

SELECT public.clear_auth_rate_limit(repeat('a', 64));
SELECT public.clear_auth_rate_limit(repeat('b', 64));

COMMIT;
