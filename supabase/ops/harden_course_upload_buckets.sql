-- Apply manually in the Supabase SQL editor after reviewing the intended upload limits.
-- Both buckets remain private. Signed-upload API models enforce the same limits.
BEGIN;

UPDATE storage.buckets
SET public = false,
    file_size_limit = 2147483648,
    allowed_mime_types = ARRAY[
      'video/mp4',
      'video/webm',
      'video/quicktime',
      'video/mpeg',
      'video/x-msvideo'
    ]::text[]
WHERE id = 'learnora-course-media';

UPDATE storage.buckets
SET public = false,
    file_size_limit = 104857600,
    allowed_mime_types = ARRAY[
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/csv',
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'image/jpeg',
      'image/png',
      'image/webp',
      'image/gif',
      'text/plain',
      'application/zip',
      'application/json'
    ]::text[]
WHERE id = 'learnora-resources';

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM storage.buckets
    WHERE id = 'learnora-course-media'
      AND public = false
      AND file_size_limit = 2147483648
      AND cardinality(allowed_mime_types) = 5
  ) THEN
    RAISE EXCEPTION 'learnora-course-media bucket security configuration failed';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM storage.buckets
    WHERE id = 'learnora-resources'
      AND public = false
      AND file_size_limit = 104857600
      AND cardinality(allowed_mime_types) = 15
  ) THEN
    RAISE EXCEPTION 'learnora-resources bucket security configuration failed';
  END IF;
END;
$$;

COMMIT;

-- Verify:
SELECT id, public, file_size_limit, allowed_mime_types
FROM storage.buckets
WHERE id IN ('learnora-course-media', 'learnora-resources')
ORDER BY id;
