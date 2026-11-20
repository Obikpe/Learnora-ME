"use client";

import { useEffect, useState } from "react";
import { ArrowLeft, CheckCircle2, MailCheck, RefreshCw } from "lucide-react";
import Logo from "../../components/brand/Logo";
import Toast from "../../components/feedback/Toast";
import { request } from "../../lib/api/client";

export default function CheckEmailPage() {
  const [email, setEmail] = useState("");
  const [secondsLeft, setSecondsLeft] = useState(30);
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setEmail(new URLSearchParams(window.location.search).get("email") || "");
  }, []);

  useEffect(() => {
    if (secondsLeft <= 0) return;
    const timer = window.setTimeout(() => setSecondsLeft(value => Math.max(0, value - 1)), 1000);
    return () => window.clearTimeout(timer);
  }, [secondsLeft]);

  async function resend() {
    if (secondsLeft > 0 || sending || !email.trim()) return;
    setSending(true);
    setError("");
    setSent(false);
    try {
      await request<any>("/auth/resend-verification", {
        method: "POST",
        body: JSON.stringify({ email: email.trim().toLowerCase() }),
      });
      setSent(true);
      setSecondsLeft(30);
    } catch (e: any) {
      setError(e?.message || "We could not send the email just now. Please try again.");
    } finally {
      setSending(false);
    }
  }

  return (
    <main className="relative grid min-h-screen place-items-center overflow-hidden bg-[var(--bg)] px-5 py-12 text-white">
      <div className="pointer-events-none absolute -left-32 top-[-8rem] size-[28rem] rounded-full bg-[#d7ad35]/[.07] blur-[100px]" />
      <div className="pointer-events-none absolute -right-32 bottom-[-10rem] size-[30rem] rounded-full bg-emerald-300/[.05] blur-[110px]" />
      <section className="relative w-full max-w-lg rounded-3xl border border-white/[.1] bg-[#111820]/95 p-7 shadow-[0_25px_90px_rgba(0,0,0,.4)] sm:p-10">
        <a href="/" className="inline-flex"><Logo /></a>
        <div className="mt-12 grid size-16 place-items-center rounded-2xl border border-[var(--gold)]/25 bg-[var(--gold)]/[.08] text-[var(--gold-light)]">
          <MailCheck size={29} strokeWidth={1.6} />
        </div>
        
        <h1 className="mt-3 font-display text-4xl leading-tight tracking-[-.035em] sm:text-5xl">Check your email.</h1>
        <p className="mt-4 text-sm leading-7 text-slate-300">
          If you are creating a new account, confirm the address below using the verification email. If it does not arrive, request another when the countdown finishes. If you already have a Learnora account, sign in instead. If it is deactivated, sign in to begin account recovery.
        </p>
        <div className="mt-7 flex items-start gap-3 rounded-2xl border border-white/[.08] bg-white/[.03] p-4">
          <MailCheck className="mt-0.5 shrink-0 text-[var(--gold-light)]" size={18} />
          <div className="min-w-0">
            <p className="text-xs text-slate-500">Email address to verify</p>
            <p className="mt-1 break-all text-sm font-semibold text-white">{email || "Enter the email address you registered with below."}</p>
          </div>
        </div>
        {!email && (
          <label className="mt-5 block text-xs font-medium text-slate-300">
            Email address
            <input type="email" required value={email} onChange={e => setEmail(e.target.value)} className="field mt-2" placeholder="you@example.com" />
          </label>
        )}
        <div className="mt-7 border-t border-white/[.08] pt-6">
          <p className="text-sm font-semibold text-white">Didn&apos;t receive the email?</p>
          <p className="mt-2 text-xs leading-6 text-slate-400">Check your spam or promotions folder. You can request another verification email when the security countdown finishes.</p>
          <button
            type="button"
            onClick={resend}
            disabled={secondsLeft > 0 || sending || !email.trim()}
            className="mt-5 inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-xl bg-[var(--gold)] px-5 text-sm font-bold text-[#17140d] transition hover:bg-[var(--gold-light)] disabled:cursor-not-allowed disabled:opacity-45"
          >
            <RefreshCw size={16} className={sending ? "animate-spin" : ""} />
            {sending ? "Sending verification email…" : secondsLeft > 0 ? `Resend email in 00:${String(secondsLeft).padStart(2, "0")}` : "Resend verification email"}
          </button>
          {sent && <p role="status" className="mt-4 flex items-center gap-2 text-xs leading-6 text-emerald-200"><CheckCircle2 size={15} /> If the account is still unverified, a new verification email has been sent.</p>}
        </div>
        <a href="/login" className="mt-7 inline-flex items-center gap-2 text-xs text-slate-500 transition hover:text-white"><ArrowLeft size={14} /> Back to sign in</a>
      </section>
      {error && <Toast title="Email could not be sent" message={error} type="error" onClose={() => setError("")} />}
    </main>
  );
}
