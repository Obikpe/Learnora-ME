"use client";

import { useCallback, useEffect, useState } from "react";
import { Search, Users, BookOpen, CheckCircle2, Clock3, ChevronLeft, ChevronRight } from "lucide-react";
import Shell from "../../components/Shell";
import { request, teamMe } from "../../lib/api";

type Learner = {
  id: string;
  name?: string | null;
  email: string;
  role: string;
  email_verified_at?: string | null;
  created_at?: string | null;
  sub_status?: string | null;
  learning_summary?: {
    enrolled_courses: number;
    completed_courses: number;
    tracked_lessons: number;
    completed_lessons: number;
  };
};

const PAGE_SIZE = 25;

export default function LearnersPage() {
  const [me, setMe] = useState<any>(null);
  const [items, setItems] = useState<Learner[]>([]);
  const [selected, setSelected] = useState<any>(null);
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async (nextOffset: number, search: string) => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ limit: String(PAGE_SIZE), offset: String(nextOffset) });
      if (search.trim()) params.set("q", search.trim());
      const result = await request<any>("/operations/learners?" + params.toString());
      setItems(result.learners || []);
      setHasMore(Boolean(result.pagination?.has_more));
      setOffset(nextOffset);
    } catch (e: any) {
      setError(e.message || "Learner records could not be loaded.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    teamMe().then(setMe).catch(e => setError(e.message || "Your staff session could not be loaded."));
    void load(0, "");
  }, [load]);

  async function openLearner(id: string) {
    setSelected(null);
    setDetailLoading(true);
    setError("");
    try {
      const result = await request<any>("/operations/learners/" + encodeURIComponent(id));
      setSelected(result);
    } catch (e: any) {
      setError(e.message || "Learner details could not be loaded.");
    } finally {
      setDetailLoading(false);
    }
  }

  if (!me) return <div className="p-10 text-slate-400">Loading secure workspace…</div>;

  return <Shell roles={me.roles || []} active="learners">
    <header className="border-b border-white/[.1] pb-6">
      <p className="section-kicker">Platform oversight / Learners</p>
      <h1 className="mt-3 font-display text-4xl tracking-tight sm:text-5xl">Learner accounts</h1>
      <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">Review individual learner accounts, enrolments and saved learning progress. Organisation and cohort records remain managed in their own workspaces.</p>
    </header>

    {error && <div role="alert" className="notice error mt-5">{error}</div>}

    <section className="mt-6 flex flex-col gap-3 sm:flex-row">
      <form className="flex min-w-0 flex-1 gap-2" onSubmit={e => { e.preventDefault(); setSubmittedQuery(query); void load(0, query); }}>
        <label className="flex min-h-11 flex-1 items-center gap-3 border border-white/10 bg-[#10151b] px-4">
          <Search size={16} className="text-slate-500"/>
          <input aria-label="Search learner email" value={query} onChange={e => setQuery(e.target.value)} placeholder="Search by email address" className="w-full bg-transparent py-2 text-sm outline-none placeholder:text-slate-600"/>
        </label>
        <button className="action" type="submit" disabled={loading}>Search</button>
      </form>
      <div className="flex items-center gap-2 text-xs text-slate-500"><Users size={15}/>{items.length} learner records on this page</div>
    </section>

    <section className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(300px,.72fr)]">
      <div className="min-w-0 overflow-hidden rounded-xl border border-white/[.08] bg-[#0e1319]">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead className="border-b border-white/[.08] bg-white/[.025] text-[10px] uppercase tracking-[.15em] text-slate-500">
              <tr><th className="px-4 py-3">Learner</th><th className="px-4 py-3">Account</th><th className="px-4 py-3">Courses</th><th className="px-4 py-3">Lessons completed</th><th className="px-4 py-3">Joined</th></tr>
            </thead>
            <tbody className="divide-y divide-white/[.06]">
              {items.map(learner => <tr key={learner.id} className="transition hover:bg-white/[.025]">
                <td className="px-4 py-4"><button type="button" onClick={() => void openLearner(learner.id)} className="text-left"><span className="block font-medium text-slate-100">{learner.name || "Unnamed learner"}</span><span className="mt-1 block text-xs text-slate-500">{learner.email}</span></button></td>
                <td className="px-4 py-4"><span className="capitalize text-slate-300">{learner.role}</span><span className="mt-1 block text-[11px] text-slate-500">{learner.email_verified_at ? "Email verified" : "Not verified"}</span></td>
                <td className="px-4 py-4 tabular-nums text-slate-300">{learner.learning_summary?.completed_courses || 0} / {learner.learning_summary?.enrolled_courses || 0}</td>
                <td className="px-4 py-4 tabular-nums text-slate-300">{learner.learning_summary?.completed_lessons || 0} / {learner.learning_summary?.tracked_lessons || 0}</td>
                <td className="px-4 py-4 text-xs text-slate-500">{learner.created_at ? new Date(learner.created_at).toLocaleDateString() : "—"}</td>
              </tr>)}
              {!loading && !items.length && <tr><td colSpan={5} className="px-4 py-12 text-center text-sm text-slate-500">No learner account records matched this search.</td></tr>}
              {loading && <tr><td colSpan={5} className="px-4 py-12 text-center text-sm text-slate-500">Loading learner records…</td></tr>}
            </tbody>
          </table>
        </div>
        <div className="flex items-center justify-between border-t border-white/[.08] px-4 py-3">
          <span className="text-xs text-slate-600">Page {Math.floor(offset / PAGE_SIZE) + 1}</span>
          <div className="flex gap-2">
            <button type="button" disabled={offset === 0 || loading} onClick={() => void load(Math.max(0, offset - PAGE_SIZE), submittedQuery)} className="mini inline-flex items-center gap-1 disabled:opacity-30"><ChevronLeft size={14}/>Previous</button>
            <button type="button" disabled={!hasMore || loading} onClick={() => void load(offset + PAGE_SIZE, submittedQuery)} className="mini inline-flex items-center gap-1 disabled:opacity-30">Next<ChevronRight size={14}/></button>
          </div>
        </div>
      </div>

      <aside className="min-w-0 rounded-xl border border-white/[.08] bg-[#0e1319] p-5">
        {detailLoading ? <p className="text-sm text-slate-500">Loading learner details…</p> : selected ? <>
          <p className="section-kicker">Learner record</p>
          <h2 className="mt-3 break-words text-xl font-semibold">{selected.learner?.name || "Unnamed learner"}</h2>
          <p className="mt-1 break-all text-xs text-slate-500">{selected.learner?.email}</p>
          <div className="mt-5 grid grid-cols-2 gap-3">
            <Summary icon={BookOpen} label="Courses" value={selected.learning_summary?.enrolled_courses || 0}/>
            <Summary icon={CheckCircle2} label="Completed" value={selected.learning_summary?.completed_courses || 0}/>
            <Summary icon={Clock3} label="Lessons tracked" value={selected.learning_summary?.tracked_lessons || 0}/>
            <Summary icon={CheckCircle2} label="Lessons done" value={selected.learning_summary?.completed_lessons || 0}/>
          </div>
          <h3 className="mt-7 text-xs font-semibold uppercase tracking-[.15em] text-slate-500">Enrolments</h3>
          <div className="mt-3 divide-y divide-white/[.06]">
            {(selected.enrolments || []).map((enrolment: any) => <div key={enrolment.id} className="py-3"><p className="text-sm text-slate-200">{enrolment.course?.title || "Course record"}</p><p className="mt-1 text-xs capitalize text-slate-500">{enrolment.status} · {enrolment.enrolled_at ? new Date(enrolment.enrolled_at).toLocaleDateString() : "date unavailable"}</p></div>)}
            {!selected.enrolments?.length && <p className="py-4 text-sm text-slate-500">No course enrolments recorded.</p>}
          </div>
          {selected.learning_summary?.progress_rows_limited && <p className="mt-3 text-xs leading-5 text-amber-200/70">Lesson history is capped at the most recent 500 records in this view.</p>}
        </> : <div className="py-10 text-center"><Users size={24} className="mx-auto text-slate-600"/><h2 className="mt-4 text-sm font-semibold text-slate-300">Select a learner</h2><p className="mt-2 text-xs leading-6 text-slate-500">Choose a record to inspect its enrolments and saved learning progress.</p></div>}
      </aside>
    </section>
  </Shell>;
}

function Summary({icon: Icon,label,value}:{icon:any;label:string;value:number}) {
  return <div className="rounded-lg border border-white/[.07] p-3"><Icon size={15} className="text-[var(--gold2)]"/><p className="mt-2 text-2xl font-semibold tabular-nums">{value}</p><p className="mt-1 text-[10px] uppercase tracking-[.12em] text-slate-600">{label}</p></div>;
}
