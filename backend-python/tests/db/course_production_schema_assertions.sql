BEGIN;

DO $course_production_test$
DECLARE
    v_user_id uuid := 'e1000000-0000-4000-8000-000000000001';
    v_staff_id uuid := 'e1000000-0000-4000-8000-000000000002';
    v_track_id uuid := 'e1000000-0000-4000-8000-000000000004';
    v_job_id uuid := 'e1000000-0000-4000-8000-000000000003';
    v_course_id uuid;
    v_second_course_id uuid;
    v_published_course_id uuid;
    v_published_course_id_again uuid;
    v_lesson_id uuid;
    v_human_lesson_id uuid;
    v_human_video_id uuid;
    v_content text;
    v_course_status text;
    v_module_status text;
    v_lesson_status text;
    v_job_status text;
    v_quiz_id uuid;
    v_quiz_published boolean;
    v_question_count integer;
    v_correct_answer text;
    v_render_job_id uuid;
    v_claim jsonb;
    v_object_key text;
    v_video_id uuid;
    v_render_status text;
    v_package_status text;
    v_video_status text;
    v_published_course_status text;
    v_published_module_status text;
    v_published_lesson_status text;
    v_published_job_status text;
    v_track_order integer;
BEGIN
    IF to_regclass('public.learnora_course_generation_jobs') IS NULL
       OR to_regclass('public.learnora_lesson_production_packages') IS NULL THEN
        RAISE EXCEPTION 'AI course production tables are missing';
    END IF;

    IF NOT (SELECT relrowsecurity FROM pg_class WHERE oid = 'public.learnora_course_generation_jobs'::regclass)
       OR NOT (SELECT relrowsecurity FROM pg_class WHERE oid = 'public.learnora_lesson_production_packages'::regclass)
       OR NOT (SELECT relrowsecurity FROM pg_class WHERE oid = 'public.learnora_video_render_jobs'::regclass) THEN
        RAISE EXCEPTION 'AI course production tables must have RLS enabled';
    END IF;

    IF NOT EXISTS (
        SELECT 1
          FROM pg_indexes
         WHERE schemaname = 'public'
           AND indexname = 'idx_lesson_videos_cloudflare_storage_path'
    ) THEN
        RAISE EXCEPTION 'Cloudflare lesson-video storage identity must be unique for retry safety';
    END IF;

    IF has_table_privilege('anon', 'public.learnora_course_generation_jobs', 'SELECT')
       OR has_table_privilege('authenticated', 'public.learnora_course_generation_jobs', 'SELECT')
       OR has_table_privilege('anon', 'public.learnora_lesson_production_packages', 'SELECT')
       OR has_table_privilege('authenticated', 'public.learnora_lesson_production_packages', 'SELECT')
       OR has_table_privilege('anon', 'public.learnora_video_render_jobs', 'SELECT')
       OR has_table_privilege('authenticated', 'public.learnora_video_render_jobs', 'SELECT') THEN
        RAISE EXCEPTION 'AI course production tables must not be directly readable by browser roles';
    END IF;

    IF NOT has_table_privilege('service_role', 'public.learnora_course_generation_jobs', 'SELECT')
       OR NOT has_table_privilege('service_role', 'public.learnora_lesson_production_packages', 'INSERT')
       OR NOT has_table_privilege('service_role', 'public.learnora_video_render_jobs', 'SELECT') THEN
        RAISE EXCEPTION 'service_role is missing required AI course production table grants';
    END IF;

    IF has_function_privilege('anon', 'public.create_course_from_generation_job(uuid)', 'EXECUTE')
       OR has_function_privilege('authenticated', 'public.create_course_from_generation_job(uuid)', 'EXECUTE')
       OR NOT has_function_privilege('service_role', 'public.create_course_from_generation_job(uuid)', 'EXECUTE')
       OR has_function_privilege('anon', 'public.publish_course_from_generation_job(uuid)', 'EXECUTE')
       OR has_function_privilege('authenticated', 'public.publish_course_from_generation_job(uuid)', 'EXECUTE')
       OR NOT has_function_privilege('service_role', 'public.publish_course_from_generation_job(uuid)', 'EXECUTE')
       OR has_function_privilege('anon', 'public.claim_next_learnora_video_render_job()', 'EXECUTE')
       OR has_function_privilege('authenticated', 'public.claim_next_learnora_video_render_job()', 'EXECUTE')
       OR NOT has_function_privilege('service_role', 'public.claim_next_learnora_video_render_job()', 'EXECUTE')
       OR has_function_privilege('anon', 'public.requeue_stale_learnora_video_render_jobs(integer)', 'EXECUTE')
       OR has_function_privilege('authenticated', 'public.requeue_stale_learnora_video_render_jobs(integer)', 'EXECUTE')
       OR NOT has_function_privilege('service_role', 'public.requeue_stale_learnora_video_render_jobs(integer)', 'EXECUTE')
       OR has_function_privilege('anon', 'public.complete_learnora_video_render_job(uuid,uuid,integer,bigint,text)', 'EXECUTE')
       OR has_function_privilege('authenticated', 'public.complete_learnora_video_render_job(uuid,uuid,integer,bigint,text)', 'EXECUTE')
       OR NOT has_function_privilege('service_role', 'public.complete_learnora_video_render_job(uuid,uuid,integer,bigint,text)', 'EXECUTE') THEN
        RAISE EXCEPTION 'Course creation RPC grants are not restricted to service_role';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM public.learnora_permissions WHERE permission_key = 'content.generate'
    ) THEN
        RAISE EXCEPTION 'content.generate permission was not seeded';
    END IF;

    IF EXISTS (SELECT 1 FROM public.learnora_staff_roles WHERE slug = 'learning_curriculum')
       AND NOT EXISTS (
           SELECT 1
             FROM public.learnora_staff_role_permissions rp
             JOIN public.learnora_staff_roles r ON r.id = rp.role_id
             JOIN public.learnora_permissions p ON p.id = rp.permission_id
            WHERE r.slug = 'learning_curriculum'
              AND p.permission_key = 'content.generate'
       ) THEN
        RAISE EXCEPTION 'learning_curriculum role is missing content.generate';
    END IF;

    INSERT INTO public.users (id, email, name)
    VALUES (v_user_id, 'course-studio-ci@example.invalid', 'Course Studio CI')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO public.learnora_staff_accounts (id, user_id, status)
    VALUES (v_staff_id, v_user_id, 'active')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO public.learnora_learning_paths (id, name, slug, status)
    VALUES (v_track_id, 'Course Studio CI Track', 'course-studio-ci-track', 'draft')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO public.learnora_course_generation_jobs (
        id, created_by_staff_id, created_by_user_id, approved_by_staff_id, target_track_id,
        course_title, course_slug, course_level, status, request_data, curriculum_data,
        provider_key, model, approved_at
    )
    VALUES (
        v_job_id, v_staff_id, v_user_id, v_staff_id, v_track_id,
        'Course Studio CI Test', 'course-studio-ci-test-unique', 'beginner', 'approved',
        '{}'::jsonb,
        '{
          "course_title":"Course Studio CI Test",
          "short_description":"A private course draft used by the schema test.",
          "course_description":"This course verifies that approved AI production packages create draft curriculum records.",
          "learning_outcomes":["Explain the test concept."],
          "prerequisites":[],
          "modules":[{
            "title":"Test Module",
            "description":"A module created only inside this transaction.",
            "lessons":[{
              "title":"Test Lesson",
              "description":"A lesson created only inside this transaction.",
              "learning_objective":"Explain the lesson objective.",
              "lesson_format":"narrated_visual",
              "estimated_minutes":2
            },{
              "title":"Human Video Lesson",
              "description":"A human-produced demonstration lesson.",
              "learning_objective":"Apply the concept in a practical demonstration.",
              "lesson_format":"demonstration",
              "estimated_minutes":3
            }]
          }]
        }'::jsonb,
        'openrouter', 'openrouter/free', now()
    );

    INSERT INTO public.learnora_lesson_production_packages (
        job_id, module_order, lesson_order, version, module_title,
        lesson_title, lesson_description, learning_objective, lesson_format, video_source,
        teaching_script, estimated_duration_seconds, concise_note, practice_activity,
        knowledge_check, video_plan, fact_check_notes, status, provider_key, model,
        approved_by_staff_id, approved_at
    )
    VALUES (
        v_job_id, 0, 0, 1, 'Test Module',
        'Test Lesson', 'A lesson created only inside this transaction.',
        'Explain the lesson objective.', 'narrated_visual', 'ai',
        'This is the private teaching script. It explains the concept, demonstrates an example, and concludes with a recap.',
        120, 'A short learner-facing note.', 'Try applying the concept to one example.',
        '[{"question":"Which option is correct?","options":["Option A","Option B"],"correct_option":1,"explanation":"Option B is correct."},{"question":"What should the learner do next?","options":["Ignore the example","Apply the concept","Skip the lesson"],"correct_option":1,"explanation":"Applying the concept reinforces understanding."}]'::jsonb,
        '[{"narration":"This is the opening narration for the lesson.","visual_direction":"A clean title slide with a simple concept diagram.","on_screen_text":["The key concept"],"visual_type":"slides"},{"narration":"It explains the concept, demonstrates an example, and concludes with a recap.","visual_direction":"Show the example and recap.","on_screen_text":["Example","Recap"],"visual_type":"slides"}]'::jsonb,
        ARRAY[]::text[], 'approved',
        'openrouter', 'openrouter/free', v_staff_id, now()
    );

    INSERT INTO public.learnora_lesson_production_packages (
        job_id, module_order, lesson_order, version, module_title,
        lesson_title, lesson_description, learning_objective, lesson_format, video_source,
        teaching_script, estimated_duration_seconds, concise_note, practice_activity,
        knowledge_check, video_plan, fact_check_notes, status, provider_key, model,
        approved_by_staff_id, approved_at
    )
    VALUES (
        v_job_id, 0, 1, 1, 'Test Module',
        'Human Video Lesson', 'A human-produced demonstration lesson.',
        'Apply the concept in a practical demonstration.', 'demonstration', 'human',
        'This is the presenter script for the human-produced demonstration. It explains the steps and expected learning outcome.',
        180, 'A concise note for the human-produced lesson.', 'Complete the demonstrated steps using the supplied practice data.',
        '[{"question":"Which option is correct?","options":["Option A","Option B"],"correct_option":1,"explanation":"Option B is correct."},{"question":"What should the learner do?","options":["Apply the demonstration","Skip the activity"],"correct_option":0,"explanation":"Applying the demonstration builds skill."}]'::jsonb,
        '[]'::jsonb,
        ARRAY[]::text[], 'approved',
        'openrouter', 'openrouter/free', v_staff_id, now()
    );

    v_course_id := public.create_course_from_generation_job(v_job_id);
    v_second_course_id := public.create_course_from_generation_job(v_job_id);

    IF v_course_id IS NULL OR v_second_course_id <> v_course_id THEN
        RAISE EXCEPTION 'Course draft creation is not idempotent';
    END IF;

    SELECT status INTO v_course_status
      FROM public.learnora_courses WHERE id = v_course_id;
    SELECT status INTO v_module_status
      FROM public.course_modules WHERE course_id = v_course_id;
    SELECT id, status, content INTO v_lesson_id, v_lesson_status, v_content
      FROM public.learnora_lessons
     WHERE module_id = (SELECT id FROM public.course_modules WHERE course_id = v_course_id)
     ORDER BY order_index
     LIMIT 1;

    SELECT id INTO v_human_lesson_id
      FROM public.learnora_lessons
     WHERE module_id = (SELECT id FROM public.course_modules WHERE course_id = v_course_id)
       AND order_index = 1;

    SELECT status INTO v_job_status
      FROM public.learnora_course_generation_jobs WHERE id = v_job_id;

    IF v_course_status <> 'draft' OR v_module_status <> 'draft' OR v_lesson_status <> 'draft' OR v_job_status <> 'created' THEN
        RAISE EXCEPTION 'Generated course hierarchy was not created in draft state';
    END IF;

    IF position('A short learner-facing note.' in v_content) = 0
       OR position('Try applying the concept' in v_content) = 0
       OR position('private teaching script' in v_content) > 0 THEN
        RAISE EXCEPTION 'Learner lesson content did not keep the concise note/practice separate from the private script';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM public.learnora_lesson_production_packages
         WHERE job_id = v_job_id AND lesson_id = v_lesson_id
           AND teaching_script LIKE '%private teaching script%'
    ) THEN
        RAISE EXCEPTION 'Private teaching script was not retained in the production package';
    END IF;

    SELECT id, is_published INTO v_quiz_id, v_quiz_published
      FROM public.quizzes WHERE lesson_id = v_lesson_id;
    SELECT count(*)::integer INTO v_question_count
      FROM public.quiz_questions WHERE quiz_id = v_quiz_id;
    SELECT correct_answer #>> '{}' INTO v_correct_answer
      FROM public.quiz_questions WHERE quiz_id = v_quiz_id ORDER BY order_index LIMIT 1;

    IF v_quiz_id IS NULL OR v_quiz_published IS DISTINCT FROM false
       OR v_question_count <> 2 OR v_correct_answer <> 'Option B' THEN
        RAISE EXCEPTION 'Generated knowledge check was not created as an unpublished quiz with the correct answer';
    END IF;

    SELECT id, object_key INTO v_render_job_id, v_object_key
      FROM public.learnora_video_render_jobs
     WHERE generation_job_id = v_job_id AND lesson_id = v_lesson_id;

    IF v_render_job_id IS NULL OR v_object_key NOT LIKE 'courses/%/modules/%/lessons/%/%.mp4' THEN
        RAISE EXCEPTION 'A private render job was not queued for the generated video lesson';
    END IF;

    IF EXISTS (
        SELECT 1 FROM public.learnora_video_render_jobs
         WHERE generation_job_id = v_job_id AND lesson_id = v_human_lesson_id
    ) THEN
        RAISE EXCEPTION 'A human-produced lesson was incorrectly queued for AI rendering';
    END IF;

    v_claim := public.claim_next_learnora_video_render_job();
    IF v_claim IS NULL OR v_claim->>'id' <> v_render_job_id::text
       OR v_claim->>'status' <> 'processing'
       OR (v_claim->>'attempt_count')::integer <> 1 THEN
        RAISE EXCEPTION 'The video worker could not claim the queued render job';
    END IF;

    SELECT status INTO v_package_status
      FROM public.learnora_lesson_production_packages
     WHERE job_id = v_job_id AND lesson_id = v_lesson_id;
    IF v_package_status <> 'rendering' THEN
        RAISE EXCEPTION 'Claiming a video job did not move its package to rendering';
    END IF;

    INSERT INTO public.lesson_videos (
        lesson_id, provider, storage_path, title, duration_seconds,
        file_size_bytes, mime_type, status, is_private, transcript_text
    )
    VALUES (
        v_lesson_id, 'cloudflare', v_object_key, 'Test Lesson', 120,
        1024, 'video/mp4', 'processing', true, 'Private teaching transcript for the test.'
    )
    RETURNING id INTO v_video_id;

    INSERT INTO public.lesson_videos (
        lesson_id, provider, storage_path, title, duration_seconds,
        file_size_bytes, mime_type, status, is_private, transcript_text
    )
    VALUES (
        v_human_lesson_id, 'cloudflare', 'courses/course-studio-ci/modules/0/lessons/human-video/human.mp4',
        'Human Video Lesson', 180, 2048, 'video/mp4', 'ready', true,
        'Human-produced video transcript for the test.'
    )
    RETURNING id INTO v_human_video_id;

    PERFORM public.complete_learnora_video_render_job(
        v_render_job_id, v_video_id, 120, 1024, repeat('a', 64)
    );

    SELECT status INTO v_render_status
      FROM public.learnora_video_render_jobs WHERE id = v_render_job_id;
    SELECT status INTO v_package_status
      FROM public.learnora_lesson_production_packages
     WHERE job_id = v_job_id AND lesson_id = v_lesson_id;
    SELECT status INTO v_video_status
      FROM public.lesson_videos WHERE id = v_video_id;

    IF v_render_status <> 'completed' OR v_package_status <> 'ready' OR v_video_status <> 'ready' THEN
        RAISE EXCEPTION 'Completing a video render did not mark the render job, package and video as ready';
    END IF;

    v_published_course_id := public.publish_course_from_generation_job(v_job_id);
    v_published_course_id_again := public.publish_course_from_generation_job(v_job_id);

    IF v_published_course_id <> v_course_id OR v_published_course_id_again <> v_course_id THEN
        RAISE EXCEPTION 'Course publication is not idempotent';
    END IF;

    SELECT status INTO v_published_course_status
      FROM public.learnora_courses WHERE id = v_course_id;
    SELECT status INTO v_published_module_status
      FROM public.course_modules WHERE course_id = v_course_id;
    SELECT status INTO v_published_lesson_status
      FROM public.learnora_lessons WHERE id = v_lesson_id;
    SELECT status INTO v_published_job_status
      FROM public.learnora_course_generation_jobs WHERE id = v_job_id;
    SELECT is_published INTO v_quiz_published
      FROM public.quizzes WHERE id = v_quiz_id;

    IF v_published_course_status <> 'published'
       OR v_published_module_status <> 'published'
       OR v_published_lesson_status <> 'published'
       OR v_published_job_status <> 'published'
       OR v_quiz_published IS DISTINCT FROM true THEN
        RAISE EXCEPTION 'Atomic publication did not publish the course hierarchy and knowledge check together';
    END IF;

    SELECT order_index INTO v_track_order
      FROM public.learnora_learning_path_courses
     WHERE path_id = v_track_id AND course_id = v_course_id;

    IF v_track_order IS DISTINCT FROM 0 THEN
        RAISE EXCEPTION 'Published course was not linked to its selected track in the expected order';
    END IF;
END;
$course_production_test$;

ROLLBACK;
