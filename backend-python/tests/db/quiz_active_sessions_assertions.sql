DO $$
DECLARE
  v_rls boolean;
  v_browser_privileges integer;
  v_service_privileges integer;
  v_unique_constraint integer;
BEGIN
  SELECT c.relrowsecurity INTO v_rls
  FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
  WHERE n.nspname='public' AND c.relname='quiz_active_sessions';
  IF v_rls IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'quiz_active_sessions must have RLS enabled';
  END IF;

  SELECT count(*) INTO v_browser_privileges
  FROM information_schema.role_table_grants
  WHERE table_schema='public' AND table_name='quiz_active_sessions'
    AND grantee IN ('anon','authenticated');
  IF v_browser_privileges <> 0 THEN
    RAISE EXCEPTION 'browser roles must not have direct quiz session table privileges';
  END IF;

  SELECT count(*) INTO v_service_privileges
  FROM information_schema.role_table_grants
  WHERE table_schema='public' AND table_name='quiz_active_sessions'
    AND grantee='service_role' AND privilege_type IN ('SELECT','INSERT','UPDATE','DELETE');
  IF v_service_privileges <> 4 THEN
    RAISE EXCEPTION 'service_role requires select/insert/update/delete on quiz_active_sessions';
  END IF;

  SELECT count(*) INTO v_unique_constraint
  FROM pg_constraint
  WHERE conrelid='public.quiz_active_sessions'::regclass
    AND conname='quiz_active_sessions_user_quiz_unique';
  IF v_unique_constraint <> 1 THEN
    RAISE EXCEPTION 'quiz_active_sessions must enforce one current session per learner and quiz';
  END IF;
END $$;
