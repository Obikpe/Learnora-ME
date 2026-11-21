-- Allow authorised Course Studio staff to revise a saved curriculum proposal safely.
-- Superseded lesson packages are archived so edited lesson positions cannot reuse stale teaching content.

CREATE OR REPLACE FUNCTION public.update_learnora_course_generation_curriculum(
    p_job_id uuid,
    p_curriculum_data jsonb
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
DECLARE
    v_job public.learnora_course_generation_jobs%ROWTYPE;
    v_module jsonb;
    v_lesson_count integer := 0;
BEGIN
    SELECT *
      INTO v_job
      FROM public.learnora_course_generation_jobs
     WHERE id = p_job_id
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Course generation job was not found';
    END IF;

    IF v_job.status NOT IN ('draft', 'review') OR v_job.created_course_id IS NOT NULL THEN
        RAISE EXCEPTION 'Only an unmaterialised course proposal can be revised';
    END IF;

    IF jsonb_typeof(p_curriculum_data) IS DISTINCT FROM 'object' THEN
        RAISE EXCEPTION 'A revised curriculum must be a JSON object';
    END IF;
    IF jsonb_typeof(p_curriculum_data->'modules') IS DISTINCT FROM 'array' THEN
        RAISE EXCEPTION 'A revised curriculum must contain a module array';
    END IF;
    IF jsonb_array_length(p_curriculum_data->'modules') < 1
       OR jsonb_array_length(p_curriculum_data->'modules') > 12 THEN
        RAISE EXCEPTION 'A revised curriculum must contain between 1 and 12 modules';
    END IF;

    FOR v_module IN
        SELECT value FROM jsonb_array_elements(p_curriculum_data->'modules')
    LOOP
        IF jsonb_typeof(v_module->'lessons') IS DISTINCT FROM 'array' THEN
            RAISE EXCEPTION 'Every revised module must contain a lesson array';
        END IF;
        IF jsonb_array_length(v_module->'lessons') < 1
           OR jsonb_array_length(v_module->'lessons') > 20 THEN
            RAISE EXCEPTION 'Every revised module must contain between 1 and 20 lessons';
        END IF;
        v_lesson_count := v_lesson_count + jsonb_array_length(v_module->'lessons');
    END LOOP;

    IF v_lesson_count > 60 THEN
        RAISE EXCEPTION 'A revised curriculum cannot exceed 60 lessons';
    END IF;

    UPDATE public.learnora_lesson_production_packages
       SET status = 'archived',
           approved_by_staff_id = NULL,
           approved_at = NULL
     WHERE job_id = p_job_id
       AND status <> 'archived';

    UPDATE public.learnora_course_generation_jobs
       SET course_title = p_curriculum_data->>'course_title',
           course_slug = trim(both '-' from regexp_replace(lower(p_curriculum_data->>'course_title'), '[^a-z0-9]+', '-', 'g')),
           curriculum_data = p_curriculum_data,
           status = 'draft',
           approved_by_staff_id = NULL,
           approved_at = NULL
     WHERE id = p_job_id;
END;
$function$;

REVOKE ALL ON FUNCTION public.update_learnora_course_generation_curriculum(uuid, jsonb)
    FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.update_learnora_course_generation_curriculum(uuid, jsonb)
    TO service_role;
