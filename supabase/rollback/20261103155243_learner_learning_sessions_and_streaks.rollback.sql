-- Rollback for 20261103155243_learner_learning_sessions_and_streaks.sql.
DROP FUNCTION IF EXISTS public.record_learner_learning_day(uuid, text, date, text, text, timestamptz);
DROP FUNCTION IF EXISTS public.get_learner_learning_seconds(uuid, text);
DROP TABLE IF EXISTS public.learner_learning_days;
DROP TABLE IF EXISTS public.learning_sessions;
