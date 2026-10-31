"use client";

import { useCallback, useEffect, useState } from "react";
import { Activity, BookOpen, CheckCircle2, GraduationCap, Users, RefreshCw } from "lucide-react";
import Shell from "../../components/Shell";
import { request, teamMe } from "../../lib/api";

export default function AnalyticsPage() {
  const [me, setMe] = useState<any>(null);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await request<any>("/operations/analytics/overview");
      setData(result);
    } catch (e: any) {
      setError(e.message || "Platform analytics could not be loaded.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    teamMe().then(setMe).catch(e => setError(e.message || "Your staff session could not be loaded."));
    void load();
  }, [load]);

  if (!me) return <div className="p-10 text-slate-400">Loading secure workspace…</div>;

  const metrics = data?.metrics || {};
  const cards = [
    { key: "individual_learners", label: "Individual learners", icon: Users, description: "Verified and unverified learner accounts." },
    { key: "new_individual_learners_30d", label: "New learners · 30 days", icon: GraduationCap, description: "New individual learner registrations." },
    { key: "published_learnora_courses", label: "Published courses", icon: BookOpen, description: "Published courses owned by Learnora." },
    { key: "active_course_enrolments", label: "Active enrolments", icon: Activity, description: "Enrolments currently marked active." },
    { key: "completed_course_enrolments", label: "Completed courses", icon: CheckCircle2, description: "Enrolments marked completed by the backend." },
    { key: "active_learners_30d", label: "Active learners · 30 days", icon: Users, description: "Distinct learners with recent lesson progress." },
    { key: "lesson_completions_30d", label: "Lesson completions · 30 days", icon: CheckCircle2, description: "Completed lesson-progress records in the window." },
  ];

  return <Shell roles={me.roles || []} active="analytics">
    <header className="flex flex-wrap items-end justify-between gap-4 border-b border-white/[.1] pb-6">
      <div><p className="section-kicker">Platform oversight / Analytics</p><h1 className="mt-3 font-display text-4xl tracking-tight sm:text-5xl">Platform analytics</h1><p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">Live metrics from learner accounts, course enrolments and saved lesson progress. The 30-day activity window is calculated by the backend.</p></div>
      <button type="button" onClick={() => void load()} disabled={loading} className="mini inline-flex items-center gap-2 disabled:opacity-50"><RefreshCw size={14} className={loading ? "animate-spin" : ""}/>Refresh</button>
    </header>

    {error && <div role="alert" className="notice error mt-5">{error}</div>}
    {loading && !data ? <p className="mt-8 text-sm text-slate-500">Loading live platform metrics…</p> : data && <>
      <section className="mt-7 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map(({key,label,icon:Icon,description}) => <article key={key} className="rounded-xl border border-white/[.08] bg-[#0e1319] p-5">
          <div className="flex items-start justify-between gap-3"><p className="text-xs font-semibold uppercase tracking-[.13em] text-slate-500">{label}</p><Icon size={18} className="shrink-0 text-[var(--gold2)]"/></div>
          <p className="mt-4 text-4xl font-semibold tabular-nums text-slate-100">{Number(metrics[key] || 0).toLocaleString()}</p>
          <p className="mt-2 text-xs leading-5 text-slate-600">{description}</p>
        </article>)}
      </section>
      {data.active_learner_sample_capped && <p role="status" className="mt-4 text-xs leading-6 text-amber-200/80">The recent lesson activity sample reached its 10,000-record cap. The active learner figure is a lower bound until the metric is moved to a database-side aggregate.</p>}
      <section className="mt-8 rounded-xl border border-white/[.08] bg-[#0e1319] p-5">
        <h2 className="text-sm font-semibold">Metric definitions</h2>
        <dl className="mt-4 grid gap-4 sm:grid-cols-2">
          {Object.entries(data.definitions || {}).map(([key,description]) => <div key={key}><dt className="text-xs font-semibold text-slate-300">{key.replaceAll("_"," ")}</dt><dd className="mt-1 text-xs leading-6 text-slate-500">{String(description)}</dd></div>)}
        </dl>
      </section>
    </>}
  </Shell>;
}
