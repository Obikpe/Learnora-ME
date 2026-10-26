-- EMERGENCY ROLLBACK ONLY.
-- Removes the shared rate-limit RPCs and bucket table. This disables the
-- database-backed protection introduced by the two 2026102615xxxx migrations.
-- Do not run until an alternative shared limiter is available.
BEGIN;
DROP FUNCTION IF EXISTS public.consume_api_rate_limit(text, integer, integer);
DROP FUNCTION IF EXISTS public.clear_auth_rate_limit(text);
DROP FUNCTION IF EXISTS public.record_auth_rate_failure(text, integer, integer);
DROP FUNCTION IF EXISTS public.check_auth_rate_limit(text, integer, integer);
DROP TABLE IF EXISTS public.auth_rate_limit_buckets;
COMMIT;
