-- Enforce one active submission per learner/project and one verified
-- project evidence row per learner/skill/submission. The live tables were
-- checked read-only and currently contain no rows or duplicate pairs.
CREATE UNIQUE INDEX IF NOT EXISTS project_submissions_one_active_per_learner_idx
  ON public.project_submissions (project_id, user_id)
  WHERE status IN ('submitted','reviewed','approved');

CREATE UNIQUE INDEX IF NOT EXISTS skill_evidence_project_submission_skill_unique_idx
  ON public.skill_evidence (user_id, skill_id, source_id)
  WHERE evidence_type = 'project' AND source_id IS NOT NULL;
