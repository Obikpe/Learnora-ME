"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ArrowLeft, ArrowRight, CheckCircle2, Circle, LockKeyhole } from "lucide-react";
import PublicNav from "../../../components/public/PublicNav";
import PublicFooter from "../../../components/public/PublicFooter";
import EmptyState from "../../../components/feedback/EmptyState";
import Skeleton from "../../../components/feedback/Skeleton";
import { request } from "../../../lib/api/client";
import { currentUser, organisationContext } from "../../../lib/api";

export default function TrackDetailPage({params}:{params:{id:string}}) {
  const [track, setTrack] = useState<any>(null);
  const [progress, setProgress] = useState<any>(null);
  const [user, setUser] = useState<any>(null);
  const [hasOrganisationContext, setHasOrganisationContext] = useState(false);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);
  const [error, setError] = useState("");

  const loadProgress = useCallback(async () => {
    try {
      const result = await request<any>("/progress/tracks/"+encodeURIComponent(params.id));
      setProgress(result);
    } catch {
      setProgress(null);
    }
  }, [params.id]);

  useEffect(() => {
    let active = true;
    setHasOrganisationContext(Boolean(organisationContext()));
    const loadTrack = () => request<any>("/public/tracks/"+encodeURIComponent(params.id))
      .then(async result => {
        if (!active) return;
        setTrack(result.track);
        try {
          const saved = await request<any>("/progress/tracks/"+encodeURIComponent(params.id));
          if (active) setProgress(saved);
        } catch {
          if (active) setProgress(null);
        }
      })
      .catch(async e => {
        try {
          // Existing individual learners retain saved progress after a track
          // is unpublished or archived from public discovery.
          const saved = await request<any>("/progress/tracks/"+encodeURIComponent(params.id));
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
          if (active) setError(e.message || "Track could not be loaded.");
        }
      })
      .finally(() => { if (active) setLoading(false); });
    currentUser().then(me => {
      if (!active) return;
      const memberships = me.organisation_memberships || [];
      const assignedLearner = Boolean(
        me.account_type === "cohort" || me.role === "witstart" || me.cohort_id || me.organisation_id || me.organisation_role === "member" ||
        me.organisation_role === "learner" ||
        memberships.some((membership: any) => ["learner", "member"].includes(membership.role) && membership.status === "active")
      );
      if (assignedLearner) {
        setUser(me);
        window.location.replace(me.account_type === "cohort" ? "/dashboard/cohort" : "/dashboard");
        return;
      }
      setUser(me);
      void loadTrack();
    }).catch(() => {
      if (active) {
        setUser(null);
        void loadTrack();
      }
    });
    return () => { active = false; };
  }, [params.id]);

  const nextCourse = useMemo(() => {
    const courses = progress?.courses || [];
    const enrolledCourses = courses.filter((item:any) => item.enrolled);
    return enrolledCourses.find((item:any) => item.required && !item.progress?.completed)
      || enrolledCourses.find((item:any) => !item.progress?.completed)
      || enrolledCourses[0]
      || courses.find((item:any) => item.required)
      || track?.courses?.[0];
  }, [progress, track]);

  async function enrol() {
    setError("");
    setEnrolling(true);
    try {
      await request<any>("/courses/tracks/"+encodeURIComponent(params.id)+"/enrol", { method: "POST" });
      await loadProgress();
      const target = track?.courses?.find((item:any) => item.required)?.course?.id || track?.courses?.[0]?.course?.id;
      if (target) location.href = "/dashboard/learning/"+encodeURIComponent(target);
    } catch (e:any) {
      if (e.status === 401 || /\(401\)|sign in|unauthori[sz]ed/i.test(e.message || "")) {
        location.href = "/login?next="+encodeURIComponent("/tracks/"+params.id);
        return;
      }
      setError(e.message || "Track enrolment could not be completed.");
    } finally {
      setEnrolling(false);
    }
  }

  if (loading) return <><PublicNav/><main className="mx-auto max-w-7xl px-5 pb-24 pt-32 lg:px-8"><Skeleton variant="course" label="Loading track"/></main><PublicFooter/></>;
  if (error && !track) return <><PublicNav/><main className="mx-auto max-w-5xl px-5 pb-24 pt-36"><EmptyState title="Track unavailable" message={error}/><Link href="/tracks" className="mt-5 inline-flex items-center gap-2 text-sm font-semibold gold"><ArrowLeft size={15}/>Back to tracks</Link></main><PublicFooter/></>;

  const requiredCount = progress?.required_courses ?? track?.required_course_count ?? 0;
  const completedCount = progress?.completed_required_courses ?? 0;
  const percent = progress?.progress_percent ?? 0;
  const isEnrolled = Boolean(progress?.enrolled);
  const isCompleted = Boolean(progress?.completed);
  const individualLearner = user?.role === "normal" && user?.account_type === "learner" && !hasOrganisationContext;

  return <>
    <PublicNav/>
    <main className="mx-auto max-w-7xl px-5 pb-24 pt-32 lg:px-8">
      <Link href="/tracks" className="inline-flex items-center gap-2 text-xs text-slate-500 transition-colors hover:text-slate-200"><ArrowLeft size={14}/>All tracks</Link>
      <header className="mt-8 grid gap-8 border-b border-white/[.1] pb-10 lg:grid-cols-[1fr_.5fr] lg:items-end">
        <div><p className="section-kicker">Learnora track</p><h1 className="mt-4 max-w-4xl font-display text-5xl leading-[1.02] tracking-[-.04em] sm:text-6xl">{track?.name}</h1><p className="mt-5 max-w-3xl text-base leading-8 text-slate-400">{track?.description || "A structured sequence of courses to help you develop and apply a connected set of skills."}</p></div>
        <div className="border border-white/[.1] bg-[#0e1319] p-5">
          <div className="flex items-center justify-between text-xs text-slate-500"><span>Track progress</span><span className="tabular-nums">{percent}%</span></div>
          <div className="mt-3 h-2 overflow-hidden bg-white/[.08]"><div className="h-full bg-[var(--gold)] transition-all" style={{width:percent+"%"}}/></div>
          <p className="mt-3 text-xs text-slate-500">{completedCount} of {requiredCount} required courses completed</p>
          {isCompleted ? <p className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-emerald-300"><CheckCircle2 size={16}/>Track completed</p> : isEnrolled ? <button type="button" disabled={!nextCourse?.course?.id} onClick={()=>{if(nextCourse?.course?.id)location.href="/dashboard/learning/"+encodeURIComponent(nextCourse.course.id)}} className="mt-5 inline-flex min-h-11 w-full items-center justify-center gap-2 bg-[var(--gold)] px-4 text-sm font-bold text-[#16140f] disabled:opacity-40">Continue learning <ArrowRight size={15}/></button> : track?.status!=="published" ? <p className="mt-5 text-xs leading-6 text-slate-500">This track is no longer open for new enrolments.</p> : !track?.self_enrol_available ? <p className="mt-5 text-xs leading-6 text-slate-500">Self-enrolment is not currently available for this track. Its required courses do not all have an active free-access policy.</p> : !user ? <Link href={"/login?next="+encodeURIComponent("/tracks/"+params.id)} className="mt-5 inline-flex min-h-11 w-full items-center justify-center gap-2 bg-[var(--gold)] px-4 text-sm font-bold text-[#16140f]">Sign in to enrol <ArrowRight size={15}/></Link> : individualLearner ? <button type="button" onClick={()=>void enrol()} disabled={enrolling} className="mt-5 inline-flex min-h-11 w-full items-center justify-center gap-2 bg-[var(--gold)] px-4 text-sm font-bold text-[#16140f] disabled:opacity-50">{enrolling?"Enrolling…":"Enrol in this track"} <ArrowRight size={15}/></button> : user.role==="normal"&&hasOrganisationContext ? <Link href={"/login?next="+encodeURIComponent("/tracks/"+params.id)} className="mt-5 inline-flex min-h-11 w-full items-center justify-center gap-2 border border-white/[.16] px-4 text-sm font-semibold text-slate-200">Switch to individual learning <ArrowRight size={15}/></Link> : <p className="mt-5 text-xs leading-6 text-slate-500">Public track enrolment is for individual learner accounts. Use your organisation's assigned learning access.</p>}
        </div>
      </header>

      {error && <div role="alert" className="notice error mt-5">{error}</div>}

      <section className="mt-10">
        <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="section-kicker">The curriculum</p><h2 className="mt-2 font-display text-3xl">Courses in this track</h2></div><p className="text-xs text-slate-500">{track?.course_count || 0} courses · ordered learning</p></div>
        <div className="mt-6 divide-y divide-white/[.08] border-y border-white/[.08]">
          {(track?.courses || []).map((item:any,index:number) => {
            const saved = progress?.courses?.find((p:any)=>p.course_id===item.course_id);
            const done = Boolean(saved?.progress?.completed);
            return <article key={item.id} className="grid gap-4 py-5 sm:grid-cols-[3rem_minmax(0,1fr)_auto] sm:items-center">
              <div className="grid size-11 place-items-center border border-white/[.1] text-sm tabular-nums text-slate-500">{String(index+1).padStart(2,"0")}</div>
              <div className="min-w-0"><div className="flex flex-wrap items-center gap-3"><h3 className="text-lg font-semibold text-slate-100">{item.course?.title}</h3>{item.required ? <span className="text-[9px] font-bold uppercase tracking-[.15em] gold">Required</span> : <span className="text-[9px] font-semibold uppercase tracking-[.15em] text-slate-500">Optional</span>}</div><p className="mt-2 text-sm leading-6 text-slate-500">{item.course?.short_description || item.course?.level || "Published Learnora course"}</p>{saved?.progress && <p className="mt-2 text-xs text-slate-500">{saved.progress.completed_lessons} of {saved.progress.total_lessons} lessons complete · {saved.progress.progress_percent}%</p>}</div>
              <div className="flex items-center gap-3">{done ? <span className="inline-flex items-center gap-2 text-xs font-semibold text-emerald-300"><CheckCircle2 size={15}/>Completed</span> : saved?.enrolled&&item.course?.status==="published" ? <Link href={"/dashboard/learning/"+encodeURIComponent(item.course?.id)} className="inline-flex min-h-10 items-center gap-2 border border-white/[.14] px-3 text-xs font-semibold text-slate-200 hover:border-[var(--gold)]">Open course <ArrowRight size={14}/></Link> : saved?.enrolled ? <span className="text-xs text-slate-500">Enrolled · course unavailable</span> : <span className="inline-flex items-center gap-2 text-xs text-slate-600"><Circle size={13}/>Not enrolled</span>}</div>
            </article>;
          })}
        </div>
      </section>
      <p className="mt-7 max-w-3xl text-xs leading-6 text-slate-600"><LockKeyhole size={13} className="mr-2 inline"/>Free track enrolment is for individual learner accounts. Organisation and cohort access continues to follow its existing assignment and entitlement rules.</p>
    </main>
    <PublicFooter/>
  </>;
}
