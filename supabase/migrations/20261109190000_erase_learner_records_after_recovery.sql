-- Permanently erase all learner-owned records after the 30-day recovery window.
-- The restricted deleted_account_history row is the sole retained learner record.
-- This migration replaces the earlier soft-anonymisation finaliser.

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
  v_fk record;
  v_col record;
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
    -- Retain only the dedicated restricted history record. Do not copy the
    -- learner profile, subscription, marketing, progress or assessment data.
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
      '{}'::jsonb,
      v_user.account_deactivation_until,
      v_user.deletion_reason,
      v_user.deletion_reason_details
    )
    ON CONFLICT (original_user_id) DO UPDATE
      SET original_email = EXCLUDED.original_email,
          display_name = EXCLUDED.display_name,
          account_role = EXCLUDED.account_role,
          account_type = EXCLUDED.account_type,
          account_created_at = EXCLUDED.account_created_at,
          deletion_requested_at = EXCLUDED.deletion_requested_at,
          deleted_at = EXCLUDED.deleted_at,
          account_snapshot = '{}'::jsonb,
          deactivation_until = EXCLUDED.deactivation_until,
          deletion_reason = EXCLUDED.deletion_reason,
          deletion_reason_details = EXCLUDED.deletion_reason_details;

    -- Remove records that identify this learner in audit/security streams.
    -- The deletion history above is the sole retained lifecycle record.
    IF to_regclass('public.audit_logs') IS NOT NULL THEN
      DELETE FROM public.audit_logs
       WHERE email = v_user.email
          OR metadata ->> 'user_id' = v_user.id::text;
    END IF;

    IF to_regclass('public.security_logs') IS NOT NULL THEN
      DELETE FROM public.security_logs
       WHERE email = v_user.email
          OR metadata ->> 'user_id' = v_user.id::text;
    END IF;

    IF to_regclass('public.learnora_audit_events') IS NOT NULL THEN
      DELETE FROM public.learnora_audit_events
       WHERE actor_user_id = v_user.id
          OR metadata ->> 'user_id' = v_user.id::text;
    END IF;

    IF to_regclass('public.learnora_cohort_lifecycle_events') IS NOT NULL THEN
      DELETE FROM public.learnora_cohort_lifecycle_events
       WHERE actor_user_id = v_user.id;
    END IF;

    IF to_regclass('public.learnora_organisation_lifecycle_events') IS NOT NULL THEN
      DELETE FROM public.learnora_organisation_lifecycle_events
       WHERE actor_user_id = v_user.id;
    END IF;

    -- Remove token, request and archived-member rows that may be keyed by
    -- email rather than a user foreign key.
    IF to_regclass('public.email_verification_tokens') IS NOT NULL THEN
      DELETE FROM public.email_verification_tokens
       WHERE email = v_user.email OR user_id = v_user.id;
    END IF;

    IF to_regclass('public.password_reset_tokens') IS NOT NULL THEN
      DELETE FROM public.password_reset_tokens
       WHERE email = v_user.email OR account_id = v_user.id;
    END IF;

    IF to_regclass('public.learnora_cohort_member_archive') IS NOT NULL THEN
      DELETE FROM public.learnora_cohort_member_archive
       WHERE email = v_user.email OR source_user_id = v_user.id;
    END IF;

    IF to_regclass('public.learnora_organisation_requests') IS NOT NULL THEN
      DELETE FROM public.learnora_organisation_requests
       WHERE email = v_user.email OR portal_user_id = v_user.id;
    END IF;

    -- Creator-owned ledger, payout and sale rows can RESTRICT deletion
    -- of the creator profile. Remove them before deleting that profile.
    IF to_regclass('public.learnora_creator_ledger') IS NOT NULL
       AND to_regclass('public.learnora_creator_accounts') IS NOT NULL THEN
      DELETE FROM public.learnora_creator_ledger
       WHERE creator_id IN (
         SELECT id FROM public.learnora_creator_accounts WHERE user_id = v_user.id
       );
    END IF;

    IF to_regclass('public.learnora_creator_payouts') IS NOT NULL
       AND to_regclass('public.learnora_creator_accounts') IS NOT NULL THEN
      DELETE FROM public.learnora_creator_payouts
       WHERE creator_id IN (
         SELECT id FROM public.learnora_creator_accounts WHERE user_id = v_user.id
       );
    END IF;

    IF to_regclass('public.learnora_creator_sales') IS NOT NULL
       AND to_regclass('public.learnora_creator_accounts') IS NOT NULL THEN
      DELETE FROM public.learnora_creator_sales
       WHERE creator_id IN (
         SELECT id FROM public.learnora_creator_accounts WHERE user_id = v_user.id
       );
    END IF;

    -- Delete every row whose foreign key RESTRICTs deletion of the learner.
    -- This covers purchases, subscriptions, creator/staff identity rows and
    -- any future restrictive FK added to users without hard-coding its name.
    FOR v_fk IN
      SELECT
        child.relname AS table_name,
        child_col.attname AS column_name
      FROM pg_constraint fk
      JOIN pg_class child ON child.oid = fk.conrelid
      JOIN pg_namespace child_ns ON child_ns.oid = child.relnamespace
      JOIN pg_class parent ON parent.oid = fk.confrelid
      JOIN pg_namespace parent_ns ON parent_ns.oid = parent.relnamespace
      JOIN LATERAL unnest(fk.conkey) WITH ORDINALITY AS child_key(attnum, ord) ON true
      JOIN LATERAL unnest(fk.confkey) WITH ORDINALITY AS parent_key(attnum, ord)
        ON parent_key.ord = child_key.ord
      JOIN pg_attribute child_col
        ON child_col.attrelid = child.oid AND child_col.attnum = child_key.attnum
      JOIN pg_attribute parent_col
        ON parent_col.attrelid = parent.oid AND parent_col.attnum = parent_key.attnum
      WHERE fk.contype = 'f'
        AND fk.confdeltype = 'r'
        AND child_ns.nspname = 'public'
        AND parent_ns.nspname = 'public'
        AND parent.relname = 'users'
        AND parent_col.attname = 'id'
    LOOP
      EXECUTE format(
        'DELETE FROM public.%I WHERE %I = $1',
        v_fk.table_name,
        v_fk.column_name
      ) USING v_user.id;
    END LOOP;

    -- Remove learner-owned rows across both FK-backed and legacy tables.
    -- Actor/creator columns are deliberately excluded: deleting a learner
    -- must not delete shared catalogue or organisation resources they helped
    -- create; their user FK is set NULL by its declared FK action.
    FOR v_col IN
      SELECT DISTINCT c.table_name, c.column_name
      FROM information_schema.columns c
      WHERE c.table_schema = 'public'
        AND c.data_type = 'uuid'
        AND c.column_name IN (
          'user_id',
          'learner_id',
          'owner_user_id',
          'buyer_user_id',
          'portal_user_id'
        )
        AND c.table_name NOT IN (
          'deleted_account_history'
        )
    LOOP
      EXECUTE format(
        'DELETE FROM public.%I WHERE %I = $1',
        v_col.table_name,
        v_col.column_name
      ) USING v_user.id;
    END LOOP;

    -- Clear account-linked contact data from any remaining email-keyed token
    -- rows before removing the live user identity.
    IF to_regclass('public.learner_marketing_unsubscribe_tokens') IS NOT NULL THEN
      DELETE FROM public.learner_marketing_unsubscribe_tokens
       WHERE user_id = v_user.id;
    END IF;

    -- The actual users row is deleted, not anonymised or left as a tombstone.
    -- ON DELETE CASCADE removes the remaining FK-cascaded learner records;
    -- ON DELETE SET NULL preserves shared resources without learner linkage.
    DELETE FROM public.users WHERE id = v_user.id;

    v_count := v_count + 1;
  END LOOP;

  RETURN v_count;
END;
$$;

REVOKE ALL ON FUNCTION public.finalize_expired_learner_account_deletions(timestamptz)
  FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.finalize_expired_learner_account_deletions(timestamptz)
  TO service_role;
