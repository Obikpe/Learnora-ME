-- Separate creator-sale actions from the general course-assignment permission.
-- No roles are granted these permissions automatically; an authorised platform
-- administrator must explicitly assign each permission to the intended finance role.
BEGIN;

INSERT INTO public.learnora_permissions (permission_key, name, description, category)
VALUES
  ('creator_sales.record', 'Record creator sales', 'Record creator marketplace sales and their financial ledger entries.', 'creator_finance'),
  ('creator_sales.release', 'Release creator sales', 'Release pending creator sales into the available balance.', 'creator_finance'),
  ('creator_sales.refund', 'Refund creator sales', 'Refund creator sales and create the corresponding ledger entries.', 'creator_finance')
ON CONFLICT (permission_key) DO NOTHING;

COMMIT;
