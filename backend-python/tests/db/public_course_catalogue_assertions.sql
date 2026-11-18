BEGIN;

DO $$
DECLARE
  v_course_id uuid := gen_random_uuid();
  v_path_id uuid := gen_random_uuid();
  v_hidden_course_id uuid := gen_random_uuid();
  v_organisation_id uuid := gen_random_uuid();
  v_organisation_course_id uuid := gen_random_uuid();
  v_tracks jsonb;
BEGIN
  INSERT INTO public.learnora_courses (
    id, title, slug, status, ownership, settings
  ) VALUES (
    v_course_id, 'CI public catalogue course',
    'ci-public-' || replace(v_course_id::text, '-', ''),
    'published', 'learnora', '{}'::jsonb
  );

  INSERT INTO public.learnora_learning_paths (
    id, name, slug, description, status, owner_user_id, organisation_id
  ) VALUES (
    v_path_id, 'CI public track',
    'ci-track-' || replace(v_path_id::text, '-', ''),
    'Public track fixture', 'published', NULL, NULL
  );

  INSERT INTO public.learnora_learning_path_courses (
    path_id, course_id, order_index, required
  ) VALUES (v_path_id, v_course_id, 0, true);

  INSERT INTO public.learnora_courses (
    id, title, slug, status, ownership, settings
  ) VALUES (
    v_hidden_course_id, 'CI unpublished course',
    'ci-hidden-' || replace(v_hidden_course_id::text, '-', ''),
    'draft', 'learnora', '{}'::jsonb
  );

  INSERT INTO public.organisations (
    id, name, slug, organisation_type, template, is_active, settings
  ) VALUES (
    v_organisation_id, 'CI public organisation',
    'ci-org-' || replace(v_organisation_id::text, '-', ''),
    'academy', 'academy', true, '{"public_directory": true, "pilot_mode": true}'::jsonb
  );

  INSERT INTO public.learnora_courses (
    id, organisation_id, title, slug, status, ownership, settings
  ) VALUES (
    v_organisation_course_id, v_organisation_id,
    'CI public organisation course',
    'ci-org-course-' || replace(v_organisation_course_id::text, '-', ''),
    'published', 'organisation', '{"public_catalogue": true}'::jsonb
  );

  SELECT catalogue.tracks
    INTO v_tracks
    FROM public.get_public_course_catalogue() AS catalogue
   WHERE catalogue.id = v_course_id;

  IF jsonb_array_length(COALESCE(v_tracks, '[]'::jsonb)) <> 1 THEN
    RAISE EXCEPTION 'Global public course must include its published global track';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM public.get_public_course_catalogue()
    WHERE id = v_organisation_course_id
  ) THEN
    RAISE EXCEPTION 'Opted-in organisation course must appear in the public catalogue';
  END IF;

  IF EXISTS (
    SELECT 1 FROM public.get_public_course_catalogue()
    WHERE id = v_hidden_course_id
  ) THEN
    RAISE EXCEPTION 'Unpublished course must not appear in the public catalogue';
  END IF;

  IF has_function_privilege('anon', 'public.get_public_course_catalogue()', 'EXECUTE')
     OR has_function_privilege('authenticated', 'public.get_public_course_catalogue()', 'EXECUTE') THEN
    RAISE EXCEPTION 'Browser roles must not execute the public catalogue RPC directly';
  END IF;

  IF NOT has_function_privilege('service_role', 'public.get_public_course_catalogue()', 'EXECUTE') THEN
    RAISE EXCEPTION 'service_role must execute the public catalogue RPC';
  END IF;
END;
$$;

ROLLBACK;
