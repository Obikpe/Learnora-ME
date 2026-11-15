-- Rollback for 20261116120000_notification_email_automation.sql.
-- This removes only notification delivery metadata and automation timestamps.
BEGIN;

DROP FUNCTION IF EXISTS public.finish_learner_notification_delivery(uuid, text, text, boolean, text, timestamptz);
DROP FUNCTION IF EXISTS public.claim_learner_notification_delivery(uuid, text, text, timestamptz);

DROP TABLE IF EXISTS public.learner_notification_deliveries;

ALTER TABLE IF EXISTS public.users
  DROP COLUMN IF EXISTS last_inactivity_email_at;

ALTER TABLE IF EXISTS public.learner_onboarding_profiles
  DROP COLUMN IF EXISTS onboarding_completed_at;

COMMIT;
