DO $$
DECLARE
  v_rls boolean;
  v_browser_privileges integer;
  v_service_privileges integer;
  v_unique integer;
  v_permission integer;
  v_role_assignments integer;
BEGIN
  SELECT c.relrowsecurity INTO v_rls
  FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
  WHERE n.nspname='public' AND c.relname='learnora_track_reviews';
  IF v_rls IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'learnora_track_reviews must have RLS enabled';
  END IF;

  SELECT count(*) INTO v_browser_privileges
  FROM information_schema.role_table_grants
  WHERE table_schema='public' AND table_name='learnora_track_reviews'
    AND grantee IN ('anon','authenticated');
  IF v_browser_privileges <> 0 THEN
    RAISE EXCEPTION 'browser roles must not have direct track-review table privileges';
  END IF;

  SELECT count(*) INTO v_service_privileges
  FROM information_schema.role_table_grants
  WHERE table_schema='public' AND table_name='learnora_track_reviews'
    AND grantee='service_role' AND privilege_type IN ('SELECT','INSERT','UPDATE','DELETE');
  IF v_service_privileges <> 4 THEN
    RAISE EXCEPTION 'service_role requires select/insert/update/delete on track reviews';
  END IF;

  SELECT count(*) INTO v_unique
  FROM pg_constraint
  WHERE conrelid='public.learnora_track_reviews'::regclass
    AND conname='learnora_track_reviews_track_user_unique';
  IF v_unique <> 1 THEN
    RAISE EXCEPTION 'one review per learner per track must be enforced';
  END IF;

  SELECT count(*) INTO v_permission
  FROM public.learnora_permissions WHERE permission_key='track_reviews.moderate';
  IF v_permission <> 1 THEN
    RAISE EXCEPTION 'dedicated track review moderation permission is missing';
  END IF;

  SELECT count(*) INTO v_role_assignments
  FROM public.learnora_staff_role_permissions rp
  JOIN public.learnora_staff_roles r ON r.id=rp.role_id
  JOIN public.learnora_permissions p ON p.id=rp.permission_id
  WHERE p.permission_key='track_reviews.moderate'
    AND r.slug IN ('super_admin','learning_curriculum');
  IF v_role_assignments <> 2 THEN
    RAISE EXCEPTION 'moderation permission must be assigned to learning curriculum and super admin roles';
  END IF;
END $$;
