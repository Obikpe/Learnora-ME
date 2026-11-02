"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, Route, CheckCircle2 } from "lucide-react";
import Shell from "../../../components/dashboard/Shell";
import Skeleton from "../../../components/feedback/Skeleton";
import EmptyState from "../../../components/feedback/EmptyState";
import { request } from "../../../lib/api/client";

type TrackProgress = {
  track: { id: string; name: string; description?: string | null; status: string };
  enrolled: boolean;
  completed: boolean;
  progress_percent: number;
  completed_required_courses: number;
  required_courses: number;
  courses: Array<{
    id: string;
    required: boolean;
    enrolled: boolean;
    course: { id: string; title: string; level?: string | null };
    progress: { progress_percent: number; completed: boolean; completed_lessons: number; total_lessons: number };
  }>;
};

export default function MyLearningTracksPage() {
  const [tracks, setTracks] = useState<TrackProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const mine = await request<any>("/progress/me");
        const ids = Array.from(new Set<string>(
          (mine.courses || []).map((row: any) => {
            const source = String(row.enrolment?.source_type || "");
            const match = source.match(/^track_enrolment:([0-9a-f-]{36})$/i);
            return match?.[1] || "";
          }).filter(Boolean)
        ));
        const results = await Promise.all(ids.map(id => request<TrackProgress>("/progress/tracks/" + encodeURIComponent(id))));
        if (active) setTracks(results);
      } catch (e: any) {
        if (active) setError(e.message || "Your learning tracks could not be loaded.");
      } finally {
        if (active) setLoading(false);
      }
    }
    void load();
    return () => { active = false; };
  }, []);

  return <Shell active="tracks">
    <header className="flex flex-wrap items-end justify-between gap-5 border-b border-white/[.08] pb-6">
      <div>
        <p className="text-xs font-bold uppercase tracking-[.18em] gold">Your learning journey</p>
        <h1 className="mt-3 font-display text-4xl sm:text-5xl">My learning tracks</h1>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">Follow the courses in each track and keep track of your progress from one place.</p>
      </div>
      <Link href="/tracks" className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-[#d7ad35] px-4 py-3 text-sm font-bold text-black">Explore tracks <ArrowRight size={15}/></Link>
    </header>

    {loading ? <div className="mt-8"><Skeleton label="Loading your learning tracks"/></div>
      : error ? <div role="alert" className="mt-8 rounded-xl border border-red-400/20 bg-red-400/[.05] p-4 text-sm text-red-200">{error}</div>
      : tracks.length ? <div className="mt-8 grid gap-5 xl:grid-cols-2">
        {tracks.map(item => <article key={item.track.id} className="rounded-2xl border border-white/[.09] bg-[#0e1319] p-5 sm:p-6">
          <div className="flex items-start justify-between gap-4">
            <div><span className="inline-flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.16em] gold"><Route size={13}/> Enrolled track</span><h2 className="mt-3 font-display text-2xl">{item.track.name}</h2><p className="mt-2 text-sm leading-6 text-slate-400">{item.track.description || "A structured sequence of courses for your learning goals."}</p></div>
            {item.completed && <CheckCircle2 className="shrink-0 text-emerald-400" size={21}/>}
          </div>
          <div className="mt-6 flex items-center justify-between gap-3 text-xs text-slate-500"><span>{item.completed_required_courses} of {item.required_courses} required courses complete</span><strong className="text-sm tabular-nums text-slate-200">{item.progress_percent}%</strong></div>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-black/20"><div className="h-full rounded-full bg-[#d7ad35]" style={{width: item.progress_percent + "%"}}/></div>
          <div className="mt-5 divide-y divide-white/[.06]">
            {item.courses.map(course => <div key={course.course.id} className="flex items-center justify-between gap-4 py-3 first:pt-0 last:pb-0">
              <div className="min-w-0"><p className="truncate text-sm font-medium">{course.course.title}</p><p className="mt-1 text-xs text-slate-500">{course.required ? "Required course" : "Optional course"} · {course.progress.completed_lessons}/{course.progress.total_lessons} lessons</p></div>
              {course.enrolled ? <Link href={"/dashboard/learning/" + course.course.id} className="shrink-0 text-xs font-semibold gold">Continue <ArrowRight size={13} className="inline"/></Link> : <span className="shrink-0 text-xs text-slate-500">Not started</span>}
            </div>)}
          </div>
        </article>)}
      </div> : <div className="mt-8"><EmptyState title="You have not joined a learning track yet" message="Explore published tracks, choose a learning journey and enrol to see your courses and progress here." action={<Link href="/tracks" className="rounded-xl bg-[#d7ad35] px-4 py-2.5 text-sm font-bold text-black">Explore learning tracks</Link>}/></div>}
  </Shell>;
}
