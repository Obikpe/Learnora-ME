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
        CHECK (status IN ('draft', 'review', 'approved', 'created', 'failed', 'cancelled')),
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
        UNIQUE (job_id, module_order, lesson_order, version)
);

CREATE INDEX IF NOT EXISTS idx_lesson_production_packages_job_position
    ON public.learnora_lesson_production_packages (job_id, module_order, lesson_order, version DESC);
CREATE INDEX IF NOT EXISTS idx_lesson_production_packages_lesson
    ON public.learnora_lesson_production_packages (lesson_id)
    WHERE lesson_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_lesson_production_packages_status
    ON public.learnora_lesson_production_packages (status, created_at DESC);

ALTER TABLE public.learnora_course_generation_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learnora_lesson_production_packages ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.learnora_course_generation_jobs FROM PUBLIC, anon, authenticated;
REVOKE ALL ON TABLE public.learnora_lesson_production_packages FROM PUBLIC, anon, authenticated;
GRANT ALL ON TABLE public.learnora_course_generation_jobs TO service_role;
GRANT ALL ON TABLE public.learnora_lesson_production_packages TO service_role;

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

    IF v_job.status = 'created' AND v_job.created_course_id IS NOT NULL THEN
        RETURN v_job.created_course_id;
    END IF;

    IF v_job.status <> 'approved' OR v_job.approved_by_staff_id IS NULL OR v_job.approved_at IS NULL THEN
        RAISE EXCEPTION 'Course generation job must be explicitly approved before course creation';
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
