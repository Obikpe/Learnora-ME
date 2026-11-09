"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ArrowRight, BookOpen, Layers3, Route, Search, SlidersHorizontal } from "lucide-react";
import Shell from "../../../../components/dashboard/Shell";
import EmptyState from "../../../../components/feedback/EmptyState";
import Skeleton from "../../../../components/feedback/Skeleton";
import { currentUser } from "../../../../lib/api";
import { request } from "../../../../lib/api/client";

type Track = {
  id: string;
  name: string;
  description?: string | null;
  course_count?: number;
  required_course_count?: number;
  courses?: Array<{ course?: { level?: string | null } }>;
};

export default function ExploreLearningTracksPage() {
  const [tracks, setTracks] = useState<Track[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState("all");

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const me = await currentUser();
        const memberships = me.organisation_memberships || [];
        const restricted = Boolean(
          me.account_type === "cohort" ||
          (me.account_type === "learner" && me.role !== "normal") ||
          me.cohort_id || me.organisation_id ||
          me.organisation_role === "member" || me.organisation_role === "learner" ||
          memberships.some((membership: any) =>
            ["learner", "member"].includes(membership.role) && membership.status === "active"
          )
        );
        if (restricted) {
          window.location.replace(me.account_type === "cohort" ? "/dashboard/cohort" : "/dashboard");
          return;
        }
        const result = await request<{ tracks?: Track[] }>("/public/tracks");
        if (active) setTracks(Array.isArray(result.tracks) ? result.tracks : []);
      } catch (cause: any) {
        if (active) setError(cause?.message || "Learning tracks could not be loaded.");
      } finally {
        if (active) setLoading(false);
      }
    }
    void load();
    return () => { active = false; };
  }, []);

  const levels = useMemo(() => Array.from(new Set(
    tracks.flatMap(track => (track.courses || [])
      .map(item => String(item.course?.level || "").trim()).filter(Boolean))
  )).sort(), [tracks]);

  const filtered = useMemo(() => tracks.filter(track => {
    const courses = track.courses || [];
    const searchable = [track.name, track.description, ...courses.map(item => item.course?.level)]
      .filter(Boolean).join(" ").toLowerCase();
    return searchable.includes(query.trim().toLowerCase()) &&
      (level === "all" || courses.some(item => String(item.course?.level || "") === level));
  }), [tracks, query, level]);

  return <Shell active="tracks">
    <header className="border-b border-[var(--border)] pb-7">
      <Link href="/dashboard/tracks" className="text-xs font-medium text-[var(--text-muted)] hover:text-[var(--primary)]">← My learning tracks</Link>
      <div className="mt-5 flex flex-wrap items-end justify-between gap-5">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[.16em] text-[var(--primary)]">Explore learning tracks</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-[var(--text-heading)] sm:text-4xl">Find your next learning path</h1>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-[var(--text-muted)]">Explore structured learning journeys, review the courses in each track and choose where you want to build your skills.</p>
        </div>
        <span className="text-xs tabular-nums text-[var(--text-muted)]">{loading ? "Loading tracks…" : `${filtered.length} tracks`}</span>
      </div>
    </header>

    <section className="mt-7 flex flex-col gap-3 sm:flex-row" aria-label="Search and filter learning tracks">
      <label className="flex min-h-12 flex-1 items-center gap-3 rounded-xl border border-[var(--border)] bg-[var(--card)] px-4 focus-within:border-[var(--primary)]">
        <Search size={16} className="text-[var(--text-muted)]" />
        <input aria-label="Search learning tracks" value={query} onChange={event => setQuery(event.target.value)} placeholder="Search tracks or skills" className="w-full bg-transparent text-sm text-[var(--text-body)] outline-none placeholder:text-[var(--text-muted)]" />
      </label>
      <label className="flex min-h-12 items-center gap-3 rounded-xl border border-[var(--border)] bg-[var(--card)] px-4">
        <SlidersHorizontal size={15} className="text-[var(--text-muted)]" />
        <span className="text-xs text-[var(--text-muted)]">Level</span>
        <select aria-label="Filter by course level" value={level} onChange={event => setLevel(event.target.value)} className="max-w-36 bg-transparent text-sm text-[var(--text-body)] outline-none">
          <option value="all">All levels</option>
          {levels.map(value => <option key={value} value={value}>{value}</option>)}
        </select>
      </label>
    </section>

    {error && <div role="alert" className="mt-6 rounded-xl border border-red-500/30 bg-red-500/5 p-4 text-sm text-red-500">{error}</div>}
    {loading ? <div className="mt-8"><Skeleton label="Loading published learning tracks" /></div>
      : filtered.length ? <section className="mt-7 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {filtered.map(track => <article key={track.id} className="flex min-h-[270px] flex-col rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5 transition-colors hover:border-[var(--primary)]/50">
          <div className="flex items-center justify-between gap-3">
            <span className="text-[10px] font-bold uppercase tracking-[.15em] text-[var(--primary)]">Learning track</span>
            <Route size={18} className="text-[var(--text-muted)]" />
          </div>
          <h2 className="mt-5 text-xl font-semibold text-[var(--text-heading)]">{track.name}</h2>
          <p className="mt-2 line-clamp-3 text-sm leading-6 text-[var(--text-muted)]">{track.description || "A structured sequence of courses to help you develop connected skills."}</p>
          <div className="mt-5 flex flex-wrap items-center gap-4 text-xs text-[var(--text-muted)]">
            <span className="inline-flex items-center gap-1.5"><BookOpen size={14}/>{track.course_count ?? track.courses?.length ?? 0} courses</span>
            <span className="inline-flex items-center gap-1.5"><Layers3 size={14}/>{track.required_course_count ?? 0} required</span>
          </div>
          <Link href={`/dashboard/tracks/explore/${encodeURIComponent(track.id)}`} className="mt-auto inline-flex min-h-10 items-center gap-2 pt-6 text-sm font-semibold text-[var(--primary)] hover:underline">View track <ArrowRight size={15}/></Link>
        </article>)}
      </section> : <div className="mt-8"><EmptyState title={tracks.length ? "No tracks match your search" : "No published learning tracks yet"} message={tracks.length ? "Try a broader search or choose a different course level." : "Published learning tracks will appear here when they become available."} /></div>}
  </Shell>;
}
