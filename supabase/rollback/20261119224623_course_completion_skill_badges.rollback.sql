-- Remove only the Introduction to Data Analytics completion badge and its awards.
BEGIN;
DELETE FROM public.learner_badges
WHERE badge_id IN (
  SELECT id FROM public.badges
  WHERE criteria->>'type' = 'course_completion'
    AND criteria->>'course_id' = 'e89cdf59-f4ad-4453-ab14-73e372fbce7e'
);
DELETE FROM public.badges
WHERE criteria->>'type' = 'course_completion'
  AND criteria->>'course_id' = 'e89cdf59-f4ad-4453-ab14-73e372fbce7e';
DELETE FROM public.skills
WHERE name = 'Data Analytics Foundations'
  AND NOT EXISTS (
    SELECT 1 FROM public.badges
    WHERE criteria->>'skill_id' = skills.id::text
  );
COMMIT;
