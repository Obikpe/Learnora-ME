-- Remove birthday and age-attestation data when an individual account is permanently closed.
-- The restricted deletion-history record intentionally does not retain date of birth.
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
         expires_at = NULL,
         trial_ends_at = NULL,
         date_of_birth = NULL,
         timezone = 'Africa/Lagos',
         age_13_plus_confirmed = false,
         age_attestation_at = NULL,
         age_attestation_version = NULL,
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
