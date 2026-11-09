"use client";

import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { CheckCircle2, KeyRound, ShieldCheck, UserRound, Trash2, AlertTriangle } from "lucide-react";
import { request } from "../../lib/api/client";
import { updateCachedCurrentUser } from "../../lib/api/auth";

export default function AccountSettings({ user }: { user: any }) {
  const [form, setForm] = useState({ current_password: "", new_password: "", confirm_password: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [showDelete, setShowDelete] = useState(false);
  const [deleteText, setDeleteText] = useState("");
  const [deletionReason, setDeletionReason] = useState("not_using");
  const [deletionReasonDetails, setDeletionReasonDetails] = useState("");
  const [deleteBusy, setDeleteBusy] = useState(false);
  const [deleteError, setDeleteError] = useState("");
  const [deleteNotice, setDeleteNotice] = useState("");
  const [marketingOptIn, setMarketingOptIn] = useState(Boolean(user?.marketing_email_opt_in));
  const [marketingBusy, setMarketingBusy] = useState(false);
  const [marketingMessage, setMarketingMessage] = useState("");

  useEffect(() => { setMarketingOptIn(Boolean(user?.marketing_email_opt_in)); }, [user?.marketing_email_opt_in]);

  async function updateMarketingPreference(enabled: boolean) {
    setMarketingBusy(true);
    setMarketingMessage("");
    try {
      await request("/account-lifecycle/marketing-preferences", { method: "PATCH", body: JSON.stringify({ enabled }) });
      setMarketingOptIn(enabled);
      updateCachedCurrentUser({ marketing_email_opt_in: enabled, marketing_in_app_opt_in: enabled });
      setMarketingMessage(enabled ? "You are opted in to Learnora marketing updates." : "You are unsubscribed from Learnora marketing updates.");
    } catch (e: any) {
      setMarketingMessage(e.message || "We could not update your email preferences.");
    } finally { setMarketingBusy(false); }
  }

  async function changePassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setNotice("");
    if (form.new_password !== form.confirm_password) {
      setError("The new passwords do not match.");
      return;
    }
    if (form.new_password.length < 8) {
      setError("Choose a new password with at least 8 characters.");
      return;
    }
    setBusy(true);
    try {
      await request("/auth/change-password", { method: "POST", body: JSON.stringify(form) });
      setForm({ current_password: "", new_password: "", confirm_password: "" });
      setNotice("Your password has been changed.");
    } catch (e: any) {
      setError(e.message || "Your password could not be changed.");
    } finally {
      setBusy(false);
    }
  }

  async function requestDeletion() {
    setDeleteError("");
    setDeleteNotice("");
    if (deleteText !== "DELETE") {
      setDeleteError("Type DELETE to confirm your request.");
      return;
    }
    setDeleteBusy(true);
    try {
      const result = await request<{ message?: string }>("/account-lifecycle/request-deletion", {
        method: "POST",
        body: JSON.stringify({ reason: deletionReason, reason_details: deletionReasonDetails.trim() || null }),
      });
      setDeleteNotice(result.message || "A confirmation link has been sent to your email address.");
      setShowDelete(false);
      setDeleteText("");
    } catch (e: any) {
      setDeleteError(e.message || "We could not send the confirmation email. Please try again.");
    } finally {
      setDeleteBusy(false);
    }
  }

  const access = user?.access_state || user?.sub_status || "Not provided";
  const hasOwnerMembership = (user?.organisation_memberships || []).some((membership: any) => membership.role === "owner" && membership.status === "active");
  const canDeleteAccount = user?.account_type === "learner" && user?.role === "normal" && user?.organisation_role !== "owner" && !hasOwnerMembership;
  return <div className="mt-7 grid gap-5 xl:grid-cols-[.85fr_1.15fr]">
    <section className="h-fit rounded-2xl border border-white/[.08] bg-[#0e1319] p-5 sm:p-6">
      <div className="flex items-center gap-3"><div className="rounded-xl bg-[#d7ad35]/10 p-2.5"><UserRound className="gold" size={19}/></div><div><h2 className="font-semibold">Account information</h2><p className="mt-1 text-xs text-slate-500">Your account details.</p></div></div>
      <dl className="mt-6 divide-y divide-white/[.06]">
        <div className="py-4 first:pt-0"><dt className="text-xs text-slate-500">Display name</dt><dd className="mt-1 break-words text-sm text-slate-200">{user?.name || "Not set"}</dd></div>
        <div className="py-4"><dt className="text-xs text-slate-500">Email address</dt><dd className="mt-1 break-words text-sm text-slate-200">{user?.email || "Not available"}</dd></div>
        <div className="py-4"><dt className="text-xs text-slate-500">Account type</dt><dd className="mt-1 text-sm capitalize text-slate-200">{String(user?.account_type || user?.role || "Learner").replaceAll("_", " ")}</dd></div>
        <div className="py-4 last:pb-0"><dt className="text-xs text-slate-500">Access status</dt><dd className="mt-1 inline-flex items-center gap-2 text-sm capitalize text-slate-200"><span className="h-1.5 w-1.5 rounded-full bg-[#d7ad35]"/>{String(access).replaceAll("_", " ")}</dd></div>
      </dl>
    </section>
    <section className="rounded-2xl border border-white/[.08] bg-[#0e1319] p-5 sm:p-6">
      <div className="flex items-center gap-3"><div className="rounded-xl bg-[#d7ad35]/10 p-2.5"><KeyRound className="gold" size={19}/></div><div><h2 className="font-semibold">Change password</h2><p className="mt-1 text-xs text-slate-500">Enter your current password and choose a new one.</p></div></div>
      {error && <p role="alert" className="mt-5 rounded-xl border border-red-400/20 bg-red-400/[.05] p-3 text-sm text-red-200">{error}</p>}
      {notice && <p role="status" className="mt-5 flex items-center gap-2 rounded-xl border border-emerald-400/20 bg-emerald-400/[.05] p-3 text-sm text-emerald-200"><CheckCircle2 size={15}/>{notice}</p>}
      <form onSubmit={changePassword} className="mt-6 space-y-4">
        <label className="block text-xs text-slate-400">Current password<input required type="password" autoComplete="current-password" value={form.current_password} onChange={e => setForm(old => ({ ...old, current_password: e.target.value }))} className="mt-2 w-full rounded-xl border border-white/10 bg-[#090c10] p-3 text-sm text-white outline-none focus:border-[#d7ad35]/50"/></label>
        <label className="block text-xs text-slate-400">New password<input required minLength={8} type="password" autoComplete="new-password" value={form.new_password} onChange={e => setForm(old => ({ ...old, new_password: e.target.value }))} className="mt-2 w-full rounded-xl border border-white/10 bg-[#090c10] p-3 text-sm text-white outline-none focus:border-[#d7ad35]/50"/><span className="mt-1 block text-[11px] text-slate-600">At least 8 characters.</span></label>
        <label className="block text-xs text-slate-400">Confirm new password<input required minLength={8} type="password" autoComplete="new-password" value={form.confirm_password} onChange={e => setForm(old => ({ ...old, confirm_password: e.target.value }))} className="mt-2 w-full rounded-xl border border-white/10 bg-[#090c10] p-3 text-sm text-white outline-none focus:border-[#d7ad35]/50"/></label>
        <button disabled={busy} className="inline-flex items-center gap-2 rounded-xl bg-[#d7ad35] px-4 py-3 text-sm font-bold text-black disabled:opacity-50"><ShieldCheck size={15}/>{busy ? "Updating password…" : "Update password"}</button>
      </form>
    </section>
    {user?.account_type === "learner" && user?.role === "normal" && <section className="xl:col-span-2 rounded-2xl border border-white/[.08] bg-[#0e1319] p-5 sm:p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="max-w-2xl">
          <h2 className="font-semibold">Marketing updates</h2>
          <p className="mt-2 text-sm leading-6 text-slate-400">Choose whether Learnora can send promotional updates by email and in-app notifications about new learning tracks, course announcements, offers and discounts. This is separate from essential account, security and enrolled-course service messages.</p>
          {marketingMessage && <p role="status" className="mt-2 text-xs text-slate-300">{marketingMessage}</p>}
        </div>
        <button type="button" disabled={marketingBusy} onClick={() => void updateMarketingPreference(!marketingOptIn)} className={`inline-flex min-h-10 shrink-0 items-center justify-center rounded-xl px-4 py-2.5 text-xs font-semibold transition disabled:opacity-50 ${marketingOptIn ? "border border-white/15 text-slate-300 hover:bg-white/5" : "bg-[#d7ad35] text-black hover:bg-[#e4c56e]"}`}>
          {marketingBusy ? "Saving…" : marketingOptIn ? "Unsubscribe from marketing" : "Opt in to marketing updates"}
        </button>
      </div>
    </section>}
    {canDeleteAccount ? <section className="xl:col-span-2 rounded-2xl border border-red-500/20 bg-[#0e1319] p-5 sm:p-6">
      <div className="flex items-start gap-3">
        <div className="rounded-xl bg-red-500/10 p-2.5 text-red-300"><AlertTriangle size={19}/></div>
        <div className="min-w-0 flex-1">
          <h2 className="font-semibold text-red-200">Delete account</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">Request account deletion. We will email a secure confirmation link to {user?.email || "your registered email address"}. After you confirm, your account is deactivated for 30 days. You can reactivate it during that period. After 30 days, the live sign-in profile will be permanently closed; limited records may be retained under Learnora’s retention policy.</p>
          <p className="mt-2 max-w-3xl text-xs leading-5 text-slate-500">You can restore your account and continue learning during the recovery period. After that, limited learning, security or audit records may be retained where required under Learnora’s privacy and retention policy. Read the <a className="underline underline-offset-4" href="/privacy">Privacy Policy</a>.</p>
          {deleteError && <p role="alert" className="mt-4 rounded-xl border border-red-400/20 bg-red-400/[.05] p-3 text-sm text-red-200">{deleteError}</p>}
          {deleteNotice && <p role="status" className="mt-4 rounded-xl border border-emerald-400/20 bg-emerald-400/[.05] p-3 text-sm text-emerald-200">{deleteNotice}</p>}
          <button type="button" onClick={() => {setShowDelete(true);setDeleteError("");setDeleteText("");setDeletionReason("not_using");setDeletionReasonDetails("");}} className="mt-5 inline-flex min-h-11 items-center gap-2 rounded-xl border border-red-400/30 px-4 py-2.5 text-sm font-semibold text-red-200 transition-colors hover:bg-red-400/10"><Trash2 size={15}/>Request account deletion</button>
        </div>
      </div>
    </section> : <section className="xl:col-span-2 rounded-2xl border border-white/[.08] bg-[#0e1319] p-5 sm:p-6"><h2 className="font-semibold">Need to close this account?</h2><p className="mt-2 text-sm leading-6 text-slate-400">Contact <a className="underline underline-offset-4" href="mailto:learnorame@gmail.com">Learnora support</a> so we can help with your account and any organisation or programme responsibilities.</p></section>}
    {showDelete && <div className="fixed inset-0 z-[90] grid place-items-center bg-black/70 p-4" role="presentation" onMouseDown={e=>{if(e.target===e.currentTarget)setShowDelete(false);}}>
      <section role="dialog" aria-modal="true" aria-labelledby="delete-account-title" className="w-full max-w-lg rounded-2xl border border-red-400/30 bg-[#11171e] p-6 shadow-2xl">
        <h2 id="delete-account-title" className="text-xl font-semibold">Confirm deletion request</h2>
        <p className="mt-3 text-sm leading-6 text-slate-400">A confirmation email will be sent to your registered address. The link expires after 60 minutes. If you confirm, your account will be deactivated for 30 days. You can reactivate it during that period. After 30 days, permanent deletion will be processed.</p>
        <label className="mt-5 block text-sm text-slate-300">Why are you leaving?
          <select value={deletionReason} onChange={e=>setDeletionReason(e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-[#090c10] p-3 text-sm text-white outline-none focus:border-red-400/50">
            <option value="not_using">I no longer need Learnora</option>
            <option value="found_alternative">I found another learning platform</option>
            <option value="missing_content">I could not find the courses or tracks I needed</option>
            <option value="technical_issues">I experienced technical problems</option>
            <option value="cost">Pricing or future costs are a concern</option>
            <option value="privacy">I have privacy or data concerns</option>
            <option value="other">Another reason</option>
          </select>
        </label>
        <label className="mt-4 block text-sm text-slate-300">Anything else you would like us to know? <span className="text-xs text-slate-500">(Optional)</span>
          <textarea maxLength={1000} rows={3} value={deletionReasonDetails} onChange={e=>setDeletionReasonDetails(e.target.value)} className="mt-2 w-full resize-y rounded-xl border border-white/10 bg-[#090c10] p-3 text-sm text-white outline-none focus:border-red-400/50" placeholder="Share any details that may help us improve Learnora."/>
        </label>
        <label className="mt-5 block text-sm text-slate-300">Type DELETE to continue<input autoComplete="off" value={deleteText} onChange={e=>setDeleteText(e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-[#090c10] p-3 text-sm text-white outline-none focus:border-red-400/50"/></label>
        {deleteError && <p role="alert" className="mt-3 text-sm text-red-300">{deleteError}</p>}
        <div className="mt-6 flex flex-wrap justify-end gap-3"><button type="button" onClick={()=>setShowDelete(false)} className="rounded-xl border border-white/15 px-4 py-2.5 text-sm text-slate-300">Cancel</button><button type="button" disabled={deleteBusy||deleteText!=="DELETE"} onClick={()=>void requestDeletion()} className="rounded-xl bg-red-600 px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-40">{deleteBusy?"Sending email…":"Send confirmation email"}</button></div>
      </section>
    </div>}
  </div>;
}
