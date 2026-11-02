-- Active quiz sessions are a server-side lock that prevents AI tutor requests
-- while a learner is taking a quiz. Sessions expire automatically if a browser
-- closes unexpectedly; normal close/submit flows release them earlier.
CREATE TABLE IF NOT EXISTS public.quiz_active_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  quiz_id uuid NOT NULL REFERENCES public.quizzes(id) ON DELETE CASCADE,
  course_id uuid NOT NULL REFERENCES public.learnora_courses(id) ON DELETE CASCADE,
  lesson_id uuid NULL REFERENCES public.learnora_lessons(id) ON DELETE SET NULL,
  started_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  CONSTRAINT quiz_active_sessions_expiry_after_start CHECK (expires_at > started_at),
);
CREATE INDEX IF NOT EXISTS quiz_active_sessions_user_expiry_idx
  ON public.quiz_active_sessions (user_id, expires_at);
CREATE INDEX IF NOT EXISTS quiz_active_sessions_quiz_idx
  ON public.quiz_active_sessions (quiz_id);
ALTER TABLE public.quiz_active_sessions ENABLE ROW LEVEL SECURITY;
REVOKE ALL PRIVILEGES ON TABLE public.quiz_active_sessions FROM PUBLIC, anon, authenticated;
GRANT ALL PRIVILEGES ON TABLE public.quiz_active_sessions TO service_role;
