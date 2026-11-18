CREATE INDEX IF NOT EXISTS certificates_course_id_idx
  ON public.certificates (course_id);
CREATE INDEX IF NOT EXISTS certificates_organisation_id_idx
  ON public.certificates (organisation_id);
CREATE INDEX IF NOT EXISTS certificates_revoked_by_idx
  ON public.certificates (revoked_by);
CREATE INDEX IF NOT EXISTS learner_learning_plans_source_track_id_idx
  ON public.learner_learning_plans (source_track_id);
CREATE INDEX IF NOT EXISTS quiz_active_sessions_course_id_idx
  ON public.quiz_active_sessions (course_id);
CREATE INDEX IF NOT EXISTS quiz_active_sessions_lesson_id_idx
  ON public.quiz_active_sessions (lesson_id);
