"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, ShieldCheck } from "lucide-react";
import Logo from "../../components/brand/Logo";
import Skeleton from "../../components/feedback/Skeleton";
import { request } from "../../lib/api/client";

export default function VerifyEmail() {
  const [state, setState] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("Checking your verification link…");

  useEffect(() => {
    const token =
      new URLSearchParams(window.location.hash.slice(1)).get("token") ||
      new URLSearchParams(window.location.search).get("token");

    // Remove the one-time token from the address bar and browser history.
    window.history.replaceState(null, "", window.location.pathname);

    if (!token) {
      setState("error");
      setMessage("This link does not contain a verification token. Request a new verification email and use the latest link.");
      return;
    }

    request<any>("/auth/verify-email", {
      method: "POST",
      body: JSON.stringify({ token }),
    })
      .then(result => {
        setState("success");
        setMessage(result.message || "Your email has been verified. You can now sign in.");
      })
      .catch(error => {
        setState("error");
        setMessage(error.message || "This verification link could not be used.");
      });
  }, []);

  return (
    <main className="grid min-h-screen place-items-center bg-[var(--bg)] px-5 text-white">
      <section className="w-full max-w-lg border border-white/[.12] bg-[#11171e] p-6 sm:p-8">
        <a href="/"><Logo /></a>
        {state === "loading" ? (
          <div className="mt-10">
            <Skeleton variant="compact" label="Verifying your email" />
          </div>
        ) : (
          <>
            <div className={"mt-10 grid h-14 w-14 place-items-center rounded-2xl " + (
              state === "success"
                ? "bg-emerald-300/10 text-emerald-200"
                : "bg-red-300/10 text-red-200"
            )}>
              {state === "success" ? <CheckCircle2 size={25} /> : <ShieldCheck size={25} />}
            </div>
            <h1 className="mt-6 font-display text-4xl">
              {state === "success" ? "Email verified" : "Verification needs attention"}
            </h1>
            <p className="mt-4 text-sm leading-7 text-slate-400">{message}</p>
            {state === "success" ? (
              <a href="/login" className="mt-7 inline-block min-h-12 rounded-lg bg-[var(--gold)] px-5 py-3.5 text-sm font-bold text-[#17140d] hover:bg-[var(--gold-light)]">
                Continue to sign in
              </a>
            ) : (
              <div className="mt-7 flex flex-wrap gap-3">
                <a href="/resend-verification" className="min-h-12 rounded-lg bg-[var(--gold)] px-4 py-3 text-sm font-bold text-[#17140d] hover:bg-[var(--gold-light)]">
                  Resend verification
                </a>
                <a href="/login" className="rounded-xl border border-white/10 px-4 py-3 text-sm">
                  Back to sign in
                </a>
              </div>
            )}
          </>
        )}
      </section>
    </main>
  );
}
