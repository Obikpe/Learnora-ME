-- Link Learnora learner subscriptions to the provider-side recurring agreement.
-- Apply only through the approved migration process after checking the target
-- Supabase project and taking the required backup. This file is not auto-applied.
ALTER TABLE public.learnora_subscriptions
    ADD COLUMN IF NOT EXISTS provider_subscription_code text,
    ADD COLUMN IF NOT EXISTS provider_email_token text;

-- A Paystack subscription code must identify at most one local subscription.
CREATE UNIQUE INDEX IF NOT EXISTS learnora_subscriptions_provider_code_uidx
    ON public.learnora_subscriptions(provider_subscription_code)
    WHERE provider_subscription_code IS NOT NULL;

COMMENT ON COLUMN public.learnora_subscriptions.provider_subscription_code
    IS 'Provider-side recurring subscription identifier; never exposed to learner clients.';
COMMENT ON COLUMN public.learnora_subscriptions.provider_email_token
    IS 'Secret required to cancel a Paystack recurring subscription; server-only, never exposed to learner clients.';
