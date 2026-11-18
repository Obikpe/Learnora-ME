DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'lesson_videos'
      AND column_name = 'transcript_text'
      AND data_type = 'text'
  ) THEN
    RAISE EXCEPTION 'lesson_videos.transcript_text migration was not applied';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'users'
      AND column_name = 'account_status'
  ) THEN
    RAISE EXCEPTION 'users.account_status migration was not applied';
  END IF;

  IF to_regprocedure('public.complete_learner_account_deletion(text,timestamp with time zone)') IS NULL THEN
    RAISE EXCEPTION 'complete_learner_account_deletion function is missing';
  END IF;

  IF has_function_privilege('anon', 'public.complete_learner_account_deletion(text,timestamp with time zone)', 'EXECUTE')
     OR has_function_privilege('authenticated', 'public.complete_learner_account_deletion(text,timestamp with time zone)', 'EXECUTE') THEN
    RAISE EXCEPTION 'Browser roles must not execute complete_learner_account_deletion';
  END IF;

  IF NOT has_function_privilege('service_role', 'public.complete_learner_account_deletion(text,timestamp with time zone)', 'EXECUTE') THEN
    RAISE EXCEPTION 'service_role must execute complete_learner_account_deletion';
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname='public' AND indexname='certificates_course_id_idx')
     OR NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname='public' AND indexname='learner_learning_plans_source_track_id_idx')
     OR NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname='public' AND indexname='quiz_active_sessions_lesson_id_idx') THEN
    RAISE EXCEPTION 'Feature foreign-key indexes are incomplete';
  END IF;
END;
$$;
