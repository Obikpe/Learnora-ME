-- Learner account deletion grace period and explicit marketing consent.
-- Existing deletion confirmation tokens remain short-lived; confirmation now
-- deactivates the account for 30 days instead of immediately anonymising it.

ALTER TABLE public.users
  ADD COLUMN IF NOT EXISTS account_deactivation_until timestamptz,
  ADD COLUMN IF NOT EXISTS account_reactivation_token_hash text,
  ADD COLUMN IF NOT EXISTS account_reactivation_expires_at timestamptz,
  ADD COLUMN IF NOT EXISTS deletion_reason text,
  ADD COLUMN IF NOT EXISTS deletion_reason_details text,
  ADD COLUMN IF NOT EXISTS marketing_email_opt_in boolean NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS marketing_in_app_opt_in boolean NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS marketing_consent_at timestamptz,
  ADD COLUMN IF NOT EXISTS marketing_consent_source text,
  ADD COLUMN IF NOT EXISTS marketing_unsubscribed_at timestamptz;

ALTER TABLE public.users
  DROP CONSTRAINT IF EXISTS users_account_status_check;
ALTER TABLE public.users
  ADD CONSTRAINT users_account_status_check
  CHECK (account_status IN ('active', 'deletion_pending', 'deactivation_pending', 'deleted'));

CREATE UNIQUE INDEX IF NOT EXISTS users_account_reactivation_token_hash_uidx
  ON public.users (account_reactivation_token_hash)
  WHERE account_reactivation_token_hash IS NOT NULL;

CREATE TABLE IF NOT EXISTS public.learner_marketing_unsubscribe_tokens (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  token_hash text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  consumed_at timestamptz
);

CREATE INDEX IF NOT EXISTS learner_marketing_unsubscribe_tokens_user_idx
  ON public.learner_marketing_unsubscribe_tokens (user_id, created_at DESC);

ALTER TABLE public.learner_marketing_unsubscribe_tokens ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.learner_marketing_unsubscribe_tokens FROM PUBLIC, anon, authenticated;
GRANT ALL ON public.learner_marketing_unsubscribe_tokens TO service_role;

CREATE INDEX IF NOT EXISTS users_deactivation_due_idx
  ON public.users (account_deactivation_until)
  WHERE account_status = 'deactivation_pending';

ALTER TABLE public.deleted_account_history
  ADD COLUMN IF NOT EXISTS deactivation_until timestamptz,
  ADD COLUMN IF NOT EXISTS deletion_reason text,
  ADD COLUMN IF NOT EXISTS deletion_reason_details text;

-- The confirmation RPC now starts the 30-day grace period. It does not
-- anonymise the learner or remove their learning history.
CREATE OR REPLACE FUNCTION public.complete_learner_account_deletion(
  p_token_hash text,
  p_deleted_at timestamptz
)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
  v_user public.users%ROWTYPE;
BEGIN
  SELECT *
    INTO v_user
    FROM public.users
   WHERE account_deletion_token_hash = p_token_hash
     AND account_status = 'deletion_pending'
     AND account_deletion_expires_at > p_deleted_at
   FOR UPDATE;

  IF NOT FOUND OR v_user.role IS DISTINCT FROM 'normal' THEN
    RETURN false;
  END IF;

  IF EXISTS (
    SELECT 1
      FROM public.organisation_members
     WHERE user_id = v_user.id
       AND role = 'owner'
       AND status = 'active'
  ) THEN
    RETURN false;
  END IF;

  UPDATE public.users
     SET account_status = 'deactivation_pending',
         account_deactivation_until = p_deleted_at + interval '30 days',
         account_deletion_token_hash = NULL,
         account_deletion_expires_at = NULL,
         account_reactivation_token_hash = NULL,
         account_reactivation_expires_at = NULL
   WHERE id = v_user.id;

  RETURN true;
END;
$$;

REVOKE ALL ON FUNCTION public.complete_learner_account_deletion(text, timestamptz) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.complete_learner_account_deletion(text, timestamptz) TO service_role;

-- Daily Vercel cron calls this bounded, concurrency-safe finalizer. Rows are
-- locked with SKIP LOCKED so overlapping invocations cannot finalise twice.
CREATE OR REPLACE FUNCTION public.finalize_expired_learner_account_deletions(
  p_now timestamptz DEFAULT now()
)
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
  v_user public.users%ROWTYPE;
  v_count integer := 0;
BEGIN
  FOR v_user IN
    SELECT *
      FROM public.users
     WHERE account_status = 'deactivation_pending'
       AND account_deactivation_until IS NOT NULL
       AND account_deactivation_until <= p_now
     ORDER BY account_deactivation_until, id
     LIMIT 100
     FOR UPDATE SKIP LOCKED
  LOOP
    INSERT INTO public.deleted_account_history (
      original_user_id,
      original_email,
      display_name,
      account_role,
      account_type,
      account_created_at,
      deletion_requested_at,
      deleted_at,
      account_snapshot,
      deactivation_until,
      deletion_reason,
      deletion_reason_details
    )
    VALUES (
      v_user.id,
      v_user.email,
      v_user.name,
      v_user.role,
      'learner',
      v_user.created_at,
      v_user.account_deletion_requested_at,
      p_now,
      jsonb_build_object(
        'email_verified_at', v_user.email_verified_at,
        'sub_status', v_user.sub_status,
        'is_paid', v_user.is_paid,
        'subscription_tier', v_user.subscription_tier,
        'expires_at', v_user.expires_at,
        'trial_ends_at', v_user.trial_ends_at,
        'marketing_email_opt_in', v_user.marketing_email_opt_in,
        'marketing_in_app_opt_in', v_user.marketing_in_app_opt_in,
        'marketing_consent_at', v_user.marketing_consent_at,
        'marketing_consent_source', v_user.marketing_consent_source,
        'marketing_unsubscribed_at', v_user.marketing_unsubscribed_at
      ),
      v_user.account_deactivation_until,
      v_user.deletion_reason,
      v_user.deletion_reason_details
    )
    ON CONFLICT (original_user_id) DO NOTHING;

    UPDATE public.learner_marketing_unsubscribe_tokens
       SET consumed_at = p_now
     WHERE user_id = v_user.id
       AND consumed_at IS NULL;

    UPDATE public.organisation_members
       SET status = 'suspended'
     WHERE user_id = v_user.id
       AND status = 'active';

    UPDATE public.organisation_team_members
       SET status = 'inactive'
     WHERE user_id = v_user.id
       AND status = 'active';

    UPDATE public.organisation_teams
       SET manager_user_id = NULL
     WHERE manager_user_id = v_user.id;

    UPDATE public.users
       SET email = 'deleted+' || replace(v_user.id::text, '-', '') || '@deleted.learnora.invalid',
           name = 'Deleted learner',
           password_hash = NULL,
           email_verified = false,
           email_verified_at = NULL,
           email_verification_token_hash = NULL,
           email_verification_expires_at = NULL,
           password_reset_token_hash = NULL,
           password_reset_expires_at = NULL,
           account_status = 'deleted',
           sub_status = 'deleted',
           is_paid = false,
           subscription_tier = 'deleted',
           expires_at = NULL,
           trial_ends_at = NULL,
           account_deletion_token_hash = NULL,
           account_deletion_expires_at = NULL,
           account_deletion_requested_at = NULL,
           account_reactivation_token_hash = NULL,
           account_reactivation_expires_at = NULL,
           account_deactivation_until = NULL,
           marketing_email_opt_in = false,
           marketing_in_app_opt_in = false,
           marketing_consent_at = NULL,
           marketing_consent_source = NULL,
           marketing_unsubscribed_at = p_now,
           deleted_at = p_now
     WHERE id = v_user.id;

    INSERT INTO public.audit_logs (
      action, email, account_type, role, metadata, created_at
    )
    VALUES (
      'learner_account_deleted',
      v_user.email,
      'learner',
      v_user.role,
      jsonb_build_object(
        'user_id', v_user.id,
        'deletion_reason', v_user.deletion_reason,
        'deactivation_until', v_user.account_deactivation_until,
        'history_retained', true
      ),
      p_now
    );

    v_count := v_count + 1;
  END LOOP;

  RETURN v_count;
END;
$$;

REVOKE ALL ON FUNCTION public.finalize_expired_learner_account_deletions(timestamptz) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.finalize_expired_learner_account_deletions(timestamptz) TO service_role;
