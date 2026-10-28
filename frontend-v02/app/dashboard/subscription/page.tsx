"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, CheckCircle2, CreditCard, ShieldCheck } from "lucide-react";
import Shell from "../../../components/dashboard/Shell";
import SectionHeader from "../../../components/dashboard/SectionHeader";
import Skeleton from "../../../components/feedback/Skeleton";
import { currentUser } from "../../../lib/api";
import { request } from "../../../lib/api/client";

type Subscription = {
  has_subscription: boolean;
  status?: string | null;
  provider?: string | null;
  plan_code?: string | null;
  billing_interval?: string | null;
  currency?: string | null;
  amount_minor?: number | null;
  current_period_end?: string | null;
  cancelled_at?: string | null;
  can_cancel?: boolean;
};

function dateLabel(value?: string | null) {
  if (!value) return "Not available";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Not available" : date.toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
}

function moneyLabel(currency?: string | null, minor?: number | null) {
  if (!currency || minor == null) return "Amount not available";
  try {
    return new Intl.NumberFormat(undefined, { style: "currency", currency, maximumFractionDigits: 2 }).format(minor / 100);
  } catch {
    return currency + " " + (minor / 100).toFixed(2);
  }
}

export default function SubscriptionPage() {
  const router = useRouter();
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const user = await currentUser();
        if (!["normal", "witstart"].includes(user.role) || user.account_type === "cohort") {
          router.replace("/dashboard");
          return;
        }
        const result = await request<Subscription>("/billing/subscription");
        if (!cancelled) setSubscription(result);
      } catch (e: any) {
        if (!cancelled) setError(e.message || "Your subscription details could not be loaded.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => { cancelled = true; };
  }, [router]);

  async function cancelSubscription() {
    if (!subscription?.can_cancel || cancelling) return;
    const confirmed = window.confirm("Cancel automatic renewal for your Learnora subscription? Paystack will be asked to stop future recurring charges. Your current paid access may remain available until the period end shown below.");
    if (!confirmed) return;
    setCancelling(true);
    setError("");
    setNotice("");
    try {
      const result = await request<any>("/billing/subscription/cancel", { method: "POST", body: JSON.stringify({}) });
      setSubscription(old => old ? { ...old, status: "cancelled", cancelled_at: result.cancelled_at || new Date().toISOString(), can_cancel: false, current_period_end: result.current_period_end || old.current_period_end } : old);
      setNotice(result.message || "Paystack confirmed the cancellation request. Future renewal has been stopped.");
    } catch (e: any) {
      setError(e.message || "The subscription could not be cancelled. No cancellation is being reported as complete.");
    } finally {
      setCancelling(false);
    }
  }

  return <Shell active="subscription">
    <SectionHeader eyebrow="Your account" title="Subscription" description="Review your Learnora learner plan and manage recurring payments." />
    {loading ? <div className="mt-8"><Skeleton variant="compact" label="Loading your subscription details" /></div> : <>
      {error && <div role="alert" className="mt-6 flex items-start gap-3 rounded-xl border border-red-400/20 bg-red-400/[.05] p-4 text-sm text-red-200"><AlertCircle size={17} className="mt-0.5 shrink-0"/><p>{error}</p></div>}
      {notice && <div role="status" className="mt-6 flex items-start gap-3 rounded-xl border border-emerald-400/20 bg-emerald-400/[.05] p-4 text-sm text-emerald-200"><CheckCircle2 size={17} className="mt-0.5 shrink-0"/><p>{notice}</p></div>}
      <section className="mt-7 max-w-3xl rounded-2xl border border-white/[.08] bg-[#0e1319] p-5 sm:p-7">
        <div className="flex items-start gap-4">
          <div className="rounded-xl border border-[#d7ad35]/20 bg-[#d7ad35]/10 p-3"><CreditCard className="gold" size={22}/></div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-bold uppercase tracking-[.18em] gold">Learner billing</p>
            <h2 className="mt-2 text-xl font-semibold">{subscription?.has_subscription ? (subscription.plan_code || "Learnora learner plan") : "No subscription record found"}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-400">{subscription?.has_subscription ? "This is the subscription record currently linked to your Learnora learner account." : "There is no Learnora subscription record linked to this account. If you believe Paystack is still charging you, contact Learnora support so the external billing record can be traced."}</p>
          </div>
          {subscription?.has_subscription && <span className={"shrink-0 rounded-full border px-3 py-1 text-xs capitalize " + (subscription.status === "active" ? "border-emerald-400/20 text-emerald-200" : "border-white/10 text-slate-300")}>{(subscription.status || "unknown").replaceAll("_", " ")}</span>}
        </div>
        {subscription?.has_subscription && <dl className="mt-7 grid gap-4 border-t border-white/[.08] pt-6 sm:grid-cols-2">
          <div><dt className="text-xs text-slate-500">Provider</dt><dd className="mt-1 text-sm capitalize text-slate-200">{subscription.provider || "Not recorded"}</dd></div>
          <div><dt className="text-xs text-slate-500">Billing interval</dt><dd className="mt-1 text-sm capitalize text-slate-200">{subscription.billing_interval || "Not recorded"}</dd></div>
          <div><dt className="text-xs text-slate-500">Recorded payment amount</dt><dd className="mt-1 text-sm text-slate-200">{moneyLabel(subscription.currency, subscription.amount_minor)}</dd></div>
          <div><dt className="text-xs text-slate-500">Current paid-through date</dt><dd className="mt-1 text-sm text-slate-200">{dateLabel(subscription.current_period_end)}</dd></div>
          {subscription.cancelled_at && <div className="sm:col-span-2"><dt className="text-xs text-slate-500">Cancellation requested</dt><dd className="mt-1 text-sm text-slate-200">{dateLabel(subscription.cancelled_at)}</dd></div>}
        </dl>}
        {subscription?.can_cancel && <div className="mt-7 border-t border-white/[.08] pt-6">
          <button type="button" disabled={cancelling} onClick={cancelSubscription} className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-red-400/25 px-4 py-3 text-sm font-semibold text-red-200 transition hover:bg-red-400/[.07] disabled:cursor-wait disabled:opacity-50">{cancelling ? <><span className="size-4 animate-spin rounded-full border-2 border-red-200/30 border-t-red-200"/>Cancelling renewal…</> : "Cancel subscription"}</button>
          <p className="mt-3 text-xs leading-6 text-slate-500">Learnora will confirm cancellation with the payment provider before showing it as cancelled. Cancelling renewal does not automatically refund a payment already made.</p>
        </div>}
        {subscription?.has_subscription && !subscription.can_cancel && subscription.status !== "cancelled" && <div className="mt-7 flex items-start gap-3 rounded-xl border border-amber-300/15 bg-amber-300/[.035] p-4 text-xs leading-6 text-amber-100"><ShieldCheck size={16} className="mt-0.5 shrink-0"/><p>This record is not currently linked to the provider credentials needed to cancel recurring billing automatically. Do not assume renewal has stopped. Contact Learnora support to reconcile the provider subscription.</p></div>}
        {subscription?.status === "cancelled" && <p className="mt-6 text-sm leading-6 text-slate-400">Renewal is marked cancelled. Your current paid-through date, if shown, indicates when existing access is due to end.</p>}
      </section>
      <p className="mt-5 max-w-3xl text-xs leading-6 text-slate-600">Only individual Learnora learner subscriptions are managed here. Organisation, cohort and internal team access is managed separately. If you deleted your Learnora account but still receive payment notifications, the external subscription must also be cancelled with the provider; deleting an account record alone cannot cancel a payment agreement held by Paystack.</p>
    </>}
  </Shell>;
}
