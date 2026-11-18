"use client";

import { useCallback, useEffect, useState } from "react";

type Consent = {
  version: 1;
  essential: true;
  functional: boolean;
  analytics: boolean;
  marketing: boolean;
  savedAt: string;
};

const STORAGE_KEY = "learnora_cookie_consent_v1";

function readConsent(): Consent | null {
  try {
    const value = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || "null");
    if (value?.version !== 1 || value?.essential !== true || typeof value.functional !== "boolean" || typeof value.analytics !== "boolean" || typeof value.marketing !== "boolean") return null;
    return value as Consent;
  } catch {
    return null;
  }
}

export default function CookieConsent() {
  const [visible, setVisible] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [consent, setConsent] = useState<Consent | null>(null);
  const [functional, setFunctional] = useState(false);
  const [analytics, setAnalytics] = useState(false);
  const [marketing, setMarketing] = useState(false);

  useEffect(() => {
    const saved = readConsent();
    setConsent(saved);
    setVisible(!saved);
    setFunctional(saved?.functional ?? false);
    setAnalytics(saved?.analytics ?? false);
    setMarketing(saved?.marketing ?? false);

    const openSettings = () => {
      const current = readConsent();
      setFunctional(current?.functional ?? false);
      setAnalytics(current?.analytics ?? false);
      setMarketing(current?.marketing ?? false);
      setVisible(false);
      setSettingsOpen(true);
    };
    const onHashChange = () => {
      if (window.location.hash === "#preferences") openSettings();
    };
    window.addEventListener("learnora:open-cookie-settings", openSettings);
    window.addEventListener("hashchange", onHashChange);
    if (window.location.hash === "#preferences") openSettings();
    return () => {
      window.removeEventListener("learnora:open-cookie-settings", openSettings);
      window.removeEventListener("hashchange", onHashChange);
    };
  }, []);

  const save = useCallback((allowFunctional: boolean, allowAnalytics: boolean, allowMarketing: boolean) => {
    const next: Consent = {
      version: 1,
      essential: true,
      functional: allowFunctional,
      analytics: allowAnalytics,
      marketing: allowMarketing,
      savedAt: new Date().toISOString(),
    };
    try {
      if (!allowFunctional) window.localStorage.removeItem("learnora_theme");
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } catch {
      // The preference panel remains usable if browser storage is blocked.
    }
    setConsent(next);
    setVisible(false);
    setSettingsOpen(false);
    setDetailsOpen(false);
    window.dispatchEvent(new CustomEvent("learnora:cookie-consent-changed", { detail: next }));
  }, []);

  const rejectOptional = () => save(false, false, false);
  const acceptOptional = () => save(true, true, true);
  const customise = () => {
    setFunctional(consent?.functional ?? false);
    setAnalytics(consent?.analytics ?? false);
    setMarketing(consent?.marketing ?? false);
    setVisible(false);
    setSettingsOpen(true);
  };

  return (
    <>
      {visible && !settingsOpen && (
        <aside aria-label="Cookie notice" className="fixed inset-x-3 bottom-3 z-[100] mx-auto max-w-4xl rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5 text-[var(--text-body)] shadow-2xl sm:inset-x-6 sm:bottom-6 sm:p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div className="max-w-2xl">
              <h2 className="text-lg font-bold text-[var(--text-heading)]">Your privacy choices</h2>
              <p className="mt-2 text-sm leading-6">Learnora uses essential cookies and browser storage for sign-in, security and core features. Optional functional preferences, analytics and marketing technologies are off unless you choose to allow them.</p>
              <button type="button" onClick={() => setDetailsOpen(value => !value)} aria-expanded={detailsOpen} className="mt-2 min-h-9 text-sm font-semibold text-[var(--primary)] underline underline-offset-4">{detailsOpen ? "View less" : "View more about essential storage"}</button>
            </div>
            <div className="flex shrink-0 flex-wrap gap-2">
              <button type="button" onClick={rejectOptional} className="min-h-11 rounded-lg border border-[var(--border)] px-3 text-sm font-semibold text-[var(--text-heading)]">Reject optional</button>
              <button type="button" onClick={customise} className="min-h-11 rounded-lg border border-[var(--border)] px-3 text-sm font-semibold text-[var(--text-heading)]">Customise</button>
              <button type="button" onClick={acceptOptional} className="min-h-11 rounded-lg bg-[var(--primary)] px-3 text-sm font-semibold text-[var(--on-primary)]">Accept optional</button>
            </div>
          </div>
          {detailsOpen && (
            <div className="mt-4 grid gap-4 border-t border-[var(--border)] pt-4 text-sm sm:grid-cols-2">
              <div><h3 className="font-semibold text-[var(--text-heading)]">Essential cookie</h3><p className="mt-1"><code>phx_token</code> keeps your authenticated Learnora session active. It is an HttpOnly first-party cookie.</p></div>
              <div><h3 className="font-semibold text-[var(--text-heading)]">Essential browser storage</h3><p className="mt-1"><code>phx_session_hint</code>, <code>phx_logged_out</code>, <code>phx_session_epoch</code>, <code>learnora_organisation_id</code>, temporary session caches and <code>learnora_cookie_consent_v1</code> support session security, core account context and remembering your privacy choices.</p></div>
              <div><h3 className="font-semibold text-[var(--text-heading)]">Functional preferences</h3><p className="mt-1"><code>learnora_theme</code> remembers your chosen appearance only if you allow functional preferences.</p></div>
              <div><h3 className="font-semibold text-[var(--text-heading)]">Optional technologies</h3><p className="mt-1">No optional analytics or advertising tags are currently configured in this Learnora ME frontend. See the <a href="/cookies" className="text-[var(--primary)] underline">Cookies and Browser Storage Notice</a> for the full list.</p></div>
            </div>
          )}
        </aside>
      )}
      {settingsOpen && (
        <aside id="preferences" aria-label="Cookie preferences" className="fixed inset-x-3 bottom-3 z-[101] mx-auto max-w-2xl rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5 text-[var(--text-body)] shadow-2xl sm:inset-x-6 sm:bottom-6 sm:p-6">
          <div className="flex items-start justify-between gap-4">
            <div><h2 className="text-lg font-bold text-[var(--text-heading)]">Cookie preferences</h2><p className="mt-1 text-sm leading-6">Essential storage is always active. Choose whether Learnora may use optional categories if they become available.</p></div>
            <button type="button" onClick={() => { setSettingsOpen(false); setVisible(!consent); }} aria-label="Close cookie preferences" className="grid size-10 shrink-0 place-items-center rounded-lg border border-[var(--border)] text-xl">×</button>
          </div>
          <div className="mt-5 divide-y divide-[var(--border)] border-y border-[var(--border)]">
            <div className="flex items-center justify-between gap-4 py-4"><div><h3 className="font-semibold text-[var(--text-heading)]">Essential</h3><p className="text-sm text-[var(--text-muted)]">Sign-in, security and core service storage. Always active.</p></div><span className="text-sm font-semibold text-[var(--text-muted)]">Always on</span></div>
            <label className="flex cursor-pointer items-center justify-between gap-4 py-4"><span><span className="block font-semibold text-[var(--text-heading)]">Functional preferences</span><span className="block text-sm text-[var(--text-muted)]">Remembers choices such as your light or dark appearance. This is optional.</span></span><input type="checkbox" checked={functional} onChange={event => setFunctional(event.target.checked)} className="size-5 accent-[var(--primary)]"/></label>
            <label className="flex cursor-pointer items-center justify-between gap-4 py-4"><span><span className="block font-semibold text-[var(--text-heading)]">Analytics</span><span className="block text-sm text-[var(--text-muted)]">Would help us understand how the site is used. No analytics tag is currently active.</span></span><input type="checkbox" checked={analytics} onChange={event => setAnalytics(event.target.checked)} className="size-5 accent-[var(--primary)]"/></label>
            <label className="flex cursor-pointer items-center justify-between gap-4 py-4"><span><span className="block font-semibold text-[var(--text-heading)]">Marketing</span><span className="block text-sm text-[var(--text-muted)]">Would allow marketing or advertising technologies. No marketing tag is currently active.</span></span><input type="checkbox" checked={marketing} onChange={event => setMarketing(event.target.checked)} className="size-5 accent-[var(--primary)]"/></label>
          </div>
          <div className="mt-5 flex flex-wrap justify-end gap-2">
            <button type="button" onClick={rejectOptional} className="min-h-11 rounded-lg border border-[var(--border)] px-4 text-sm font-semibold">Reject optional</button>
            <button type="button" onClick={() => save(functional, analytics, marketing)} className="min-h-11 rounded-lg border border-[var(--border)] px-4 text-sm font-semibold">Save choices</button>
            <button type="button" onClick={acceptOptional} className="min-h-11 rounded-lg bg-[var(--primary)] px-4 text-sm font-semibold text-[var(--on-primary)]">Accept optional</button>
          </div>
          <p className="mt-3 text-xs text-[var(--text-muted)]">You can change these choices at any time from the Cookies and Browser Storage page.</p>
        </aside>
      )}
    </>
  );
}
