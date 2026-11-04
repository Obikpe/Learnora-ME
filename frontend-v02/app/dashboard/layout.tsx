"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { currentUser } from "../../lib/api";
import Skeleton from "../../components/feedback/Skeleton";

export default function Layout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [authorised, setAuthorised] = useState(false);
  const [checking, setChecking] = useState(true);
  const [error, setError] = useState("");

  const signIn = useCallback(() => {
    const next = pathname && pathname.startsWith("/") ? pathname : "/dashboard";
    window.location.replace("/login?next=" + encodeURIComponent(next));
  }, [pathname]);

  const validate = useCallback(async () => {
    setChecking(true);
    setError("");
    try {
      await currentUser();
      setAuthorised(true);
    } catch (cause: any) {
      const status = Number(cause?.status || 0);
      setAuthorised(false);
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
        await currentUser();
        if (active) setAuthorised(true);
      } catch (cause: any) {
        if (!active) return;
        const status = Number(cause?.status || 0);
        setAuthorised(false);
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

  if (!authorised) {
    return (
      <main className="min-h-screen bg-[var(--bg)] p-6">
        <div className="mx-auto max-w-5xl pt-12">
          {checking ? <Skeleton label="Checking your Learnora session" /> : (
            <section role="alert" className="mx-auto max-w-xl rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 sm:p-8">
              <h1 className="text-xl font-bold text-[var(--text-heading)]">Your learning workspace is unavailable</h1>
              <p className="mt-3 text-sm leading-7 text-[var(--text-muted)]">{error || "Your session could not be verified."}</p>
              <div className="mt-6 flex flex-wrap gap-3">
                <button type="button" onClick={() => void validate()} className="min-h-10 rounded-lg bg-[var(--primary)] px-4 text-sm font-semibold text-[var(--on-primary)]">Try again</button>
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
