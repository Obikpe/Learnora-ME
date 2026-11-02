ALTER TABLE public.users
  ADD COLUMN IF NOT EXISTS account_status text NOT NULL DEFAULT 'active',
  ADD COLUMN IF NOT EXISTS account_deletion_token_hash text,
  ADD COLUMN IF NOT EXISTS account_deletion_expires_at timestamptz,
  ADD COLUMN IF NOT EXISTS account_deletion_requested_at timestamptz,
  ADD COLUMN IF NOT EXISTS deleted_at timestamptz;

ALTER TABLE public.users
  DROP CONSTRAINT IF EXISTS users_account_status_check;
ALTER TABLE public.users
  ADD CONSTRAINT users_account_status_check
  CHECK (account_status IN ('active', 'deletion_pending', 'deleted'));

CREATE UNIQUE INDEX IF NOT EXISTS users_account_deletion_token_hash_uidx
  ON public.users (account_deletion_token_hash)
  WHERE account_deletion_token_hash IS NOT NULL;

CREATE TABLE IF NOT EXISTS public.deleted_account_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  original_user_id uuid NOT NULL UNIQUE,
  original_email text NOT NULL,
  display_name text,
  account_role text,
  account_type text NOT NULL DEFAULT 'learner',
  account_created_at timestamptz,
  deletion_requested_at timestamptz,
  deleted_at timestamptz NOT NULL,
  account_snapshot jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS deleted_account_history_deleted_at_idx
  ON public.deleted_account_history (deleted_at DESC);

ALTER TABLE public.deleted_account_history ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.deleted_account_history FROM PUBLIC, anon, authenticated;
GRANT ALL ON public.deleted_account_history TO service_role;

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
     AND account_status IN ('active', 'deletion_pending')
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

  INSERT INTO public.deleted_account_history (
    original_user_id,
    original_email,
    display_name,
    account_role,
    account_type,
    account_created_at,
    deletion_requested_at,
    deleted_at,
    account_snapshot
  )
  VALUES (
    v_user.id,
    v_user.email,
    v_user.name,
    v_user.role,
    'learner',
    v_user.created_at,
    v_user.account_deletion_requested_at,
    p_deleted_at,
    jsonb_build_object(
      'email_verified_at', v_user.email_verified_at,
      'sub_status', v_user.sub_status,
      'is_paid', v_user.is_paid,
      'subscription_tier', v_user.subscription_tier,
      'expires_at', v_user.expires_at,
      'trial_ends_at', v_user.trial_ends_at
    )
  )
  ON CONFLICT (original_user_id) DO NOTHING;

  IF NOT FOUND THEN
    RETURN false;
  END IF;

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
         account_deletion_token_hash = NULL,
         account_deletion_expires_at = NULL,
         account_deletion_requested_at = NULL,
         deleted_at = p_deleted_at
   WHERE id = v_user.id;

  RETURN true;
END;
$$;

REVOKE ALL ON FUNCTION public.complete_learner_account_deletion(text, timestamptz) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.complete_learner_account_deletion(text, timestamptz) TO service_role;
