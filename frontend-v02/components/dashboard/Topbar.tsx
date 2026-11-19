"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Bell, Check, X, Headset, CircleUserRound, LogOut, Sun, Moon } from "lucide-react";
import { useTheme } from "../../components/providers/ThemeProvider";
import { clearToken } from "../../lib/api";
import { request } from "../../lib/api/client";

type NoticePreview = {
  id: string;
  title: string;
  body: string;
  action_url?: string | null;
  created_at?: string;
};
type ToastNotice = NoticePreview & { extraCount?: number };
const POLL_INTERVAL_MS = 15000;
const MAX_TRACKED_IDS = 100;

function safeInternalPath(value?: string | null) {
  return value && value.startsWith("/") && !value.startsWith("//") ? value : "/dashboard/notifications";
}

export default function Topbar({ admin = false }: { admin?: boolean }) {
  const router = useRouter();
  const { theme, toggleTheme } = useTheme();
  const [unread, setUnread] = useState(0);
  const [toast, setToast] = useState<ToastNotice | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewItems, setPreviewItems] = useState<NoticePreview[]>([]);
  const [accountOpen, setAccountOpen] = useState(false);
  const lastSeenIds = useRef<Set<string> | null>(null);
  const browserSeenIds = useRef<Set<string> | null>(null);
  const inFlight = useRef(false);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const notificationMenuRef = useRef<HTMLDivElement | null>(null);
  const accountMenuRef = useRef<HTMLDivElement | null>(null);

  const showToast = useCallback((notice: ToastNotice) => {
    setToast(notice);
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 9000);
  }, []);

  const refresh = useCallback(async () => {
    if (admin || inFlight.current || typeof window === "undefined") return;
    inFlight.current = true;
    try {
      const [countResult, feed] = await Promise.all([
        request<{ unread_count?: number }>("/notifications/unread-count"),
        request<{ notifications?: NoticePreview[] }>("/notifications/me?limit=10"),
      ]);
      setUnread(Math.max(0, Number(countResult.unread_count || 0)));
      const notices = Array.isArray(feed.notifications) ? feed.notifications : [];
      setPreviewItems(notices.slice(0, 5));
      const currentIds = new Set(notices.map(notice => notice.id));

      if (lastSeenIds.current === null) {
        lastSeenIds.current = currentIds;
        let savedBrowserIds: string[] | null = null;
        try {
          const saved = localStorage.getItem("learnora_last_notification_ids");
          if (saved) savedBrowserIds = JSON.parse(saved);
        } catch { savedBrowserIds = null; }
        browserSeenIds.current = savedBrowserIds ? new Set(savedBrowserIds) : currentIds;
        if (savedBrowserIds) {
          const savedSet = new Set(savedBrowserIds);
          const missed = notices
            .filter(notice => !savedSet.has(notice.id))
            .sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime());
          if (missed.length) {
            showToast({ ...missed[0], extraCount: Math.max(0, missed.length - 1) });
            if (localStorage.getItem("learnora_desktop_notifications") === "enabled" &&
              "Notification" in window && Notification.permission === "granted") {
              missed.slice(0, 3).reverse().forEach(notice => {
                try {
                  const alert = new Notification(notice.title, { body: notice.body, tag: notice.id });
                  alert.onclick = () => {
                    window.focus();
                    router.push(safeInternalPath(notice.action_url));
                    alert.close();
                  };
                } catch { /* In-app notifications remain available. */ }
              });
            }
          }
        }
      } else {
        const fresh = notices
          .filter(notice => !lastSeenIds.current!.has(notice.id))
          .sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime());
        if (fresh.length) {
          showToast({ ...fresh[0], extraCount: Math.max(0, fresh.length - 1) });
          const browserEnabled = localStorage.getItem("learnora_desktop_notifications") === "enabled" &&
            "Notification" in window && Notification.permission === "granted";
          if (browserEnabled) {
            const alreadyBrowserSeen = browserSeenIds.current || new Set<string>();
            fresh.slice(0, 3).reverse().forEach(notice => {
              if (alreadyBrowserSeen.has(notice.id)) return;
              try {
                const alert = new Notification(notice.title, { body: notice.body, tag: notice.id });
                alert.onclick = () => {
                  window.focus();
                  router.push(safeInternalPath(notice.action_url));
                  alert.close();
                };
              } catch { /* In-app notifications remain available. */ }
            });
          }
        }
        lastSeenIds.current = currentIds;
      }

      const priorBrowserIds = browserSeenIds.current || new Set<string>();
      currentIds.forEach(id => priorBrowserIds.add(id));
      browserSeenIds.current = new Set(Array.from(priorBrowserIds).slice(-MAX_TRACKED_IDS));
      try {
        localStorage.setItem("learnora_last_notification_ids", JSON.stringify(Array.from(browserSeenIds.current)));
      } catch { /* In-memory deduplication still works. */ }
    } catch {
      // Notification service outages must not interrupt dashboard navigation.
    } finally {
      inFlight.current = false;
    }
  }, [admin, router, showToast]);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => {
      if (document.visibilityState === "visible") void refresh();
    }, POLL_INTERVAL_MS);
    const onFocus = () => {
      if (document.visibilityState === "visible") void refresh();
    };
    window.addEventListener("focus", onFocus);
    document.addEventListener("visibilitychange", onFocus);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("focus", onFocus);
      document.removeEventListener("visibilitychange", onFocus);
      if (toastTimer.current) clearTimeout(toastTimer.current);
    };
  }, [refresh]);


  // Compact menus on phones and tablets behave like mutually exclusive popovers.
  // Desktop interaction is intentionally unchanged.
  useEffect(() => {
    const media = window.matchMedia("(max-width: 1023px)");
    const closeOnOutsideInteraction = (event: PointerEvent) => {
      if (!media.matches) return;
      const target = event.target as Node | null;
      if (
        target &&
        !notificationMenuRef.current?.contains(target) &&
        !accountMenuRef.current?.contains(target)
      ) {
        setPreviewOpen(false);
        setAccountOpen(false);
      }
    };
    const closeOnEscape = (event: KeyboardEvent) => {
      if (media.matches && event.key === "Escape") {
        setPreviewOpen(false);
        setAccountOpen(false);
      }
    };
    document.addEventListener("pointerdown", closeOnOutsideInteraction);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("pointerdown", closeOnOutsideInteraction);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, []);

  const actionClass = "grid size-10 place-items-center rounded-full border border-[var(--border)] bg-[var(--card)] text-[var(--text-body)] transition-colors hover:border-[var(--primary)] hover:bg-[var(--primary-tint)] hover:text-[var(--primary)]";

  return <>
    <div className="flex shrink-0 items-center gap-2">
      <button type="button" onClick={toggleTheme} aria-pressed={theme === "dark"} aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"} title={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"} className="theme-toggle theme-toggle-compact"><span className="theme-toggle-track"><span className="theme-toggle-thumb"><span key={theme} className="theme-toggle-icon">{theme === "dark" ? <Moon size={13}/> : <Sun size={13}/>}</span></span></span></button>
      {!admin && <a href="mailto:learnorame@gmail.com?subject=Learnora%20ME%20Support" onClick={() => { if (window.matchMedia("(max-width: 1023px)").matches) { setPreviewOpen(false); setAccountOpen(false); } }} aria-label="Customer support" title="Customer support" className={`${actionClass} dashboard-support-action`}><Headset size={17}/></a>}
      {!admin && <div className="relative" ref={notificationMenuRef}>
        <button type="button" onClick={() => { if (window.matchMedia("(max-width: 1023px)").matches) setAccountOpen(false); setPreviewOpen(value => !value); }} aria-expanded={previewOpen} aria-label={unread ? `Notifications preview, ${unread} unread` : "Notifications preview"} className={`relative ${actionClass}`}>
          <Bell size={17}/>
          {unread > 0 && <span aria-label={`${unread} unread notifications`} className="absolute -right-1 -top-1 grid min-h-5 min-w-5 place-items-center rounded-full border-2 border-[var(--bg)] bg-[var(--accent)] px-1 text-[10px] font-bold text-[var(--on-accent)]">{unread > 99 ? "99+" : unread}</span>}
        </button>
        {previewOpen && <aside role="dialog" aria-label="Notification preview" className="absolute right-0 top-full z-[80] mt-2 flex max-h-[min(28rem,calc(100vh-6rem))] w-[min(22rem,calc(100vw-1.5rem))] max-w-[calc(100vw-1.5rem)] flex-col overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-2xl">
          <div className="flex shrink-0 items-center justify-between gap-2 border-b border-[var(--border)] px-4 py-3">
            <div className="min-w-0">
              <span className="block text-xs font-semibold text-[var(--text-heading)]">Notifications</span>
              <span className="mt-0.5 block text-[10px] text-[var(--text-muted)]">{unread} unread</span>
            </div>
            <button type="button" onClick={() => setPreviewOpen(false)} aria-label="Close notification preview" className="grid size-8 shrink-0 place-items-center rounded-lg text-[var(--text-muted)] hover:bg-[var(--bg-soft)]"><X size={16}/></button>
          </div>
          {previewItems.length ? <div className="min-h-0 overflow-y-auto">
            {previewItems.map(item => <button key={item.id} type="button" onClick={() => { setPreviewOpen(false); router.push("/dashboard/notifications?selected=" + encodeURIComponent(item.id)); }} className="block w-full border-b border-[var(--border)] px-4 py-3 text-left transition hover:bg-[var(--bg-soft)] last:border-b-0">
              <span className="block truncate text-xs font-semibold leading-5 text-[var(--text-heading)]">{item.title}</span>
              <span className="mt-1 block line-clamp-2 break-words text-[11px] leading-4 text-[var(--text-muted)]">{item.body}</span>
            </button>)}
          </div> : <p className="px-4 py-6 text-xs text-[var(--text-muted)]">No notifications yet.</p>}
          <button type="button" onClick={() => { setPreviewOpen(false); router.push("/dashboard/notifications"); }} className="shrink-0 border-t border-[var(--border)] px-4 py-3 text-left text-[11px] font-semibold text-[var(--primary)] hover:bg-[var(--bg-soft)]">View all notifications</button>
        </aside>}
      </div>}
      <div className="relative" ref={accountMenuRef}>
        <button type="button" onClick={() => { if (window.matchMedia("(max-width: 1023px)").matches) setPreviewOpen(false); setAccountOpen(value => !value); }} aria-expanded={accountOpen} aria-label="Account and profile menu" title="Account and profile" className={actionClass}><CircleUserRound size={18}/></button>
        {accountOpen && <div className="absolute right-0 top-full z-[75] mt-2 w-52 rounded-xl border border-[var(--border)] bg-[var(--card)] p-2 shadow-xl">
          <Link href={admin ? "/dashboard/admin" : "/dashboard/settings"} onClick={() => setAccountOpen(false)} className="block rounded-lg px-3 py-2.5 text-sm text-[var(--text-body)] hover:bg-[var(--bg-soft)]">{admin ? "Admin overview" : "Account settings"}</Link>
          <button type="button" onClick={async () => { setAccountOpen(false); const confirmed = await clearToken(); window.location.replace(confirmed ? "/" : "/login?reason=logout-unconfirmed"); }} className="flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm text-[var(--text-body)] hover:bg-[var(--bg-soft)]"><LogOut size={15}/>Sign out</button>
        </div>}
      </div>
    </div>

    {toast && !admin && <div role="status" aria-live="polite" className="fixed right-4 top-20 z-[70] w-[min(26rem,calc(100vw-2rem))] overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--card)] shadow-2xl">
      <div className="flex items-start gap-3 p-4">
        <span className="mt-0.5 grid size-9 shrink-0 place-items-center rounded-xl bg-[var(--primary-tint)] text-[var(--primary)]"><Bell size={17}/></span>
        <button type="button" onClick={() => { router.push(safeInternalPath(toast.action_url)); setToast(null); }} className="min-w-0 flex-1 text-left">
          <span className="block text-[10px] font-bold uppercase tracking-[.12em] text-[var(--primary)]">New learning update</span>
          <span className="mt-1 block text-sm font-semibold text-[var(--text-heading)]">{toast.title}</span>
          <span className="mt-1 block text-xs leading-5 text-[var(--text-muted)]">{toast.body}</span>
          {!!toast.extraCount && <span className="mt-2 block text-[11px] font-medium text-[var(--primary)]">+{toast.extraCount} more update{toast.extraCount === 1 ? "" : "s"}</span>}
          <span className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-[var(--primary)]">View update <Check size={13}/></span>
        </button>
        <button type="button" aria-label="Dismiss notification" onClick={() => setToast(null)} className="grid size-7 shrink-0 place-items-center rounded-lg text-[var(--text-muted)] hover:bg-[var(--bg-soft)]"><X size={15}/></button>
      </div>
      <div className="h-0.5 bg-[var(--primary-tint)]"><div className="h-full w-full origin-left animate-[toast-progress_9s_linear_forwards] bg-[var(--primary)]"/></div>
    </div>}
  </>;
}
