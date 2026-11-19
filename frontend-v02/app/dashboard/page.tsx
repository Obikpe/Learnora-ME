"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { ArrowRight, Award, BookOpen, CheckCircle2, Clock3, FileText, GraduationCap } from "lucide-react";
import { currentUser, getCachedCurrentUser } from "../../lib/api";
import { request } from "../../lib/api/client";
import Shell from "../../components/dashboard/Shell";
import Skeleton from "../../components/feedback/Skeleton";
import LearnerAssistant from "../../components/dashboard/LearnerAssistant";

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

function apiErrorStatus(error: unknown): number {
  return typeof error === "object" && error !== null && "status" in error
    ? Number((error as { status?: unknown }).status || 0)
    : 0;
}

async function loadCoreProgress() {
  let lastError: unknown;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      return await request<Record<string, unknown>>("/progress/me");
    } catch (error: unknown) {
      lastError = error;
      const status = apiErrorStatus(error);
      const transient = !status || [429, 500, 502, 503, 504].includes(status);
      if (!transient || attempt === 2) break;
      await new Promise(resolve => window.setTimeout(resolve, attempt === 0 ? 350 : 900));
    }
  }
  throw lastError;
}

function CourseCard({ row, completed }: { row: any; completed: boolean }) {
  const course = row.course || {};
  const courseId = String(course.id || row.enrolment?.course_id || "");
  const progress = percent(row);
  const next = row.next_item;
  return <article className="grid gap-4 rounded-xl border border-[var(--border)] bg-[var(--card)] p-5 sm:grid-cols-[minmax(0,1fr)_minmax(13rem,.8fr)_auto] sm:items-center">
    <div className="min-w-0">
      <div className="mb-2 flex items-center gap-2 text-xs text-[var(--text-muted)]">
        <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-[var(--bg-soft)] text-[var(--primary)]"><GraduationCap size={16}/></span>
        <span>{course.ownership === "learnora" ? "Learnora ME" : "Organisation course"}</span>
        {completed && <span className="inline-flex items-center gap-1 rounded-md bg-[var(--success-tint)] px-2 py-1 text-[10px] font-semibold text-[var(--success)]"><CheckCircle2 size={12}/> Completed</span>}
      </div>
      <h2 className="text-base font-bold leading-6 text-[var(--text-heading)]">{course.title || "Learnora course"}</h2>
      <p className="mt-1 text-xs text-[var(--text-muted)]">{completed ? "Completed " + dateLabel(row.enrolment?.completed_at) : "Enrolled " + dateLabel(row.enrolment?.enrolled_at)}</p>
      <div className="mt-4">
        <div className="mb-1.5 flex items-center justify-between text-[11px]"><span className="text-[var(--text-muted)]">Course progress</span><span className="font-semibold tabular-nums text-[var(--text-heading)]">{progress}%</span></div>
        <div className="h-2 overflow-hidden rounded-full bg-[var(--bg-soft)]" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={progress}><span className="block h-full rounded-full bg-[var(--primary)]" style={{ width: progress + "%" }}/></div>
        <p className="mt-2 text-[11px] text-[var(--text-muted)]">{row.completed_lessons || 0} of {row.total_lessons || 0} lessons completed</p>
      </div>
    </div>
    <div className="flex min-h-[76px] items-center justify-between gap-3 rounded-lg bg-[var(--bg-soft)] p-4">
      <div className="min-w-0">
        <p className="text-[10px] font-semibold uppercase tracking-wide text-[var(--text-muted)]">{completed ? "Course result" : "Next learning item"}</p>
        <p className="mt-1.5 truncate text-sm font-semibold text-[var(--text-heading)]">{completed ? "Course completed" : next?.title || (progress > 0 ? "Continue your course" : "Start your first lesson")}</p>
        {!completed && <p className="mt-1 text-[11px] text-[var(--text-muted)]">{next?.type === "assessment" ? "Assessment" : "Course lesson"}</p>}
      </div>
      {completed ? <CheckCircle2 size={20} className="shrink-0 text-[var(--success)]"/> : <BookOpen size={20} className="shrink-0 text-[var(--primary)]"/>}
    </div>
    <Link href={courseId ? "/courses/" + encodeURIComponent(courseId) : "/courses"} className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-[var(--on-primary)] hover:bg-[var(--primary-hover)]">
      {completed ? "Review course" : progress > 0 ? "Resume" : "Get started"} <ArrowRight size={14}/>
    </Link>
  </article>;
}

function RecommendedCourseCard({ course }: { course: any }) {
  const id = String(course.id || "");
  const free = course.settings?.is_free === true || course.settings?.access_type === "free";
  const href = "/courses/" + encodeURIComponent(id) + (free ? "?enrol=1" : "");
  return <article className="flex min-w-0 flex-col rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
    {course.thumbnail_url && <Image unoptimized src={course.thumbnail_url} alt="" width={640} height={360} sizes="(max-width: 768px) 100vw, 50vw" loading="lazy" className="mb-4 aspect-[16/9] w-full rounded-lg object-cover"/>}
    <p className="text-[10px] font-semibold uppercase tracking-wide text-[var(--primary)]">{course.level || "Course"}</p>
    <h3 className="mt-2 text-sm font-bold leading-5 text-[var(--text-heading)]">{course.title}</h3>
    <p className="mt-2 line-clamp-3 flex-1 text-xs leading-5 text-[var(--text-muted)]">{course.short_description || course.description || ""}</p>
    <div className="mt-3 flex items-center justify-between gap-2">
      {course.estimated_hours ? <span className="text-[11px] text-[var(--text-muted)]">{course.estimated_hours} hours</span> : <span/>}
      <Link href={href} className="inline-flex items-center gap-1 text-xs font-semibold text-[var(--primary)]">{free ? "Enrol for free" : "View course"} <ArrowRight size={13}/></Link>
    </div>
  </article>;
}

export default function MyLearningPage() {
  const [user, setUser] = useState<any>(() => getCachedCurrentUser());
  const [learning, setLearning] = useState<any>(null);
  const [activitySummary, setActivitySummary] = useState<any>(null);
  const [learningPlan, setLearningPlan] = useState<any>(null);
  const [evidence, setEvidence] = useState<any>({ skills: [], evidence: [] });
  const [credentials, setCredentials] = useState<any>({ certificates: [] });
  const [catalogue, setCatalogue] = useState<any[]>([]);
  const [catalogueLoading, setCatalogueLoading] = useState(false);
  const [goal, setGoal] = useState("");
  const [tab, setTab] = useState<Tab>("in-progress");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [certificateError, setCertificateError] = useState(false);
  const [evidenceError, setEvidenceError] = useState(false);

  const load = useCallback(async (me?: any) => {
    setError("");
    const progressResult = await Promise.allSettled([
      loadCoreProgress(),
    ]);
    const progressResponse = progressResult[0];
    const progressLoaded = progressResponse.status === "fulfilled";
    const progressData = progressLoaded ? progressResponse.value : null;

    if (progressData) {
      setLearning(progressData);
      setError("");
    } else {
      // Keep the last successful dashboard data when a refresh fails transiently.
      const failure = (progressResponse as PromiseRejectedResult).reason as (Error & { status?: number }) | undefined;
      if (failure?.status === 401) {
        if (typeof window !== "undefined") window.location.replace("/login");
        return;
      }
      setError("Your learning records are temporarily unavailable. We are reconnecting automatically.");
    }

    // The core learning view should not wait for optional summary, plan,
    // recommendations, evidence or certificate requests.
    setLoading(false);

    const hasOrganisationMembership = (me?.organisation_memberships || []).some((membership:any) => membership.status === "active");
    const assignedOnlyAccount = Boolean(
      me?.account_type === "cohort" ||
      me?.role === "witstart" ||
      me?.cohort_id ||
      me?.organisation_id ||
      me?.organisation_role ||
      (me?.organisation_memberships || []).some((membership:any) =>
        ["learner", "member"].includes(membership.role) && membership.status === "active"
      )
    );
    const allowPublicRecommendations = !assignedOnlyAccount && !hasOrganisationMembership;

    const backgroundTasks: Promise<unknown>[] = [
      request<any>("/learner/learning-plan")
        .then(result => setLearningPlan(result?.plan || null))
        .catch(() => {}),
      request<any>("/evidence/me")
        .then(result => { setEvidence(result); setEvidenceError(false); })
        .catch(() => setEvidenceError(true)),
      request<any>("/credentials/me")
        .then(result => { setCredentials(result); setCertificateError(false); })
        .catch(() => setCertificateError(true)),
    ];

    if (progressLoaded && allowPublicRecommendations) {
      setCatalogueLoading(true);
      backgroundTasks.push(
        request<any>("/public/courses")
          .then(result => setCatalogue(Array.isArray(result.courses) ? result.courses : Array.isArray(result.data) ? result.data : []))
          .catch(() => {})
          .finally(() => setCatalogueLoading(false))
      );
    } else {
      setCatalogue([]);
      setCatalogueLoading(false);
    }

    await Promise.allSettled(backgroundTasks);
  }, []);

  // A transient first-load failure is retried in the background. Learners
  // should not have to diagnose or manually restart dashboard loading.
  useEffect(() => {
    if (!user || !error) return;
    const timer = window.setTimeout(() => { void load(user); }, 8000);
    return () => window.clearTimeout(timer);
  }, [error, load, user]);

  useEffect(() => {
    let cancelled = false;
    currentUser().then(async me => {
      if (cancelled) return;
      if (me.account_type === "cohort") { location.href = "/dashboard/cohort"; return; }
      if (me.role === "organisation_prospect") { location.href = "/organisation-portal"; return; }
      const privileged = (me.organisation_memberships || []).filter((membership: any) => ["owner", "admin"].includes(membership.role));
      if (me.organisation_id && ["owner", "admin"].includes(me.organisation_role)) { location.href = "/dashboard/organisation"; return; }
      if (privileged.length) { location.href = "/dashboard/organisation" + (privileged.length > 1 && !me.organisation_id ? "?choose=1" : ""); return; }
      if (cancelled) return;
      setUser(me);
      const dashboardLoad = load(me);
      if (me.role === "normal") {
        try {
          const onboarding = await request<any>("/learner/onboarding");
          if (!onboarding.completed) { location.href = "/onboarding"; return; }
          const profile = onboarding.profile || onboarding;
          if (!cancelled) setGoal(profile.goal || profile.career_goal || profile.learning_goal || profile.preferred_track || "");
        } catch {}
      }
      await dashboardLoad;
    }).catch(() => { if (!cancelled) location.href = "/login"; });
    return () => { cancelled = true; };
  }, []);

  // Refresh learning records when the learner returns and periodically while the dashboard is open.
  useEffect(() => {
    if (!user) return;
    let lastRefresh = Date.now();
    const refresh = () => {
      if (document.visibilityState !== "visible" || Date.now() - lastRefresh < 15_000) return;
      lastRefresh = Date.now();
      void load(user);
    };
    const timer = window.setInterval(refresh, 60_000);
    window.addEventListener("focus", refresh);
    document.addEventListener("visibilitychange", refresh);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("focus", refresh);
      document.removeEventListener("visibilitychange", refresh);
    };
  }, [load, user]);

  // Keep the live session totals and meaningful-day streak current while the dashboard is open.
  useEffect(() => {
    if (!user) return;
    let active = true;
    const refreshSummary = async () => {
      if (document.visibilityState !== "visible") return;
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "Africa/Lagos";
      try {
        const summary = await request<any>("/progress/learning-summary?timezone=" + encodeURIComponent(timezone));
        if (active) setActivitySummary(summary);
      } catch {
        // Preserve the last confirmed summary when tracking is temporarily unavailable.
      }
    };
    void refreshSummary();
    const timer = window.setInterval(() => { void refreshSummary(); }, 60_000);
    const onFocus = () => { void refreshSummary(); };
    window.addEventListener("focus", onFocus);
    document.addEventListener("visibilitychange", onFocus);
    return () => {
      active = false;
      window.clearInterval(timer);
      window.removeEventListener("focus", onFocus);
      document.removeEventListener("visibilitychange", onFocus);
    };
  }, [user]);

  const assignedLearner = Boolean(
    user?.account_type === "cohort" ||
    user?.role === "witstart" ||
    user?.organisation_id ||
    user?.organisation_role === "member" ||
    user?.cohort_id ||
    user?.organisation_role === "learner" ||
    (user?.organisation_memberships || []).some((membership: any) =>
      ["learner", "member"].includes(membership.role) && membership.status === "active"
    )
  );
  const courses = useMemo(() => learning?.courses || [], [learning?.courses]);
  const inProgress = useMemo(() => courses.filter((row: any) => !(row.completed || row.enrolment?.status === "completed")), [courses]);
  const completed = useMemo(() => courses.filter((row: any) => row.completed || row.enrolment?.status === "completed"), [courses]);
  const enrolledIds = useMemo(() => new Set(courses.map((row: any) => String(row.course?.id || row.enrolment?.course_id || ""))), [courses]);
  const recommendations = useMemo(() => {
    const tokens = goal.toLowerCase().split(/[^a-z0-9]+/).filter((token: string) => token.length > 2);
    return catalogue
      .filter((course: any) => course.id && !enrolledIds.has(String(course.id)))
      .map((course: any, index: number) => {
        const searchable = [course.title, course.short_description, course.description, course.level].join(" ").toLowerCase();
        const score = tokens.reduce((total: number, token: string) => total + (searchable.includes(token) ? 1 : 0), 0);
        return { course, score, index };
      })
      .sort((a: any, b: any) => b.score - a.score || a.index - b.index)
      .slice(0, 3)
      .map((item: any) => item.course);
  }, [catalogue, enrolledIds, goal]);
  const completedLessons = courses.reduce((sum: number, row: any) => sum + Number(row.completed_lessons || 0), 0);
  const totalLessons = courses.reduce((sum: number, row: any) => sum + Number(row.total_lessons || 0), 0);
  const overallTotalUnits = courses.reduce((sum: number, row: any) => sum + Number(row.total_units ?? row.total_lessons ?? 0), 0);
  const overallCompletedUnits = courses.reduce((sum: number, row: any) => {
    const total = Number(row.total_units ?? row.total_lessons ?? 0);
    const done = row.completed || row.enrolment?.status === "completed"
      ? total
      : Number(row.completed_units ?? row.completed_lessons ?? 0);
    return sum + Math.max(0, Math.min(total, done));
  }, 0);
  const overallProgress = overallTotalUnits ? Math.round((overallCompletedUnits / overallTotalUnits) * 100) : 0;
  const learningSeconds = Number(activitySummary?.learning_time_seconds || 0);
  const learningTimeLabel = learningSeconds >= 3600
    ? Math.floor(learningSeconds / 3600) + "h " + Math.floor((learningSeconds % 3600) / 60) + "m"
    : learningSeconds >= 60 ? Math.floor(learningSeconds / 60) + "m" : learningSeconds + "s";
  const recentLearningDays = activitySummary?.learning_days || [];
  const lastAccessed = learning?.last_accessed_item || null;
  const continueItem = lastAccessed || (() => {
    const row = inProgress.find((item:any) => item.next_item?.id);
    return row ? {
      id: row.next_item.id,
      title: row.next_item.title,
      course_id: row.course?.id || row.enrolment?.course_id,
      course_title: row.course?.title || "Your course",
    } : null;
  })();
  const dailyGoalMinutes = learningPlan?.weekly_time_minutes ? Math.ceil(Number(learningPlan.weekly_time_minutes) / 7) : null;
  const dailyGoalText = continueItem?.title || learningPlan?.plan_data?.weeks?.[0]?.guidance?.focus || "";
  const certificates = credentials?.certificates || [];
  const skills = evidence?.skills || [];
  const earnedSkills = skills.filter((skill: any) => skill.status && skill.status !== "not_started");
  const badges = evidence?.badges || [];
  const recentCertificates = certificates.slice(0, 3);

  if (!user || loading) return <Shell active="learning" restricted={assignedLearner}><Skeleton label="Loading your learning records"/></Shell>;

  const tabs: { id: Tab; label: string; count: number }[] = [
    { id: "in-progress", label: "In Progress", count: inProgress.length },
    { id: "completed", label: "Completed", count: completed.length },
    { id: "skills", label: "Skills", count: earnedSkills.length },
    { id: "certificates", label: "Certificates", count: certificates.length },
  ];

  return <Shell active="learning" restricted={assignedLearner}>
    <section className="flex flex-wrap items-start justify-between gap-5 pb-6">
      <div className="flex min-w-0 items-center gap-4">
        <div className="grid size-14 shrink-0 place-items-center rounded-full bg-[var(--primary-tint)] text-xl font-bold text-[var(--primary)] sm:size-16 sm:text-2xl" aria-hidden="true">{(user.name || user.email || "L").trim().charAt(0).toUpperCase()}</div>
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wide text-[var(--primary)]">My Learning</p>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-[var(--text-heading)] sm:text-3xl">Welcome back{user.name ? ", " + user.name.split(" ")[0] : ""}</h1>
          {goal && <p className="mt-1 text-sm text-[var(--text-muted)]">Learning goal: {goal}</p>}
        </div>
      </div>
      <div className="flex items-center gap-2">
        {!assignedLearner && <Link href="/courses" className="inline-flex min-h-10 items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 text-xs font-semibold text-[var(--on-primary)] hover:bg-[var(--primary-hover)]">Explore courses <ArrowRight size={14}/></Link>}
        {!assignedLearner && <LearnerAssistant courses={catalogue} goal={goal} learning={courses} />}
      </div>
    </section>

    {error && <div role="status" className="mb-5 rounded-xl border border-[var(--warning)]/25 bg-[var(--warning)]/[.05] px-4 py-3 text-sm text-[var(--warning)]">{error} You can keep using the dashboard; we’ll refresh the learning records automatically when the connection recovers.</div>}

    <section className="grid grid-cols-2 gap-3 xl:grid-cols-4" aria-label="Learning summary">
      <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4"><p className="text-xs text-[var(--text-muted)]">Active courses</p><p className="mt-2 text-2xl font-bold tabular-nums text-[var(--text-heading)]">{learning ? inProgress.length : "—"}</p></div>
      <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4"><p className="text-xs text-[var(--text-muted)]">Lessons completed</p><p className="mt-2 text-2xl font-bold tabular-nums text-[var(--text-heading)]">{learning ? completedLessons : "—"}<span className="ml-1 text-sm font-medium text-[var(--text-muted)]">/ {learning ? totalLessons : "—"}</span></p></div>
      <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4"><p className="text-xs text-[var(--text-muted)]">Learning time</p><p className="mt-2 text-2xl font-bold tabular-nums text-[var(--text-heading)]">{learningTimeLabel}</p></div>
      <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4"><p className="text-xs text-[var(--text-muted)]">Learning streak</p><p className="mt-2 text-2xl font-bold tabular-nums text-[var(--text-heading)]">{Number(activitySummary?.current_streak || 0) + (Number(activitySummary?.current_streak || 0) === 1 ? " day" : " days")}</p></div>
    </section>
    <section className="mt-4 rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
      <div className="mb-2 flex items-center justify-between gap-3"><h2 className="text-sm font-semibold text-[var(--text-heading)]">Overall learning progress</h2><span className="text-sm font-bold tabular-nums text-[var(--text-heading)]">{learning && overallTotalUnits ? overallProgress + "%" : "—"}</span></div>
      <div className="h-2 overflow-hidden rounded-full bg-[var(--bg-soft)]"><div className="h-full rounded-full bg-[var(--primary)]" style={{width: overallProgress + "%"}}/></div>
      <p className="mt-2 text-xs text-[var(--text-muted)]">{!learning ? "Learning data is unavailable until your records load." : overallTotalUnits ? "Progress across all your enrolled courses, including completed courses (" + overallTotalUnits + " learning items)." : "Your progress will appear when you enrol in a course."}</p>
    </section>

    <div className="mt-7 flex gap-6 overflow-x-auto border-b border-[var(--border)]" role="tablist" aria-label="My learning sections">
      {tabs.map(item => <button key={item.id} type="button" role="tab" aria-selected={tab === item.id} onClick={() => setTab(item.id)} className={"-mb-px inline-flex shrink-0 items-center gap-2 border-b-2 px-1 pb-3 pt-2 text-sm transition " + (tab === item.id ? "border-[var(--primary)] font-bold text-[var(--text-heading)]" : "border-transparent text-[var(--text-muted)] hover:text-[var(--primary)]")}>
        {item.label}<span className="rounded-full bg-[var(--bg-soft)] px-2 py-0.5 text-[10px] tabular-nums text-[var(--text-muted)]">{item.count}</span>
      </button>)}
    </div>

    {continueItem && <section className="mt-6 rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5 sm:p-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="min-w-0"><p className="text-xs font-semibold uppercase tracking-wide text-[var(--primary)]">Continue learning</p><h2 className="mt-1 text-lg font-bold text-[var(--text-heading)]">{continueItem.title}</h2><p className="mt-1 text-xs text-[var(--text-muted)]">{continueItem.course_title}</p></div>
        <Link href={"/courses/" + encodeURIComponent(continueItem.course_id)} className="inline-flex min-h-10 items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-[var(--on-primary)]">Continue <ArrowRight size={14}/></Link>
      </div>
    </section>}
    <div className="mt-6 grid items-start gap-7 xl:grid-cols-[minmax(0,1fr)_19rem]">
      <section className="min-w-0" role="tabpanel">
        {tab === "in-progress" && (!learning
          ? <div className="empty">Your learning records are temporarily unavailable. Learnora will keep trying automatically.</div>
          : inProgress.length
          ? <div className="space-y-4">{inProgress.map((row: any) => <CourseCard key={row.enrolment?.id || row.course?.id} row={row} completed={false}/>)}</div>
          : courses.length === 0
            ? <section>
                <h2 className="mb-4 text-lg font-bold text-[var(--text-heading)]">Recommended courses</h2>
                {recommendations.length ? <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{recommendations.map((course: any) => <RecommendedCourseCard key={course.id} course={course}/>)}</div> : <div className="empty">{assignedLearner ? "Your organisation has not assigned a course to your account yet. Check back later or contact your learning coordinator." : catalogueLoading ? "Finding courses for you…" : <>Nothing here yet. <Link href="/courses">Explore courses</Link> to get started.</>}</div>}
              </section>
            : <div className="empty">{assignedLearner ? "Your assigned courses are complete. Your organisation will provide the next learning activity." : <>Nothing here yet. <Link href="/courses">Explore courses</Link> to get started.</>}</div>)}
        {tab === "completed" && (!learning
          ? <div className="empty">Your learning records are temporarily unavailable. Learnora will keep trying automatically.</div>
          : completed.length
          ? <div className="space-y-4">{completed.map((row: any) => <CourseCard key={row.enrolment?.id || row.course?.id} row={row} completed/>)}</div>
          : <div className="py-2"><h2 className="mb-3 text-base font-semibold text-[var(--text-heading)]">No completed courses</h2><div className="empty">{assignedLearner ? "You have no completed assigned courses yet." : <>Nothing here yet. <Link href="/courses">Explore courses</Link> to get started.</>}</div></div>)}
        {tab === "skills" && <section>
          <h2 className="mb-4 text-lg font-bold text-[var(--text-heading)]">Skills and achievements</h2>
          {evidenceError ? <p className="py-8 text-sm text-[var(--text-muted)]">Skills could not be loaded.</p> : <>
            {badges.length > 0 && <div className="mb-5 grid gap-3 sm:grid-cols-2">{badges.map((badge: any) => <article key={badge.id} className="flex items-start gap-3 rounded-xl border border-[var(--primary)]/25 bg-[var(--primary-tint)] p-4"><span className="grid size-10 shrink-0 place-items-center rounded-full bg-[var(--card)] text-[var(--primary)]"><Award size={19}/></span><div><h3 className="text-sm font-bold text-[var(--text-heading)]">{badge.name || "Learning achievement"}</h3><p className="mt-1 text-xs leading-5 text-[var(--text-muted)]">{badge.description || "Achievement awarded by Learnora."}</p></div></article>)}</div>}
            {earnedSkills.length ? <div className="grid gap-3 md:grid-cols-2">{earnedSkills.map((skill: any) => <article key={skill.skill_id || skill.id} className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4"><div className="flex items-start justify-between gap-3"><div><h3 className="font-semibold text-[var(--text-heading)]">{skill.skill_name || skill.name}</h3><p className="mt-1 text-xs text-[var(--text-muted)]">{skill.category || "Skill"}</p></div><span className="text-xs capitalize text-[var(--text-muted)]">{String(skill.status || "not_started").replaceAll("_", " ")}</span></div><div className="mt-4 h-2 overflow-hidden rounded-full bg-[var(--bg-soft)]"><div className="h-full rounded-full bg-[var(--primary)]" style={{ width: Math.max(0, Math.min(100, Number(skill.proficiency) || 0)) + "%" }}/></div><p className="mt-2 text-[11px] text-[var(--text-muted)]">{skill.verified_evidence_count || 0} verified evidence items · {skill.course_completion_count || 0} completed courses · {Number(skill.proficiency) || 0}% verified proficiency</p></article>)}</div> : !badges.length ? <div className="empty">Complete a course or submit work for review to start earning skill achievements.</div> : null}
          </>}
        </section>}
        {tab === "certificates" && <section>
          <h2 className="mb-4 text-lg font-bold text-[var(--text-heading)]">Certificates</h2>
          {certificateError ? <div className="empty">Certificates could not be loaded.</div> : certificates.length ? <div className="space-y-3">{certificates.map((cert: any) => <article key={cert.id} className="flex items-center gap-3 rounded-xl border border-[var(--border)] bg-[var(--card)] p-4"><span className="grid size-10 shrink-0 place-items-center rounded-lg bg-[var(--primary-tint)] text-[var(--primary)]"><Award size={19}/></span><div className="min-w-0 flex-1"><h3 className="truncate text-sm font-semibold text-[var(--text-heading)]">{cert.course_title}</h3><p className="mt-1 text-xs text-[var(--text-muted)]">Issued {dateLabel(cert.issued_at)}</p></div><Link href={cert.verification_url || "/dashboard/certificates"} className="shrink-0 text-xs font-semibold text-[var(--primary)]">View</Link></article>)}</div> : <p className="py-8 text-sm text-[var(--text-muted)]">Nothing here yet.</p>}
        </section>}
      </section>

      <aside className="space-y-4">
        <section className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
          <h2 className="text-sm font-bold text-[var(--text-heading)]">Today’s learning goal</h2>
          {dailyGoalText ? <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">{dailyGoalText}</p> : <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">Choose your next assigned lesson or create a learning plan to set a clear focus for today.</p>}
          {dailyGoalMinutes ? <p className="mt-2 text-xs text-[var(--text-muted)]">Suggested daily share: {dailyGoalMinutes} minutes, based on your saved weekly plan.</p> : null}
          <Link href="/dashboard/learning-plan" className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-[var(--primary)]">View learning plan <ArrowRight size={13}/></Link>
        </section>
        <section className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
          <div className="flex items-center justify-between gap-2"><h2 className="text-sm font-bold text-[var(--text-heading)]">Recent learning activity</h2><Link href="/dashboard/calendar" className="text-xs font-semibold text-[var(--primary)]">Calendar</Link></div>
          {recentLearningDays.length ? <div className="mt-4 space-y-3">{recentLearningDays.slice(0,5).map((day:any) => <div key={day.activity_date} className="flex items-start justify-between gap-3"><div><p className="text-xs font-semibold text-[var(--text-heading)]">{new Date(day.activity_date + "T12:00:00").toLocaleDateString("en-GB",{day:"numeric",month:"short",year:"numeric"})}</p><p className="mt-1 text-[11px] text-[var(--text-muted)]">{(day.activity_types || []).map((type:string) => type.replaceAll("_"," ")).join(" · ")}</p></div><span className="text-[11px] tabular-nums text-[var(--text-muted)]">{day.activity_count} activity</span></div>)}</div> : <p className="mt-3 text-sm text-[var(--text-muted)]">Completed lessons, passed quizzes and submitted assignments will appear here.</p>}
        </section>
        {recommendations.length > 0 && <section className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
          <h2 className="text-sm font-bold text-[var(--text-heading)]">Recommended for you</h2>
          <div className="mt-4 space-y-3">{recommendations.map((course:any) => <div key={course.id} className="flex items-start gap-3 border-b border-[var(--border)] pb-3 last:border-0 last:pb-0">
            {course.thumbnail_url ? <Image unoptimized src={course.thumbnail_url} alt="" width={56} height={56} sizes="56px" className="size-14 shrink-0 rounded-lg object-cover"/> : <span className="grid size-14 shrink-0 place-items-center rounded-lg bg-[var(--bg-soft)] text-[var(--primary)]"><BookOpen size={19}/></span>}
            <div className="min-w-0"><p className="text-xs font-semibold leading-5 text-[var(--text-heading)]">{course.title}</p><p className="mt-1 line-clamp-2 text-[11px] leading-4 text-[var(--text-muted)]">{course.short_description || course.description || "Explore this course."}</p><Link href={"/courses/" + encodeURIComponent(course.id)} className="mt-2 inline-flex items-center gap-1 text-[11px] font-semibold text-[var(--primary)]">View course <ArrowRight size={12}/></Link></div>
          </div>)}</div>
        </section>}

        <section className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
          <div className="flex items-center gap-2"><Clock3 size={17} className="text-[var(--primary)]"/><h2 className="text-sm font-bold text-[var(--text-heading)]">Learning snapshot</h2></div>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div><p className="text-2xl font-bold tabular-nums text-[var(--text-heading)]">{Number(activitySummary?.longest_streak || 0) + (Number(activitySummary?.longest_streak || 0) === 1 ? " day" : " days")}</p><p className="mt-1 text-xs text-[var(--text-muted)]">Longest streak</p></div>
            <div><p className="text-2xl font-bold tabular-nums text-[var(--success)]">{completed.length}</p><p className="mt-1 text-xs text-[var(--text-muted)]">Completed</p></div>
            <div><p className="text-2xl font-bold tabular-nums text-[var(--text-heading)]">{completedLessons}</p><p className="mt-1 text-xs text-[var(--text-muted)]">Lessons completed</p></div>
            <div><p className="text-2xl font-bold tabular-nums text-[var(--text-heading)]">{certificates.length}</p><p className="mt-1 text-xs text-[var(--text-muted)]">Certificates</p></div>
          </div>
        </section>
        <section className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
          <div className="flex items-center justify-between gap-2"><h2 className="text-sm font-bold text-[var(--text-heading)]">Recent certificates</h2><Award size={17} className="text-[var(--primary)]"/></div>
          {certificateError ? <div className="empty mt-3">Certificates could not be loaded.</div> : recentCertificates.length ? <div className="mt-4 space-y-4">{recentCertificates.map((cert: any) => <div key={cert.id} className="flex items-start gap-3"><span className="grid size-8 shrink-0 place-items-center rounded-md bg-[var(--bg-soft)] text-[var(--primary)]"><FileText size={15}/></span><div className="min-w-0"><p className="text-xs font-semibold leading-5 text-[var(--text-heading)]">{cert.course_title}</p><p className="mt-1 text-[11px] text-[var(--text-muted)]">{dateLabel(cert.issued_at)}</p></div></div>)}</div> : <p className="mt-3 text-sm text-[var(--text-muted)]">Nothing here yet.</p>}
        </section>
      </aside>
    </div>
  </Shell>;
}
