-- Defense in depth: SECURITY DEFINER cohort assignment triggers must not
-- resolve names through a caller-controlled search path. Their SQL bodies
-- qualify application objects with public.* and use only pg_catalog built-ins.
BEGIN;
ALTER FUNCTION public.validate_cohort_member_course_assignment() SET search_path = '';
ALTER FUNCTION public.validate_cohort_member_lesson_assignment() SET search_path = '';
COMMIT;
