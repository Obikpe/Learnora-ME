"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ArrowRight, BookOpen, CheckCircle2, Flame, RefreshCw } from "lucide-react";
import Shell from "../../../components/dashboard/Shell";
import StatCard from "../../../components/dashboard/StatCard";
import Skeleton from "../../../components/feedback/Skeleton";
import { request } from "../../../lib/api/client";

function formatLearningTime(value: unknown) {
  const seconds = Math.max(0, Math.floor(Number(value) || 0));
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (hours) return hours + "h " + minutes + "m";
  if (minutes) return minutes + "m";
  return seconds + "s";
}

function activityDate(value: string) {
  const date = new Date(value + "T12:00:00");
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}

export default function CohortDashboardPage() {
  const [learner, setLearner] = useState<any>(null);
  const [courses, setCourses] = useState<any[]>([]);
  const [activitySummary, setActivitySummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    setRefreshing(true);
    setError("");
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "Africa/Lagos";
    const [meResult, learningResult, activityResult] = await Promise.allSettled([
      request<any>("/cohort-auth/me"),
      request<any>("/cohort-learning/me/courses"),
      request<any>("/progress/learning-summary?timezone=" + encodeURIComponent(timezone)),
    ]);

    if (meResult.status === "fulfilled") {
      setLearner(meResult.value.account || null);
    }
    if (learningResult.status === "fulfilled") {
      const response = learningResult.value;
      setLearner(response.learner || (meResult.status === "fulfilled" ? meResult.value.account : null));
      const assigned = Array.isArray(response.courses) ? response.courses : [];
      const detailed = await Promise.all(assigned.map(async (row: any) => {
        const courseId = String(row.course?.id || row.course_id || "");
        if (!courseId) return { ...row, lessons: [], progress: [] };
        const [lessonResult, progressResult] = await Promise.allSettled([
          request<any>("/cohort-learning/me/courses/" + encodeURIComponent(courseId) + "/lessons"),
          request<any>("/cohort-learning/me/courses/" + encodeURIComponent(courseId) + "/progress"),
        ]);
        return {
          ...row,
          lessons: lessonResult.status === "fulfilled" ? lessonResult.value.lessons || [] : [],
          progress: progressResult.status === "fulfilled" ? progressResult.value.progress || [] : [],
        };
      }));
      setCourses(detailed);
    } else {
      setCourses([]);
      setError(learningResult.reason?.message || "Your assigned learning could not be loaded.");
    }
    setActivitySummary(activityResult.status === "fulfilled" ? activityResult.value : null);
    setLoading(false);
    setRefreshing(false);
  }

  useEffect(() => { void load(); }, []);

  const courseStats = useMemo(() => courses.reduce((total, row) => {
    const lessons = Array.isArray(row.lessons) ? row.lessons : [];
    const progress = Array.isArray(row.progress) ? row.progress : [];
    total.totalLessons += lessons.length;
    total.completedLessons += lessons.filter((lesson: any) =>
      progress.some((item: any) => String(item.lesson_id) === String(lesson.id) && item.completed)
    ).length;
    return total;
  }, { totalLessons: 0, completedLessons: 0 }), [courses]);

  const learningDays = activitySummary?.learning_days || [];
  const learningSeconds = Number(activitySummary?.learning_time_seconds || 0);
  const learningTimeLabel = activitySummary ? formatLearningTime(learningSeconds) : "—";
  const learnerName = [learner?.first_name, learner?.last_name].filter(Boolean).join(" ") || learner?.name || "";

  if (loading) {
    return <Shell active="learning" restricted role="assigned" trackLearning={false}><Skeleton label="Loading your assigned learning"/></Shell>;
  }

  return <Shell active="learning" restricted role="assigned" trackLearning={false}>
    <section className="flex flex-wrap items-start justify-between gap-5 pb-6">
      <div className="flex min-w-0 items-center gap-4">
        <div className="grid size-14 shrink-0 place-items-center rounded-full bg-[var(--primary-tint)] text-xl font-bold text-[var(--primary)] sm:size-16 sm:text-2xl" aria-hidden="true">
          {(learnerName || "L").trim().charAt(0).toUpperCase()}
        </div>
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wide text-[var(--primary)]">My Learning</p>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-[var(--text-heading)] sm:text-3xl">
            Welcome back{learner?.first_name ? ", " + learner.first_name : ""}
          </h1>
          <p className="mt-1 text-sm text-[var(--text-muted)]">Your assigned courses and learning progress.</p>
        </div>
      </div>
      <button type="button" onClick={() => void load()} disabled={refreshing} className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-[var(--border)] px-3 py-2 text-xs font-semibold text-[var(--text-body)] hover:bg-[var(--bg-soft)] disabled:opacity-50">
        <RefreshCw size={14} className={refreshing ? "animate-spin" : ""}/> Refresh
      </button>
    </section>

    {error && <p role="alert" className="mb-5 text-sm text-[var(--warning)]">{error}</p>}

    <section className="grid grid-cols-2 gap-3 xl:grid-cols-4" aria-label="Learning summary">
      <StatCard label="Assigned courses" value={courses.length}/>
      <StatCard label="Lessons completed" value={courseStats.completedLessons} detail={"of " + courseStats.totalLessons + " assigned lessons"}/>
      <StatCard label="Learning time" value={learningTimeLabel} detail="Time spent actively learning"/>
      <StatCard label="Learning streak" value={activitySummary ? activitySummary.current_streak + " days" : "—"} detail={activitySummary ? "Longest: " + activitySummary.longest_streak + " days" : "Activity summary unavailable"}/>
    </section>

    <section className="mt-4 rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
      <div className="mb-2 flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold text-[var(--text-heading)]">Assigned learning progress</h2>
        <span className="text-sm font-bold tabular-nums text-[var(--text-heading)]">
          {courseStats.totalLessons ? Math.round(courseStats.completedLessons / courseStats.totalLessons * 100) + "%" : "—"}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-[var(--bg-soft)]">
        <div className="h-full rounded-full bg-[var(--primary)]" style={{ width: (courseStats.totalLessons ? courseStats.completedLessons / courseStats.totalLessons * 100 : 0) + "%" }}/>
      </div>
      <p className="mt-2 text-xs text-[var(--text-muted)]">
        {courseStats.totalLessons ? "Progress across the lessons assigned to your cohort account." : "Your progress will appear when lessons are assigned to your account."}
      </p>
    </section>

    <section className="mt-8">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-[var(--primary)]">Your learning plan</p>
          <h2 className="mt-1 text-xl font-bold text-[var(--text-heading)]">Assigned courses</h2>
        </div>
        <span className="text-xs text-[var(--text-muted)]">{courses.length} {courses.length === 1 ? "course" : "courses"}</span>
      </div>

      {courses.length ? <div className="space-y-4">
        {courses.map((row: any) => {
          const course = row.course || {};
          const lessons = Array.isArray(row.lessons) ? row.lessons : [];
          const progress = Array.isArray(row.progress) ? row.progress : [];
          const completed = lessons.filter((lesson: any) =>
            progress.some((item: any) => String(item.lesson_id) === String(lesson.id) && item.completed)
          ).length;
          const percent = lessons.length ? Math.round(completed / lessons.length * 100) : 0;
          return <article key={row.id} className="grid gap-4 rounded-xl border border-[var(--border)] bg-[var(--card)] p-5 sm:grid-cols-[minmax(0,1fr)_minmax(13rem,.8fr)_auto] sm:items-center">
            <div className="min-w-0">
              <div className="mb-2 flex items-center gap-2 text-xs text-[var(--text-muted)]">
                <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-[var(--bg-soft)] text-[var(--primary)]"><BookOpen size={16}/></span>
                <span>Assigned learning</span>
              </div>
              <h3 className="text-base font-bold leading-6 text-[var(--text-heading)]">{course.title || "Assigned course"}</h3>
              <p className="mt-1 line-clamp-2 text-xs text-[var(--text-muted)]">{course.short_description || course.description || "Open this course to study the lessons assigned to you."}</p>
              <div className="mt-4">
                <div className="mb-1.5 flex items-center justify-between text-[11px]">
                  <span className="text-[var(--text-muted)]">Course progress</span>
                  <span className="font-semibold tabular-nums text-[var(--text-heading)]">{percent}%</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-[var(--bg-soft)]">
                  <span className="block h-full rounded-full bg-[var(--primary)]" style={{ width: percent + "%" }}/>
                </div>
                <p className="mt-2 text-[11px] text-[var(--text-muted)]">{completed} of {lessons.length} assigned lessons completed</p>
              </div>
            </div>
            <div className="flex min-h-[76px] items-center justify-between gap-3 rounded-lg bg-[var(--bg-soft)] p-4">
              <div className="min-w-0">
                <p className="text-[10px] font-semibold uppercase tracking-wide text-[var(--text-muted)]">Your next step</p>
                <p className="mt-1.5 truncate text-sm font-semibold text-[var(--text-heading)]">
                  {lessons.find((lesson: any) => !progress.some((item: any) => String(item.lesson_id) === String(lesson.id) && item.completed))?.title || (lessons.length ? "All assigned lessons completed" : "Lessons are being prepared")}
                </p>
                <p className="mt-1 text-[11px] text-[var(--text-muted)]">{course.estimated_hours ? course.estimated_hours + " estimated hours" : lessons.length + " assigned lessons"}</p>
              </div>
              {percent === 100 ? <CheckCircle2 size={20} className="shrink-0 text-[var(--success)]"/> : <BookOpen size={20} className="shrink-0 text-[var(--primary)]"/>}
            </div>
            <Link href={"/dashboard/cohort/courses/" + encodeURIComponent(course.id || row.course_id)} className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-[var(--on-primary)] hover:bg-[var(--primary-hover)]">
              {percent ? "Continue" : "Start learning"} <ArrowRight size={14}/>
            </Link>
          </article>;
        })}
      </div> : <div className="rounded-xl border border-dashed border-[var(--border)] bg-[var(--card)] p-8 text-center">
        <BookOpen className="mx-auto text-[var(--text-muted)]" size={26}/>
        <h3 className="mt-4 font-semibold text-[var(--text-heading)]">Your learning plan is being prepared</h3>
        <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[var(--text-muted)]">Your organisation has not assigned a course to your cohort account yet. Check back later or contact your cohort coordinator.</p>
      </div>}
    </section>

    <section className="mt-8 rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-bold text-[var(--text-heading)]">Recent learning activity</h2>
          <p className="mt-1 text-xs text-[var(--text-muted)]">Your learning consistency over recent days.</p>
        </div>
        <span className="inline-flex items-center gap-1 text-xs text-[var(--text-muted)]"><Flame size={14}/>{learningDays.length} days</span>
      </div>
      {learningDays.length ? <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {learningDays.slice(0, 6).map((day: any) => <article key={day.activity_date} className="rounded-lg bg-[var(--bg-soft)] p-4">
          <p className="text-sm font-semibold text-[var(--text-heading)]">{activityDate(day.activity_date)}</p>
          <p className="mt-2 text-xs capitalize leading-5 text-[var(--text-muted)]">{(day.activity_types || []).map((type: string) => type.replaceAll("_", " ")).join(" · ")}</p>
          <p className="mt-2 text-[11px] text-[var(--text-muted)]">{day.activity_count} recorded {day.activity_count === 1 ? "activity" : "activities"}</p>
        </article>)}
      </div> : <p className="mt-4 text-sm text-[var(--text-muted)]">{activitySummary ? "Complete an assigned lesson to begin building your learning history." : "Learning activity is temporarily unavailable. Your course assignments are unaffected."}</p>}
    </section>
  </Shell>;
}
