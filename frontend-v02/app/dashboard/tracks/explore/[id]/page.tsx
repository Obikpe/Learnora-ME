"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, ArrowRight, CheckCircle2, Circle, LockKeyhole } from "lucide-react";
import Shell from "../../../../../components/dashboard/Shell";
import EmptyState from "../../../../../components/feedback/EmptyState";
import Skeleton from "../../../../../components/feedback/Skeleton";
import { currentUser, organisationContext } from "../../../../../lib/api";
import { request } from "../../../../../lib/api/client";

export default function SignedInTrackDetailPage() {
  const params = useParams<{id:string}>();
  const router = useRouter();
  const [track, setTrack] = useState<any>(null);
  const [progress, setProgress] = useState<any>(null);
  const [user, setUser] = useState<any>(null);
  const [hasOrganisationContext, setHasOrganisationContext] = useState(false);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);
  const [error, setError] = useState("");

  const loadProgress = useCallback(async () => {
    try {
      const result = await request<any>("/progress/tracks/" + encodeURIComponent(params.id));
      setProgress(result);
    } catch {
      setProgress(null);
    }
  }, [params.id]);

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
        if (!active) return;
        setUser(me);
        setHasOrganisationContext(Boolean(organisationContext()));
        try {
          const result = await request<any>("/public/tracks/" + encodeURIComponent(params.id));
          if (active) setTrack(result.track);
        } catch (cause: any) {
          // Existing learners can still open a track they joined if it is no
          // longer listed for new enrolments.
          try {
            const saved = await request<any>("/progress/tracks/" + encodeURIComponent(params.id));
            if (active) {
              setProgress(saved);
              setTrack({
                ...saved.track,
                courses: saved.courses,
                course_count: saved.courses?.length || 0,
                required_course_count: saved.required_courses || 0,
              });
            }
          } catch {
            if (active) setError(cause?.message || "This learning track could not be loaded.");
          }
        }
        if (active) {
          try {
            const saved = await request<any>("/progress/tracks/" + encodeURIComponent(params.id));
            setProgress(saved);
          } catch { setProgress(null); }
        }
      } catch (cause: any) {
        if (active) setError(cause?.message || "Your learning session could not be verified.");
      } finally {
        if (active) setLoading(false);
      }
    }
    void load();
    return () => { active = false; };
  }, [params.id]);

  const nextCourse = useMemo(() => {
    const courses = progress?.courses || [];
    const enrolled = courses.filter((item: any) => item.enrolled);
    return enrolled.find((item: any) => item.required && !item.progress?.completed)
      || enrolled.find((item: any) => !item.progress?.completed)
      || enrolled[0]
      || courses.find((item: any) => item.required)
      || track?.courses?.[0];
  }, [progress, track]);

  async function enrol() {
    setError("");
    setEnrolling(true);
    try {
      await request<any>("/courses/tracks/" + encodeURIComponent(params.id) + "/enrol", { method: "POST" });
      await loadProgress();
      const target = track?.courses?.find((item: any) => item.required)?.course?.id || track?.courses?.[0]?.course?.id;
      if (target) router.push("/dashboard/learning/" + encodeURIComponent(target));
    } catch (cause: any) {
      setError(cause?.message || "Track enrolment could not be completed.");
    } finally {
      setEnrolling(false);
    }
  }

  if (loading) return <Shell active="tracks"><Skeleton variant="course" label="Loading learning track" /></Shell>;
  if (!track) return <Shell active="tracks"><div className="py-10"><EmptyState title="Track unavailable" message={error || "This learning track could not be found."} action={<Link href="/dashboard/tracks/explore" className="font-semibold text-[var(--primary)]">Back to explore tracks</Link>} /></div></Shell>;

  const requiredCount = progress?.required_courses ?? track.required_course_count ?? 0;
  const completedCount = progress?.completed_required_courses ?? 0;
  const percent = progress?.progress_percent ?? 0;
  const isEnrolled = Boolean(progress?.enrolled);
  const isCompleted = Boolean(progress?.completed);
  const individualLearner = user?.role === "normal" && user?.account_type === "learner" && !hasOrganisationContext;
  const canSelfEnrol = individualLearner && track.status === "published" && track.self_enrol_available;

  return <Shell active="tracks">
    <Link href="/dashboard/tracks/explore" className="inline-flex items-center gap-2 text-xs font-medium text-[var(--text-muted)] hover:text-[var(--primary)]"><ArrowLeft size={14}/>All learning tracks</Link>
    <header className="mt-6 grid gap-7 border-b border-[var(--border)] pb-8 lg:grid-cols-[1fr_.55fr] lg:items-end">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[.16em] text-[var(--primary)]">Learning track</p>
        <h1 className="mt-3 text-3xl font-bold tracking-tight text-[var(--text-heading)] sm:text-5xl">{track.name}</h1>
        <p className="mt-4 max-w-3xl text-sm leading-7 text-[var(--text-muted)]">{track.description || "A structured sequence of courses to help you develop and apply a connected set of skills."}</p>
      </div>
      <section className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
        <div className="flex items-center justify-between text-xs text-[var(--text-muted)]"><span>Track progress</span><span className="tabular-nums">{percent}%</span></div>
        <div className="mt-3 h-2 overflow-hidden rounded-full bg-[var(--bg-soft)]"><div className="h-full rounded-full bg-[var(--primary)] transition-all" style={{ width: percent + "%" }} /></div>
        <p className="mt-3 text-xs text-[var(--text-muted)]">{completedCount} of {requiredCount} required courses completed</p>
        {isCompleted ? <p className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-emerald-500"><CheckCircle2 size={16}/>Track completed</p>
          : isEnrolled ? <button type="button" disabled={!nextCourse?.course?.id} onClick={() => nextCourse?.course?.id && router.push("/dashboard/learning/" + encodeURIComponent(nextCourse.course.id))} className="mt-5 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-[var(--primary)] px-4 text-sm font-semibold text-[var(--on-primary)] disabled:opacity-40">Continue learning <ArrowRight size={15}/></button>
          : canSelfEnrol ? <button type="button" onClick={() => void enrol()} disabled={enrolling} className="mt-5 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-[var(--primary)] px-4 text-sm font-semibold text-[var(--on-primary)] disabled:opacity-50">{enrolling ? "Enrolling…" : "Enrol in this track"} <ArrowRight size={15}/></button>
          : track.status !== "published" ? <p className="mt-5 text-xs leading-6 text-[var(--text-muted)]">This track is no longer open for new enrolments.</p>
          : !track.self_enrol_available ? <p className="mt-5 text-xs leading-6 text-[var(--text-muted)]">Self-enrolment is not currently available for this track.</p>
          : <p className="mt-5 text-xs leading-6 text-[var(--text-muted)]">This account cannot self-enrol in public learning tracks.</p>}
      </section>
    </header>

    {error && <div role="alert" className="mt-5 rounded-xl border border-red-500/30 bg-red-500/5 p-4 text-sm text-red-500">{error}</div>}
    <section className="mt-9">
      <div className="flex flex-wrap items-end justify-between gap-3"><div><p className="text-xs font-semibold uppercase tracking-[.16em] text-[var(--primary)]">Curriculum</p><h2 className="mt-2 text-2xl font-bold text-[var(--text-heading)]">Courses in this track</h2></div><p className="text-xs text-[var(--text-muted)]">{track.course_count || track.courses?.length || 0} courses · ordered learning</p></div>
      <div className="mt-5 divide-y divide-[var(--border)] border-y border-[var(--border)]">
        {(track.courses || []).map((item: any, index: number) => {
          const saved = progress?.courses?.find((course: any) => course.course_id === item.course_id || course.course?.id === item.course?.id);
          const done = Boolean(saved?.progress?.completed);
          return <article key={item.id || item.course?.id || index} className="grid gap-3 py-5 sm:grid-cols-[2.75rem_minmax(0,1fr)_auto] sm:items-center">
            <div className="grid size-10 place-items-center rounded-lg border border-[var(--border)] text-xs tabular-nums text-[var(--text-muted)]">{String(index + 1).padStart(2, "0")}</div>
            <div className="min-w-0"><div className="flex flex-wrap items-center gap-3"><h3 className="text-base font-semibold text-[var(--text-heading)]">{item.course?.title}</h3><span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)]">{item.required ? "Required" : "Optional"}</span></div><p className="mt-1 text-sm leading-6 text-[var(--text-muted)]">{item.course?.short_description || item.course?.level || "Published Learnora course"}</p>{saved?.progress && <p className="mt-2 text-xs text-[var(--text-muted)]">{saved.progress.completed_lessons} of {saved.progress.total_lessons} lessons complete · {saved.progress.progress_percent}%</p>}</div>
            <div className="flex items-center gap-3">{done ? <span className="inline-flex items-center gap-2 text-xs font-semibold text-emerald-500"><CheckCircle2 size={15}/>Completed</span> : saved?.enrolled && item.course?.status === "published" ? <Link href={"/dashboard/learning/" + encodeURIComponent(item.course.id)} className="inline-flex min-h-9 items-center gap-2 rounded-lg border border-[var(--border)] px-3 text-xs font-semibold text-[var(--text-body)] hover:border-[var(--primary)]">Open course <ArrowRight size={14}/></Link> : saved?.enrolled ? <span className="text-xs text-[var(--text-muted)]">Enrolled · course unavailable</span> : <span className="inline-flex items-center gap-2 text-xs text-[var(--text-muted)]"><Circle size={13}/>Not enrolled</span>}</div>
          </article>;
        })}
      </div>
    </section>
    <p className="mt-7 max-w-3xl text-xs leading-6 text-[var(--text-muted)]"><LockKeyhole size={13} className="mr-2 inline"/>Track enrolment remains subject to the published track&apos;s free-access and self-enrolment settings.</p>
  </Shell>;
}
