"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CheckCircle2, LoaderCircle, MailX } from "lucide-react";
import { request } from "../../lib/api/client";

export default function UnsubscribePage() {
  const [token, setToken] = useState("");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setToken(new URLSearchParams(window.location.hash.replace(/^#/, "")).get("token") || "");
  }, []);

  async function unsubscribe() {
    if (!token || busy) return;
    setBusy(true);
    setError("");
    try {
      await request("/account-lifecycle/marketing-unsubscribe", {
        method: "POST",
        body: JSON.stringify({ token }),
      });
      setDone(true);
      window.history.replaceState(null, "", window.location.pathname);
    } catch (e: any) {
      setError(e.message || "We could not update your email preferences. Please contact Learnora support.");
    } finally {
      setBusy(false);
    }
  }

  return <main className="grid min-h-screen place-items-center bg-[var(--bg)] px-4 py-12">
    <section className="w-full max-w-lg rounded-3xl border border-white/10 bg-[#0e1319] p-7 sm:p-10">
      <Link href="/" className="font-display text-2xl">Learnora <span className="gold">ME</span></Link>
      {done ? <>
        <CheckCircle2 className="mt-10 text-emerald-400" size={34}/>
        <h1 className="mt-4 font-display text-3xl">You are unsubscribed</h1>
        <p className="mt-3 text-sm leading-7 text-slate-400">You will no longer receive Learnora marketing emails or promotional in-app notifications. Essential account, security and relevant learning-service messages may still be sent.</p>
      </> : <>
        <MailX className="mt-10 text-[var(--gold-light)]" size={34}/>
        <h1 className="mt-4 font-display text-3xl">Manage marketing emails</h1>
        <p className="mt-3 text-sm leading-7 text-slate-400">Confirm that you want to stop receiving Learnora marketing emails and promotional in-app notifications about new tracks, course announcements, offers and discounts.</p>
        {error && <p role="alert" className="mt-5 rounded-xl border border-red-400/20 bg-red-400/[.05] p-3 text-sm text-red-200">{error}</p>}
        {!token && <p role="alert" className="mt-5 text-sm text-amber-200">This unsubscribe link is missing its confirmation token. You can update your preferences from Account Settings after signing in.</p>}
        <button type="button" disabled={!token||busy} onClick={()=>void unsubscribe()} className="mt-6 inline-flex min-h-11 items-center gap-2 rounded-xl bg-[#d7ad35] px-5 py-3 text-sm font-semibold text-black disabled:opacity-40">{busy?<LoaderCircle className="animate-spin" size={16}/>:null}{busy?"Updating preferences…":"Unsubscribe from marketing updates"}</button>
      </>}
      <p className="mt-8 text-xs text-slate-500">Need help? <a className="underline underline-offset-4" href="mailto:learnorame@gmail.com">Contact Learnora support</a>.</p>
    </section>
  </main>;
}
