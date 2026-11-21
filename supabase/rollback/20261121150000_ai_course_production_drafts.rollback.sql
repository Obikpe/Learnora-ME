-- Rollback for 20261121150000_ai_course_production_drafts.sql.
-- This migration is additive and must only be rolled back before any generated
-- course drafts or lesson production packages are relied upon.
DROP FUNCTION IF EXISTS public.create_course_from_generation_job(uuid);
DROP TABLE IF EXISTS public.learnora_lesson_production_packages;
DROP TABLE IF EXISTS public.learnora_course_generation_jobs;
DROP FUNCTION IF EXISTS public.touch_course_production_updated_at();

DELETE FROM public.learnora_staff_role_permissions
 WHERE permission_id IN (
     SELECT id FROM public.learnora_permissions WHERE permission_key = 'content.generate'
 );

DELETE FROM public.learnora_permissions
 WHERE permission_key = 'content.generate';
