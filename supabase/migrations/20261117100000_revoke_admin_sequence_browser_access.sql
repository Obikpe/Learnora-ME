-- Remove unnecessary browser-role access to the legacy admins identity sequence.
-- Backend writes use the server-side service_role key; browser clients have no
-- direct table privileges and must not be able to advance or inspect this sequence.
BEGIN;

REVOKE ALL PRIVILEGES ON SEQUENCE public.admins_id_seq
  FROM PUBLIC, anon, authenticated;

COMMIT;
