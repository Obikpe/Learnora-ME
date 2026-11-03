-- Roll back atomic session coordination only after the application has
-- stopped calling these RPCs. Keep learning_sessions and learner_learning_days
-- intact; they contain user learning history.
drop function if exists public.start_learner_learning_session(uuid, text, text);
drop function if exists public.heartbeat_learner_learning_session(uuid, uuid, text, boolean);
drop function if exists public.end_learner_learning_session(uuid, uuid, text, boolean);
drop index if exists public.learning_sessions_one_active_per_learner_idx;
