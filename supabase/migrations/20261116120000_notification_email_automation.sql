-- Durable, idempotent delivery tracking for approved automated learner messages.
-- All access is backend/service-role only; learners continue to read notifications
-- through the authenticated notifications API.

ALTER TABLE public.users
  ADD COLUMN IF NOT EXISTS last_inactivity_email_at timestamptz;

ALTER TABLE public.learner_onboarding_profiles
  ADD COLUMN IF NOT EXISTS onboarding_completed_at timestamptz;

UPDATE public.learner_onboarding_profiles
   SET onboarding_completed_at = COALESCE(updated_at, created_at, now())
 WHERE onboarding_completed = true
   AND onboarding_completed_at IS NULL;

CREATE TABLE IF NOT EXISTS public.learner_notification_deliveries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  event_key text NOT NULL,
  channel text NOT NULL CHECK (channel IN ('in_app', 'email')),
  status text NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'sending', 'sent', 'failed', 'suppressed')),
  attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
  next_attempt_at timestamptz NOT NULL DEFAULT now(),
  sent_at timestamptz,
  last_error text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (user_id, event_key, channel)
);

CREATE INDEX IF NOT EXISTS learner_notification_deliveries_retry_idx
  ON public.learner_notification_deliveries (status, next_attempt_at)
  WHERE status IN ('pending', 'failed', 'sending');

ALTER TABLE public.learner_notification_deliveries ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.learner_notification_deliveries FROM PUBLIC, anon, authenticated;
GRANT ALL ON public.learner_notification_deliveries TO service_role;

CREATE OR REPLACE FUNCTION public.claim_learner_notification_delivery(
  p_user_id uuid,
  p_event_key text,
  p_channel text,
  p_now timestamptz DEFAULT now()
) RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
  v_id uuid;
BEGIN
  IF p_channel NOT IN ('in_app', 'email') OR length(p_event_key) < 1 OR length(p_event_key) > 240 THEN
    RAISE EXCEPTION 'Invalid notification delivery key or channel';
  END IF;

  INSERT INTO public.learner_notification_deliveries (
    user_id, event_key, channel, status, attempts, next_attempt_at, created_at, updated_at
  ) VALUES (
    p_user_id, p_event_key, p_channel, 'sending', 1, p_now, p_now, p_now
  )
  ON CONFLICT (user_id, event_key, channel) DO UPDATE
    SET status = 'sending',
        attempts = public.learner_notification_deliveries.attempts + 1,
        next_attempt_at = p_now,
        updated_at = p_now,
        last_error = NULL
    WHERE (
      public.learner_notification_deliveries.status IN ('pending', 'failed')
      AND public.learner_notification_deliveries.next_attempt_at <= p_now
    ) OR (
      public.learner_notification_deliveries.status = 'sending'
      AND public.learner_notification_deliveries.updated_at < p_now - interval '15 minutes'
    )
  RETURNING id INTO v_id;

  RETURN v_id IS NOT NULL;
END;
$$;

CREATE OR REPLACE FUNCTION public.finish_learner_notification_delivery(
  p_user_id uuid,
  p_event_key text,
  p_channel text,
  p_success boolean,
  p_error text DEFAULT NULL,
  p_now timestamptz DEFAULT now()
) RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
  UPDATE public.learner_notification_deliveries
     SET status = CASE WHEN p_success THEN 'sent' ELSE 'failed' END,
         sent_at = CASE WHEN p_success THEN p_now ELSE sent_at END,
         next_attempt_at = CASE WHEN p_success THEN p_now ELSE p_now + interval '1 hour' END,
         last_error = CASE WHEN p_success THEN NULL ELSE left(coalesce(p_error, 'Delivery failed'), 500) END,
         updated_at = p_now
   WHERE user_id = p_user_id
     AND event_key = p_event_key
     AND channel = p_channel
     AND status = 'sending';
END;
$$;

REVOKE ALL ON FUNCTION public.claim_learner_notification_delivery(uuid, text, text, timestamptz) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.finish_learner_notification_delivery(uuid, text, text, boolean, text, timestamptz) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.claim_learner_notification_delivery(uuid, text, text, timestamptz) TO service_role;
GRANT EXECUTE ON FUNCTION public.finish_learner_notification_delivery(uuid, text, text, boolean, text, timestamptz) TO service_role;
