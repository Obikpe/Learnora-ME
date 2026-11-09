"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CheckCircle2, AlertTriangle, LoaderCircle } from "lucide-react";
import { request } from "../../lib/api/client";
import { clearToken } from "../../lib/api";

export default function ConfirmAccountDeletionPage() {
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  useEffect(() => {
    const value = new URLSearchParams(window.location.hash.replace(/^#/, "")).get("token") || "";
    setToken(value);
    setLoading(false);
  }, []);

  async function confirm() {
    if (!token || busy) return;
    setBusy(true);
    setError("");
    try {
      await request("/account-lifecycle/confirm-deletion", {
        method: "POST",
        body: JSON.stringify({ token }),
      });
      clearToken();
      window.history.replaceState(null, "", window.location.pathname);
      setDone(true);
    } catch (e: any) {
      setError(e.message || "We could not complete account deletion. Please contact Learnora support.");
    } finally {
      setBusy(false);
    }
  }

  return <main className="grid min-h-screen place-items-center bg-[var(--bg)] px-4 py-12">
    <section className="w-full max-w-xl rounded-3xl border border-white/10 bg-[#0e1319] p-7 sm:p-10">
      <Link href="/" className="font-display text-2xl">Learnora <span className="gold">ME</span></Link>
      {loading ? <div className="mt-10 flex items-center gap-3 text-sm text-slate-400"><LoaderCircle className="animate-spin" size={18}/>Loading confirmation…</div> : done ? <>
        <CheckCircle2 className="mt-10 text-emerald-400" size={34}/>
        <h1 className="mt-4 font-display text-3xl">Account deactivated</h1>
        <p className="mt-3 text-sm leading-7 text-slate-400">Your account is now deactivated. You have 30 days to reactivate it using the link sent to your email. After the recovery period, your account and all account-linked learner records will be permanently erased. Only a restricted account-deletion history record will be retained.</p>
        <Link href="/login" className="mt-6 inline-flex rounded-xl bg-[#d7ad35] px-5 py-3 text-sm font-bold text-black">Return to Learnora</Link>
      </> : <>
        <AlertTriangle className="mt-10 text-red-300" size={34}/>
        <h1 className="mt-4 font-display text-3xl">Confirm account deletion</h1>
        <p className="mt-3 text-sm leading-7 text-slate-400">Confirming will deactivate your Learnora account for 30 days. You can reactivate it during that period. After 30 days, your account and all account-linked learner records will be permanently erased. Only a restricted account-deletion history record will be retained.</p>
        {error && <p role="alert" className="mt-5 rounded-xl border border-red-400/20 bg-red-400/[.05] p-3 text-sm text-red-200">{error}</p>}
        {!token && <p role="alert" className="mt-5 rounded-xl border border-amber-400/20 bg-amber-400/[.05] p-3 text-sm text-amber-100">This confirmation link is missing or invalid. Request a new link from Settings.</p>}
        <div className="mt-6 flex flex-wrap gap-3"><button type="button" disabled={!token||busy} onClick={()=>void confirm()} className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-red-600 px-5 py-3 text-sm font-semibold text-white disabled:opacity-40">{busy?<LoaderCircle className="animate-spin" size={16}/>:null}{busy?"Deactivating account…":"Confirm deactivation"}</button><Link href="/login" className="inline-flex min-h-11 items-center rounded-xl border border-white/15 px-5 py-3 text-sm text-slate-300">Cancel</Link></div>
      </>}
      <p className="mt-8 text-xs text-slate-500">Need help? <a className="underline underline-offset-4" href="mailto:learnorame@gmail.com">Contact Learnora support</a>.</p>
    </section>
  </main>;
}
