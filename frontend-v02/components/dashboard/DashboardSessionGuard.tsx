"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { currentUser } from "../../lib/api";
import Skeleton from "../../components/feedback/Skeleton";

async function verifySessionWithRetry() {
  let lastError: any;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      return await currentUser();
    } catch (error: any) {
      lastError = error;
      const status = Number(error?.status || 0);
      if ([401, 403, 409].includes(status) || attempt === 2) break;
      await new Promise(resolve => window.setTimeout(resolve, attempt === 0 ? 350 : 900));
    }
  }
  throw lastError;
}

export default function DashboardSessionGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [authorised, setAuthorised] = useState(false);
  const [checking, setChecking] = useState(true);
  const [error, setError] = useState("");
  const [retryable, setRetryable] = useState(false);

  const signIn = useCallback(() => {
    const next = pathname && pathname.startsWith("/") ? pathname : "/dashboard";
    window.location.replace("/login?next=" + encodeURIComponent(next));
  }, [pathname]);

  const validate = useCallback(async () => {
    setChecking(true);
    setError("");
    try {
      await verifySessionWithRetry();
      setAuthorised(true);
      setRetryable(false);
    } catch (cause: any) {
      const status = Number(cause?.status || 0);
      setAuthorised(false);
      setRetryable(![401, 403, 409].includes(status));
      if (status === 401 || status === 403) {
        signIn();
        return;
      }
      setError(
        status === 409
          ? (cause?.message || "Your account needs attention before you can continue.")
          : "We could not verify your Learnora session. Check your connection and try again.",
      );
    } finally {
      setChecking(false);
    }
  }, [signIn]);

  useEffect(() => {
    let active = true;
    const runValidation = async () => {
      setChecking(true);
      setError("");
      try {
        await verifySessionWithRetry();
        if (active) { setAuthorised(true); setRetryable(false); }
      } catch (cause: any) {
        if (!active) return;
        const status = Number(cause?.status || 0);
        setAuthorised(false);
        setRetryable(![401, 403, 409].includes(status));
        if (status === 401 || status === 403) {
          signIn();
          return;
        }
        setError(
          status === 409
            ? (cause?.message || "Your account needs attention before you can continue.")
            : "We could not verify your Learnora session. Check your connection and try again.",
        );
      } finally {
        if (active) setChecking(false);
      }
    };

    void runValidation();
    const onPageShow = () => {
      if (sessionStorage.getItem("phx_logged_out") === "1" || localStorage.getItem("phx_logged_out") === "1") signIn();
      else void runValidation();
    };
    const onStorage = (event: StorageEvent) => {
      if (event.key === "phx_logged_out" && event.newValue === "1") signIn();
    };
    window.addEventListener("pageshow", onPageShow);
    window.addEventListener("storage", onStorage);
    return () => {
      active = false;
      window.removeEventListener("pageshow", onPageShow);
      window.removeEventListener("storage", onStorage);
    };
  }, [pathname, signIn]);

  useEffect(() => {
    if (authorised || checking || !retryable) return;
    const timer = window.setTimeout(() => { void validate(); }, 8000);
    return () => window.clearTimeout(timer);
  }, [authorised, checking, retryable, validate]);

  if (!authorised) {
    return (
      <main className="min-h-screen bg-[var(--bg)] p-6">
        <div className="mx-auto max-w-5xl pt-12">
          {checking ? <Skeleton label="Checking your Learnora session" /> : (
            <section role="alert" className="mx-auto max-w-xl rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 sm:p-8">
              <h1 className="text-xl font-bold text-[var(--text-heading)]">Your learning workspace is unavailable</h1>
              <p className="mt-3 text-sm leading-7 text-[var(--text-muted)]">{error || "Your session could not be verified."}</p>
              <div className="mt-6 flex flex-wrap gap-3">
                <a href="/login" className="inline-flex min-h-10 items-center rounded-lg border border-[var(--border)] px-4 text-sm font-semibold text-[var(--text-heading)]">Sign in</a>
                <a href="mailto:learnorame@gmail.com" className="inline-flex min-h-10 items-center px-2 text-sm font-semibold text-[var(--primary)]">Contact support</a>
              </div>
            </section>
          )}
        </div>
      </main>
    );
  }
  return children;
}
