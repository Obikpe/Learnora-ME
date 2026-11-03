"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  ArrowRight, BookOpen, CheckCircle2, Compass, Clock3, FileCheck2,
  Sparkles, Users, CalendarDays, Route, GraduationCap
} from "lucide-react";
import { currentUser, getCachedCurrentUser } from "../../lib/api";
import { progress, evidence } from "../../lib/api/learning";
import { request } from "../../lib/api/client";
import Shell from "../../components/dashboard/Shell";
import StatCard from "../../components/dashboard/StatCard";
import EmptyState from "../../components/feedback/EmptyState";
import Skeleton from "../../components/feedback/Skeleton";

function courseProgress(row: any) {
  const direct = Number(row?.progress_percent ?? row?.progress?.progress_percent);
  if (Number.isFinite(direct) && direct > 0) return Math.min(100, Math.round(direct));
  const total = Number(row?.tracked_lessons ?? row?.progress?.total_lessons ?? 0);
  const complete = Number(row?.completed_lessons ?? row?.progress?.completed_lessons ?? 0);
  return total > 0 ? Math.min(100, Math.round(complete / total * 100)) : 0;
}

export default function Page() {
  const [u, setU] = useState<any>(() => getCachedCurrentUser());
  const [learning, setLearning] = useState<any>(null);
  const [record, setRecord] = useState<any>(null);
  const [teams, setTeams] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    currentUser().then(async me => {
      if (me.role === "organisation_prospect") { location.href = "/organisation-portal"; return; }
      if (me.role === "witstart") { location.href = "/dashboard/witstart"; return; }
      if (me.role === "normal") {
        try {
          const onboarding = await request<any>("/learner/onboarding");
          if (!onboarding.completed) { location.href = "/onboarding"; return; }
        } catch {}
      }
      const privileged = (me.organisation_memberships || []).filter((membership: any) =>
        ["owner", "admin"].includes(membership.role)
      );
      if (me.organisation_id && ["owner", "admin"].includes(me.organisation_role)) {
        location.href = "/dashboard/organisation";
        return;
      }
      if (privileged.length) {
        location.href = "/dashboard/organisation" + (privileged.length > 1 && !me.organisation_id ? "?choose=1" : "");
        return;
      }
      if (cancelled) return;
      setU(me);
      const [p, e, r] = await Promise.allSettled([
        progress(), evidence(), request<any>("/learner/recommendations")
      ]);
      if (cancelled) return;
      let failed = false;
      if (p.status === "fulfilled") setLearning(p.value);
      else failed = true;
      if (e.status === "fulfilled") setRecord(e.value);
      else failed = true;
      if (r.status === "fulfilled") setRecommendations(r.value);
      if (failed) setErr("Some learning records are temporarily unavailable. Please try again shortly.");
      setLoading(false);
      request<any>("/organisations/my-teams").then(result => {
        if (!cancelled) setTeams(result.teams || []);
      }).catch(() => { if (!cancelled) setTeams([]); });
    }).catch(() => { if (!cancelled) location.href = "/login"; });
    return () => { cancelled = true; };
  }, []);

  const enrolled = learning?.courses || [];
  const completedLessons = useMemo(
    () => enrolled.reduce((count: number, row: any) => count + Number(row.completed_lessons || 0), 0),
    [enrolled]
  );
  const trackedLessons = useMemo(
    () => enrolled.reduce((count: number, row: any) => count + Number(row.tracked_lessons || 0), 0),
    [enrolled]
  );
  const evidenceRows = record?.evidence || [];
  const recommendationRows = [
    ...(recommendations?.recommended || []),
    ...(recommendations?.other_courses || [])
  ].slice(0, 6);
  const currentRow = enrolled[0];
  const currentCourse = currentRow?.course || {};
  const currentPercent = courseProgress(currentRow);

  if (!u || loading) return <Shell active="overview"><Skeleton label="Preparing your learning workspace"/></Shell>;

  return <Shell active="overview">
    <section className="relative overflow-hidden rounded-3xl border border-[var(--border)] bg-[var(--hero-bg)] px-5 py-7 sm:px-8 sm:py-9">
      <div aria-hidden="true" className="pointer-events-none absolute -right-20 -top-48 size-[28rem] rounded-full bg-[var(--hero-shape)] opacity-70"/>
      <div aria-hidden="true" className="pointer-events-none absolute right-36 -top-32 size-72 rounded-full bg-[var(--hero-shape)] opacity-40"/>
      <div className="relative z-10">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-[.14em] text-[var(--primary)]">Your learning workspace</p>
            <h1 className="mt-2 text-2xl font-bold tracking-tight text-[var(--text-heading)] sm:text-3xl">
              Welcome back{u.name ? ", " + u.name.split(" ")[0] : ""}.
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-body)]">
              Pick up where you left off, explore something new and keep building your skills.
            </p>
          </div>
          <Link href="/courses" className="inline-flex min-h-11 items-center gap-2 rounded-lg bg-[var(--accent)] px-4 py-2.5 text-sm font-bold text-[var(--on-accent)] transition hover:bg-[var(--accent-hover)]">
            Explore courses <ArrowRight size={16}/>
          </Link>
        </div>

        <div className="mt-7 grid gap-4 lg:grid-cols-[minmax(0,1fr)_18rem]">
          <article className="grid min-h-64 overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--card)] shadow-[var(--shadow)] sm:grid-cols-[.9fr_1.1fr]">
            <div className="flex flex-col justify-between p-5 sm:p-6">
              <div>
                <p className="text-xs font-semibold text-[var(--primary)]">Pick up your learning</p>
                {currentCourse.id ? <>
                  <h2 className="mt-3 text-xl font-bold leading-snug text-[var(--text-heading)]">{currentCourse.title || "Your course"}</h2>
                  <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">
                    {currentRow.completed_lessons || 0} of {currentRow.tracked_lessons || 0} tracked lessons completed
                  </p>
                </> : <>
                  <h2 className="mt-3 text-xl font-bold leading-snug text-[var(--text-heading)]">Your next learning step starts here.</h2>
                  <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">Explore the course catalogue and choose a subject you want to develop.</p>
                </>}
              </div>
              <div className="mt-6">
                {currentCourse.id ? <>
                  <div className="mb-2 flex items-center justify-between gap-3 text-xs">
                    <span className="text-[var(--text-muted)]">Course progress</span>
                    <strong className="tabular-nums text-[var(--text-heading)]">{currentPercent}%</strong>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-[var(--border)]">
                    <span className="block h-full rounded-full bg-[var(--success)]" style={{ width: currentPercent + "%" }}/>
                  </div>
                  <Link href={"/dashboard/learning/" + currentCourse.id} className="mt-5 inline-flex min-h-10 items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-[var(--on-primary)] hover:bg-[var(--primary-hover)]">
                    Resume learning <ArrowRight size={15}/>
                  </Link>
                </> : <Link href="/courses" className="mt-5 inline-flex min-h-10 items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-[var(--on-primary)] hover:bg-[var(--primary-hover)]">
                  Browse courses <ArrowRight size={15}/>
                </Link>}
              </div>
            </div>
            <div className="relative flex min-h-48 items-center justify-center overflow-hidden bg-[var(--primary-tint)] p-6">
              {currentCourse.thumbnail_url
                ? <img src={currentCourse.thumbnail_url} alt="" className="absolute inset-0 h-full w-full object-cover"/>
                : <svg viewBox="0 0 440 260" role="img" aria-label="Abstract learning progress illustration" className="h-full w-full max-w-lg">
                    <g stroke="var(--primary)" strokeOpacity=".18" strokeWidth="1"><path d="M0 52H440M0 104H440M0 156H440M0 208H440"/><path d="M55 0V260M125 0V260M195 0V260M265 0V260M335 0V260M405 0V260"/></g>
                    <path d="M0 205 C45 195 60 160 100 174 S160 120 205 139 S270 75 310 102 S375 42 440 30" fill="none" stroke="var(--primary)" strokeWidth="4" strokeLinecap="round"/>
                    <path d="M0 205 C45 195 60 160 100 174 S160 120 205 139 S270 75 310 102 S375 42 440 30 L440 260H0Z" fill="var(--primary)" fillOpacity=".10"/>
                    <circle cx="310" cy="102" r="7" fill="var(--accent)" stroke="var(--card)" strokeWidth="4"/>
                    <circle cx="440" cy="30" r="7" fill="var(--primary)" stroke="var(--card)" strokeWidth="4"/>
                  </svg>}
              <div className="absolute bottom-4 left-4 rounded-lg border border-[var(--border)] bg-[var(--card)]/90 px-3 py-2 text-xs font-semibold text-[var(--text-heading)] shadow-[var(--shadow)]">
                {currentCourse.id ? "Continue your course" : "Learn at your own pace"}
              </div>
            </div>
          </article>

          <aside className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-4 shadow-[var(--shadow)]">
              <div className="flex items-center gap-2 text-sm font-semibold text-[var(--text-heading)]"><CheckCircle2 size={17} className="text-[var(--success)]"/> Your learning activity</div>
              <div className="mt-4 flex items-end justify-between gap-3">
                <div><p className="text-3xl font-bold tabular-nums text-[var(--text-heading)]">{completedLessons}</p><p className="mt-1 text-xs text-[var(--text-muted)]">Lessons completed</p></div>
                <div className="text-right"><p className="text-2xl font-semibold tabular-nums text-[var(--text-heading)]">{evidenceRows.length}</p><p className="mt-1 text-xs text-[var(--text-muted)]">Evidence records</p></div>
              </div>
            </div>
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-4 shadow-[var(--shadow)]">
              <div className="flex items-center gap-2 text-sm font-semibold text-[var(--text-heading)]"><Route size={17} className="text-[var(--primary)]"/> Learning tracks</div>
              <p className="mt-2 text-xs leading-5 text-[var(--text-muted)]">Keep your courses organised around a structured learning journey.</p>
              <Link href="/dashboard/tracks" className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-[var(--primary)] hover:text-[var(--primary-hover)]">View my tracks <ArrowRight size={13}/></Link>
            </div>
          </aside>
        </div>
      </div>
    </section>

    {err && <div role="status" className="mt-6 rounded-xl border border-[var(--warning)]/30 bg-[var(--warning-tint)] p-4 text-sm text-[var(--warning)]">
      <p>{err}</p><button type="button" onClick={() => location.reload()} className="mt-2 font-semibold underline underline-offset-4">Try again</button>
    </div>}

    <section className="mt-7 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Enrolled courses" value={enrolled.length}/>
      <StatCard label="Lessons completed" value={completedLessons}/>
      <StatCard label="Lessons tracked" value={trackedLessons}/>
      <StatCard label="Evidence records" value={evidenceRows.length}/>
    </section>

    {enrolled.length > 1 && <section className="mt-10">
      <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div><p className="text-xs font-semibold uppercase tracking-[.12em] text-[var(--primary)]">Keep going</p><h2 className="mt-1 text-xl font-bold text-[var(--text-heading)]">Your courses</h2></div>
        
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        {enrolled.slice(1, 5).map((row: any) => {
          const course = row.course || {};
          const percent = courseProgress(row);
          return <Link key={row.enrolment?.id || course.id} href={"/dashboard/learning/" + course.id}
            className="group flex items-center gap-4 rounded-xl border border-[var(--border)] bg-[var(--card)] p-4 shadow-[var(--shadow)] transition hover:border-[var(--primary)]">
            <span className="grid size-11 shrink-0 place-items-center rounded-lg bg-[var(--primary-tint)] text-[var(--primary)]"><BookOpen size={19}/></span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-sm font-semibold text-[var(--text-heading)]">{course.title || "Enrolled course"}</span>
              <span className="mt-1 block text-xs text-[var(--text-muted)]">{row.completed_lessons || 0} of {row.tracked_lessons || 0} tracked lessons</span>
              <span className="mt-2 block h-1.5 overflow-hidden rounded-full bg-[var(--border)]"><span className="block h-full rounded-full bg-[var(--success)]" style={{ width: percent + "%" }}/></span>
            </span>
            <ArrowRight size={16} className="shrink-0 text-[var(--text-muted)] transition group-hover:text-[var(--primary)]"/>
          </Link>;
        })}
      </div>
    </section>}

    <section className="mt-10">
      <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div><p className="text-xs font-semibold uppercase tracking-[.12em] text-[var(--primary)]">A useful next step</p><h2 className="mt-1 text-xl font-bold text-[var(--text-heading)]">Recommended for you</h2><p className="mt-1 text-sm text-[var(--text-muted)]">Courses selected from your learning preferences and available catalogue.</p></div>
        <Link href="/courses" className="inline-flex items-center gap-1 text-xs font-semibold text-[var(--primary)]">Explore all courses <ArrowRight size={14}/></Link>
      </div>
      {recommendations ? recommendationRows.length ? <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {recommendationRows.map((item: any) => {
          const course = item.course || {};
          return <Link key={course.id} href={"/courses/" + course.id} className="group flex min-h-64 flex-col overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-[var(--shadow)] transition hover:-translate-y-0.5 hover:border-[var(--primary)]">
            <div className="relative flex h-28 items-center justify-center overflow-hidden bg-[var(--primary-tint)]">
              {course.thumbnail_url ? <img src={course.thumbnail_url} alt="" className="absolute inset-0 h-full w-full object-cover"/> : <GraduationCap size={34} className="text-[var(--primary)]"/>}
              {course.level && <span className="absolute left-3 top-3 rounded-full border border-[var(--border)] bg-[var(--card)]/90 px-3 py-1 text-[10px] font-semibold capitalize text-[var(--text-body)]">{course.level}</span>}
            </div>
            <div className="flex flex-1 flex-col p-4">
              <h3 className="font-semibold leading-6 text-[var(--text-heading)] group-hover:text-[var(--primary)]">{course.title || "Learnora course"}</h3>
              <p className="mt-2 line-clamp-3 flex-1 text-xs leading-5 text-[var(--text-muted)]">{course.short_description || item.reason || "Explore the course curriculum and learning outcomes."}</p>
              <div className="mt-4 flex items-center justify-between gap-3 border-t border-[var(--border)] pt-3">
                <span className="text-[11px] text-[var(--text-muted)]">{item.reason || "Suggested for you"}</span>
                <span className="inline-flex shrink-0 items-center gap-1 text-xs font-semibold text-[var(--primary)]">{course.estimated_hours != null && <><Clock3 size={12}/>{course.estimated_hours}h</>}<ArrowRight size={14}/></span>
              </div>
            </div>
          </Link>;
        })}
      </div> : <EmptyState title="No recommendations yet" message="Browse the catalogue to find a course that matches what you want to learn." action={<Link href="/courses" className="rounded-lg bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-[var(--on-primary)]">Explore courses</Link>}/>
      : <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5 text-sm text-[var(--text-muted)]">Recommendations are temporarily unavailable. You can still explore all published courses.</div>}
    </section>

    {teams.length > 0 && <section className="mt-10 rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5 shadow-[var(--shadow)] sm:p-6">
      <div className="flex items-center justify-between gap-3"><div><h2 className="text-lg font-bold text-[var(--text-heading)]">Your organisation teams</h2><p className="mt-1 text-sm text-[var(--text-muted)]">Open a team workspace to continue collaborating.</p></div><Users size={20} className="text-[var(--primary)]"/></div>
      <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {teams.map((team: any) => <Link key={team.id} href={"/dashboard/team/" + team.id} className="rounded-xl border border-[var(--border)] bg-[var(--bg-soft)] p-4 transition hover:border-[var(--primary)]">
          <div className="flex items-start justify-between gap-3"><p className="font-semibold text-[var(--text-heading)]">{team.name}</p><span className="rounded-full bg-[var(--primary-tint)] px-2 py-1 text-[10px] capitalize text-[var(--primary)]">{team.membership?.role || "member"}</span></div>
          <p className="mt-2 text-xs leading-5 text-[var(--text-muted)]">{team.description || "Organisation team"}</p>
          <span className="mt-4 inline-flex items-center gap-2 text-xs font-semibold text-[var(--primary)]">Open team <ArrowRight size={13}/></span>
        </Link>)}
      </div>
    </section>}

    <section className="mt-8 flex items-start gap-3 rounded-xl border border-[var(--border)] bg-[var(--bg-soft)] p-4">
      <FileCheck2 className="mt-0.5 shrink-0 text-[var(--primary)]" size={17}/>
      <p className="text-xs leading-6 text-[var(--text-muted)]">Your learning activity and evidence are kept together so you can review what you have completed and the work you have submitted.</p>
    </section>
  </Shell>;
}
