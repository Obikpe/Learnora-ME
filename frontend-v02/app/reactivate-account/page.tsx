"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CheckCircle2, LoaderCircle, ShieldCheck, AlertTriangle } from "lucide-react";
import { request } from "../../lib/api/client";

export default function ReactivateAccountPage() {
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  useEffect(() => {
    const value = new URLSearchParams(window.location.hash.replace(/^#/, "")).get("token") || "";
    const address = new URLSearchParams(window.location.search).get("email") || "";
    setToken(value);
    setEmail(address);
    setLoading(false);
  }, []);

  async function reactivate() {
    if (!token || busy) return;
    setBusy(true);
    setError("");
    try {
      await request("/account-lifecycle/reactivate", {
        method: "POST",
        body: JSON.stringify({ token }),
      });
      window.history.replaceState(null, "", window.location.pathname);
      setDone(true);
    } catch (e: any) {
      setError(e.message || "We could not reactivate this account. Request a new link or contact Learnora support.");
    } finally {
      setBusy(false);
    }
  }

  return <main className="grid min-h-screen place-items-center bg-[var(--bg)] px-4 py-12">
    <section className="w-full max-w-xl rounded-3xl border border-white/10 bg-[#0e1319] p-7 sm:p-10">
      <Link href="/" className="font-display text-2xl">Learnora <span className="gold">ME</span></Link>
      {loading ? <div className="mt-10 flex items-center gap-3 text-sm text-slate-400"><LoaderCircle className="animate-spin" size={18}/>Loading activation link…</div> : done ? <>
        <CheckCircle2 className="mt-10 text-emerald-400" size={34}/>
        <h1 className="mt-4 font-display text-3xl">Your account is active again</h1>
        <p className="mt-3 text-sm leading-7 text-slate-400">Your Learnora account has been reactivated. Sign in with your existing email address and password to continue learning.</p>
        <Link href="/login" className="mt-6 inline-flex rounded-xl bg-[#d7ad35] px-5 py-3 text-sm font-bold text-black">Sign in to Learnora</Link>
      </> : <>
        <ShieldCheck className="mt-10 text-[var(--gold-light)]" size={34}/>
        <h1 className="mt-4 font-display text-3xl">Reactivate your account</h1>
        <p className="mt-3 text-sm leading-7 text-slate-400">You can reactivate your account within 30 days of confirming deletion. This secure activation link is valid for 24 hours.</p>
        {error && <p role="alert" className="mt-5 rounded-xl border border-red-400/20 bg-red-400/[.05] p-3 text-sm text-red-200">{error}</p>}
        {!token && email && <p role="status" className="mt-5 rounded-xl border border-emerald-400/20 bg-emerald-400/[.05] p-3 text-sm leading-6 text-emerald-100">We sent an activation link to <strong className="break-all">{email}</strong>. Check your inbox and open the link within 24 hours. You will reactivate your existing account and keep your learning history.</p>}
        {!token && !email && <p role="alert" className="mt-5 rounded-xl border border-amber-400/20 bg-amber-400/[.05] p-3 text-sm text-amber-100"><AlertTriangle className="mr-2 inline" size={15}/>This activation link is missing or invalid. Return to sign-up and enter your email again to request a new link.</p>}
        <div className="mt-6 flex flex-wrap gap-3">{token && <button type="button" disabled={busy} onClick={()=>void reactivate()} className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-[#d7ad35] px-5 py-3 text-sm font-semibold text-black disabled:opacity-40">{busy?<LoaderCircle className="animate-spin" size={16}/>:null}{busy?"Reactivating…":"Reactivate account"}</button>}<Link href="/login" className="inline-flex min-h-11 items-center rounded-xl border border-white/15 px-5 py-3 text-sm text-slate-300">Return to sign in</Link></div>
      </>}
      <p className="mt-8 text-xs text-slate-500">Need help? <a className="underline underline-offset-4" href="mailto:learnorame@gmail.com">Contact Learnora support</a>.</p>
    </section>
  </main>;
}
