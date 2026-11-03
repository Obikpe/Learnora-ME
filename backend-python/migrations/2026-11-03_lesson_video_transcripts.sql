-- Add an optional transcript to each lesson video.
-- Apply this migration to the Learnora Supabase database before relying on transcript-aware AI.
ALTER TABLE public.lesson_videos
  ADD COLUMN IF NOT EXISTS transcript_text text;

COMMENT ON COLUMN public.lesson_videos.transcript_text IS
  'Plain-text transcript or captions for the video, used as authenticated lesson context by Learnora AI.';
