-- Collect a learner's date of birth and a timestamped minimum-age declaration.
-- Birth dates are private account data and remain accessible only to the backend service role.
ALTER TABLE public.users
  ADD COLUMN IF NOT EXISTS date_of_birth date,
  ADD COLUMN IF NOT EXISTS timezone text NOT NULL DEFAULT 'Africa/Lagos',
  ADD COLUMN IF NOT EXISTS age_13_plus_confirmed boolean NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS age_attestation_at timestamptz,
  ADD COLUMN IF NOT EXISTS age_attestation_version text;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
      FROM pg_constraint
     WHERE conname = 'users_age_attestation_consistency_check'
       AND conrelid = 'public.users'::regclass
  ) THEN
    ALTER TABLE public.users
      ADD CONSTRAINT users_age_attestation_consistency_check
      CHECK (
        (age_13_plus_confirmed = false
          AND age_attestation_at IS NULL
          AND age_attestation_version IS NULL)
        OR
        (age_13_plus_confirmed = true
          AND date_of_birth IS NOT NULL
          AND age_attestation_at IS NOT NULL
          AND age_attestation_version IS NOT NULL)
      );
  END IF;

  IF NOT EXISTS (
    SELECT 1
      FROM pg_constraint
     WHERE conname = 'users_timezone_name_check'
       AND conrelid = 'public.users'::regclass
  ) THEN
    ALTER TABLE public.users
      ADD CONSTRAINT users_timezone_name_check
      CHECK (length(timezone) BETWEEN 1 AND 64);
  END IF;
END
$$;

COMMENT ON COLUMN public.users.date_of_birth IS
  'Private date of birth supplied at registration; used for minimum-age checks and birthday messages.';
COMMENT ON COLUMN public.users.timezone IS
  'IANA time zone supplied by the browser for local birthday delivery and date calculations.';
COMMENT ON COLUMN public.users.age_13_plus_confirmed IS
  'Records the required user declaration that they are at least 13 years old.';
COMMENT ON COLUMN public.users.age_attestation_at IS
  'Server timestamp when the user confirmed the age and truthful-information declarations.';
COMMENT ON COLUMN public.users.age_attestation_version IS
  'Version of the age/truthfulness declaration presented at registration.';
