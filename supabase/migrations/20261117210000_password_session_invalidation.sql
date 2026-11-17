-- Track the last password change so previously issued JWT sessions can be rejected.
-- Existing accounts remain compatible: NULL preserves their current sessions until
-- the next successful password change or reset. New rows receive a timestamp.
ALTER TABLE public.users
    ADD COLUMN IF NOT EXISTS password_changed_at timestamptz;

ALTER TABLE public.admins
    ADD COLUMN IF NOT EXISTS password_changed_at timestamptz;

ALTER TABLE public.users
    ALTER COLUMN password_changed_at SET DEFAULT now();

ALTER TABLE public.admins
    ALTER COLUMN password_changed_at SET DEFAULT now();

COMMENT ON COLUMN public.users.password_changed_at IS
    'Timestamp of the latest password change/reset; JWTs issued before it are invalid.';
COMMENT ON COLUMN public.admins.password_changed_at IS
    'Timestamp of the latest password change/reset; JWTs issued before it are invalid.';
