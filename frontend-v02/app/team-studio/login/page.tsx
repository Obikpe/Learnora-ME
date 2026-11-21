"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

async function internalRequest(path: string, init: RequestInit = {}) {
  const response = await fetch("/api/internal" + path, {
    ...init,
    credentials: "same-origin",
    cache: "no-store",
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = typeof body.detail === "string" ? body.detail : "Internal staff sign-in failed.";
    throw new Error(error);
  }
  return body;
}

export default function TeamStudioLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await internalRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email: email.trim(), password }),
      });
      await internalRequest("/course-studio/access");
      router.replace("/team-studio");
    } catch (err: any) {
      setError(err?.message || "Unable to verify internal course-studio access.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#090d12] px-5 py-12 text-slate-100">
      <div className="mx-auto flex min-h-[75vh] max-w-md flex-col justify-center">
        <a href="/" className="text-xl font-semibold tracking-tight">Learnora <span className="text-[#d7ad35]">ME</span></a>
        <p className="mt-10 text-xs font-bold uppercase tracking-[.2em] text-[#d7ad35]">Internal staff workspace</p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight">Course Studio</h1>
        <p className="mt-3 text-sm leading-6 text-slate-400">Sign in with your Learnora internal staff account.</p>
        <form onSubmit={submit} className="mt-8 grid gap-5 rounded-2xl border border-white/10 bg-white/[.03] p-6">
          <label className="grid gap-2 text-sm text-slate-300">Work email
            <input type="email" autoComplete="username" required value={email} onChange={e => setEmail(e.target.value)} className="min-h-12 rounded-xl border border-white/10 bg-black/20 px-4 text-white outline-none focus:border-[#d7ad35]/60" />
          </label>
          <label className="grid gap-2 text-sm text-slate-300">Password
            <input type="password" autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)} className="min-h-12 rounded-xl border border-white/10 bg-black/20 px-4 text-white outline-none focus:border-[#d7ad35]/60" />
          </label>
          {error && <p role="alert" className="rounded-lg border border-red-400/20 bg-red-400/5 p-3 text-sm text-red-200">{error}</p>}
          <button disabled={busy} className="min-h-12 rounded-xl bg-[#d7ad35] px-5 font-semibold text-black disabled:cursor-not-allowed disabled:opacity-60">{busy ? "Verifying access…" : "Sign in to Course Studio"}</button>
        </form>
      </div>
    </main>
  );
}
