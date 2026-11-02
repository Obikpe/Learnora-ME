-- Assertions for the learner plan migration on a disposable PostgreSQL/Supabase-schema fixture.
DO $$
DECLARE
  plans_oid regclass := to_regclass('public.learner_learning_plans');
  rls_enabled boolean;
BEGIN
  IF plans_oid IS NULL THEN
    RAISE EXCEPTION 'learner_learning_plans table was not created';
  END IF;

  SELECT c.relrowsecurity
    INTO rls_enabled
    FROM pg_class c
   WHERE c.oid = plans_oid;
  IF NOT COALESCE(rls_enabled, false) THEN
    RAISE EXCEPTION 'learner_learning_plans must have RLS enabled';
  END IF;

  IF has_table_privilege('anon', plans_oid, 'SELECT')
     OR has_table_privilege('anon', plans_oid, 'INSERT')
     OR has_table_privilege('authenticated', plans_oid, 'SELECT')
     OR has_table_privilege('authenticated', plans_oid, 'INSERT') THEN
    RAISE EXCEPTION 'browser roles must not have direct learner plan table access';
  END IF;

  IF NOT has_table_privilege('service_role', plans_oid, 'SELECT')
     OR NOT has_table_privilege('service_role', plans_oid, 'INSERT')
     OR NOT has_table_privilege('service_role', plans_oid, 'UPDATE')
     OR NOT has_table_privilege('service_role', plans_oid, 'DELETE') THEN
    RAISE EXCEPTION 'service_role must have the required backend table privileges';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
     WHERE conrelid = plans_oid
       AND contype = 'f'
       AND conname LIKE '%user_id%'
  ) THEN
    RAISE EXCEPTION 'learner_learning_plans must retain its user foreign key';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
     WHERE schemaname = 'public'
       AND tablename = 'learner_learning_plans'
       AND indexname = 'learner_learning_plans_user_status_created_idx'
  ) THEN
    RAISE EXCEPTION 'learner plan owner/status index is missing';
  END IF;
END $$;
