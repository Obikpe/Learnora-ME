-- Track completion reviews are private by default and public only after
-- explicit learner consent plus staff approval.
CREATE TABLE IF NOT EXISTS public.learnora_track_reviews (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  track_id uuid NOT NULL REFERENCES public.learnora_learning_paths(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  rating smallint NOT NULL,
  comment text NULL,
  public_consent boolean NOT NULL DEFAULT false,
  moderation_status text NOT NULL DEFAULT 'pending',
  moderated_by uuid NULL REFERENCES public.users(id) ON DELETE SET NULL,
  moderated_at timestamptz NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT learnora_track_reviews_rating_check CHECK (rating BETWEEN 1 AND 5),
  CONSTRAINT learnora_track_reviews_comment_length_check CHECK (comment IS NULL OR char_length(comment) <= 2000),
  CONSTRAINT learnora_track_reviews_moderation_status_check CHECK (moderation_status IN ('pending','approved','rejected')),
  CONSTRAINT learnora_track_reviews_track_user_unique UNIQUE (track_id, user_id)
);

CREATE INDEX IF NOT EXISTS learnora_track_reviews_track_created_idx
  ON public.learnora_track_reviews (track_id, created_at DESC);
CREATE INDEX IF NOT EXISTS learnora_track_reviews_moderation_idx
  ON public.learnora_track_reviews (moderation_status, created_at DESC);
CREATE INDEX IF NOT EXISTS learnora_track_reviews_public_idx
  ON public.learnora_track_reviews (track_id, rating)
  WHERE public_consent = true AND moderation_status = 'approved';

ALTER TABLE public.learnora_track_reviews ENABLE ROW LEVEL SECURITY;
REVOKE ALL PRIVILEGES ON TABLE public.learnora_track_reviews FROM PUBLIC, anon, authenticated;
GRANT ALL PRIVILEGES ON TABLE public.learnora_track_reviews TO service_role;

-- The catalog-only CI baseline intentionally omits production role rows.
-- Ensure only the two system roles required by this dedicated permission exist.
INSERT INTO public.learnora_staff_roles (name, slug, description, is_system_role, status)
SELECT 'Super Admin', 'super_admin', 'Platform-wide administration.', true, 'active'
WHERE NOT EXISTS (SELECT 1 FROM public.learnora_staff_roles WHERE slug = 'super_admin');

INSERT INTO public.learnora_staff_roles (name, slug, description, is_system_role, status)
SELECT 'Learning & Curriculum', 'learning_curriculum', 'Manage learning design and curriculum.', false, 'active'
WHERE NOT EXISTS (SELECT 1 FROM public.learnora_staff_roles WHERE slug = 'learning_curriculum');

INSERT INTO public.learnora_permissions (permission_key, name, description, category)
VALUES (
  'track_reviews.moderate',
  'Moderate Track Reviews',
  'Review learner feedback and control whether consented track reviews may be published.',
  'learning'
)
ON CONFLICT (permission_key) DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  category = EXCLUDED.category;

INSERT INTO public.learnora_staff_role_permissions (role_id, permission_id)
SELECT role.id, permission.id
FROM public.learnora_staff_roles role
CROSS JOIN public.learnora_permissions permission
WHERE role.slug IN ('super_admin','learning_curriculum')
  AND permission.permission_key = 'track_reviews.moderate'
ON CONFLICT (role_id, permission_id) DO NOTHING;
