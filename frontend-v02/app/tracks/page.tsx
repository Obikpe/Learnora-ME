"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, BookOpen, Route, Layers3 } from "lucide-react";
import PublicNav from "../../components/public/PublicNav";
import PublicFooter from "../../components/public/PublicFooter";
import EmptyState from "../../components/feedback/EmptyState";
import { request } from "../../lib/api/client";

export default function TracksPage() {
  const [tracks, setTracks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    request<any>("/public/tracks")
      .then(result => { if (active) setTracks(result.tracks || []); })
      .catch(e => { if (active) setError(e.message || "Tracks could not be loaded."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  return <>
    <PublicNav/>
    <main className="mx-auto max-w-7xl px-5 pb-24 pt-32 lg:px-8">
      <header className="grid gap-8 border-b border-white/[.1] pb-12 lg:grid-cols-[1fr_.7fr] lg:items-end">
        <div><p className="section-kicker">Structured learning journeys</p><h1 className="mt-5 max-w-4xl font-display text-5xl leading-[1.02] tracking-[-.04em] sm:text-6xl lg:text-7xl">Follow a track. Build a body of work.</h1></div>
        <p className="max-w-xl text-base leading-8 text-slate-400">Tracks bring related courses together in a deliberate order. Work through the required courses, keep your progress and see how far you have come.</p>
      </header>

      {error && <div role="alert" className="notice error mt-7">{error}</div>}
      {loading ? <p className="py-16 text-sm text-slate-500">Loading published tracks…</p> : tracks.length ? <section className="grid gap-5 py-10 md:grid-cols-2 xl:grid-cols-3">
        {tracks.map(track => <article key={track.id} className="flex min-h-[300px] flex-col border border-white/[.09] bg-[#0e1319] p-6 transition-colors hover:border-[var(--gold)]/40">
          <div className="flex items-center justify-between gap-3"><span className="text-[10px] font-bold uppercase tracking-[.18em] gold">Learnora track</span><Route size={18} className="text-slate-600"/></div>
          <h2 className="mt-5 font-display text-2xl leading-tight">{track.name}</h2>
          <p className="mt-3 line-clamp-3 text-sm leading-7 text-slate-400">{track.description || "A structured sequence of courses to help you develop and apply a connected set of skills."}</p>
          <div className="mt-6 flex flex-wrap items-center gap-4 text-xs text-slate-500"><span className="inline-flex items-center gap-2"><BookOpen size={14}/>{track.course_count} courses</span><span className="inline-flex items-center gap-2"><Layers3 size={14}/>{track.required_course_count} required</span></div>
          <div className="mt-auto pt-7"><Link href={"/tracks/"+track.id} className="inline-flex min-h-11 items-center gap-2 border border-white/[.15] px-4 text-sm font-semibold text-slate-100 transition-colors hover:border-[var(--gold)] hover:text-[var(--gold2)]">View track <ArrowRight size={15}/></Link></div>
        </article>)}
      </section> : <div className="py-16"><EmptyState title="No published tracks yet" message="New structured learning tracks will appear here when Learnora publishes them."/></div>}
    </main>
    <PublicFooter/>
  </>;
}
