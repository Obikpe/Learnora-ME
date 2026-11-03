"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  ArrowRight, Award, BookOpen, CheckCircle2, Clock3, FileText,
  GraduationCap, RefreshCw, ShieldCheck, Sparkles
} from "lucide-react";
import { currentUser, getCachedCurrentUser } from "../../lib/api";
import { request } from "../../lib/api/client";
import Shell from "../../components/dashboard/Shell";
import EmptyState from "../../components/feedback/EmptyState";
import Skeleton from "../../components/feedback/Skeleton";

type Tab = "in-progress" | "completed" | "skills" | "certificates";

function percent(row: any) {
  if (row?.completed || row?.enrolment?.status === "completed") return 100;
  return Math.max(0, Math.min(100, Math.round(Number(row?.progress_percent) || 0)));
}

function dateLabel(value?: string | null) {
  if (!value) return "Not yet started";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "—" : date.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}

function CourseCard({ row, completed }: { row: any; completed: boolean }) {
  const course = row.course || {};
  const courseId = String(course.id || row.enrolment?.course_id || "");
  const progress = percent(row);
  const next = row.next_item;
  const organisationLabel = course.ownership === "learnora" ? "Learnora ME" : "Organisation course";
  return <article className="group relative grid gap-5 rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5 shadow-[var(--shadow)] transition hover:border-[var(--primary)] sm:grid-cols-[minmax(0,1fr)_minmax(15rem,.9fr)_auto] sm:items-center sm:p-6">
    <div className="min-w-0">
      <div className="mb-2 flex items-center gap-2 text-xs font-semibold text-[var(--text-muted)]">
        <span className="grid size-8 shrink-0 place-items-center rounded-lg border border-[var(--border)] bg-[var(--bg-soft)] text-[var(--primary)]"><GraduationCap size={16}/></span>
        <span>{organisationLabel}</span>
        {completed && <span className="inline-flex items-center gap-1 rounded-full bg-[var(--success-tint)] px-2 py-1 text-[10px] font-bold text-[var(--success)]"><CheckCircle2 size={12}/> Completed</span>}
      </div>
      <h2 className="text-base font-bold leading-6 text-[var(--text-heading)]">{course.title || "Learnora course"}</h2>
      <p className="mt-1 text-xs text-[var(--text-muted)]">
        {completed
          ? "Completed " + dateLabel(row.enrolment?.completed_at)
          : row.enrolment?.status === "active" && !row.last_activity_at
            ? "Enrolled " + dateLabel(row.enrolment?.enrolled_at)
            : "Last activity " + dateLabel(row.last_activity_at || row.enrolment?.enrolled_at)}
      </p>
      <div className="mt-4">
        <div className="mb-2 flex items-center justify-between gap-3 text-xs">
          <span className="text-[var(--text-muted)]">{row.completed_lessons || 0} of {row.total_lessons || 0} lessons completed</span>
          <strong className="tabular-nums text-[var(--text-heading)]">{progress}%</strong>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-[var(--border)]" role="progressbar" aria-label={course.title + " progress"} aria-valuemin={0} aria-valuemax={100} aria-valuenow={progress}>
          <span className="block h-full rounded-full bg-[var(--primary)] transition-all" style={{ width: progress + "%" }}/>
        </div>
      </div>
    </div>
    <div className="flex min-h-[88px] items-center justify-between gap-4 rounded-xl border border-[var(--border)] bg-[var(--bg-soft)] p-4">
      <div className="min-w-0">
        <p className="text-[10px] font-bold uppercase tracking-[.12em] text-[var(--text-muted)]">{completed ? "Course result" : "Pick up where you left off"}</p>
        <p className="mt-2 truncate text-sm font-semibold text-[var(--text-heading)]">{completed ? "All course requirements completed" : next?.title || (progress > 0 ? "Continue your course" : "Start your first lesson")}</p>
        <p className="mt-1 text-xs text-[var(--text-muted)]">{completed ? (row.total_assessments ? (row.completed_assessments || 0) + " of " + row.total_assessments + " assessments passed" : "Lessons completed") : next?.type === "assessment" ? "Assessment to complete" : "Course learning item"}</p>
      </div>
      {completed ? <CheckCircle2 className="shrink-0 text-[var(--success)]" size={21}/> : <BookOpen className="shrink-0 text-[var(--primary)]" size={21}/>}
    </div>
    <Link href={courseId ? "/courses/" + encodeURIComponent(courseId) : "/courses"} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-[var(--on-primary)] transition hover:bg-[var(--primary-hover)]">
      {completed ? "Review course" : progress > 0 ? "Resume" : "Get started"} <ArrowRight size={15}/>
    </Link>
  </article>;
}

export default function MyLearningPage() {
  const [user, setUser] = useState<any>(() => getCachedCurrentUser());
  const [learning, setLearning] = useState<any>(null);
  const [evidence, setEvidence] = useState<any>(null);
  const [credentials, setCredentials] = useState<any>(null);
  const [tab, setTab] = useState<Tab>("in-progress");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [evidenceUnavailable, setEvidenceUnavailable] = useState(false);
  const [credentialsUnavailable, setCredentialsUnavailable] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  async function load() {
    setRefreshing(true);
    setError("");
    const [p, e, c] = await Promise.allSettled([
      request<any>("/progress/me"),
      request<any>("/evidence/me"),
      request<any>("/credentials/me"),
    ]);
    if (p.status === "fulfilled") setLearning(p.value);
    else setError("Your course enrolments and completion records could not be loaded. Please try again.");
    setEvidenceUnavailable(e.status !== "fulfilled");
    setCredentialsUnavailable(c.status !== "fulfilled");
    if (e.status === "fulfilled") setEvidence(e.value);
    if (c.status === "fulfilled") setCredentials(c.value);
    setLoading(false);
    setRefreshing(false);
  }

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
      const privileged = (me.organisation_memberships || []).filter((membership: any) => ["owner", "admin"].includes(membership.role));
      if (me.organisation_id && ["owner", "admin"].includes(me.organisation_role)) { location.href = "/dashboard/organisation"; return; }
      if (privileged.length) { location.href = "/dashboard/organisation" + (privileged.length > 1 && !me.organisation_id ? "?choose=1" : ""); return; }
      if (cancelled) return;
      setUser(me);
      await load();
    }).catch(() => { if (!cancelled) location.href = "/login"; });
    return () => { cancelled = true; };
  }, []);

  const courses = learning?.courses || [];
  const inProgress = useMemo(() => courses.filter((row: any) => !(row.completed || row.enrolment?.status === "completed")), [courses]);
  const completed = useMemo(() => courses.filter((row: any) => row.completed || row.enrolment?.status === "completed"), [courses]);
  const completedLessons = courses.reduce((sum: number, row: any) => sum + Number(row.completed_lessons || 0), 0);
  const totalLessons = courses.reduce((sum: number, row: any) => sum + Number(row.total_lessons || 0), 0);
  const certificates = credentials?.certificates || [];
  const skills = evidence?.skills || [];
  const verifiedEvidence = (evidence?.evidence || []).filter((row: any) => row.verification_state === "verified").length;
  const recentCertificates = certificates.slice(0, 3);

  if (!user || loading) return <Shell active="learning"><Skeleton label="Loading your learning records"/></Shell>;

  const tabs: { id: Tab; label: string; count?: number }[] = [
    { id: "in-progress", label: "In Progress", count: inProgress.length },
    { id: "completed", label: "Completed", count: completed.length },
    { id: "skills", label: "Skills", count: skills.length },
    { id: "certificates", label: "Certificates", count: certificates.length },
  ];

  return <Shell active="learning">
    <section className="flex flex-wrap items-start justify-between gap-6 pb-7">
      <div className="flex min-w-0 items-start gap-4">
        <div className="grid size-14 shrink-0 place-items-center rounded-full bg-[var(--primary)] text-xl font-bold text-[var(--on-primary)] sm:size-16 sm:text-2xl" aria-hidden="true">
          {(user.name || user.email || "L").trim().charAt(0).toUpperCase()}
        </div>
        <div className="min-w-0">
          <p className="text-xs font-bold uppercase tracking-[.14em] text-[var(--primary)]">Your learning workspace</p>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-[var(--text-heading)] sm:text-3xl">My Learning{user.name ? ", " + user.name.split(" ")[0] : ""}</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-muted)]">Your enrolled courses, learning progress and completed achievements, all in one place.</p>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <button type="button" onClick={() => void load()} disabled={refreshing} className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-[var(--border)] px-3 py-2 text-xs font-semibold text-[var(--text-body)] hover:bg-[var(--bg-soft)] disabled:opacity-50">
          <RefreshCw size={14} className={refreshing ? "animate-spin" : ""}/> Refresh
        </button>
        <Link href="/courses" className="inline-flex min-h-10 items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 text-xs font-semibold text-[var(--on-primary)] hover:bg-[var(--primary-hover)]">
          Explore courses <ArrowRight size={14}/>
        </Link>
      </div>
    </section>

    {error && <div role="alert" className="mb-6 rounded-xl border border-[var(--warning)]/30 bg-[var(--warning-tint)] p-4 text-sm text-[var(--warning)]">{error}</div>}

    <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4" aria-label="Learning summary">
      <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4"><p className="text-xs text-[var(--text-muted)]">Enrolled courses</p><p className="mt-2 text-2xl font-bold tabular-nums text-[var(--text-heading)]">{courses.length}</p></div>
      <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4"><p className="text-xs text-[var(--text-muted)]">In progress</p><p className="mt-2 text-2xl font-bold tabular-nums text-[var(--text-heading)]">{inProgress.length}</p></div>
      <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4"><p className="text-xs text-[var(--text-muted)]">Courses completed</p><p className="mt-2 text-2xl font-bold tabular-nums text-[var(--success)]">{completed.length}</p></div>
      <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4"><p className="text-xs text-[var(--text-muted)]">Lessons completed</p><p className="mt-2 text-2xl font-bold tabular-nums text-[var(--text-heading)]">{completedLessons}<span className="ml-1 text-sm font-medium text-[var(--text-muted)]">/ {totalLessons}</span></p></div>
    </section>

    <div className="mt-8 flex gap-6 overflow-x-auto border-b border-[var(--border)]" role="tablist" aria-label="My learning sections">
      {tabs.map(item => <button key={item.id} type="button" role="tab" aria-selected={tab === item.id} onClick={() => setTab(item.id)}
        className={"-mb-px inline-flex shrink-0 items-center gap-2 border-b-2 px-1 pb-3 pt-2 text-sm transition " + (tab === item.id ? "border-[var(--primary)] font-bold text-[var(--text-heading)]" : "border-transparent text-[var(--text-muted)] hover:text-[var(--primary)]")}>
        {item.label}<span className={"rounded-full px-2 py-0.5 text-[10px] tabular-nums " + (tab === item.id ? "bg-[var(--primary-tint)] text-[var(--primary)]" : "bg-[var(--bg-soft)] text-[var(--text-muted)]")}>{item.count}</span>
      </button>)}
    </div>

    <div className="mt-6 grid items-start gap-7 xl:grid-cols-[minmax(0,1fr)_19rem]">
      <section className="min-w-0" role="tabpanel">
        {tab === "in-progress" && (inProgress.length
          ? <div className="space-y-4">{inProgress.map((row: any) => <CourseCard key={row.enrolment?.id || row.course?.id} row={row} completed={false}/>)}</div>
          : <EmptyState title="No courses in progress" message="Courses you enrol in will appear here. Choose a course and start learning whenever you are ready." action={<Link href="/courses" className="rounded-lg bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-[var(--on-primary)]">Explore courses</Link>}/>)}
        {tab === "completed" && (completed.length
          ? <div className="space-y-4">{completed.map((row: any) => <CourseCard key={row.enrolment?.id || row.course?.id} row={row} completed/>)}</div>
          : <EmptyState title="No completed courses yet" message="When you finish all published lessons and required assessments, the course will move here." action={<Link href="/courses" className="rounded-lg bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-[var(--on-primary)]">Explore courses</Link>}/>)}
        {tab === "skills" && <section>
          <div className="mb-4 flex items-center justify-between gap-3"><div><h2 className="text-lg font-bold text-[var(--text-heading)]">Your skills</h2><p className="mt-1 text-xs text-[var(--text-muted)]">Skills are based on reviewed evidence, not simply on course enrolment.</p></div><Link href="/dashboard/skills" className="text-xs font-semibold text-[var(--primary)]">View skill map <ArrowRight size={13} className="inline"/></Link></div>
          {evidenceUnavailable ? <p role="alert" className="rounded-xl border border-[var(--warning)]/30 bg-[var(--warning-tint)] p-4 text-sm text-[var(--warning)]">Your skill records could not be loaded. Refresh to try again.</p> : skills.length ? <div className="grid gap-3 md:grid-cols-2">{skills.map((skill: any) => <article key={skill.skill_id || skill.id} className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4"><div className="flex items-start justify-between gap-3"><div><h3 className="font-semibold text-[var(--text-heading)]">{skill.skill_name || skill.name}</h3><p className="mt-1 text-xs text-[var(--text-muted)]">{skill.category || "Skill"}</p></div><span className="text-xs capitalize text-[var(--text-muted)]">{String(skill.status || "not_started").replaceAll("_", " ")}</span></div><div className="mt-4 h-2 overflow-hidden rounded-full bg-[var(--border)]"><div className="h-full rounded-full bg-[var(--primary)]" style={{ width: Math.max(0, Math.min(100, Number(skill.proficiency) || 0)) + "%" }}/></div><p className="mt-2 text-[11px] text-[var(--text-muted)]">{skill.verified_evidence_count || 0} verified evidence items · {Number(skill.proficiency) || 0}%</p></article>)}</div> : <EmptyState title="No skills earned yet" message="As your work is reviewed and mapped to skills, verified achievements will appear here."/>}
          <p className="mt-4 text-xs text-[var(--text-muted)]">{verifiedEvidence} verified evidence records currently support your skill profile.</p>
        </section>}
        {tab === "certificates" && <section>
          <div className="mb-4 flex items-center justify-between gap-3"><div><h2 className="text-lg font-bold text-[var(--text-heading)]">Your certificates</h2><p className="mt-1 text-xs text-[var(--text-muted)]">Only certificates issued and saved to your account appear here.</p></div><Link href="/dashboard/certificates" className="text-xs font-semibold text-[var(--primary)]">Manage certificates <ArrowRight size={13} className="inline"/></Link></div>
          {credentialsUnavailable ? <p role="alert" className="rounded-xl border border-[var(--warning)]/30 bg-[var(--warning-tint)] p-4 text-sm text-[var(--warning)]">Your certificate records could not be loaded. Refresh to try again.</p> : certificates.length ? <div className="space-y-3">{certificates.map((cert: any) => <article key={cert.id} className="flex items-center gap-3 rounded-xl border border-[var(--border)] bg-[var(--card)] p-4"><span className="grid size-10 shrink-0 place-items-center rounded-lg bg-[var(--primary-tint)] text-[var(--primary)]"><Award size={19}/></span><div className="min-w-0 flex-1"><h3 className="truncate text-sm font-semibold text-[var(--text-heading)]">{cert.course_title}</h3><p className="mt-1 text-xs text-[var(--text-muted)]">Issued {dateLabel(cert.issued_at)} · {cert.valid === false ? "Revoked" : "Valid"}</p></div><Link href={cert.verification_url || "/dashboard/certificates"} className="shrink-0 text-xs font-semibold text-[var(--primary)]">View</Link></article>)}</div> : <EmptyState title="No certificates issued yet" message="Complete a course and meet its published assessment requirements to become eligible." action={<Link href="/dashboard/certificates" className="rounded-lg border border-[var(--border)] px-4 py-2.5 text-sm font-semibold">View certificate requirements</Link>}/>}
        </section>}
      </section>

      <aside className="space-y-4">
        <section className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--card)]">
          <div className="p-5"><div className="flex items-center gap-2"><Clock3 size={17} className="text-[var(--primary)]"/><h2 className="text-sm font-bold text-[var(--text-heading)]">Learning overview</h2></div>
            <div className="mt-5 grid grid-cols-2 gap-4"><div><p className="text-2xl font-bold tabular-nums text-[var(--text-heading)]">{inProgress.length}</p><p className="mt-1 text-xs text-[var(--text-muted)]">In progress</p></div><div><p className="text-2xl font-bold tabular-nums text-[var(--success)]">{completed.length}</p><p className="mt-1 text-xs text-[var(--text-muted)]">Completed</p></div><div><p className="text-2xl font-bold tabular-nums text-[var(--text-heading)]">{completedLessons}</p><p className="mt-1 text-xs text-[var(--text-muted)]">Lessons completed</p></div><div><p className="text-2xl font-bold tabular-nums text-[var(--text-heading)]">{certificates.length}</p><p className="mt-1 text-xs text-[var(--text-muted)]">Certificates</p></div></div>
          </div>
          <div className="border-t border-[var(--border)] p-5"><h3 className="text-sm font-bold text-[var(--text-heading)]">Keep learning</h3><p className="mt-2 text-xs leading-5 text-[var(--text-muted)]">Your enrolled courses stay here, including courses you have registered for but have not started yet.</p><Link href="/courses" className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-[var(--primary)]">Explore the catalogue <ArrowRight size={13}/></Link></div>
        </section>

        <section className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
          <div className="flex items-center justify-between gap-2"><h2 className="text-sm font-bold text-[var(--text-heading)]">Recent certificates</h2><Award size={17} className="text-[var(--primary)]"/></div>
          {credentialsUnavailable ? <p className="mt-3 text-xs leading-5 text-[var(--warning)]">Certificate records are temporarily unavailable.</p> : recentCertificates.length ? <div className="mt-4 space-y-4">{recentCertificates.map((cert: any) => <div key={cert.id} className="flex items-start gap-3"><span className="grid size-8 shrink-0 place-items-center rounded-md border border-[var(--border)] bg-[var(--bg-soft)] text-[var(--primary)]"><FileText size={15}/></span><div className="min-w-0"><p className="text-xs font-semibold leading-5 text-[var(--text-heading)]">{cert.course_title}</p><p className="mt-1 text-[11px] text-[var(--text-muted)]">{dateLabel(cert.issued_at)}</p></div></div>)}</div> : <p className="mt-3 text-xs leading-5 text-[var(--text-muted)]">Certificates will appear here once they have been issued.</p>}
          <Link href="/dashboard/certificates" className="mt-4 inline-flex items-center gap-1 text-xs font-semibold text-[var(--primary)]">View certificates <ArrowRight size={13}/></Link>
        </section>

        <section className="rounded-xl border border-[var(--border)] bg-[var(--bg-soft)] p-5">
          <div className="flex items-center gap-2"><ShieldCheck size={17} className="text-[var(--success)]"/><h2 className="text-sm font-bold text-[var(--text-heading)]">How completion works</h2></div>
          <p className="mt-2 text-xs leading-5 text-[var(--text-muted)]">A course moves to Completed only when its published lessons and required assessments have been completed and the backend confirms the result.</p>
        </section>
      </aside>
    </div>
  </Shell>;
}
