ALTER TABLE public.lesson_videos ADD COLUMN IF NOT EXISTS transcript_text text;
COMMENT ON COLUMN public.lesson_videos.transcript_text IS 'Plain-text transcript or captions for the video, used as authenticated lesson context by Learnora AI.';
