DO $$
DECLARE
  v_active integer;
  v_evidence integer;
BEGIN
  SELECT count(*) INTO v_active
  FROM pg_indexes
  WHERE schemaname='public' AND tablename='project_submissions'
    AND indexname='project_submissions_one_active_per_learner_idx'
    AND indexdef ILIKE '%WHERE (status = ANY%';
  IF v_active <> 1 THEN
    RAISE EXCEPTION 'active project submissions must be unique per learner and project';
  END IF;

  SELECT count(*) INTO v_evidence
  FROM pg_indexes
  WHERE schemaname='public' AND tablename='skill_evidence'
    AND indexname='skill_evidence_project_submission_skill_unique_idx'
    AND indexdef ILIKE '%WHERE (evidence_type =%';
  IF v_evidence <> 1 THEN
    RAISE EXCEPTION 'project evidence must be unique per learner, skill and submission';
  END IF;
END $$;
