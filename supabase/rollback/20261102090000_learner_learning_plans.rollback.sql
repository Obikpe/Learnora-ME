-- Rollback for 20261102090000_learner_learning_plans.sql.
-- This removes saved personalised plans; export any learner plan data before running.
DROP TABLE IF EXISTS public.learner_learning_plans;
