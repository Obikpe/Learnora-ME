-- AI-assisted course production drafts and private lesson production packages.
-- All generated content remains internal until staff approval creates a draft course.
-- This migration is additive; it does not alter existing courses or learner records.

CREATE TABLE IF NOT EXISTS public.learnora_course_generation_jobs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_by_staff_id uuid NOT NULL REFERENCES public.learnora_staff_accounts(id) ON DELETE RESTRICT,
    created_by_user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    approved_by_staff_id uuid REFERENCES public.learnora_staff_accounts(id) ON DELETE SET NULL,
    target_track_id uuid REFERENCES public.learnora_learning_paths(id) ON DELETE SET NULL,
    created_course_id uuid REFERENCES public.learnora_courses(id) ON DELETE SET NULL,
    course_title text NOT NULL,
    course_slug text NOT NULL,
    course_level text NOT NULL CHECK (course_level IN ('beginner', 'intermediate', 'advanced', 'mixed')),
    status text NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'review', 'approved', 'created', 'published', 'failed', 'cancelled')),
    published_at timestamptz,
    request_data jsonb NOT NULL DEFAULT '{}'::jsonb,
    curriculum_data jsonb NOT NULL DEFAULT '{}'::jsonb,
    provider_key text,
    model text,
    prompt_version text NOT NULL DEFAULT 'curriculum-v1',
    input_tokens integer CHECK (input_tokens IS NULL OR input_tokens >= 0),
    output_tokens integer CHECK (output_tokens IS NULL OR output_tokens >= 0),
    error_summary text,
    approved_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_course_generation_jobs_creator_created
    ON public.learnora_course_generation_jobs (created_by_staff_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_course_generation_jobs_status_created
    ON public.learnora_course_generation_jobs (status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_course_generation_jobs_target_track
    ON public.learnora_course_generation_jobs (target_track_id)
    WHERE target_track_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS public.learnora_lesson_production_packages (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id uuid NOT NULL REFERENCES public.learnora_course_generation_jobs(id) ON DELETE CASCADE,
    lesson_id uuid REFERENCES public.learnora_lessons(id) ON DELETE SET NULL,
    approved_by_staff_id uuid REFERENCES public.learnora_staff_accounts(id) ON DELETE SET NULL,
    module_order integer NOT NULL CHECK (module_order >= 0),
    lesson_order integer NOT NULL CHECK (lesson_order >= 0),
    version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
    module_title text NOT NULL,
    lesson_title text NOT NULL,
    lesson_description text NOT NULL,
    learning_objective text NOT NULL,
    lesson_format text NOT NULL
        CHECK (lesson_format IN ('narrated_visual', 'demonstration', 'text_practice', 'mixed')),
    video_source text NOT NULL DEFAULT 'ai'
        CHECK (video_source IN ('ai', 'human')),
    teaching_script text NOT NULL,
    estimated_duration_seconds integer NOT NULL
        CHECK (estimated_duration_seconds BETWEEN 30 AND 300),
    concise_note text NOT NULL
        CHECK (length(concise_note) <= 700),
    practice_activity text,
    knowledge_check jsonb NOT NULL DEFAULT '[]'::jsonb
        CHECK (jsonb_typeof(knowledge_check) = 'array'),
    video_plan jsonb NOT NULL DEFAULT '[]'::jsonb
        CHECK (jsonb_typeof(video_plan) = 'array'),
    fact_check_notes text[] NOT NULL DEFAULT ARRAY[]::text[],
    status text NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'review', 'approved', 'rendering', 'ready', 'failed', 'archived')),
    provider_key text,
    model text,
    prompt_version text NOT NULL DEFAULT 'lesson-package-v1',
    approved_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT learnora_lesson_production_packages_job_position_version_key
        UNIQUE (job_id, module_order, lesson_order, version),
    CONSTRAINT learnora_lesson_production_packages_human_video_format_check
        CHECK (video_source <> 'human' OR lesson_format <> 'text_practice')
);

CREATE INDEX IF NOT EXISTS idx_lesson_production_packages_job_position
    ON public.learnora_lesson_production_packages (job_id, module_order, lesson_order, version DESC);
CREATE INDEX IF NOT EXISTS idx_lesson_production_packages_lesson
    ON public.learnora_lesson_production_packages (lesson_id)
    WHERE lesson_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_lesson_production_packages_status
    ON public.learnora_lesson_production_packages (status, created_at DESC);

CREATE TABLE IF NOT EXISTS public.learnora_video_render_jobs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    generation_job_id uuid NOT NULL REFERENCES public.learnora_course_generation_jobs(id) ON DELETE CASCADE,
    production_package_id uuid NOT NULL REFERENCES public.learnora_lesson_production_packages(id) ON DELETE CASCADE,
    lesson_id uuid NOT NULL REFERENCES public.learnora_lessons(id) ON DELETE CASCADE,
    lesson_video_id uuid REFERENCES public.lesson_videos(id) ON DELETE SET NULL,
    object_key text NOT NULL UNIQUE,
    voice_id text NOT NULL DEFAULT 'bf_emma',
    status text NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'processing', 'completed', 'failed', 'cancelled')),
    priority integer NOT NULL DEFAULT 0,
    attempt_count integer NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    max_attempts integer NOT NULL DEFAULT 3 CHECK (max_attempts BETWEEN 1 AND 5),
    duration_seconds integer CHECK (duration_seconds IS NULL OR duration_seconds BETWEEN 1 AND 300),
    file_size_bytes bigint CHECK (file_size_bytes IS NULL OR file_size_bytes > 0),
    checksum_sha256 text,
    error_summary text,
    queued_by_staff_id uuid REFERENCES public.learnora_staff_accounts(id) ON DELETE SET NULL,
    claimed_at timestamptz,
    started_at timestamptz,
    completed_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT learnora_video_render_jobs_package_key UNIQUE (production_package_id)
);

CREATE INDEX IF NOT EXISTS idx_learnora_video_render_jobs_queue
    ON public.learnora_video_render_jobs (status, priority DESC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_learnora_video_render_jobs_generation_job
    ON public.learnora_video_render_jobs (generation_job_id);
CREATE INDEX IF NOT EXISTS idx_learnora_video_render_jobs_lesson
    ON public.learnora_video_render_jobs (lesson_id);

ALTER TABLE public.learnora_course_generation_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learnora_lesson_production_packages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learnora_video_render_jobs ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.learnora_course_generation_jobs FROM PUBLIC, anon, authenticated;
REVOKE ALL ON TABLE public.learnora_lesson_production_packages FROM PUBLIC, anon, authenticated;
REVOKE ALL ON TABLE public.learnora_video_render_jobs FROM PUBLIC, anon, authenticated;
GRANT ALL ON TABLE public.learnora_course_generation_jobs TO service_role;
GRANT ALL ON TABLE public.learnora_lesson_production_packages TO service_role;
GRANT ALL ON TABLE public.learnora_video_render_jobs TO service_role;

CREATE OR REPLACE FUNCTION public.touch_course_production_updated_at()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = ''
AS $function$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$function$;

REVOKE ALL ON FUNCTION public.touch_course_production_updated_at() FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.touch_course_production_updated_at() TO service_role;

DROP TRIGGER IF EXISTS trg_course_generation_jobs_updated_at
    ON public.learnora_course_generation_jobs;
CREATE TRIGGER trg_course_generation_jobs_updated_at
    BEFORE UPDATE ON public.learnora_course_generation_jobs
    FOR EACH ROW EXECUTE FUNCTION public.touch_course_production_updated_at();

DROP TRIGGER IF EXISTS trg_lesson_production_packages_updated_at
    ON public.learnora_lesson_production_packages;
CREATE TRIGGER trg_lesson_production_packages_updated_at
    BEFORE UPDATE ON public.learnora_lesson_production_packages
    FOR EACH ROW EXECUTE FUNCTION public.touch_course_production_updated_at();

DROP TRIGGER IF EXISTS trg_video_render_jobs_updated_at
    ON public.learnora_video_render_jobs;
CREATE TRIGGER trg_video_render_jobs_updated_at
    BEFORE UPDATE ON public.learnora_video_render_jobs
    FOR EACH ROW EXECUTE FUNCTION public.touch_course_production_updated_at();

CREATE OR REPLACE FUNCTION public.create_course_from_generation_job(p_job_id uuid)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
DECLARE
    v_job public.learnora_course_generation_jobs%ROWTYPE;
    v_module jsonb;
    v_lesson jsonb;
    v_module_order integer;
    v_lesson_order integer;
    v_module_id uuid;
    v_lesson_id uuid;
    v_course_id uuid;
    v_course_slug text;
    v_lesson_slug text;
    v_lesson_content text;
    v_lesson_type text;
    v_duration_minutes integer;
    v_package public.learnora_lesson_production_packages%ROWTYPE;
    v_quiz_id uuid;
    v_question jsonb;
    v_question_order integer;
    v_correct_index integer;
    v_correct_answer text;
    v_estimated_hours numeric;
BEGIN
    SELECT *
      INTO v_job
      FROM public.learnora_course_generation_jobs
     WHERE id = p_job_id
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Course generation job was not found';
    END IF;

    IF v_job.status IN ('created', 'published') AND v_job.created_course_id IS NOT NULL THEN
        RETURN v_job.created_course_id;
    END IF;

    IF v_job.status <> 'approved' OR v_job.approved_by_staff_id IS NULL OR v_job.approved_at IS NULL THEN
        RAISE EXCEPTION 'Course generation job must be explicitly approved before course creation';
    END IF;

    IF v_job.target_track_id IS NOT NULL AND NOT EXISTS (
        SELECT 1
          FROM public.learnora_learning_paths lp
         WHERE lp.id = v_job.target_track_id
           AND lp.owner_user_id IS NULL
           AND lp.organisation_id IS NULL
           AND lp.status <> 'archived'
    ) THEN
        RAISE EXCEPTION 'Only an active global Learnora ME track can be the target of this course draft';
    END IF;

    IF jsonb_typeof(v_job.curriculum_data->'modules') IS DISTINCT FROM 'array'
       OR jsonb_array_length(v_job.curriculum_data->'modules') = 0 THEN
        RAISE EXCEPTION 'Course generation job has no valid module structure';
    END IF;

    v_course_slug := COALESCE(
        NULLIF(v_job.course_slug, ''),
        trim(both '-' from regexp_replace(lower(v_job.course_title), '[^a-z0-9]+', '-', 'g'))
    );

    IF EXISTS (
        SELECT 1
          FROM public.learnora_courses c
         WHERE c.organisation_id IS NULL
           AND c.slug = v_course_slug
    ) THEN
        v_course_slug := v_course_slug || '-' || substr(replace(p_job_id::text, '-', ''), 1, 8);
    END IF;

    SELECT COALESCE(sum(latest.estimated_duration_seconds), 0)::numeric / 3600
      INTO v_estimated_hours
      FROM (
          SELECT DISTINCT ON (p.module_order, p.lesson_order)
                 p.estimated_duration_seconds
            FROM public.learnora_lesson_production_packages p
           WHERE p.job_id = p_job_id
             AND p.status = 'approved'
           ORDER BY p.module_order, p.lesson_order, p.version DESC
      ) AS latest;

    INSERT INTO public.learnora_courses (
        title, slug, short_description, description, level, status,
        ownership, estimated_hours, settings, created_by
    )
    VALUES (
        v_job.course_title,
        v_course_slug,
        v_job.curriculum_data->>'short_description',
        v_job.curriculum_data->>'course_description',
        v_job.course_level,
        'draft',
        'learnora',
        v_estimated_hours,
        jsonb_build_object(
            'ai_generated', true,
            'generation_job_id', p_job_id,
            'learning_outcomes', COALESCE(v_job.curriculum_data->'learning_outcomes', '[]'::jsonb),
            'prerequisites', COALESCE(v_job.curriculum_data->'prerequisites', '[]'::jsonb),
            'target_track_id', v_job.target_track_id
        ),
        v_job.created_by_user_id
    )
    RETURNING id INTO v_course_id;

    FOR v_module, v_module_order IN
        SELECT value, ordinality::integer - 1
          FROM jsonb_array_elements(v_job.curriculum_data->'modules')
               WITH ORDINALITY AS modules(value, ordinality)
    LOOP
        INSERT INTO public.course_modules (course_id, title, description, order_index, status)
        VALUES (v_course_id, v_module->>'title', v_module->>'description', v_module_order, 'draft')
        RETURNING id INTO v_module_id;

        IF jsonb_typeof(v_module->'lessons') IS DISTINCT FROM 'array'
           OR jsonb_array_length(v_module->'lessons') = 0 THEN
            RAISE EXCEPTION 'Generated module % has no lessons', v_module_order;
        END IF;

        FOR v_lesson, v_lesson_order IN
            SELECT value, ordinality::integer - 1
              FROM jsonb_array_elements(v_module->'lessons')
                   WITH ORDINALITY AS lessons(value, ordinality)
        LOOP
            SELECT *
              INTO v_package
              FROM public.learnora_lesson_production_packages p
             WHERE p.job_id = p_job_id
               AND p.module_order = v_module_order
               AND p.lesson_order = v_lesson_order
               AND p.version = (
                   SELECT max(p2.version)
                     FROM public.learnora_lesson_production_packages p2
                    WHERE p2.job_id = p_job_id
                      AND p2.module_order = v_module_order
                      AND p2.lesson_order = v_lesson_order
               )
               AND p.status = 'approved'
             LIMIT 1;

            IF NOT FOUND THEN
                RAISE EXCEPTION 'Lesson production package is not approved for module % lesson %',
                    v_module_order, v_lesson_order;
            END IF;

            v_lesson_content := v_package.concise_note;
            IF NULLIF(trim(v_package.practice_activity), '') IS NOT NULL THEN
                v_lesson_content := v_lesson_content || E'\n\n## Practice\n\n' || v_package.practice_activity;
            END IF;

            v_lesson_type := CASE v_package.lesson_format
                WHEN 'text_practice' THEN 'text'
                WHEN 'mixed' THEN 'mixed'
                ELSE 'video'
            END;

            v_duration_minutes := greatest(
                1,
                least(5, ceil(v_package.estimated_duration_seconds::numeric / 60)::integer)
            );

            v_lesson_slug := trim(
                both '-' from regexp_replace(lower(v_lesson->>'title'), '[^a-z0-9]+', '-', 'g')
            ) || '-' || (v_module_order + 1)::text || '-' || (v_lesson_order + 1)::text;

            INSERT INTO public.learnora_lessons (
                module_id, title, slug, description, order_index,
                lesson_type, content, duration_minutes, status
            )
            VALUES (
                v_module_id,
                v_lesson->>'title',
                v_lesson_slug,
                v_lesson->>'description',
                v_lesson_order,
                v_lesson_type,
                v_lesson_content,
                v_duration_minutes,
                'draft'
            )
            RETURNING id INTO v_lesson_id;

            UPDATE public.learnora_lesson_production_packages
               SET lesson_id = v_lesson_id
             WHERE id = v_package.id;

            IF jsonb_typeof(v_package.knowledge_check) = 'array'
               AND jsonb_array_length(v_package.knowledge_check) > 0 THEN
                INSERT INTO public.quizzes (
                    course_id, module_id, lesson_id, title, description,
                    passing_score, is_published
                )
                VALUES (
                    v_course_id,
                    v_module_id,
                    v_lesson_id,
                    'Quick check: ' || (v_lesson->>'title'),
                    'Check your understanding of ' || (v_lesson->>'title') || '.',
                    70,
                    false
                )
                RETURNING id INTO v_quiz_id;

                FOR v_question, v_question_order IN
                    SELECT value, ordinality::integer - 1
                      FROM jsonb_array_elements(v_package.knowledge_check)
                           WITH ORDINALITY AS questions(value, ordinality)
                LOOP
                    v_correct_index := NULLIF(v_question->>'correct_option', '')::integer;
                    IF jsonb_typeof(v_question->'options') IS DISTINCT FROM 'array' THEN
                        RAISE EXCEPTION 'Knowledge-check options are invalid for lesson %', v_lesson_order;
                    END IF;
                    IF v_correct_index IS NULL
                       OR v_correct_index < 0
                       OR v_correct_index >= jsonb_array_length(v_question->'options')
                       OR NULLIF(trim(v_question->>'question'), '') IS NULL THEN
                        RAISE EXCEPTION 'Knowledge-check answer or question is invalid for lesson %', v_lesson_order;
                    END IF;

                    v_correct_answer := v_question->'options'->>v_correct_index;
                    INSERT INTO public.quiz_questions (
                        quiz_id, question, question_type, options, correct_answer,
                        explanation, points, order_index
                    )
                    VALUES (
                        v_quiz_id,
                        v_question->>'question',
                        'multiple_choice',
                        v_question->'options',
                        to_jsonb(v_correct_answer),
                        v_question->>'explanation',
                        1,
                        v_question_order
                    );
                END LOOP;
            END IF;

            IF v_package.video_source = 'ai'
               AND v_package.lesson_format <> 'text_practice'
               AND jsonb_typeof(v_package.video_plan) = 'array'
               AND jsonb_array_length(v_package.video_plan) > 0 THEN
                INSERT INTO public.learnora_video_render_jobs (
                    generation_job_id, production_package_id, lesson_id,
                    object_key, voice_id, status, queued_by_staff_id
                )
                VALUES (
                    p_job_id,
                    v_package.id,
                    v_lesson_id,
                    'courses/' || v_course_id::text ||
                    '/modules/' || v_module_id::text ||
                    '/lessons/' || v_lesson_id::text ||
                    '/' || v_package.id::text || '.mp4',
                    'bf_emma',
                    'queued',
                    v_job.approved_by_staff_id
                )
                ON CONFLICT (production_package_id) DO NOTHING;
            END IF;
        END LOOP;
    END LOOP;

    UPDATE public.learnora_course_generation_jobs
       SET status = 'created',
           created_course_id = v_course_id
     WHERE id = p_job_id;

    RETURN v_course_id;
END;
$function$;

REVOKE ALL ON FUNCTION public.create_course_from_generation_job(uuid) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.create_course_from_generation_job(uuid) TO service_role;


CREATE OR REPLACE FUNCTION public.publish_course_from_generation_job(p_job_id uuid)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
DECLARE
    v_job public.learnora_course_generation_jobs%ROWTYPE;
    v_course_id uuid;
    v_module_count integer;
    v_last_module_order integer;
BEGIN
    SELECT *
      INTO v_job
      FROM public.learnora_course_generation_jobs
     WHERE id = p_job_id
     FOR UPDATE;

    IF NOT FOUND OR v_job.created_course_id IS NULL
       OR v_job.status NOT IN ('created', 'published') THEN
        RAISE EXCEPTION 'A created course draft is required before publication';
    END IF;

    v_course_id := v_job.created_course_id;

    PERFORM 1
      FROM public.learnora_courses
     WHERE id = v_course_id
       AND ownership = 'learnora'
       AND organisation_id IS NULL
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'The generated global course could not be found';
    END IF;

    IF (SELECT status FROM public.learnora_courses WHERE id = v_course_id) = 'published' THEN
        UPDATE public.learnora_course_generation_jobs
           SET status = 'published',
               published_at = COALESCE(published_at, now())
         WHERE id = p_job_id;
        RETURN v_course_id;
    END IF;

    IF (SELECT status FROM public.learnora_courses WHERE id = v_course_id) <> 'draft' THEN
        RAISE EXCEPTION 'Only a draft course can be published';
    END IF;

    IF v_job.target_track_id IS NOT NULL AND NOT EXISTS (
        SELECT 1
          FROM public.learnora_learning_paths lp
         WHERE lp.id = v_job.target_track_id
           AND lp.owner_user_id IS NULL
           AND lp.organisation_id IS NULL
           AND lp.status <> 'archived'
    ) THEN
        RAISE EXCEPTION 'The selected global track is no longer available for publication';
    END IF;

    SELECT count(*)::integer, max(order_index)
      INTO v_module_count, v_last_module_order
      FROM public.course_modules
     WHERE course_id = v_course_id;

    IF v_module_count = 0 THEN
        RAISE EXCEPTION 'A course must contain at least one module before publication';
    END IF;

    IF EXISTS (
        SELECT 1
          FROM public.course_modules m
         WHERE m.course_id = v_course_id
           AND NOT EXISTS (
               SELECT 1
                 FROM public.learnora_lessons l
                WHERE l.module_id = m.id
           )
    ) THEN
        RAISE EXCEPTION 'Every course module must contain at least one lesson before publication';
    END IF;

    IF EXISTS (
        SELECT 1
          FROM public.learnora_lessons l
          JOIN public.course_modules m ON m.id = l.module_id
         WHERE m.course_id = v_course_id
           AND NOT EXISTS (
               SELECT 1
                 FROM public.learnora_lesson_production_packages p
                WHERE p.lesson_id = l.id
                  AND p.version = (
                      SELECT max(p2.version)
                        FROM public.learnora_lesson_production_packages p2
                       WHERE p2.lesson_id = l.id
                  )
           )
    ) THEN
        RAISE EXCEPTION 'Every generated lesson must have a saved production package before publication';
    END IF;

    IF EXISTS (
        SELECT 1
          FROM public.learnora_lesson_production_packages p
          JOIN public.learnora_lessons l ON l.id = p.lesson_id
          JOIN public.course_modules m ON m.id = l.module_id
         WHERE m.course_id = v_course_id
           AND p.version = (
               SELECT max(p2.version)
                 FROM public.learnora_lesson_production_packages p2
                WHERE p2.lesson_id = l.id
           )
           AND (
               (p.lesson_format = 'text_practice' AND p.status NOT IN ('approved', 'ready'))
               OR (p.video_source = 'human' AND p.status NOT IN ('approved', 'ready'))
               OR (p.video_source = 'ai' AND p.lesson_format <> 'text_practice' AND p.status <> 'ready')
           )
    ) THEN
        RAISE EXCEPTION 'Every video lesson must finish rendering and every text lesson must be approved before publication';
    END IF;

    IF EXISTS (
        SELECT 1
          FROM public.learnora_video_render_jobs j
         WHERE j.generation_job_id = p_job_id
           AND j.status <> 'completed'
    ) THEN
        RAISE EXCEPTION 'All lesson videos must finish rendering before publication';
    END IF;

    IF EXISTS (
        SELECT 1
          FROM public.learnora_lesson_production_packages p
          JOIN public.learnora_lessons l ON l.id = p.lesson_id
          JOIN public.course_modules m ON m.id = l.module_id
         WHERE m.course_id = v_course_id
           AND p.version = (
               SELECT max(p2.version)
                 FROM public.learnora_lesson_production_packages p2
                WHERE p2.lesson_id = l.id
           )
           AND p.lesson_format <> 'text_practice'
           AND NOT EXISTS (
               SELECT 1
                 FROM public.lesson_videos lv
                WHERE lv.lesson_id = l.id
                  AND lv.status = 'ready'
                  AND lv.is_private IS TRUE
                  AND (
                      (p.video_source = 'ai' AND lv.provider = 'cloudflare')
                      OR (p.video_source = 'human' AND lv.provider = 'cloudflare')
                  )
           )
    ) THEN
        RAISE EXCEPTION 'Every video lesson must have a ready private video asset before publication';
    END IF;

    IF EXISTS (
        SELECT 1
          FROM public.course_modules m
         WHERE m.course_id = v_course_id
           AND m.order_index < v_last_module_order
           AND NOT EXISTS (
               SELECT 1
                 FROM public.quizzes q
                WHERE q.course_id = v_course_id
                  AND q.module_id = m.id
           )
    ) THEN
        RAISE EXCEPTION 'Every module before the final module needs a knowledge check before publication';
    END IF;

    IF EXISTS (
        SELECT 1
          FROM public.quizzes q
         WHERE q.course_id = v_course_id
           AND NOT EXISTS (
               SELECT 1
                 FROM public.quiz_questions qq
                WHERE qq.quiz_id = q.id
           )
    ) THEN
        RAISE EXCEPTION 'Every knowledge check must contain at least one question before publication';
    END IF;

    IF EXISTS (
        SELECT 1
          FROM public.quizzes q
          JOIN public.quiz_questions qq ON qq.quiz_id = q.id
         WHERE q.course_id = v_course_id
           AND (
               qq.question_type <> 'multiple_choice'
               OR NULLIF(trim(qq.question), '') IS NULL
               OR jsonb_typeof(qq.options) IS DISTINCT FROM 'array'
               OR CASE WHEN jsonb_typeof(qq.options) = 'array' THEN jsonb_array_length(qq.options) ELSE 0 END < 2
               OR NULLIF(qq.correct_answer #>> '{}', '') IS NULL
               OR NOT EXISTS (
                   SELECT 1
                     FROM jsonb_array_elements_text(
                         CASE WHEN jsonb_typeof(qq.options) = 'array' THEN qq.options ELSE '[]'::jsonb END
                      ) AS option_item(value)
                    WHERE option_item.value = qq.correct_answer #>> '{}'
               )
           )
    ) THEN
        RAISE EXCEPTION 'Every knowledge-check question must have valid options and a correct answer';
    END IF;

    IF EXISTS (
        SELECT 1
          FROM public.learnora_learning_path_courses course_link
          JOIN public.learnora_learning_path_courses track_link
            ON track_link.path_id = course_link.path_id
          JOIN public.learnora_enrolments e ON e.course_id = track_link.course_id
         WHERE course_link.course_id = v_course_id
           AND e.source_type = 'track_enrolment:' || course_link.path_id::text
           AND e.status IN ('active', 'completed')
    ) THEN
        RAISE EXCEPTION 'A linked track curriculum has been locked by learner enrolments; create a successor track instead';
    END IF;

    IF v_job.target_track_id IS NOT NULL THEN
        IF EXISTS (
            SELECT 1
              FROM public.learnora_learning_path_courses lpc
              JOIN public.learnora_enrolments e ON e.course_id = lpc.course_id
             WHERE lpc.path_id = v_job.target_track_id
               AND e.source_type = 'track_enrolment:' || v_job.target_track_id::text
               AND e.status IN ('active', 'completed')
        ) THEN
            RAISE EXCEPTION 'The selected track curriculum has been locked by learner enrolments; create a successor track instead';
        END IF;

        IF NOT EXISTS (
            SELECT 1
              FROM public.learnora_learning_path_courses lpc
             WHERE lpc.path_id = v_job.target_track_id
               AND lpc.course_id = v_course_id
        ) THEN
            INSERT INTO public.learnora_learning_path_courses (
                path_id, course_id, order_index, required
            )
            SELECT
                v_job.target_track_id,
                v_course_id,
                COALESCE(MAX(lpc.order_index) + 1, 0),
                true
              FROM public.learnora_learning_path_courses lpc
             WHERE lpc.path_id = v_job.target_track_id;
        END IF;
    END IF;

    UPDATE public.quizzes
       SET is_published = true
     WHERE course_id = v_course_id;

    UPDATE public.learnora_lessons l
       SET status = 'published'
      FROM public.course_modules m
     WHERE m.id = l.module_id
       AND m.course_id = v_course_id;

    UPDATE public.course_modules
       SET status = 'published'
     WHERE course_id = v_course_id;

    UPDATE public.learnora_courses
       SET status = 'published'
     WHERE id = v_course_id;

    UPDATE public.learnora_course_generation_jobs
       SET status = 'published',
           published_at = now()
     WHERE id = p_job_id;

    RETURN v_course_id;
END;
$function$;

REVOKE ALL ON FUNCTION public.publish_course_from_generation_job(uuid) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.publish_course_from_generation_job(uuid) TO service_role;


CREATE OR REPLACE FUNCTION public.claim_next_learnora_video_render_job()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
DECLARE
    v_job public.learnora_video_render_jobs%ROWTYPE;
BEGIN
    SELECT *
      INTO v_job
      FROM public.learnora_video_render_jobs
     WHERE status = 'queued'
       AND attempt_count < max_attempts
     ORDER BY priority DESC, created_at ASC
     FOR UPDATE SKIP LOCKED
     LIMIT 1;

    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    UPDATE public.learnora_video_render_jobs
       SET status = 'processing',
           attempt_count = attempt_count + 1,
           claimed_at = now(),
           started_at = COALESCE(started_at, now()),
           error_summary = NULL
     WHERE id = v_job.id
     RETURNING * INTO v_job;

    UPDATE public.learnora_lesson_production_packages
       SET status = 'rendering'
     WHERE id = v_job.production_package_id
       AND status IN ('approved', 'failed', 'rendering');

    RETURN to_jsonb(v_job);
END;
$function$;

REVOKE ALL ON FUNCTION public.claim_next_learnora_video_render_job() FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.claim_next_learnora_video_render_job() TO service_role;


CREATE OR REPLACE FUNCTION public.requeue_stale_learnora_video_render_jobs(p_stale_minutes integer DEFAULT 20)
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
DECLARE
    v_count integer;
BEGIN
    WITH stale AS (
        UPDATE public.learnora_video_render_jobs j
           SET status = CASE WHEN j.attempt_count < j.max_attempts THEN 'queued' ELSE 'failed' END,
               error_summary = 'Render worker lease expired before completion',
               claimed_at = NULL
         WHERE j.status = 'processing'
           AND j.claimed_at < now() - make_interval(mins => greatest(5, p_stale_minutes))
         RETURNING j.production_package_id, j.lesson_video_id, j.lesson_id, j.object_key, j.status
    ),
    failed_videos AS (
        UPDATE public.lesson_videos lv
           SET status = 'failed'
          FROM stale s
         WHERE (lv.id = s.lesson_video_id
                OR (lv.lesson_id = s.lesson_id AND lv.provider = 'cloudflare' AND lv.storage_path = s.object_key))
           AND lv.status = 'processing'
        RETURNING lv.id
    )
    UPDATE public.learnora_lesson_production_packages p
       SET status = CASE WHEN s.status = 'queued' THEN 'approved' ELSE 'failed' END
      FROM stale s
     WHERE p.id = s.production_package_id;

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$function$;

REVOKE ALL ON FUNCTION public.requeue_stale_learnora_video_render_jobs(integer) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.requeue_stale_learnora_video_render_jobs(integer) TO service_role;


CREATE OR REPLACE FUNCTION public.complete_learnora_video_render_job(
    p_job_id uuid,
    p_lesson_video_id uuid,
    p_duration_seconds integer,
    p_file_size_bytes bigint,
    p_checksum_sha256 text
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
DECLARE
    v_job public.learnora_video_render_jobs%ROWTYPE;
BEGIN
    SELECT *
      INTO v_job
      FROM public.learnora_video_render_jobs
     WHERE id = p_job_id
     FOR UPDATE;

    IF NOT FOUND OR v_job.status <> 'processing' THEN
        RAISE EXCEPTION 'Video render job is not currently processing';
    END IF;

    IF p_duration_seconds IS NULL OR p_duration_seconds < 1 OR p_duration_seconds > 300
       OR p_file_size_bytes IS NULL OR p_file_size_bytes <= 0
       OR p_checksum_sha256 IS NULL OR length(p_checksum_sha256) <> 64 THEN
        RAISE EXCEPTION 'Rendered video metadata is invalid';
    END IF;

    IF NOT EXISTS (
        SELECT 1
          FROM public.lesson_videos lv
         WHERE lv.id = p_lesson_video_id
           AND lv.lesson_id = v_job.lesson_id
           AND lv.provider = 'cloudflare'
           AND lv.storage_path = v_job.object_key
           AND lv.status = 'processing'
    ) THEN
        RAISE EXCEPTION 'Uploaded video row does not match the render job';
    END IF;

    UPDATE public.lesson_videos
       SET status = 'ready'
     WHERE id = p_lesson_video_id;

    UPDATE public.learnora_video_render_jobs
       SET status = 'completed',
           lesson_video_id = p_lesson_video_id,
           duration_seconds = p_duration_seconds,
           file_size_bytes = p_file_size_bytes,
           checksum_sha256 = p_checksum_sha256,
           completed_at = now(),
           error_summary = NULL
     WHERE id = p_job_id;

    UPDATE public.learnora_lesson_production_packages
       SET status = 'ready'
     WHERE id = v_job.production_package_id
       AND status = 'rendering';
END;
$function$;

REVOKE ALL ON FUNCTION public.complete_learnora_video_render_job(uuid, uuid, integer, bigint, text) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.complete_learnora_video_render_job(uuid, uuid, integer, bigint, text) TO service_role;

INSERT INTO public.learnora_permissions (permission_key, name, description, category)
VALUES (
    'content.generate',
    'Generate AI Course Content',
    'Create and review AI-assisted Learnora ME course drafts and lesson production packages.',
    'content'
)
ON CONFLICT (permission_key) DO UPDATE
SET name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category;

INSERT INTO public.learnora_staff_role_permissions (role_id, permission_id)
SELECT r.id, p.id
  FROM public.learnora_staff_roles r
 CROSS JOIN public.learnora_permissions p
 WHERE r.slug IN ('super_admin', 'learning_curriculum')
   AND p.permission_key = 'content.generate'
ON CONFLICT (role_id, permission_id) DO NOTHING;

COMMENT ON TABLE public.learnora_course_generation_jobs IS
    'Private internal Learnora ME AI course-generation jobs and curriculum drafts; never learner-visible.';
COMMENT ON TABLE public.learnora_lesson_production_packages IS
    'Private teaching scripts, concise notes, activities and video storyboards generated for a course draft.';
COMMENT ON TABLE public.learnora_video_render_jobs IS
    'Private asynchronous rendering queue for approved Learnora ME lesson videos; workers claim jobs through a service-role-only RPC.';
