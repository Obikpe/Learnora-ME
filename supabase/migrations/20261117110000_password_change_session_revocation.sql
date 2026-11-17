-- Track password changes for every identity type that can receive a JWT.
-- Setting the initial value to now() intentionally invalidates all pre-migration
-- sessions once this migration is applied. New and changed passwords continue to
-- update this timestamp, and JWT iat values retain sub-second precision.

ALTER TABLE public.users
  ADD COLUMN IF NOT EXISTS password_changed_at timestamptz;

UPDATE public.users
   SET password_changed_at = COALESCE(password_changed_at, now())
 WHERE password_changed_at IS NULL;

ALTER TABLE public.users
  ALTER COLUMN password_changed_at SET DEFAULT now(),
  ALTER COLUMN password_changed_at SET NOT NULL;

ALTER TABLE public.admins
  ADD COLUMN IF NOT EXISTS password_changed_at timestamptz;

UPDATE public.admins
   SET password_changed_at = COALESCE(password_changed_at, now())
 WHERE password_changed_at IS NULL;

ALTER TABLE public.admins
  ALTER COLUMN password_changed_at SET DEFAULT now(),
  ALTER COLUMN password_changed_at SET NOT NULL;

COMMENT ON COLUMN public.users.password_changed_at IS
  'Timestamp used to invalidate previously issued learner and staff JWT sessions after a password change or reset.';

COMMENT ON COLUMN public.admins.password_changed_at IS
  'Timestamp used to invalidate previously issued legacy administrator JWT sessions after a password change or reset.';
