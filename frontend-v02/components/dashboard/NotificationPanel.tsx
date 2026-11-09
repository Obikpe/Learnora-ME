"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Bell, BellRing, Clock3, ExternalLink, X } from "lucide-react";
import { request } from "../../lib/api/client";

type Notice = {
  id: string;
  notification_type: string;
  title: string;
  body: string;
  action_url?: string | null;
  read_at?: string | null;
  created_at: string;
};

function relativeTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Recently";
  const seconds = Math.max(0, Math.floor((Date.now() - date.getTime()) / 1000));
  if (seconds < 60) return "Just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export default function NotificationPanel({
  open,
  initialSelectedId,
  onClose,
}: {
  open: boolean;
  initialSelectedId?: string;
  onClose: () => void;
}) {
  const [items, setItems] = useState<Notice[]>([]);
  const [selectedId, setSelectedId] = useState(initialSelectedId || "");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState("");

  useEffect(() => {
    setSelectedId(initialSelectedId || "");
  }, [initialSelectedId]);

  useEffect(() => {
    if (!open) return;
    let active = true;
    setLoading(true);
    setError("");
    request<{ notifications?: Notice[] }>("/notifications/me?limit=100")
      .then(result => {
        if (!active) return;
        const notices = Array.isArray(result.notifications) ? result.notifications : [];
        setItems(notices);
        setSelectedId(current => current && notices.some(item => item.id === current) ? current : notices[0]?.id || "");
      })
      .catch(() => {
        if (active) setError("Notifications could not be loaded. Please try again.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, [open]);

  const selected = useMemo(
    () => items.find(item => item.id === selectedId) || items[0] || null,
    [items, selectedId],
  );
  const unreadCount = items.filter(item => !item.read_at).length;

  async function select(item: Notice) {
    setSelectedId(item.id);
    if (item.read_at || busyId) return;
    setBusyId(item.id);
    try {
      await request(`/notifications/${encodeURIComponent(item.id)}/read`, { method: "PATCH" });
      setItems(old => old.map(notice => notice.id === item.id
        ? { ...notice, read_at: new Date().toISOString() }
        : notice));
    } catch {
      setError("This notification could not be marked as read.");
    } finally {
      setBusyId("");
    }
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[100] flex justify-end" role="presentation">
      <button type="button" aria-label="Close notifications" onClick={onClose} className="absolute inset-0 bg-black/55 backdrop-blur-[2px]"/>
      <section role="dialog" aria-modal="true" aria-label="Notifications" className="relative flex h-full w-full max-w-6xl flex-col border-l border-[var(--border)] bg-[var(--bg)] shadow-2xl">
        <header className="flex shrink-0 items-center justify-between gap-4 border-b border-[var(--border)] px-5 py-4 sm:px-7">
          <div className="flex min-w-0 items-center gap-3">
            <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-[var(--primary-tint)] text-[var(--primary)]"><BellRing size={18}/></span>
            <div>
              <h2 className="text-base font-bold text-[var(--text-heading)]">Notifications</h2>
              <p className="mt-0.5 text-xs text-[var(--text-muted)]">{unreadCount} unread updates</p>
            </div>
          </div>
          <button type="button" onClick={onClose} aria-label="Close notifications" title="Close notifications" className="grid size-10 shrink-0 place-items-center rounded-lg border border-[var(--border)] text-[var(--text-muted)] transition hover:bg-[var(--bg-soft)] hover:text-[var(--text-heading)]"><X size={18}/></button>
        </header>

        {error && <div role="alert" className="mx-5 mt-4 border border-[var(--error)]/25 bg-[var(--error)]/[.06] px-4 py-3 text-sm text-[var(--error)] sm:mx-7">{error}</div>}

        <div className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[minmax(0,1fr)_20rem]">
          <main className="min-h-[16rem] overflow-y-auto border-b border-[var(--border)] p-5 sm:p-7 lg:border-b-0 lg:border-r">
            {loading ? <div className="space-y-4" aria-label="Loading notification"><div className="h-7 w-2/3 animate-pulse rounded bg-[var(--skeleton)]"/><div className="h-3 w-1/3 animate-pulse rounded bg-[var(--skeleton)]"/><div className="mt-8 h-28 animate-pulse rounded bg-[var(--skeleton)]"/></div>
            : selected ? <>
              <p className="text-[10px] font-bold uppercase tracking-[.16em] text-[var(--primary)]">Selected notification</p>
              <h3 className="mt-3 max-w-3xl text-2xl font-bold leading-tight tracking-tight text-[var(--text-heading)] sm:text-3xl">{selected.title}</h3>
              <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-[var(--text-muted)]">
                <span className="inline-flex items-center gap-1.5"><Clock3 size={13}/>{relativeTime(selected.created_at)}</span>
                <span>{selected.notification_type === "course_published" ? "Course release" : selected.notification_type === "course_updated" ? "Course update" : "Learnora update"}</span>
                {!selected.read_at && <span className="rounded-full bg-[var(--primary-tint)] px-2 py-1 font-semibold text-[var(--primary)]">New</span>}
              </div>
              <p className="mt-8 max-w-3xl whitespace-pre-wrap text-sm leading-7 text-[var(--text-body)]">{selected.body}</p>
              {selected.action_url && selected.action_url.startsWith("/") && !selected.action_url.startsWith("//") && <Link href={selected.action_url} onClick={onClose} className="mt-8 inline-flex min-h-10 items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2.5 text-xs font-semibold text-[var(--on-primary)] hover:bg-[var(--primary-hover)]">Open related page <ExternalLink size={14}/></Link>}
            </> : <div className="grid min-h-64 place-items-center text-center"><div><Bell size={28} className="mx-auto text-[var(--text-muted)]"/><p className="mt-4 text-sm font-semibold text-[var(--text-heading)]">No notifications yet</p><p className="mt-1 text-xs text-[var(--text-muted)]">New learning updates will appear here.</p></div></div>}
          </main>

          <aside className="min-h-0 overflow-y-auto bg-[var(--card)]" aria-label="Notification list">
            <div className="sticky top-0 z-10 flex items-center justify-between border-b border-[var(--border)] bg-[var(--card)] px-4 py-3">
              <h3 className="text-xs font-bold uppercase tracking-[.13em] text-[var(--text-muted)]">All notifications</h3>
              <span className="text-[11px] tabular-nums text-[var(--text-muted)]">{items.length}</span>
            </div>
            {items.map(item => <button key={item.id} type="button" onClick={() => void select(item)} aria-current={selected?.id === item.id ? "true" : undefined} className={`block w-full border-b border-[var(--border)] px-4 py-4 text-left transition ${selected?.id === item.id ? "bg-[var(--primary-tint)]" : "hover:bg-[var(--bg-soft)]"}`}>
              <span className="flex items-center gap-2">
                <span className={`min-w-0 flex-1 truncate text-xs font-semibold ${item.read_at ? "text-[var(--text-body)]" : "text-[var(--text-heading)]"}`}>{item.title}</span>
                {!item.read_at && <span className="size-2 shrink-0 rounded-full bg-[var(--primary)]" aria-label="Unread"/>}
              </span>
              <span className="mt-2 block line-clamp-2 text-[11px] leading-5 text-[var(--text-muted)]">{item.body}</span>
              <span className="mt-2 block text-[10px] text-[var(--text-muted)]">{relativeTime(item.created_at)}</span>
            </button>)}
          </aside>
        </div>
      </section>
    </div>
  );
}
