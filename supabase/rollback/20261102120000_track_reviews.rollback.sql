-- Rollback for 20261102120000_track_reviews.sql.
DELETE FROM public.learnora_staff_role_permissions
WHERE permission_id IN (
  SELECT id FROM public.learnora_permissions WHERE permission_key = 'track_reviews.moderate'
);
DELETE FROM public.learnora_permissions WHERE permission_key = 'track_reviews.moderate';
DROP TABLE IF EXISTS public.learnora_track_reviews;
