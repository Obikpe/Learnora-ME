"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, BookOpen, Route, Layers3, Search, SlidersHorizontal } from "lucide-react";
import PublicNav from "../../components/public/PublicNav";
import PublicFooter from "../../components/public/PublicFooter";
import EmptyState from "../../components/feedback/EmptyState";
import { request } from "../../lib/api/client";
import { currentUser } from "../../lib/api";

export default function TracksClient({ initialTracks, initialError }: { initialTracks: any[]; initialError?: string | null }) {
  const [tracks, setTracks] = useState<any[]>(initialTracks);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(initialError || "");
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState("all");

  async function loadTracks() {
    setLoading(true);
    setError("");
    try {
      const result = await request<any>("/public/tracks");
      setTracks(Array.isArray(result.tracks) ? result.tracks : []);
    } catch (e: any) {
      setError(e.message || "Tracks could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let active = true;
    currentUser().then(me => {
      if (!active) return;
      const memberships = me.organisation_memberships || [];
      const assignedLearner = Boolean(
        me.account_type === "cohort" || (me.account_type === "learner" && me.role !== "normal") || me.cohort_id || me.organisation_id || me.organisation_role === "member" ||
        me.organisation_role === "learner" ||
        memberships.some((membership: any) => ["learner", "member"].includes(membership.role) && membership.status === "active")
      );
      if (assignedLearner) window.location.replace(me.account_type === "cohort" ? "/dashboard/cohort" : "/dashboard");
    }).catch(() => {});
    return () => { active = false; };
  }, []);

  const levels = Array.from(new Set(tracks.flatMap((track:any) => (track.courses||[]).map((item:any) => String(item.course?.level||"").trim()).filter(Boolean)))).sort();
  const filtered = tracks.filter((track:any) => {
    const courses = track.courses || [];
    const text = [track.name,track.description,...courses.map((item:any)=>item.course?.title),...courses.map((item:any)=>item.course?.short_description)].filter(Boolean).join(" ").toLowerCase();
    return text.includes(query.trim().toLowerCase()) && (level==="all" || courses.some((item:any)=>String(item.course?.level||"")===level));
  });

  return <>
    <PublicNav/>
    <main id="main-content" className="mx-auto max-w-7xl px-5 pb-24 pt-32 lg:px-8">
      <header className="grid gap-8 border-b border-white/[.1] pb-12 lg:grid-cols-[1fr_.7fr] lg:items-end">
        <div><h1 className="mt-5 max-w-4xl font-display text-5xl leading-[1.02] tracking-[-.04em] sm:text-6xl lg:text-7xl">Follow a track. Build a body of work.</h1></div>
        <p className="max-w-xl text-base leading-8 text-slate-400">Tracks bring related courses together in a deliberate order. Work through the required courses, keep your progress and see how far you have come.</p>
      </header>

      
      <section className="mt-8 flex flex-col gap-3 md:flex-row" aria-label="Search and filter learning tracks">
        <label className="flex min-h-12 flex-1 items-center gap-3 border border-white/10 bg-[#10151b] px-4 focus-within:border-[#d7ad35]/60"><Search size={16} className="text-slate-500"/><input aria-label="Search tracks" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search tracks, skills or courses" className="w-full bg-transparent py-3 text-sm outline-none placeholder:text-slate-600"/></label>
        <label className="flex min-h-12 items-center gap-3 border border-white/10 bg-[#10151b] px-4"><SlidersHorizontal size={15} className="text-slate-500"/><span className="text-xs text-slate-500">Level</span><select aria-label="Filter tracks by course level" value={level} onChange={e=>setLevel(e.target.value)} className="bg-transparent py-3 text-sm text-slate-200 outline-none"><option value="all">All levels</option>{levels.map(x=><option key={x} value={x}>{x}</option>)}</select></label>
        <span className="flex items-center text-xs tabular-nums text-slate-500">{loading?"Loading…":filtered.length+" tracks"}</span>
      </section>
      {loading ? <div className="grid gap-5 py-10 md:grid-cols-2 xl:grid-cols-3" aria-label="Loading tracks">{Array.from({length:6}).map((_,i)=><div key={i} className="animate-pulse border border-white/[.09] bg-[#0e1319] p-6"><div className="h-4 w-1/3 bg-white/[.08]"/><div className="mt-6 h-7 w-3/4 bg-white/[.08]"/><div className="mt-4 h-16 bg-white/[.05]"/><div className="mt-7 h-10 w-1/2 bg-white/[.06]"/></div>)}</div> : error ? <div role="alert" className="border border-white/10 bg-[#10151b] p-8"><EmptyState title="Tracks unavailable" message={error}/><button type="button" disabled={loading} onClick={() => void loadTracks()} className="mt-4 min-h-11 border border-white/20 px-4 text-sm font-semibold">{loading ? "Retrying…" : "Try again"}</button></div> : filtered.length ? <section className="grid gap-5 py-10 md:grid-cols-2 xl:grid-cols-3">
        {filtered.map(track => <article key={track.id} className="flex min-h-[300px] flex-col border border-white/[.09] bg-[#0e1319] p-6 transition-colors hover:border-[var(--gold)]/40">
          <div className="flex items-center justify-between gap-3"><span className="text-[10px] font-bold uppercase tracking-[.18em] gold">Learnora track</span><Route size={18} className="text-slate-600"/></div>
          <h2 className="mt-5 font-display text-2xl leading-tight">{track.name}</h2>
          <p className="mt-3 line-clamp-3 text-sm leading-7 text-slate-400">{track.description || "A structured sequence of courses to help you develop and apply a connected set of skills."}</p>
          <div className="mt-6 flex flex-wrap items-center gap-4 text-xs text-slate-500"><span className="inline-flex items-center gap-2"><BookOpen size={14}/>{track.course_count} courses</span><span className="inline-flex items-center gap-2"><Layers3 size={14}/>{track.required_course_count} required</span><span>{Array.from(new Set((track.courses||[]).map((item:any)=>item.course?.level).filter(Boolean))).join(" · ")}</span></div>
          <div className="mt-auto pt-7"><Link href={"/tracks/"+track.id} className="inline-flex min-h-11 items-center gap-2 border border-white/[.15] px-4 text-sm font-semibold text-slate-100 transition-colors hover:border-[var(--gold)] hover:text-[var(--gold2)]">View track <ArrowRight size={15}/></Link></div>
        </article>)}
      </section> : <div className="py-16"><EmptyState title={tracks.length?"No tracks match your filters":"No published tracks yet"} message={tracks.length?"Try a broader search or a different course level.":"New structured learning tracks will appear here when Learnora publishes them."}/></div>}
    </main>
    <PublicFooter/>
  </>;
}
