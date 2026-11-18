"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { currentUser } from "../../lib/api";
import Skeleton from "../../components/feedback/Skeleton";

function apiErrorStatus(error: unknown): number {
  return typeof error === "object" && error !== null && "status" in error
    ? Number((error as { status?: unknown }).status || 0)
    : 0;
}

function apiErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Your account needs attention before you can continue.";
}

async function verifySessionWithRetry() {
  let lastError: unknown;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      return await currentUser();
    } catch (error: unknown) {
      lastError = error;
      const status = apiErrorStatus(error);
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
    } catch (cause: unknown) {
      const status = apiErrorStatus(cause);
      setAuthorised(false);
      setRetryable(![401, 403, 409].includes(status));
      if (status === 401 || status === 403) {
        signIn();
        return;
      }
      setError(
        status === 409
          ? (apiErrorMessage(cause) || "Your account needs attention before you can continue.")
          : "We could not verify your Learnora session yet. We’ll keep checking automatically while the connection recovers.",
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
      } catch (cause: unknown) {
        if (!active) return;
        const status = apiErrorStatus(cause);
        setAuthorised(false);
        setRetryable(![401, 403, 409].includes(status));
        if (status === 401 || status === 403) {
          signIn();
          return;
        }
        setError(
          status === 409
            ? (apiErrorMessage(cause) || "Your account needs attention before you can continue.")
            : "We could not verify your Learnora session yet. We’ll keep checking automatically while the connection recovers.",
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
