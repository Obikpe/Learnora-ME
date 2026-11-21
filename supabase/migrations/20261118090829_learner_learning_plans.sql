-- Optional, versioned learner plans layered over the canonical published track catalogue.
-- The plan stores references to real course/track records; it never edits track curriculum.
CREATE TABLE IF NOT EXISTS public.learner_learning_plans (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  source_track_id uuid NULL REFERENCES public.learnora_learning_paths(id) ON DELETE SET NULL,
  goal text NOT NULL,
  weekly_time_minutes integer NOT NULL CHECK (weekly_time_minutes BETWEEN 15 AND 3000),
  plan_data jsonb NOT NULL DEFAULT '{}'::jsonb,
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
  generated_by text NOT NULL DEFAULT 'learnora-ai',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS learner_learning_plans_user_status_created_idx
  ON public.learner_learning_plans (user_id, status, created_at DESC);
ALTER TABLE public.learner_learning_plans ENABLE ROW LEVEL SECURITY;
REVOKE ALL PRIVILEGES ON TABLE public.learner_learning_plans FROM PUBLIC, anon, authenticated;
GRANT ALL PRIVILEGES ON TABLE public.learner_learning_plans TO service_role;
