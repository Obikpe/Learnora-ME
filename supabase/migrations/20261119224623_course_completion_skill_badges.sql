-- Recognise foundational course completion without conflating it with verified skill mastery.
BEGIN;

WITH skill AS (
  INSERT INTO public.skills (name, category, description)
  VALUES (
    'Data Analytics Foundations',
    'Data Analytics',
    'Foundational exposure to analytical thinking, the analytics lifecycle, types of analytics, and data-informed decision-making through the Introduction to Data Analytics course.'
  )
  ON CONFLICT (name) DO UPDATE
    SET category = EXCLUDED.category,
        description = EXCLUDED.description
  RETURNING id
),
new_badge AS (
  INSERT INTO public.badges (name, description, criteria)
  SELECT
    'Data Analytics Foundations',
    'Awarded for completing Introduction to Data Analytics. This recognises course completion and is not a claim of independently verified professional competence.',
    jsonb_build_object(
      'type', 'course_completion',
      'course_id', 'e89cdf59-f4ad-4453-ab14-73e372fbce7e',
      'skill_id', skill.id
    )
  FROM skill
  WHERE NOT EXISTS (
    SELECT 1 FROM public.badges
    WHERE criteria->>'type' = 'course_completion'
      AND criteria->>'course_id' = 'e89cdf59-f4ad-4453-ab14-73e372fbce7e'
  )
  RETURNING id
),
resolved_badge AS (
  SELECT id FROM new_badge
  UNION ALL
  SELECT id FROM public.badges
  WHERE criteria->>'type' = 'course_completion'
    AND criteria->>'course_id' = 'e89cdf59-f4ad-4453-ab14-73e372fbce7e'
    AND NOT EXISTS (SELECT 1 FROM new_badge)
  LIMIT 1
)
INSERT INTO public.learner_badges (badge_id, user_id, awarded_at)
SELECT badge.id, enrolment.user_id, COALESCE(enrolment.completed_at, now())
FROM resolved_badge AS badge
CROSS JOIN public.learnora_enrolments AS enrolment
WHERE enrolment.course_id = 'e89cdf59-f4ad-4453-ab14-73e372fbce7e'
  AND enrolment.status = 'completed'
ON CONFLICT (badge_id, user_id) DO NOTHING;

COMMENT ON TABLE public.learner_badges IS
  'Learner achievements. Course-completion badges are recognition of completed learning, not verified professional mastery.';

COMMIT;
