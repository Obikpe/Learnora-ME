"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Bell, BellRing, Check, CheckCheck, Clock3, ExternalLink, RefreshCw, Sparkles, X } from "lucide-react";
import Shell from "../../../components/dashboard/Shell";
import EmptyState from "../../../components/feedback/EmptyState";
import { request } from "../../../lib/api/client";
import { currentUser } from "../../../lib/api";

type Notice = {
  id: string;
  notification_type: string;
  title: string;
  body: string;
  action_url?: string | null;
  data?: Record<string, unknown>;
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

export default function NotificationsPage() {
  const router = useRouter();
  const [items, setItems] = useState<Notice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<"all" | "unread">("all");
  const [selectedId, setSelectedId] = useState("");
  const [busyId, setBusyId] = useState("");
  const [markingAll, setMarkingAll] = useState(false);
  const [desktopStatus, setDesktopStatus] = useState("checking");

  useEffect(() => {
    if (typeof window === "undefined" || !("Notification" in window)) {
      setDesktopStatus("unsupported");
      return;
    }
    const permission = Notification.permission;
    setDesktopStatus(permission);
    if (permission === "granted" && localStorage.getItem("learnora_desktop_notifications") === "enabled") setDesktopStatus("enabled");
  }, []);

  async function enableDesktopAlerts() {
    if (typeof window === "undefined" || !("Notification" in window)) {
      setDesktopStatus("unsupported");
      return;
    }
    try {
      const permission = Notification.permission === "default" ? await Notification.requestPermission() : Notification.permission;
      if (permission === "granted") {
        localStorage.setItem("learnora_desktop_notifications", "enabled");
        localStorage.setItem("learnora_last_notification_ids", JSON.stringify(items.map(item => item.id)));
        setDesktopStatus("enabled");
      } else {
        localStorage.removeItem("learnora_desktop_notifications");
        setDesktopStatus(permission);
      }
    } catch {
      setDesktopStatus("unsupported");
    }
  }

  const load = useCallback(async (quiet = false) => {
    if (!quiet) setLoading(true);
    setError("");
    try {
      await currentUser();
      const result = await request<{notifications?: Notice[]}>("/notifications/me?limit=100");
      setItems(Array.isArray(result.notifications) ? result.notifications : []);
    } catch (e: any) {
      if (/401|unauthori[sz]ed|not authenticated|session has expired/i.test(e?.message || "")) {
        if (typeof window !== "undefined") window.location.replace("/");
        return;
      }
      setError("Notifications are temporarily unavailable. Please try again.");
    } finally {
      if (!quiet) setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined") setSelectedId(new URLSearchParams(window.location.search).get("selected") || "");
    void load();
    const timer = window.setInterval(() => {
      if (document.visibilityState === "visible") void load(true);
    }, 15000);
    const onFocus = () => { if (document.visibilityState === "visible") void load(true); };
    window.addEventListener("focus", onFocus);
    document.addEventListener("visibilitychange", onFocus);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("focus", onFocus);
      document.removeEventListener("visibilitychange", onFocus);
    };
  }, [load]);

  const unreadCount = useMemo(() => items.filter(item => !item.read_at).length, [items]);
  const visible = useMemo(() => filter === "unread" ? items.filter(item => !item.read_at) : items, [filter, items]);
  const selectedNotice = visible.find(item => item.id === selectedId) || visible[0] || null;

  async function markRead(item: Notice) {
    if (item.read_at || busyId) return;
    setBusyId(item.id);
    try {
      await request(`/notifications/${encodeURIComponent(item.id)}/read`, { method: "PATCH" });
      setItems(old => old.map(n => n.id === item.id ? { ...n, read_at: new Date().toISOString() } : n));
    } catch (e: any) {
      setError("This notification could not be marked as read. Please try again.");
    } finally {
      setBusyId("");
    }
  }

  async function selectNotice(item: Notice) {
    setSelectedId(item.id);
    router.replace("/dashboard/notifications?selected=" + encodeURIComponent(item.id));
    await markRead(item);
  }

  function closeNotifications() {
    router.back();
  }

  function openRelatedPage(item: Notice) {
    const target = item.action_url;
    if (target && target.startsWith("/") && !target.startsWith("//")) router.push(target);
  }

  async function markAllRead() {
    if (!unreadCount || markingAll) return;
    setMarkingAll(true);
    setError("");
    try {
      await request("/notifications/read-all", { method: "POST" });
      const now = new Date().toISOString();
      setItems(old => old.map(item => item.read_at ? item : { ...item, read_at: now }));
    } catch (e: any) {
      setError("Notifications could not be marked as read. Please try again.");
    } finally {
      setMarkingAll(false);
    }
  }

  return <Shell active="notifications">
    <div className="flex flex-col gap-5 border-b border-white/[.09] pb-7 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p className="section-kicker">Your learning signal</p>
        <h1 className="mt-3 font-display text-4xl tracking-tight sm:text-5xl">Notifications<span className="text-[#d7ad35]">.</span></h1>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">New courses matched to your track, changes to courses you follow, and updates tied to your learning journey. Learnora checks for new activity while your workspace is open.</p>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <div className="border border-white/[.1] bg-white/[.025] px-4 py-3">
          <p className="text-[10px] font-semibold uppercase tracking-[.16em] text-slate-500">Unread</p>
          <p className="mt-1 text-2xl font-semibold tabular-nums">{unreadCount}</p>
        </div>
        <button type="button" onClick={enableDesktopAlerts} disabled={desktopStatus === "unsupported" || desktopStatus === "enabled"} title={desktopStatus === "denied" ? "Allow notifications in your browser settings to enable alerts" : undefined} className="inline-flex min-h-11 items-center gap-2 border border-white/[.1] px-3 text-xs font-semibold text-slate-300 transition hover:border-[#d7ad35]/35 hover:text-[#f2d477] disabled:cursor-not-allowed disabled:opacity-50">
          <BellRing size={15}/>{desktopStatus === "enabled" ? "Desktop alerts on" : desktopStatus === "unsupported" ? "Alerts unavailable" : desktopStatus === "denied" ? "Alerts blocked" : "Enable desktop alerts"}
        </button>
        <button type="button" onClick={markAllRead} disabled={!unreadCount || markingAll} className="inline-flex min-h-11 items-center gap-2 border border-[#d7ad35]/35 px-4 text-xs font-semibold text-[#f2d477] transition hover:bg-[#d7ad35]/10 disabled:cursor-not-allowed disabled:opacity-40">
          <CheckCheck size={15}/>{markingAll ? "Updating…" : "Mark all read"}
        </button>
      </div>
    </div>

    {desktopStatus === "enabled" && <p className="mt-3 text-xs text-slate-600">Browser alerts are enabled on this device while Learnora is open. The in-app inbox continues to work even when browser alerts are unavailable.</p>}
    {desktopStatus === "denied" && <p className="mt-3 text-xs text-amber-200/70">Browser alerts are blocked by your browser. You can still receive in-app updates here.</p>}
    <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
      <div className="inline-flex border border-white/[.1] bg-[#0c1015] p-1" aria-label="Notification filter">
        <button type="button" onClick={() => setFilter("all")} aria-pressed={filter === "all"} className={`min-h-9 px-4 text-xs font-semibold transition ${filter === "all" ? "bg-white/[.09] text-white" : "text-slate-500 hover:text-white"}`}>All updates <span className="ml-1 tabular-nums text-slate-500">{items.length}</span></button>
        <button type="button" onClick={() => setFilter("unread")} aria-pressed={filter === "unread"} className={`min-h-9 px-4 text-xs font-semibold transition ${filter === "unread" ? "bg-white/[.09] text-white" : "text-slate-500 hover:text-white"}`}>Unread <span className="ml-1 tabular-nums text-slate-500">{unreadCount}</span></button>
      </div>
      <button type="button" onClick={() => void load()} className="inline-flex min-h-9 items-center gap-2 text-xs text-slate-500 transition hover:text-white"><RefreshCw size={14}/>Refresh inbox</button>
    </div>

    {error && <div role="alert" className="mt-5 flex flex-wrap items-center justify-between gap-3 border border-red-400/20 bg-red-400/[.05] px-4 py-3 text-sm text-red-200"><span>{error}</span><button onClick={() => void load()} className="text-xs font-semibold underline underline-offset-4">Try again</button></div>}

    {loading ? <div className="mt-6 grid gap-3 lg:grid-cols-[minmax(0,1fr)_19rem]" aria-label="Loading notifications"><div className="h-64 animate-pulse border border-white/[.07] bg-white/[.025]"/><div className="h-64 animate-pulse border border-white/[.07] bg-white/[.025]"/></div>
    : visible.length === 0 ? <div className="mt-7 border border-white/[.08] bg-[#0d1218] p-8 sm:p-12">
        <EmptyState title={filter === "unread" ? "You are all caught up" : "Your inbox is clear"} message={filter === "unread" ? "There are no unread notifications. New relevant course releases and updates will appear here automatically." : "When a course matching your saved track is published, or a course you follow changes, updates will appear here."}/>
        <Link href="/courses" className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-[#f2d477] hover:text-white">Explore published courses <ExternalLink size={14}/></Link>
      </div>
    : <div className="mt-6 grid min-h-[28rem] gap-4 lg:grid-cols-[minmax(0,1fr)_19rem]">
        <section className="min-w-0 border border-white/[.08] bg-[#0d1218] p-5 sm:p-7" aria-label="Selected notification">
          <div className="flex items-start justify-between gap-4 border-b border-white/[.08] pb-5">
            <div className="min-w-0">
              <p className="text-[10px] font-bold uppercase tracking-[.16em] text-[#d7ad35]">Notification details</p>
              <h2 className="mt-2 text-xl font-semibold leading-7 text-white sm:text-2xl">{selectedNotice?.title || "Select a notification"}</h2>
            </div>
            <button type="button" onClick={closeNotifications} aria-label="Close notifications" title="Close notifications" className="grid size-10 shrink-0 place-items-center border border-white/[.12] text-slate-400 transition hover:border-white/30 hover:text-white"><X size={18}/></button>
          </div>
          {selectedNotice ? <>
            <div className="mt-5 flex flex-wrap items-center gap-3 text-xs text-slate-500">
              <span className="inline-flex items-center gap-1.5"><Clock3 size={13}/>{relativeTime(selectedNotice.created_at)}</span>
              <span>{selectedNotice.notification_type === "course_published" ? "Course release" : selectedNotice.notification_type === "course_updated" ? "Course update" : "Learnora update"}</span>
              {!selectedNotice.read_at && <span className="text-[#f2d477]">Unread</span>}
            </div>
            <p className="mt-6 max-w-3xl whitespace-pre-wrap text-sm leading-7 text-slate-300">{selectedNotice.body}</p>
            {selectedNotice.action_url && <button type="button" onClick={() => openRelatedPage(selectedNotice)} className="mt-8 inline-flex min-h-10 items-center gap-2 border border-[#d7ad35]/35 px-4 text-xs font-semibold text-[#f2d477] transition hover:bg-[#d7ad35]/10">Open related page <ExternalLink size={14}/></button>}
          </> : <p className="mt-6 text-sm text-slate-500">Choose an update from the notification list.</p>}
        </section>
        <aside className="min-w-0 border border-white/[.08] bg-[#0b0f14]" aria-label="Notification list">
          <div className="flex items-center justify-between border-b border-white/[.08] px-4 py-3">
            <h2 className="text-xs font-semibold uppercase tracking-[.12em] text-slate-400">All notifications</h2>
            <span className="text-[10px] tabular-nums text-slate-600">{visible.length}</span>
          </div>
          <div className="max-h-[34rem] overflow-y-auto">
            {visible.map(item => <button key={item.id} type="button" onClick={() => void selectNotice(item)} aria-current={selectedNotice?.id === item.id ? "true" : undefined} className={`block w-full border-b border-white/[.06] px-4 py-4 text-left transition ${selectedNotice?.id === item.id ? "bg-[#d7ad35]/[.09]" : "hover:bg-white/[.035]"}`}>
              <span className="flex items-center gap-2">
                {item.notification_type === "course_published" ? <Sparkles size={14} className="shrink-0 text-[#d7ad35]"/> : <Bell size={14} className="shrink-0 text-slate-500"/>}
                <span className={`min-w-0 flex-1 truncate text-xs font-semibold ${item.read_at ? "text-slate-300" : "text-white"}`}>{item.title}</span>
                {!item.read_at && <span className="size-1.5 shrink-0 rounded-full bg-[#d7ad35]" aria-label="Unread"/>}
              </span>
              <span className="mt-2 block line-clamp-2 text-[11px] leading-5 text-slate-500">{item.body}</span>
              <span className="mt-2 block text-[10px] text-slate-600">{relativeTime(item.created_at)}</span>
            </button>)}
          </div>
        </aside>
      </div>}
  </Shell>;
}
