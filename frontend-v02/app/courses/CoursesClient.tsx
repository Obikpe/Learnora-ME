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

export default function CoursesClient({ initialCourses, initialError }: { initialCourses: any[]; initialError?: string | null }) {
  const [signedIn, setSignedIn] = useState(false);
  const [items, setItems] = useState<any[]>(initialCourses);
  const [error, setError] = useState(initialError || "");
  const [loading, setLoading] = useState(false);
  const [showSkeleton, setShowSkeleton] = useState(false);
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState("all");
  const [track, setTrack] = useState("all");
  const [topic, setTopic] = useState("all");
  const [duration, setDuration] = useState("all");
  const [price, setPrice] = useState("all");
  const [rating, setRating] = useState("all");
  const [sort, setSort] = useState("newest");
  const [filtersReady, setFiltersReady] = useState(false);
  const [page, setPage] = useState(1);
  const pageSize = 12;

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
    const params = new URLSearchParams(window.location.search);
    setLevel(params.get("level") || "all");
    setTrack(params.get("track") || "all");
    setTopic(params.get("topic") || "all");
    setDuration(params.get("duration") || "all");
    setPrice(params.get("price") || "all");
    setRating(params.get("rating") || "all");
    setSort(params.get("sort") || "newest");
    setPage(Math.max(1, Number(params.get("page") || 1)));
    setFiltersReady(true);
    currentUser().then(me => {
      if (!active) return;
      const memberships = me.organisation_memberships || [];
      const assignedLearner = Boolean(
        me.account_type === "cohort" ||
        (me.account_type === "learner" && me.role !== "normal") ||
        me.cohort_id ||
        me.organisation_id ||
        me.organisation_role === "learner" ||
        me.organisation_role === "member" ||
        memberships.some((membership: any) => ["learner", "member"].includes(membership.role) && membership.status === "active")
      );
      if (assignedLearner) {
        window.location.replace(me.account_type === "cohort" ? "/dashboard/cohort" : "/dashboard");
        return;
      }
      setSignedIn(true);
    }).catch(() => {
      if (!active) return;
      setSignedIn(false);
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

  const topics = useMemo(() => {
    const values = items.flatMap(course => Array.isArray(course.settings?.topics) ? course.settings.topics : []);
    return ["all", ...Array.from(new Set(values.map((value: any) => String(value).trim()).filter(Boolean))).sort((a,b) => a.localeCompare(b))];
  }, [items]);

  const hasRatings = items.some(course => Number.isFinite(Number(course.average_rating ?? course.rating)));
  const filtered = useMemo(() => {
    const result = items.filter(course => {
      const courseTracks = Array.isArray(course.tracks) ? course.tracks.map((item: any) => String(item.name || "")) : [];
      const courseTopics = Array.isArray(course.settings?.topics) ? course.settings.topics.map((value: any) => String(value)) : [];
      const searchable = [course.title, course.short_description, course.description, course.level, courseTracks.join(" "), courseTopics.join(" ")].filter(Boolean).join(" ").toLowerCase();
      const hours = Number(course.estimated_hours || 0);
      const isFree = course.settings?.is_free === true || course.settings?.access_type === "free" || course.settings?.price === 0;
      const score = Number(course.average_rating ?? course.rating);
      return searchable.includes(query.trim().toLowerCase())
        && (level === "all" || course.level === level)
        && (track === "all" || courseTracks.includes(track))
        && (topic === "all" || courseTopics.includes(topic))
        && (duration === "all" || (duration === "under-2" && hours > 0 && hours < 2) || (duration === "2-5" && hours >= 2 && hours <= 5) || (duration === "over-5" && hours > 5))
        && (price === "all" || (price === "free" && isFree) || (price === "paid" && !isFree))
        && (rating === "all" || (rating === "4" && score >= 4));
    });
    return result.sort((a,b) => {
      if (sort === "title") return String(a.title || "").localeCompare(String(b.title || ""));
      if (sort === "shortest") return Number(a.estimated_hours || Infinity) - Number(b.estimated_hours || Infinity);
      if (sort === "longest") return Number(b.estimated_hours || 0) - Number(a.estimated_hours || 0);
      if (sort === "rating") return Number(b.average_rating ?? b.rating ?? 0) - Number(a.average_rating ?? a.rating ?? 0);
      return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime();
    });
  }, [items, query, level, track, topic, duration, price, rating, sort]);

  useEffect(() => {
    if (!filtersReady) return;
    const params = new URLSearchParams();
    if (query.trim()) params.set("search", query.trim());
    if (page > 1) params.set("page", String(page));
    for (const [key, value] of [["level",level],["track",track],["topic",topic],["duration",duration],["price",price],["rating",rating],["sort",sort]] as const) {
      if (value !== "all" && !(key === "sort" && value === "newest")) params.set(key, value);
    }
    const next = params.toString();
    const url = next ? window.location.pathname + "?" + next : window.location.pathname;
    window.history.replaceState(null, "", url);
  }, [filtersReady, query, level, track, topic, duration, price, rating, sort, page]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const pageItems = filtered.slice((page - 1) * pageSize, page * pageSize);

  const usedImages = new Set<string>();
  [
    IMAGES.hero, IMAGES.learners, IMAGES.instructors, IMAGES.organisations,
    IMAGES.portfolio, IMAGES.studio, IMAGES.library, IMAGES.workshop,
    IMAGES.tutors, IMAGES.community, IMAGES.aboutHero, IMAGES.aboutVision,
    IMAGES.learnerPage, IMAGES.instructorPage, IMAGES.organisationPage, IMAGES.login,
  ].forEach(url => usedImages.add(url.split("?")[0]));

  const catalogue = <main id="main-content" className={"mx-auto max-w-7xl px-5 pb-24 " + (signedIn ? "pt-8" : "pt-32") + " lg:px-8"}>
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
        <div className="flex flex-col flex-wrap gap-3 md:flex-row md:items-center">
          <label className="flex min-h-12 flex-1 items-center gap-3 border border-white/10 bg-[#10151b] px-4 focus-within:border-[#d7ad35]/60">
            <Search size={17} className="shrink-0 text-slate-500"/>
            <input aria-label="Search courses" list="course-search-suggestions" value={query} onChange={e => { setPage(1); setQuery(e.target.value); }} placeholder="Search skills, topics or course names" className="w-full bg-transparent py-3 text-sm outline-none placeholder:text-slate-600"/>
            <datalist id="course-search-suggestions">{[...topics.slice(1), ...tracks.slice(1), ...levels.slice(1)].map(value => <option key={value} value={value}/>)}</datalist>
          </label>
          <label className="flex min-h-12 items-center gap-3 border border-white/10 bg-[#10151b] px-4">
            <SlidersHorizontal size={16} className="text-slate-500"/>
            <span className="text-xs text-slate-500">Level</span>
            <select aria-label="Filter by level" value={level} onChange={e => { setPage(1); setLevel(e.target.value); }} className="max-w-40 bg-transparent py-3 text-sm text-slate-200 outline-none">
              {levels.map(x => <option key={x} value={x} className="bg-[#10151b]">{x === "all" ? "All levels" : x}</option>)}
            </select>
          </label>
          <label className="flex min-h-12 items-center gap-3 border border-white/10 bg-[#10151b] px-4">
            <span className="text-xs text-slate-500">Track</span>
            <select aria-label="Filter by learning track" value={track} onChange={e => { setPage(1); setTrack(e.target.value); }} className="max-w-52 bg-transparent py-3 text-sm text-slate-200 outline-none">
              {tracks.map(x => <option key={x} value={x} className="bg-[#10151b]">{x === "all" ? "All tracks" : x}</option>)}
            </select>
          </label>
          <label className="flex min-h-12 items-center gap-3 border border-white/10 bg-[#10151b] px-4">
            <span className="text-xs text-slate-500">Topic</span>
            <select aria-label="Filter by topic" value={topic} onChange={e => { setPage(1); setTopic(e.target.value); }} className="max-w-48 bg-transparent py-3 text-sm text-slate-200 outline-none">
              {topics.map(x => <option key={x} value={x}>{x === "all" ? "All topics" : x}</option>)}
            </select>
          </label>
          <label className="flex min-h-12 items-center gap-3 border border-white/10 bg-[#10151b] px-4">
            <span className="text-xs text-slate-500">Duration</span>
            <select aria-label="Filter by duration" value={duration} onChange={e => { setPage(1); setDuration(e.target.value); }} className="max-w-40 bg-transparent py-3 text-sm text-slate-200 outline-none">
              <option value="all">Any length</option><option value="under-2">Under 2 hours</option><option value="2-5">2–5 hours</option><option value="over-5">Over 5 hours</option>
            </select>
          </label>
          <label className="flex min-h-12 items-center gap-3 border border-white/10 bg-[#10151b] px-4">
            <span className="text-xs text-slate-500">Price</span>
            <select aria-label="Filter by price" value={price} onChange={e => { setPage(1); setPrice(e.target.value); }} className="max-w-32 bg-transparent py-3 text-sm text-slate-200 outline-none">
              <option value="all">Any price</option><option value="free">Free</option><option value="paid">Paid</option>
            </select>
          </label>
          {hasRatings && <label className="flex min-h-12 items-center gap-3 border border-white/10 bg-[#10151b] px-4">
            <span className="text-xs text-slate-500">Rating</span>
            <select aria-label="Filter by rating" value={rating} onChange={e => { setPage(1); setRating(e.target.value); }} className="max-w-32 bg-transparent py-3 text-sm text-slate-200 outline-none">
              <option value="all">Any rating</option><option value="4">4.0 and above</option>
            </select>
          </label>}
          <label className="flex min-h-12 items-center gap-3 border border-white/10 bg-[#10151b] px-4">
            <span className="text-xs text-slate-500">Sort</span>
            <select aria-label="Sort courses" value={sort} onChange={e => { setPage(1); setSort(e.target.value); }} className="max-w-40 bg-transparent py-3 text-sm text-slate-200 outline-none">
              <option value="newest">Newest</option><option value="title">Title</option><option value="shortest">Shortest</option><option value="longest">Longest</option>{hasRatings && <option value="rating">Top rated</option>}
            </select>
          </label>
          <div className="flex items-center gap-3">
            <span className="text-xs tabular-nums text-slate-500">{loading ? "Updating…" : `${filtered.length} of ${items.length} ${items.length === 1 ? "course" : "courses"}`}</span>
            {(query || level !== "all" || track !== "all" || topic !== "all" || duration !== "all" || price !== "all" || rating !== "all" || sort !== "newest") && <button type="button" onClick={() => {setQuery("");setLevel("all");setTrack("all");setTopic("all");setDuration("all");setPrice("all");setRating("all");setSort("newest");}} className="min-h-11 text-xs font-semibold text-[#f2d477] hover:text-white">Clear filters</button>}
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
            {pageItems.map(course => {
              const candidate = typeof course.thumbnail_url === "string" ? course.thumbnail_url.trim() : "";
              const imageKey = candidate ? candidate.split("?")[0] : "";
              const image = imageKey && !usedImages.has(imageKey) ? candidate : "";
              if (image) usedImages.add(imageKey);
              const category = Array.isArray(course.settings?.topics) ? course.settings.topics[0] : course.tracks?.[0]?.name;
              const instructorName = course.instructor?.name || course.instructor_name || course.creator_name;
              const ratingValue = Number(course.average_rating ?? course.rating);
              const learnerCount = Number(course.learner_count ?? course.enrolment_count);
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
                    {category && <span className="inline-flex border border-white/[.12] px-2.5 py-1 text-[10px] uppercase tracking-[.12em] text-slate-400">{category}</span>}
                    <h2 className="mt-2 font-display text-2xl leading-snug">{course.title}</h2>
                    {(course.settings?.is_free === true || course.settings?.access_type === "free") && (
                      <p className="mt-2 text-[10px] font-bold uppercase tracking-[.16em] text-[#f2d477]">Free for individual learners</p>
                    )}
                    <p className="mt-3 min-h-12 text-sm leading-6 text-slate-400">{course.short_description || course.description || "Explore the curriculum and available access options."}</p>
                    {(instructorName || Number.isFinite(ratingValue) || Number.isFinite(learnerCount)) && <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-500">{instructorName && <span>By {instructorName}</span>}{Number.isFinite(ratingValue) && ratingValue > 0 && <span aria-label={"Rating " + ratingValue.toFixed(1) + " out of 5"}>★ {ratingValue.toFixed(1)}</span>}{Number.isFinite(learnerCount) && learnerCount > 0 && <span>{learnerCount.toLocaleString()} learners</span>}</div>}
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
        {!loading && !error && filtered.length > pageSize && <nav aria-label="Course catalogue pages" className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-white/[.1] pt-5"><span className="text-xs text-slate-500">Page {page} of {totalPages}</span><div className="flex items-center gap-2"><button type="button" disabled={page <= 1} onClick={() => setPage(value => Math.max(1, value - 1))} className="min-h-11 border border-white/15 px-4 text-sm disabled:opacity-40">Previous</button><button type="button" disabled={page >= totalPages} onClick={() => setPage(value => Math.min(totalPages, value + 1))} className="min-h-11 border border-white/15 px-4 text-sm disabled:opacity-40">Next</button></div></nav>}

        {!loading && !error && filtered.length === 0 && (
          <div><EmptyState title={query || level !== "all" || track !== "all" || topic !== "all" || duration !== "all" || price !== "all" ? "No courses match those filters" : "No published courses yet"} message={query || level !== "all" || track !== "all" || topic !== "all" || duration !== "all" || price !== "all" ? "Try a broader search or explore one of the available topics below." : "There are no published courses available to browse at the moment. Draft courses are not shown as available learning."}/>{topics.length > 1 && <div className="mt-5 flex flex-wrap gap-2">{topics.slice(1,6).map(value=><button key={value} type="button" onClick={()=>{setTopic(value);setPage(1);}} className="min-h-11 border border-white/15 px-3 text-xs text-slate-300 hover:border-[var(--gold)]">{value}</button>)}</div>}</div>
        )}
      </section>
    </main>;
  return signedIn ? <Shell active="discover">{catalogue}</Shell> : <div className="min-h-screen"><PublicNav/>{catalogue}<PublicFooter/></div>;
}
