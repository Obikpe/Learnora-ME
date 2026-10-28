"use client";

import { useEffect, useState } from "react";
import { BookOpen, CalendarDays, Users } from "lucide-react";
import Shell from "../../../components/dashboard/Shell";
import SectionHeader from "../../../components/dashboard/SectionHeader";
import EmptyState from "../../../components/feedback/EmptyState";
import Skeleton from "../../../components/feedback/Skeleton";
import { request } from "../../../lib/api/client";

type TeachingAssignment = {
  id: string;
  assigned_lesson_count: number;
  completed_lesson_count: number;
  in_progress_lesson_count: number;
  completion_percent: number;
  lesson_progress?: Array<{
    lesson_id: string;
    title: string;
    order_index?: number | null;
    duration_minutes?: number | null;
    progress_percent: number;
    completed: boolean;
    status: "completed" | "in_progress" | "not_started";
  }>;
  cohort: {
    id: string;
    name: string;
    status: string;
    start_date?: string | null;
    end_date?: string | null;
    organisation_name?: string | null;
  };
  learner: { member_id: string; name: string; username?: string | null };
  course: { id: string; title: string; estimated_hours?: number | null };
};

function dateLabel(value?: string | null) {
  if (!value) return "";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "" : date.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

export default function InstructorWorkspace() {
  const [assignments, setAssignments] = useState<TeachingAssignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedAssignments, setExpandedAssignments] = useState<Record<string, boolean>>({});

  async function load() {
    setLoading(true);
    setError("");
    try {
      const result = await request<{ assignments?: TeachingAssignment[] }>("/instructor/me/assignments");
      setAssignments(result.assignments || []);
    } catch (e: any) {
      setError(e.message || "Your teaching assignments could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void load(); }, []);

  const learnerCount = new Set(assignments.map(item => item.learner.member_id)).size;
  const courseCount = new Set(assignments.map(item => item.course.id)).size;
  const cohortCount = new Set(assignments.map(item => item.cohort.id)).size;

  return <Shell active="instructor">
    <SectionHeader eyebrow="Teaching workspace" title="Your learners" description="Review the cohort learners and courses that have been assigned to you by your organisation." />
    {loading ? <div className="mt-8"><Skeleton variant="workspace" label="Loading your teaching assignments" /></div> : <>
      {error && <div role="alert" className="mt-6 rounded-xl border border-red-400/20 bg-red-400/[.05] p-4 text-sm text-red-200"><p>{error}</p><button type="button" onClick={() => void load()} className="mt-3 font-semibold underline underline-offset-4">Try again</button></div>}
      {!error && assignments.length > 0 && <div className="mt-7 grid gap-4 sm:grid-cols-3">
        {[{ label: "Assigned learners", value: learnerCount, icon: Users }, { label: "Assigned courses", value: courseCount, icon: BookOpen }, { label: "Cohorts", value: cohortCount, icon: CalendarDays }].map(({ label, value, icon: Icon }) => <div key={label} className="rounded-2xl border border-white/[.08] bg-[#0e1319] p-5"><div className="flex items-center justify-between gap-3"><p className="text-xs text-slate-500">{label}</p><Icon size={17} className="gold" /></div><p className="mt-4 font-display text-4xl">{value}</p></div>)}
      </div>}
      {!error && assignments.length === 0 ? <div className="mt-7"><EmptyState title="No teaching assignments yet" message="When an organisation assigns you to a learner's course, the cohort, learner and course will appear here. If you expected an assignment, ask your organisation administrator to check your active instructor membership and learner assignment." /></div> : !error && <div className="mt-7 grid gap-4 xl:grid-cols-2">
        {assignments.map(item => <article key={item.id} className="rounded-2xl border border-white/[.08] bg-[#0e1319] p-5 sm:p-6">
          <div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-[10px] font-bold uppercase tracking-[.18em] gold">{item.cohort.organisation_name || "Organisation"}</p><h2 className="mt-2 text-lg font-semibold">{item.learner.name}</h2><p className="mt-1 text-xs text-slate-500">{item.learner.username ? "@" + item.learner.username : "Cohort learner"}</p></div><span className="rounded-full border border-emerald-400/20 px-3 py-1 text-[10px] capitalize text-emerald-200">{item.cohort.status}</span></div>
          <div className="mt-5 rounded-xl border border-white/[.07] bg-black/15 p-4"><div className="flex items-start gap-3"><BookOpen size={18} className="mt-0.5 shrink-0 gold"/><div className="min-w-0"><p className="font-medium">{item.course.title}</p><p className="mt-1 text-xs text-slate-500">{item.assigned_lesson_count} assigned lesson{item.assigned_lesson_count === 1 ? "" : "s"}{item.course.estimated_hours != null ? " · " + item.course.estimated_hours + " estimated hours" : ""}</p></div></div>
            <div className="mt-4 border-t border-white/[.07] pt-4">
              <div className="flex items-center justify-between gap-3 text-xs"><span className="text-slate-400">Lesson progress</span><span className="text-slate-200">{item.completed_lesson_count} of {item.assigned_lesson_count} complete</span></div>
              <div role="progressbar" aria-label={item.learner.name + " lesson completion"} aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.max(0, Math.min(100, item.completion_percent || 0))} className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-[#d7ad35] transition-all" style={{ width: Math.max(0, Math.min(100, item.completion_percent || 0)) + "%" }}/></div>
              <p className="mt-2 text-[11px] text-slate-500">{item.in_progress_lesson_count} lesson{item.in_progress_lesson_count === 1 ? "" : "s"} in progress</p>
            </div>
            <button
              type="button"
              aria-expanded={Boolean(expandedAssignments[item.id])}
              aria-controls={"lesson-progress-" + item.id}
              onClick={() => setExpandedAssignments(old => ({ ...old, [item.id]: !old[item.id] }))}
              className="mt-4 text-xs font-semibold gold underline-offset-4 hover:underline"
            >
              {expandedAssignments[item.id] ? "Hide lesson details" : "View lesson details"}
            </button>
            {expandedAssignments[item.id] && <div id={"lesson-progress-" + item.id} className="mt-3 space-y-3 border-t border-white/[.07] pt-3">
              {!item.lesson_progress?.length ? <p className="text-xs text-slate-500">No active lessons are currently assigned to this learner for this course.</p> : item.lesson_progress.map(lesson => {
                const percent = Math.max(0, Math.min(100, lesson.progress_percent || 0));
                return <div key={lesson.lesson_id} className="rounded-lg border border-white/[.06] bg-black/10 p-3">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div><p className="text-xs font-medium text-slate-200">{lesson.title}</p>{lesson.duration_minutes != null && <p className="mt-1 text-[10px] text-slate-600">{lesson.duration_minutes} min</p>}</div>
                    <span className={"text-[10px] capitalize " + (lesson.status === "completed" ? "text-emerald-200" : lesson.status === "in_progress" ? "text-[#f2d477]" : "text-slate-500")}>{lesson.status.replaceAll("_", " ")}</span>
                  </div>
                  <div className="mt-2 h-1 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-[#d7ad35]" style={{ width: percent + "%" }} /></div>
                  <p className="mt-1 text-right text-[10px] text-slate-600">{percent}%</p>
                </div>;
              })}
            </div>}
          </div>
          <div className="mt-4 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500"><span>{item.cohort.name}</span><span>{dateLabel(item.cohort.start_date)}{item.cohort.start_date && item.cohort.end_date ? " – " : ""}{dateLabel(item.cohort.end_date)}</span></div>
        </article>)}
      </div>}
    </>}
  </Shell>;
}
