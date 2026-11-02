-- Rollback for 20261102100000_quiz_active_sessions.sql.
-- Active sessions are transient quiz locks; no learner results are stored here.
DROP TABLE IF EXISTS public.quiz_active_sessions;
