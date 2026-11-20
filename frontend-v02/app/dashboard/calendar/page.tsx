"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import Shell from "../../../components/dashboard/Shell";
import Skeleton from "../../../components/feedback/Skeleton";
import LearningCalendar from "../../../components/dashboard/LearningCalendar";
import { request } from "../../../lib/api/client";

export default function LearningCalendarPage() {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "Africa/Lagos";
    request<any>("/progress/learning-summary?timezone=" + encodeURIComponent(timezone))
      .then(setSummary).catch(() => setSummary(null)).finally(() => setLoading(false));
  }, []);
  return <Shell active="calendar">
    <div className="mb-6 flex items-center justify-between gap-3">
      <div><h1 className="mt-1 text-2xl font-bold text-[var(--text-heading)]">Learning calendar</h1><p className="mt-1 text-sm text-[var(--text-muted)]">Days when you completed meaningful learning activities.</p></div>
      <Link href="/dashboard" className="inline-flex items-center gap-2 text-sm font-semibold text-[var(--primary)]"><ArrowLeft size={15}/> Dashboard</Link>
    </div>
    {loading ? <Skeleton label="Loading your learning calendar"/> : summary
      ? <div className="max-w-2xl rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5"><LearningCalendar activityDates={(summary.learning_days || []).map((day:any) => day.activity_date)}/><p className="mt-4 text-xs text-[var(--text-muted)]">A day is marked when you complete a lesson, pass a quiz or submit an assignment. Signing in alone does not mark a learning day.</p></div>
      : <p className="rounded-xl border border-[var(--border)] p-5 text-sm text-[var(--text-muted)]">Your learning calendar is temporarily unavailable.</p>}
  </Shell>;
}
