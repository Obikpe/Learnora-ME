"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, BookOpen, CheckCircle2, Circle, Clock3, RefreshCw } from "lucide-react";
import Shell from "../../../../../components/dashboard/Shell";
import Skeleton from "../../../../../components/feedback/Skeleton";
import { request } from "../../../../../lib/api/client";

export default function CohortCoursePage() {
  const params = useParams();
  const courseId = String(params.courseId || "");
  const [course, setCourse] = useState<any>(null);
  const [lessons, setLessons] = useState<any[]>([]);
  const [progress, setProgress] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    setRefreshing(true);
    setError("");
    try {
      const [courseResult, lessonResult, progressResult] = await Promise.all([
        request<any>("/cohort-learning/me/courses"),
        request<any>("/cohort-learning/me/courses/" + encodeURIComponent(courseId) + "/lessons"),
        request<any>("/cohort-learning/me/courses/" + encodeURIComponent(courseId) + "/progress"),
      ]);
      const assigned = (courseResult.courses || []).find((row: any) =>
        String(row.course?.id || row.course_id) === courseId
      );
      if (!assigned?.course) throw new Error("This course is not assigned to your account.");
      setCourse(assigned.course);
      setLessons(lessonResult.lessons || []);
      setProgress(Object.fromEntries((progressResult.progress || []).map((row: any) => [String(row.lesson_id), row])));
    } catch (e: any) {
      setError(e?.message || "The assigned lessons could not be loaded.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => { if (courseId) void load(); }, [courseId]);

  const completedCount = useMemo(() => lessons.filter((lesson: any) => progress[String(lesson.id)]?.completed).length, [lessons, progress]);
  const percent = lessons.length ? Math.round(completedCount / lessons.length * 100) : 0;

  if (loading) return <Shell active="learning" restricted role="assigned" trackLearning={false}><Skeleton label="Loading your assigned course"/></Shell>;

  return <Shell active="learning" restricted role="assigned" trackLearning={false}>
    <div className="mb-6">
      <Link href="/dashboard/cohort" className="inline-flex items-center gap-2 text-xs font-semibold text-[var(--text-muted)] hover:text-[var(--primary)]"><ArrowLeft size={14}/> Back to My Learning</Link>
    </div>

    {error ? <section role="alert" className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
      <h1 className="text-lg font-bold text-[var(--text-heading)]">Course unavailable</h1>
      <p className="mt-2 text-sm text-[var(--text-muted)]">{error}</p>
      <button type="button" onClick={() => void load()} disabled={refreshing} className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-[var(--primary)]"><RefreshCw size={14} className={refreshing ? "animate-spin" : ""}/> Try again</button>
    </section> : <>
      <section className="flex flex-wrap items-start justify-between gap-5 pb-6">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wide text-[var(--primary)]">Assigned course</p>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-[var(--text-heading)] sm:text-3xl">{course?.title || "Course lessons"}</h1>
          {course?.short_description || course?.description ? <p className="mt-2 max-w-3xl text-sm leading-6 text-[var(--text-muted)]">{course.short_description || course.description}</p> : null}
        </div>
        <button type="button" onClick={() => void load()} disabled={refreshing} className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-[var(--border)] px-3 py-2 text-xs font-semibold text-[var(--text-body)] hover:bg-[var(--bg-soft)] disabled:opacity-50"><RefreshCw size={14} className={refreshing ? "animate-spin" : ""}/> Refresh</button>
      </section>

      <section className="mb-6 rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
        <div className="flex items-center justify-between gap-3">
          <div><p className="text-xs text-[var(--text-muted)]">Assigned lesson progress</p><p className="mt-1 text-2xl font-bold tabular-nums text-[var(--text-heading)]">{completedCount} <span className="text-sm font-medium text-[var(--text-muted)]">/ {lessons.length} completed</span></p></div>
          <span className="text-sm font-bold tabular-nums text-[var(--primary)]">{percent}%</span>
        </div>
        <div className="mt-3 h-2 overflow-hidden rounded-full bg-[var(--bg-soft)]"><div className="h-full rounded-full bg-[var(--primary)]" style={{ width: percent + "%" }}/></div>
      </section>

      <section>
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-lg font-bold text-[var(--text-heading)]">Course lessons</h2>
          <span className="text-xs text-[var(--text-muted)]">{lessons.length} assigned</span>
        </div>
        {lessons.length ? <div className="space-y-3">
          {lessons.map((lesson: any, index: number) => {
            const saved = progress[String(lesson.id)] || {};
            const done = Boolean(saved.completed);
            return <Link key={lesson.id} href={"/dashboard/cohort/courses/" + encodeURIComponent(courseId) + "/lessons/" + encodeURIComponent(lesson.id)} className="grid gap-3 rounded-xl border border-[var(--border)] bg-[var(--card)] p-4 transition-colors hover:border-[var(--primary)] sm:grid-cols-[auto_minmax(0,1fr)_auto] sm:items-center">
              <span className="grid size-10 shrink-0 place-items-center rounded-lg bg-[var(--bg-soft)] text-xs font-semibold tabular-nums text-[var(--text-muted)]">{String(index + 1).padStart(2, "0")}</span>
              <span className="min-w-0">
                <span className="flex flex-wrap items-center gap-2">
                  <span className="font-semibold text-[var(--text-heading)]">{lesson.title || "Lesson"}</span>
                  {done && <span className="inline-flex items-center gap-1 rounded-md bg-[var(--success-tint)] px-2 py-1 text-[10px] font-semibold text-[var(--success)]"><CheckCircle2 size={12}/> Completed</span>}
                </span>
                <span className="mt-1 block line-clamp-2 text-xs leading-5 text-[var(--text-muted)]">{lesson.description || lesson.module?.title || "Open this assigned lesson to study the material."}</span>
                <span className="mt-2 flex flex-wrap items-center gap-3 text-[11px] text-[var(--text-muted)]"><span className="inline-flex items-center gap-1"><Clock3 size={12}/>{lesson.duration_minutes || 0} min</span><span>{Number(saved.progress_percent || 0)}% complete</span></span>
              </span>
              {done ? <CheckCircle2 size={19} className="shrink-0 text-[var(--success)]"/> : <Circle size={19} className="shrink-0 text-[var(--text-muted)]"/>}
            </Link>;
          })}
        </div> : <div className="rounded-xl border border-dashed border-[var(--border)] bg-[var(--card)] p-8 text-center">
          <BookOpen className="mx-auto text-[var(--text-muted)]" size={25}/>
          <h3 className="mt-3 font-semibold text-[var(--text-heading)]">No lessons assigned yet</h3>
          <p className="mt-2 text-sm text-[var(--text-muted)]">Your organisation may still be configuring your learning plan.</p>
        </div>}
      </section>
    </>}
  </Shell>;
}
