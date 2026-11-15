-- Database assertions for the notification delivery automation migration.
DO $$
DECLARE
  v_delivery_table oid := to_regclass('public.learner_notification_deliveries');
  v_claim regprocedure := to_regprocedure('public.claim_learner_notification_delivery(uuid,text,text,timestamp with time zone)');
  v_finish regprocedure := to_regprocedure('public.finish_learner_notification_delivery(uuid,text,text,boolean,text,timestamp with time zone)');
BEGIN
  IF v_delivery_table IS NULL THEN
    RAISE EXCEPTION 'learner_notification_deliveries table is missing';
  END IF;
  IF NOT (SELECT relrowsecurity FROM pg_class WHERE oid = v_delivery_table) THEN
    RAISE EXCEPTION 'learner_notification_deliveries must have RLS enabled';
  END IF;
  IF has_table_privilege('anon', v_delivery_table, 'SELECT')
     OR has_table_privilege('authenticated', v_delivery_table, 'SELECT')
     OR has_table_privilege('anon', v_delivery_table, 'INSERT')
     OR has_table_privilege('authenticated', v_delivery_table, 'INSERT') THEN
    RAISE EXCEPTION 'Browser roles must not access delivery records';
  END IF;
  IF v_claim IS NULL OR v_finish IS NULL THEN
    RAISE EXCEPTION 'Notification delivery RPC functions are missing';
  END IF;
  IF NOT has_function_privilege('service_role', v_claim, 'EXECUTE')
     OR NOT has_function_privilege('service_role', v_finish, 'EXECUTE') THEN
    RAISE EXCEPTION 'service_role must be able to execute delivery RPC functions';
  END IF;
  IF has_function_privilege('anon', v_claim, 'EXECUTE')
     OR has_function_privilege('authenticated', v_claim, 'EXECUTE')
     OR has_function_privilege('anon', v_finish, 'EXECUTE')
     OR has_function_privilege('authenticated', v_finish, 'EXECUTE') THEN
    RAISE EXCEPTION 'Browser roles must not execute notification delivery RPC functions';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = v_delivery_table
      AND contype = 'u'
      AND pg_get_constraintdef(oid) ILIKE '%user_id, event_key, channel%'
  ) THEN
    RAISE EXCEPTION 'Recipient/event/channel uniqueness constraint is missing';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='public' AND table_name='users'
      AND column_name='last_inactivity_email_at'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='public' AND table_name='learner_onboarding_profiles'
      AND column_name='onboarding_completed_at'
  ) THEN
    RAISE EXCEPTION 'Notification automation timestamp columns are missing';
  END IF;
END $$;
