"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ArrowRight, BookOpen, Clock3, Search, SlidersHorizontal } from "lucide-react";
import PublicNav from "../../components/public/PublicNav";
import PublicFooter from "../../components/public/PublicFooter";
import EmptyState from "../../components/feedback/EmptyState";
import { courses, currentUser } from "../../lib/api";
import Shell from "../../components/dashboard/Shell";
import { IMAGES } from "../../lib/constants";

export default function Courses() {
  const [signedIn, setSignedIn] = useState(false);
  const [authResolved, setAuthResolved] = useState(false);
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [showSkeleton, setShowSkeleton] = useState(false);
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState("all");
  const [track, setTrack] = useState("all");

  async function loadCourses() {
    setLoading(true);
    setError("");
    try {
      const result = await courses();
      setItems(result.data || result.courses || []);
    } catch (e: any) {
      setError(e.message || "Courses could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let active = true;
    const initialSearch = new URLSearchParams(window.location.search).get("search") || "";
    if (initialSearch) setQuery(initialSearch);
    currentUser().then(me => {
      if (!active) return;
      const memberships = me.organisation_memberships || [];
      const assignedLearner = Boolean(
        me.account_type === "cohort" ||
        me.role === "witstart" ||
        me.cohort_id ||
        me.organisation_role === "learner" ||
        memberships.some((membership: any) => membership.role === "learner" && membership.status === "active")
      );
      if (assignedLearner) {
        window.location.replace(me.account_type === "cohort" ? "/dashboard/cohort" : "/dashboard");
        return;
      }
      setSignedIn(true);
      void loadCourses();
    }).catch(() => {
      if (!active) return;
      setSignedIn(false);
      void loadCourses();
    }).finally(() => {
      if (active) setAuthResolved(true);
    });
    return () => { active = false; };
  }, []);
  useEffect(() => {
    if (!loading) { setShowSkeleton(false); return; }
    const timeout = window.setTimeout(() => setShowSkeleton(true), 180);
    return () => window.clearTimeout(timeout);
  }, [loading]);

  const levels = useMemo(() => {
    const values = items.map(course => String(course.level || "").trim()).filter(Boolean);
    return ["all", ...Array.from(new Set(values))];
  }, [items]);

  const tracks = useMemo(() => {
    const values = items.flatMap(course =>
      (Array.isArray(course.tracks) ? course.tracks : [])
        .map((item: any) => String(item.name || "").trim())
        .filter(Boolean)
    );
    return ["all", ...Array.from(new Set(values)).sort((a, b) => a.localeCompare(b))];
  }, [items]);

  const filtered = useMemo(() => {
    return items.filter(course => {
      const courseTracks = Array.isArray(course.tracks)
        ? course.tracks.map((item: any) => String(item.name || ""))
        : [];
      const topics = Array.isArray(course.settings?.topics) ? course.settings.topics.join(" ") : "";
      const searchable = [
        course.title,
        course.short_description,
        course.description,
        course.level,
        courseTracks.join(" "),
        topics,
      ].filter(Boolean).join(" ").toLowerCase();
      return searchable.includes(query.trim().toLowerCase())
        && (level === "all" || course.level === level)
        && (track === "all" || courseTracks.includes(track));
    });
  }, [items, query, level, track]);

  const usedImages = new Set<string>();
  [
    IMAGES.hero, IMAGES.learners, IMAGES.instructors, IMAGES.organisations,
    IMAGES.portfolio, IMAGES.studio, IMAGES.library, IMAGES.workshop,
    IMAGES.tutors, IMAGES.community, IMAGES.aboutHero, IMAGES.aboutVision,
    IMAGES.learnerPage, IMAGES.instructorPage, IMAGES.organisationPage, IMAGES.login,
  ].forEach(url => usedImages.add(url.split("?")[0]));

  if (!authResolved) return <main className="min-h-screen bg-[var(--bg)] p-8"><div className="mx-auto max-w-7xl pt-12 text-sm text-[var(--text-muted)]">Loading course catalogue…</div></main>;

  const catalogue = <main className={"mx-auto max-w-7xl px-5 pb-24 " + (signedIn ? "pt-8" : "pt-32") + " lg:px-8"}>
      <section className="grid gap-10 border-b border-white/[.1] pb-12 lg:grid-cols-[1fr_.6fr] lg:items-end">
        <div>
          <p className="section-kicker">The Learnora catalogue</p>
          <h1 className="mt-5 max-w-4xl font-display text-5xl leading-[1.02] tracking-[-.04em] sm:text-6xl lg:text-7xl">Find the skill. Put it to work.</h1>
          <p className="mt-6 max-w-2xl text-base leading-8 text-slate-400 sm:text-lg">Explore published learning, compare the curriculum and choose a useful next step. Course availability and enrolment rules are based on live platform records.</p>
        </div>
        <div className="border-l border-[#d7ad35]/50 pl-5">
          <BookOpen size={22} className="gold"/>
          <p className="mt-4 text-lg font-semibold">Find your next step</p>
          <p className="mt-2 text-sm leading-6 text-slate-500">Browse published courses by level, topic or learning track.</p>
        </div>
      </section>

      <section className="mt-8" aria-label="Course search and filters">
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <label className="flex min-h-12 flex-1 items-center gap-3 border border-white/10 bg-[#10151b] px-4 focus-within:border-[#d7ad35]/60">
            <Search size={17} className="shrink-0 text-slate-500"/>
            <input aria-label="Search courses" value={query} onChange={e => setQuery(e.target.value)} placeholder="Search skills, topics or course names" className="w-full bg-transparent py-3 text-sm outline-none placeholder:text-slate-600"/>
          </label>
          <label className="flex min-h-12 items-center gap-3 border border-white/10 bg-[#10151b] px-4">
            <SlidersHorizontal size={16} className="text-slate-500"/>
            <span className="text-xs text-slate-500">Level</span>
            <select aria-label="Filter by level" value={level} onChange={e => setLevel(e.target.value)} className="max-w-40 bg-transparent py-3 text-sm text-slate-200 outline-none">
              {levels.map(x => <option key={x} value={x} className="bg-[#10151b]">{x === "all" ? "All levels" : x}</option>)}
            </select>
          </label>
          <label className="flex min-h-12 items-center gap-3 border border-white/10 bg-[#10151b] px-4">
            <span className="text-xs text-slate-500">Track</span>
            <select aria-label="Filter by learning track" value={track} onChange={e => setTrack(e.target.value)} className="max-w-52 bg-transparent py-3 text-sm text-slate-200 outline-none">
              {tracks.map(x => <option key={x} value={x} className="bg-[#10151b]">{x === "all" ? "All tracks" : x}</option>)}
            </select>
          </label>
          <div className="flex items-center gap-3">
            <span className="text-xs tabular-nums text-slate-500">{loading ? "Loading catalogue…" : `${filtered.length} ${filtered.length === 1 ? "course" : "courses"}`}</span>
            {(query || level !== "all" || track !== "all") && <button type="button" onClick={() => {setQuery("");setLevel("all");setTrack("all");}} className="text-xs font-semibold text-[#f2d477] hover:text-white">Clear filters</button>}
          </div>
        </div>
      </section>

      <section className="mt-8" aria-live="polite">
        {loading && showSkeleton && (
          <div className="grid gap-px border border-white/10 bg-white/10 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, index) => (
              <div key={index} className="animate-pulse bg-[#10151b]">
                <div className="h-52 bg-[#171e27]" />
                <div className="space-y-3 p-5">
                  <div className="h-4 w-2/3 bg-white/[.06]" />
                  <div className="h-3 w-full bg-white/[.04]" />
                  <div className="h-3 w-4/5 bg-white/[.04]" />
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && error && (
          <div className="border border-white/10 bg-[#10151b] p-8 sm:p-10">
            <EmptyState title="Courses unavailable" message={error} />
            <button onClick={loadCourses} className="mt-4 border border-white/15 px-4 py-2.5 text-sm font-semibold hover:border-[#d7ad35]/50">Try again</button>
          </div>
        )}

        {!loading && !error && filtered.length > 0 && (
          <div className="landing-course-grid">
            {filtered.map(course => {
              const candidate = typeof course.thumbnail_url === "string" ? course.thumbnail_url.trim() : "";
              const imageKey = candidate ? candidate.split("?")[0] : "";
              const image = imageKey && !usedImages.has(imageKey) ? candidate : "";
              if (image) usedImages.add(imageKey);
              return (
                <Link key={course.id} href={"/courses/" + course.id} className="landing-course-card group min-w-0">
                  <div className="landing-course-image relative">
                    {image ? (
                      <img src={image} alt="" loading="lazy" className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.035]" />
                    ) : (
                      <div className="flex h-full items-end justify-between p-5">
                        <BookOpen size={42} className="text-white/30" />
                        <span className="text-xs uppercase tracking-[.18em] text-[#f2d477]">Learnora / Course</span>
                      </div>
                    )}
                    <span className="absolute left-4 top-4 border border-white/15 bg-[#080a0d] px-3 py-1.5 text-[10px] uppercase tracking-[.15em] text-slate-200">{course.level || "All levels"}</span>
                    {Array.isArray(course.tracks) && course.tracks.length > 0 && (
                      <span className="absolute bottom-4 left-4 max-w-[85%] truncate border border-[#d7ad35]/35 bg-[#080a0d]/90 px-3 py-1.5 text-[10px] uppercase tracking-[.12em] text-[#f2d477]">
                        {course.tracks.slice(0, 2).map((item: any) => item.name).join(" · ")}
                      </span>
                    )}
                  </div>
                  <div className="landing-course-copy">
                    <h2 className="font-display text-2xl leading-snug">{course.title}</h2>
                    {(course.settings?.is_free === true || course.settings?.access_type === "free") && (
                      <p className="mt-2 text-[10px] font-bold uppercase tracking-[.16em] text-[#f2d477]">Free for individual learners</p>
                    )}
                    <p className="mt-3 min-h-12 text-sm leading-6 text-slate-400">{course.short_description || course.description || "Explore the curriculum and available access options."}</p>
                    <div className="mt-5 flex items-center justify-between gap-3 border-t border-white/[.08] pt-4 text-xs text-slate-500">
                      <span className="inline-flex items-center gap-2"><Clock3 size={14} />{course.estimated_hours ? course.estimated_hours + " hours" : "Self-paced"}</span>
                      <span className="inline-flex items-center gap-2 font-semibold text-[#f2d477]">View course <ArrowRight size={14} /></span>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}

        {!loading && !error && filtered.length === 0 && (
          <EmptyState
            title={query || level !== "all" || track !== "all" ? "No courses match those filters" : "No published courses yet"}
            message={query || level !== "all" || track !== "all" ? "Try a broader search, another level or a different learning track." : "Learnora has not returned published courses from the backend yet. Draft content is intentionally not shown as available learning."}
          />
        )}
      </section>
    </main>;
  return signedIn ? <Shell active="discover">{catalogue}</Shell> : <div className="min-h-screen"><PublicNav/>{catalogue}<PublicFooter/></div>;
}
