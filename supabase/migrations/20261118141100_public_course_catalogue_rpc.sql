-- Collapse the public course catalogue's multi-query visibility and track
-- assembly into one server-only RPC. This avoids serial PostgREST round trips
-- while retaining the same creator approval and organisation opt-in rules.
CREATE INDEX IF NOT EXISTS idx_path_courses_course_path
  ON public.learnora_learning_path_courses (course_id, path_id);

CREATE OR REPLACE FUNCTION public.get_public_course_catalogue()
RETURNS TABLE (
  id uuid,
  organisation_id uuid,
  creator_id uuid,
  title text,
  slug text,
  short_description text,
  description text,
  level text,
  status text,
  ownership text,
  thumbnail_url text,
  estimated_hours numeric,
  settings jsonb,
  created_at timestamptz,
  tracks jsonb
)
LANGUAGE sql
STABLE
SECURITY INVOKER
SET search_path = ''
AS $function$
  SELECT
    c.id,
    c.organisation_id,
    c.creator_id,
    c.title,
    c.slug,
    c.short_description,
    c.description,
    c.level,
    c.status,
    c.ownership,
    c.thumbnail_url,
    c.estimated_hours,
    c.settings,
    c.created_at,
    CASE
      WHEN c.ownership = 'learnora' AND c.organisation_id IS NULL THEN
        COALESCE((
          SELECT jsonb_agg(
            jsonb_build_object(
              'id', lp.id,
              'name', lp.name,
              'slug', lp.slug,
              'order_index', lpc.order_index,
              'required', lpc.required IS DISTINCT FROM false
            )
            ORDER BY lpc.order_index, lp.name
          )
          FROM public.learnora_learning_path_courses AS lpc
          JOIN public.learnora_learning_paths AS lp
            ON lp.id = lpc.path_id
          WHERE lpc.course_id = c.id
            AND lp.owner_user_id IS NULL
            AND lp.organisation_id IS NULL
            AND lp.status = 'published'
        ), '[]'::jsonb)
      ELSE '[]'::jsonb
    END AS tracks
  FROM public.learnora_courses AS c
  LEFT JOIN public.organisations AS o
    ON o.id = c.organisation_id
  LEFT JOIN public.learnora_creator_accounts AS ca
    ON ca.id = c.creator_id
  WHERE c.status = 'published'
    AND (
      (c.ownership = 'learnora' AND c.organisation_id IS NULL)
      OR (
        c.ownership = 'creator'
        AND ca.status IN ('approved', 'active')
      )
      OR (
        c.ownership = 'organisation'
        AND c.settings ->> 'public_catalogue' = 'true'
        AND o.is_active IS TRUE
        AND o.settings ->> 'public_directory' = 'true'
      )
    )
  ORDER BY c.created_at DESC;
$function$;

REVOKE ALL ON FUNCTION public.get_public_course_catalogue() FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.get_public_course_catalogue() TO service_role;
