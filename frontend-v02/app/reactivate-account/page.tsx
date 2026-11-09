"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CheckCircle2, LoaderCircle, ShieldCheck, Mail, Eye, EyeOff } from "lucide-react";
import { request } from "../../lib/api/client";

export default function ReactivateAccountPage() {
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [sent, setSent] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    const value = new URLSearchParams(window.location.hash.replace(/^#/, "")).get("token") || "";
    const address = new URLSearchParams(window.location.search).get("email") || "";
    setToken(value);
    setEmail(address);
    setLoading(false);
  }, []);

  async function sendLink(e: React.FormEvent) {
    e.preventDefault();
    if (busy || !email.trim()) return;
    setBusy(true);
    setError("");
    try {
      await request("/account-lifecycle/request-reactivation", {
        method: "POST",
        body: JSON.stringify({ email: email.trim().toLowerCase() }),
      });
      setSent(true);
    } catch (e: any) {
      setError(e.message || "We could not send the reactivation email. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  async function reactivate(e: React.FormEvent) {
    e.preventDefault();
    if (!token || busy || !password) return;
    setBusy(true);
    setError("");
    try {
      await request("/account-lifecycle/reactivate", {
        method: "POST",
        body: JSON.stringify({ token, password }),
      });
      window.history.replaceState(null, "", window.location.pathname);
      setDone(true);
    } catch (e: any) {
      setError(e.message || "We could not reactivate this account. Check your password and try again.");
    } finally {
      setBusy(false);
    }
  }

  return <main className="grid min-h-screen place-items-center bg-[var(--bg)] px-4 py-12">
    <section className="w-full max-w-xl rounded-3xl border border-white/10 bg-[#0e1319] p-7 sm:p-10">
      <Link href="/" className="font-display text-2xl">Learnora <span className="gold">ME</span></Link>
      {loading ? <div className="mt-10 flex items-center gap-3 text-sm text-slate-400"><LoaderCircle className="animate-spin" size={18}/>Loading account status…</div> : done ? <>
        <CheckCircle2 className="mt-10 text-emerald-400" size={34}/>
        <h1 className="mt-4 font-display text-3xl">Your account is active again</h1>
        <p className="mt-3 text-sm leading-7 text-slate-400">Your original Learnora account and learning history have been restored. Sign in with your existing email address and password to continue.</p>
        <Link href="/login" className="mt-6 inline-flex rounded-xl bg-[#d7ad35] px-5 py-3 text-sm font-bold text-black">Sign in to Learnora</Link>
      </> : token ? <>
        <ShieldCheck className="mt-10 text-[var(--gold-light)]" size={34}/>
        <h1 className="mt-4 font-display text-3xl">Confirm it’s your account</h1>
        <p className="mt-3 text-sm leading-7 text-slate-400">Your secure reactivation link is valid for up to 24 hours, subject to the 30-day recovery period. Enter the password you used for this Learnora account to restore it.</p>
        <form onSubmit={reactivate} className="mt-6 grid gap-4">
          <label htmlFor="reactivation-password" className="grid gap-2 text-xs font-medium text-slate-300">Existing account password
            <span className="relative block"><input id="reactivation-password" type={showPassword ? "text" : "password"} autoComplete="current-password" required value={password} onChange={e=>setPassword(e.target.value)} className="field pr-12" placeholder="Enter your existing password"/><button type="button" aria-label={showPassword ? "Hide password" : "Show password"} onClick={()=>setShowPassword(v=>!v)} className="absolute inset-y-0 right-0 grid w-12 place-items-center text-slate-500">{showPassword?<EyeOff size={17}/>:<Eye size={17}/>}</button></span>
          </label>
          {error && <p role="alert" className="rounded-xl border border-red-400/20 bg-red-400/[.05] p-3 text-sm text-red-200">{error}</p>}
          <button type="submit" disabled={busy || !password} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-[#d7ad35] px-5 py-3 text-sm font-semibold text-black disabled:opacity-40">{busy?<LoaderCircle className="animate-spin" size={16}/>:null}{busy?"Confirming…":"Confirm and reactivate account"}</button>
        </form>
      </> : <>
        <Mail className="mt-10 text-[var(--gold-light)]" size={34}/>
        <h1 className="mt-4 font-display text-3xl">Your account can be reactivated</h1>
        <p className="mt-3 text-sm leading-7 text-slate-400">This email belongs to a Learnora account that was deactivated. You can restore the same account and keep your learning history within 30 days of deactivation. Request a secure reactivation link below. We will only send the email after you request it.</p>
        {sent ? <p role="status" className="mt-5 rounded-xl border border-emerald-400/20 bg-emerald-400/[.05] p-4 text-sm leading-6 text-emerald-100">If the account can still be recovered, a reactivation link has been sent. Check your inbox and open it to continue. You will then need to enter the password for your original account.</p> : <form onSubmit={sendLink} className="mt-6 grid gap-4">
          <label htmlFor="reactivation-email" className="grid gap-2 text-xs font-medium text-slate-300">Email address<input id="reactivation-email" type="email" autoComplete="email" required value={email} onChange={e=>setEmail(e.target.value)} className="field" placeholder="you@example.com"/></label>
          {error && <p role="alert" className="rounded-xl border border-red-400/20 bg-red-400/[.05] p-3 text-sm text-red-200">{error}</p>}
          <button type="submit" disabled={busy || !email.trim()} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-[#d7ad35] px-5 py-3 text-sm font-semibold text-black disabled:opacity-40">{busy?<LoaderCircle className="animate-spin" size={16}/>:null}{busy?"Sending…":"Send reactivation link"}</button>
        </form>}
        <div className="mt-6 flex flex-wrap gap-3"><Link href="/login" className="inline-flex min-h-11 items-center rounded-xl border border-white/15 px-5 py-3 text-sm text-slate-300">Return to sign in</Link><Link href="/register" className="inline-flex min-h-11 items-center rounded-xl border border-white/15 px-5 py-3 text-sm text-slate-300">Back to sign up</Link></div>
      </>}
      <p className="mt-8 text-xs text-slate-500">Need help? <a className="underline underline-offset-4" href="mailto:learnorame@gmail.com">Contact Learnora support</a>.</p>
    </section>
  </main>;
}
