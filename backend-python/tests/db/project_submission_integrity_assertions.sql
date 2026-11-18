DO $$
DECLARE
  v_active integer;
  v_evidence integer;
BEGIN
  SELECT count(*) INTO v_active
  FROM pg_index i
  JOIN pg_class idx ON idx.oid = i.indexrelid
  JOIN pg_class tbl ON tbl.oid = i.indrelid
  JOIN pg_namespace ns ON ns.oid = tbl.relnamespace
  WHERE ns.nspname = 'public'
    AND tbl.relname = 'project_submissions'
    AND idx.relname = 'project_submissions_one_active_per_learner_idx'
    AND i.indisunique
    AND pg_get_expr(i.indpred, i.indrelid) ILIKE '%status%'
    AND pg_get_expr(i.indpred, i.indrelid) ILIKE '%submitted%'
    AND pg_get_expr(i.indpred, i.indrelid) ILIKE '%reviewed%'
    AND pg_get_expr(i.indpred, i.indrelid) ILIKE '%approved%';
  IF v_active <> 1 THEN
    RAISE EXCEPTION 'active project submissions must be unique per learner and project';
  END IF;

  SELECT count(*) INTO v_evidence
  FROM pg_index i
  JOIN pg_class idx ON idx.oid = i.indexrelid
  JOIN pg_class tbl ON tbl.oid = i.indrelid
  JOIN pg_namespace ns ON ns.oid = tbl.relnamespace
  WHERE ns.nspname = 'public'
    AND tbl.relname = 'skill_evidence'
    AND idx.relname = 'skill_evidence_project_submission_skill_unique_idx'
    AND i.indisunique
    AND pg_get_expr(i.indpred, i.indrelid) ILIKE '%evidence_type%'
    AND pg_get_expr(i.indpred, i.indrelid) ILIKE '%project%'
    AND pg_get_expr(i.indpred, i.indrelid) ILIKE '%source_id IS NOT NULL%';
  IF v_evidence <> 1 THEN
    RAISE EXCEPTION 'project evidence must be unique per learner, skill and submission';
  END IF;
END $$;
