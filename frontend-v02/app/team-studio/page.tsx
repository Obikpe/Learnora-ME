"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

type OutlineModule = { title: string; lessons: string[] };
type Curriculum = {
  course_title: string;
  short_description: string;
  course_description: string;
  learning_outcomes: string[];
  prerequisites: string[];
  modules: Array<{ title: string; description: string; lessons: Array<{ title: string; description: string; learning_objective: string; lesson_format: string; estimated_minutes: number }> }>;
  quality_review: string[];
};
type LessonPackage = {
  teaching_script: string;
  estimated_duration_seconds: number;
  concise_note: string;
  practice_activity?: string | null;
  knowledge_check: Array<{ question: string; options: string[]; correct_option: number; explanation: string }>;
  video_plan: Array<{ narration: string; visual_direction: string; on_screen_text: string[]; visual_type: string }>;
  fact_check_notes: string[];
};

async function internalRequest(path: string, init: RequestInit = {}) {
  const response = await fetch("/api/internal" + path, {
    ...init,
    credentials: "same-origin",
    cache: "no-store",
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401) throw Object.assign(new Error("Your internal staff session has expired. Please sign in again."), { status: 401 });
    throw new Error(typeof body.detail === "string" ? body.detail : "The request could not be completed.");
  }
  return body;
}

function splitLines(value: string) {
  return value.split(/\r?\n/).map(x => x.trim()).filter(Boolean);
}

function parseOutline(value: string): OutlineModule[] {
  const modules: OutlineModule[] = [];
  let current: OutlineModule | null = null;
  const ensureModule = () => {
    if (!current) {
      current = { title: "Module 1", lessons: [] };
      modules.push(current);
    }
    return current;
  };
  for (const raw of value.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line) continue;
    const heading = line.match(/^(?:#{1,3}\s*)?module\s*\d*\s*[:.\-–]?\s*(.+)$/i);
    if (heading) {
      current = { title: heading[1].trim(), lessons: [] };
      modules.push(current);
      continue;
    }
    const lesson = line.replace(/^(?:[-*•]\s*|lesson\s*\d*\s*[:.\-–]?\s*)/i, "").trim();
    if (lesson) ensureModule().lessons.push(lesson);
  }
  return modules.filter(module => module.title.trim() && module.lessons.length);
}

function formatDuration(seconds: number) {
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds % 60;
  return minutes ? minutes + "m " + remainder + "s" : remainder + " seconds";
}

export default function TeamCourseStudioPage() {
  const router = useRouter();
  const [staff, setStaff] = useState<any>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [authError, setAuthError] = useState("");
  const [courseTitle, setCourseTitle] = useState("");
  const [courseDescription, setCourseDescription] = useState("");
  const [level, setLevel] = useState("beginner");
  const [audience, setAudience] = useState("");
  const [tracks, setTracks] = useState<Array<{id:string;name:string;status:string}>>([]);
  const [targetTrackId, setTargetTrackId] = useState("");
  const [prerequisites, setPrerequisites] = useState("");
  const [outcomes, setOutcomes] = useState("");
  const [outlineText, setOutlineText] = useState("");
  const [curriculum, setCurriculum] = useState<Curriculum | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [createDraftBusy, setCreateDraftBusy] = useState(false);
  const [createDraftError, setCreateDraftError] = useState("");
  const [createdCourseId, setCreatedCourseId] = useState<string | null>(null);
  const [canPublish, setCanPublish] = useState(false);
  const [newTrackOpen, setNewTrackOpen] = useState(false);
  const [newTrackName, setNewTrackName] = useState("");
  const [newTrackSlug, setNewTrackSlug] = useState("");
  const [newTrackDescription, setNewTrackDescription] = useState("");
  const [trackCreateBusy, setTrackCreateBusy] = useState(false);
  const [trackCreateError, setTrackCreateError] = useState("");
  const [trackPublishBusy, setTrackPublishBusy] = useState(false);
  const [trackPublishError, setTrackPublishError] = useState("");
  const [publishedCourse, setPublishedCourse] = useState(false);
  const [publishBusy, setPublishBusy] = useState(false);
  const [publishError, setPublishError] = useState("");
  const [renderJobs, setRenderJobs] = useState<Array<{id:string;status:string;attempt_count:number;max_attempts:number;error_summary?:string}>>([]);
  const [renderJobsQueued, setRenderJobsQueued] = useState<number | null>(null);
  const [curriculumBusy, setCurriculumBusy] = useState(false);
  const [generationError, setGenerationError] = useState("");
  const [packages, setPackages] = useState<Record<string, LessonPackage>>({});
  const [packageBusy, setPackageBusy] = useState<Record<string, boolean>>({});
  const [packageErrors, setPackageErrors] = useState<Record<string, string>>({});
  const [batchBusy, setBatchBusy] = useState(false);
  const [batchProgress, setBatchProgress] = useState({ completed: 0, total: 0 });
  
  const outline = useMemo(() => parseOutline(outlineText), [outlineText]);
  const lessonCount = useMemo(() => curriculum?.modules.reduce((sum, module) => sum + module.lessons.length, 0) || 0, [curriculum]);

  useEffect(() => {
    let active = true;
    internalRequest("/course-studio/access")
      .then(async data => { if (active) setStaff(data.staff); try { const trackData = await internalRequest("/course-studio/tracks"); if (active) setTracks(trackData.tracks || []); } catch {} try { await internalRequest("/course-studio/publish-access"); if (active) setCanPublish(true); } catch { if (active) setCanPublish(false); } })
      .catch((error: any) => {
        if (!active) return;
        if (error.status === 401) router.replace("/team-studio/login");
        else setAuthError(error.message || "This staff account does not have course-studio permission.");
      })
      .finally(() => { if (active) setAuthLoading(false); });
    return () => { active = false; };
  }, [router]);

  useEffect(() => {
    if (!staff) return;
    const savedJobId = new URLSearchParams(window.location.search).get("job");
    if (!savedJobId) return;
    let active = true;
    internalRequest("/course-studio/jobs/" + encodeURIComponent(savedJobId))
      .then(data => {
        if (!active) return;
        const job = data.job;
        const requestData = job.request_data || {};
        setJobId(job.id);
        setCurriculum(job.curriculum_data);
        setCourseTitle(job.course_title || requestData.course_title || "");
        setCourseDescription(requestData.course_description || job.curriculum_data?.course_description || "");
        setLevel(job.course_level || "beginner");
        setAudience(requestData.target_audience || "");
        setPrerequisites((requestData.prerequisites || []).join("\n"));
        setOutcomes((requestData.learning_outcomes || []).join("\n"));
        setTargetTrackId(job.target_track_id || "");
        setOutlineText((requestData.outline || []).map((module: any, index: number) =>
          "Module " + (index + 1) + ": " + module.title + "\n" + (module.lessons || []).map((lesson: string) => "- " + lesson).join("\n")
        ).join("\n\n"));
        const latest: Record<string, {version:number; package:LessonPackage}> = {};
        for (const row of data.packages || []) {
          const key = row.module_order + ":" + row.lesson_order;
          if (!latest[key] || Number(row.version) > latest[key].version) {
            latest[key] = {
              version: Number(row.version),
              package: {
                teaching_script: row.teaching_script,
                estimated_duration_seconds: row.estimated_duration_seconds,
                concise_note: row.concise_note,
                practice_activity: row.practice_activity,
                knowledge_check: row.knowledge_check || [],
                video_plan: row.video_plan || [],
                fact_check_notes: row.fact_check_notes || [],
              },
            };
          }
        }
        setPackages(Object.fromEntries(Object.entries(latest).map(([key, value]) => [key, value.package])));
        setCreatedCourseId(["created", "published"].includes(job.status) ? job.created_course_id : null);
        setPublishedCourse(job.status === "published");
        setRenderJobs(data.render_jobs || []);
        setRenderJobsQueued((data.render_jobs || []).filter((job:any) => job.status === "queued" || job.status === "processing").length);
      })
      .catch((error: any) => {
        if (active) setGenerationError(error.message || "The saved course draft could not be restored.");
      });
    return () => { active = false; };
  }, [staff]);

  const logout = useCallback(async () => {
    try { await internalRequest("/auth/logout", { method: "POST" }); } catch {}
    router.replace("/team-studio/login");
  }, [router]);

  async function createTrack() {
    if (!newTrackName.trim() || !newTrackSlug.trim() || !canPublish || trackCreateBusy) return;
    setTrackCreateBusy(true);
    setTrackCreateError("");
    try {
      const result = await internalRequest("/tracks", {
        method: "POST",
        body: JSON.stringify({ name: newTrackName.trim(), slug: newTrackSlug.trim(), description: newTrackDescription.trim() || null }),
      });
      const refreshed = await internalRequest("/course-studio/tracks");
      setTracks(refreshed.tracks || []);
      setTargetTrackId(result.track.id);
      setNewTrackName("");
      setNewTrackSlug("");
      setNewTrackDescription("");
      setNewTrackOpen(false);
    } catch (error: any) {
      setTrackCreateError(error.message || "The track could not be created.");
    } finally {
      setTrackCreateBusy(false);
    }
  }

  async function generateCurriculum() {
    setGenerationError("");
    setPackages({});
    setPackageErrors({});
    setJobId(null);
    setCreatedCourseId(null);
    setPublishedCourse(false);
    setPublishError("");
    setRenderJobs([]);
    setRenderJobsQueued(null);
    setCreateDraftError("");
    if (!courseTitle.trim() || !courseDescription.trim() || !audience.trim() || !outcomes.trim() || !outline.length) {
      setGenerationError("Complete the course brief, audience, learning outcomes and at least one module with lessons.");
      return;
    }
    setCurriculumBusy(true);
    try {
      const result = await internalRequest("/course-studio/curriculum", {
        method: "POST",
        body: JSON.stringify({
          course_title: courseTitle.trim(),
          course_description: courseDescription.trim(),
          level,
          target_audience: audience.trim(),
          target_track_id: targetTrackId || null,
          prerequisites: splitLines(prerequisites),
          learning_outcomes: splitLines(outcomes),
          outline,
        }),
      });
      setJobId(result.job_id);
      router.replace("/team-studio?job=" + encodeURIComponent(result.job_id));
      setCurriculum(result.curriculum);
    } catch (error: any) {
      setGenerationError(error.message || "The curriculum could not be generated.");
    } finally {
      setCurriculumBusy(false);
    }
  }

  async function generateLessonPackage(moduleIndex: number, lessonIndex: number) {
    if (!curriculum || !jobId || createdCourseId) return false;
    const key = moduleIndex + ":" + lessonIndex;
    setPackageBusy(old => ({ ...old, [key]: true }));
    setPackageErrors(old => ({ ...old, [key]: "" }));
    try {
      const result = await internalRequest("/course-studio/lesson-package", {
        method: "POST",
        body: JSON.stringify({
          job_id: jobId,
          module_order: moduleIndex,
          lesson_order: lessonIndex,
        }),
      });
      setPackages(old => ({ ...old, [key]: result.lesson_package }));
      return true;
    } catch (error: any) {
      setPackageErrors(old => ({ ...old, [key]: error.message || "Lesson package generation failed." }));
      return false;
    } finally {
      setPackageBusy(old => ({ ...old, [key]: false }));
    }
  }

  async function generateAllMissingPackages() {
    if (!curriculum || !jobId || batchBusy || createdCourseId) return;
    const missing = curriculum.modules.flatMap((module, moduleIndex) =>
      module.lessons.map((_, lessonIndex) => ({ moduleIndex, lessonIndex, key: moduleIndex + ":" + lessonIndex }))
    ).filter(item => !packages[item.key]);
    if (!missing.length) return;
    setBatchBusy(true);
    setBatchProgress({ completed: 0, total: missing.length });
    for (const item of missing) {
      const succeeded = await generateLessonPackage(item.moduleIndex, item.lessonIndex);
      setBatchProgress(progress => ({ ...progress, completed: progress.completed + 1 }));
      if (!succeeded) break;
    }
    setBatchBusy(false);
  }

  async function publishSelectedTrack() {
    if (!targetTrackId || !canPublish || trackPublishBusy) return;
    setTrackPublishBusy(true);
    setTrackPublishError("");
    try {
      await internalRequest("/tracks/" + encodeURIComponent(targetTrackId), {
        method: "PATCH",
        body: JSON.stringify({ status: "published" }),
      });
      const refreshed = await internalRequest("/course-studio/tracks");
      setTracks(refreshed.tracks || []);
    } catch (error: any) {
      setTrackPublishError(error.message || "The learning track could not be published.");
    } finally {
      setTrackPublishBusy(false);
    }
  }

  async function publishCourse() {
    if (!jobId || !createdCourseId || !canPublish || publishedCourse || publishBusy) return;
    setPublishBusy(true);
    setPublishError("");
    try {
      const result = await internalRequest("/course-studio/jobs/" + encodeURIComponent(jobId) + "/publish", {
        method: "POST",
      });
      setPublishedCourse(result.status === "published");
    } catch (error: any) {
      setPublishError(error.message || "The course could not be published.");
    } finally {
      setPublishBusy(false);
    }
  }

  async function createDraftCourse() {
    if (!jobId || !curriculum || Object.keys(packages).length !== lessonCount || Object.values(packageBusy).some(Boolean) || createdCourseId) return;
    setCreateDraftBusy(true);
    setCreateDraftError("");
    try {
      const result = await internalRequest("/course-studio/jobs/" + jobId + "/create-draft", {
        method: "POST",
        body: JSON.stringify({}),
      });
      setCreatedCourseId(result.course_id);
      setPublishedCourse(false);
      setPublishError("");
      setRenderJobsQueued(result.render_jobs_queued ?? 0);
      const refreshed = await internalRequest("/course-studio/jobs/" + jobId);
      setRenderJobs(refreshed.render_jobs || []);
    } catch (error: any) {
      setCreateDraftError(error.message || "The draft course could not be created.");
    } finally {
      setCreateDraftBusy(false);
    }
  }

  if (authLoading) return <main className="grid min-h-screen place-items-center bg-[#090d12] text-slate-300">Verifying internal staff access…</main>;
  if (!staff) return <main className="min-h-screen bg-[#090d12] px-5 py-16 text-slate-100"><div className="mx-auto max-w-xl rounded-2xl border border-white/10 p-6"><h1 className="text-2xl font-semibold">Course Studio access unavailable</h1><p className="mt-3 text-sm leading-6 text-slate-400">{authError || "This internal account does not have permission to generate course content."}</p><button onClick={() => void logout()} className="mt-5 rounded-xl border border-white/10 px-4 py-2 text-sm">Sign out</button></div></main>;

  return (
    <main className="min-h-screen bg-[#090d12] px-4 py-6 text-slate-100 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-5">
          <div><a href="/" className="text-lg font-semibold">Learnora <span className="text-[#d7ad35]">ME</span></a><p className="mt-2 text-[10px] font-bold uppercase tracking-[.2em] text-[#d7ad35]">Internal course production</p><h1 className="mt-1 text-3xl font-semibold tracking-tight sm:text-4xl">Course Studio</h1><p className="mt-2 text-xs text-slate-500">Signed in as {staff.name || staff.email}</p></div>
          <button onClick={() => void logout()} className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-300 hover:bg-white/[.04]">Sign out</button>
        </header>

        <section className="mt-7 grid gap-5 lg:grid-cols-[minmax(0,1fr)_19rem]">
          <div className="space-y-5">
            <div className="rounded-2xl border border-white/10 bg-white/[.025] p-5 sm:p-6">
              <div><p className="text-xs font-bold uppercase tracking-[.16em] text-slate-500">Step 1</p><h2 className="mt-2 text-xl font-semibold">Course brief</h2><p className="mt-2 text-sm leading-6 text-slate-400">Describe the course and provide the outline. AI will review the sequence and return a structured curriculum proposal.</p></div>
              <div className="mt-5 grid gap-4 sm:grid-cols-2">
                <label className="grid gap-2 text-sm text-slate-300 sm:col-span-2">Course title<input value={courseTitle} onChange={e => setCourseTitle(e.target.value)} placeholder="e.g. Data Analytics" className="min-h-11 w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-[#d7ad35]/60" /></label>
                <label className="grid gap-2 text-sm text-slate-300 sm:col-span-2">Course description<textarea value={courseDescription} onChange={e => setCourseDescription(e.target.value)} rows={3} placeholder="What should learners understand and be able to do by the end?" className="min-h-11 w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-[#d7ad35]/60" /></label>
                <label className="grid gap-2 text-sm text-slate-300">Level<select value={level} onChange={e => setLevel(e.target.value)} className="min-h-11 w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-[#d7ad35]/60"><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option><option value="mixed">Mixed</option></select></label>
                <label className="grid gap-2 text-sm text-slate-300">Target audience<input value={audience} onChange={e => setAudience(e.target.value)} placeholder="e.g. beginners with no analytics experience" className="min-h-11 w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-[#d7ad35]/60" /></label>
                <div className="grid gap-2 text-sm text-slate-300"><label className="grid gap-2">Track (optional)<select value={targetTrackId} onChange={e => setTargetTrackId(e.target.value)} className="min-h-11 w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none focus:border-[#d7ad35]/60"><option value="">Standalone course</option>{tracks.map(track => <option key={track.id} value={track.id}>{track.name} · {track.status}</option>)}</select><span className="text-[11px] leading-5 text-slate-500">The selected track is linked only when the course is published, after the system rechecks that the track curriculum is not locked. Leave this blank for a standalone course.</span></label>{canPublish && <button type="button" onClick={() => setNewTrackOpen(value => !value)} className="justify-self-start text-xs font-semibold text-[#e7c76d]">{newTrackOpen ? "Cancel new track" : "Create a new track"}</button>}</div>
                {newTrackOpen && <div className="rounded-xl border border-white/10 bg-black/20 p-4 sm:col-span-2"><h3 className="text-sm font-semibold">Create a learning track</h3><div className="mt-3 grid gap-3 sm:grid-cols-2"><label className="grid gap-2 text-xs text-slate-400">Track name<input value={newTrackName} onChange={event => { const value = event.target.value; setNewTrackName(value); setNewTrackSlug(value.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")); }} className="min-h-10 rounded-lg border border-white/10 bg-black/20 px-3 text-sm text-white" placeholder="Front-end Web Development"/></label><label className="grid gap-2 text-xs text-slate-400">Track slug<input value={newTrackSlug} onChange={event => setNewTrackSlug(event.target.value)} className="min-h-10 rounded-lg border border-white/10 bg-black/20 px-3 text-sm text-white" placeholder="front-end-web-development"/></label><label className="grid gap-2 text-xs text-slate-400 sm:col-span-2">Track description<textarea value={newTrackDescription} onChange={event => setNewTrackDescription(event.target.value)} rows={2} className="rounded-lg border border-white/10 bg-black/20 px-3 py-2 text-sm text-white" placeholder="A structured learning journey for front-end web development."/></label></div>{trackCreateError && <p role="alert" className="mt-3 text-xs text-red-200">{trackCreateError}</p>}<button type="button" onClick={() => void createTrack()} disabled={trackCreateBusy || newTrackName.trim().length < 2 || newTrackSlug.trim().length < 2} className="mt-3 rounded-lg bg-[#d7ad35] px-4 py-2.5 text-xs font-semibold text-black disabled:opacity-40">{trackCreateBusy ? "Creating track…" : "Create track"}</button></div>}
                <label className="grid gap-2 text-sm text-slate-300">Prerequisites (one per line)<textarea value={prerequisites} onChange={e => setPrerequisites(e.target.value)} rows={3} className="min-h-11 w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-[#d7ad35]/60" placeholder="Leave blank if none" /></label>
                <label className="grid gap-2 text-sm text-slate-300">Learning outcomes (one per line)<textarea value={outcomes} onChange={e => setOutcomes(e.target.value)} rows={3} className="min-h-11 w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-[#d7ad35]/60" placeholder="Explain what learners should be able to do" /></label>
                <label className="grid gap-2 text-sm text-slate-300 sm:col-span-2">Course outline<textarea value={outlineText} onChange={e => setOutlineText(e.target.value)} rows={9} className="min-h-11 w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-[#d7ad35]/60 font-mono text-xs leading-6" placeholder={"Module 1: Introduction to Data Analytics\n- What is data analytics?\n- Careers in data analytics\n- Why become a data analyst?\n- Data analytics vs data analysis\n\nModule 2: Data and Data Types\n- What is data?\n- Structured and unstructured data"} /></label>
              </div>
              <div className="mt-4 flex flex-wrap items-center justify-between gap-3"><p className="text-xs text-slate-500">{outline.length} modules · {outline.reduce((n, item) => n + item.lessons.length, 0)} outline lessons detected</p><button onClick={() => void generateCurriculum()} disabled={curriculumBusy || batchBusy || Object.values(packageBusy).some(Boolean) || Boolean(createdCourseId)} className="rounded-xl bg-[#d7ad35] px-5 py-3 text-sm font-semibold text-black disabled:opacity-50">{curriculumBusy ? "Reviewing outline…" : "Generate curriculum proposal"}</button></div>
              {generationError && <p role="alert" className="mt-4 rounded-lg border border-red-400/20 bg-red-400/5 p-3 text-sm text-red-200">{generationError}</p>}
            </div>

            {curriculum && <section className="space-y-4">
              <div className="flex flex-wrap items-end justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-[.16em] text-slate-500">Step 2</p><h2 className="mt-2 text-2xl font-semibold">Curriculum proposal</h2><p className="mt-1 text-sm text-slate-400">{curriculum.modules.length} modules · {lessonCount} lessons · review before accepting</p></div><button disabled={batchBusy || Object.values(packageBusy).some(Boolean)} onClick={() => { setCurriculum(null); setPackages({}); setJobId(null); setCreatedCourseId(null); setPublishedCourse(false); setPublishError(""); setRenderJobs([]); setRenderJobsQueued(null); setCreateDraftError(""); router.replace("/team-studio"); }} className="rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-400">Discard proposal</button></div>
              <div className="rounded-2xl border border-white/10 bg-white/[.025] p-5"><h3 className="text-xl font-semibold">{curriculum.course_title}</h3><p className="mt-2 text-sm leading-6 text-slate-400">{curriculum.short_description}</p><p className="mt-3 text-sm leading-6 text-slate-300">{curriculum.course_description}</p><div className="mt-4 grid gap-4 sm:grid-cols-2"><div><p className="text-xs font-bold uppercase tracking-wider text-slate-500">Learning outcomes</p><ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-300">{curriculum.learning_outcomes.map((x,i)=><li key={i}>{x}</li>)}</ul></div><div><p className="text-xs font-bold uppercase tracking-wider text-slate-500">Prerequisites</p><ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-300">{(curriculum.prerequisites||[]).map((x,i)=><li key={i}>{x}</li>)}</ul></div></div></div>
              {curriculum.modules.map((module, mi) => <article key={mi} className="rounded-2xl border border-white/10 bg-white/[.025] p-5"><p className="text-[10px] font-bold uppercase tracking-[.16em] text-[#d7ad35]">Module {mi+1}</p><h3 className="mt-2 text-lg font-semibold">{module.title}</h3><p className="mt-1 text-sm text-slate-400">{module.description}</p><div className="mt-4 space-y-3">{module.lessons.map((lesson, li) => { const key = mi + ":" + li; const pkg = packages[key]; return <div key={key} className="rounded-xl border border-white/[.08] bg-black/20 p-4"><div className="flex flex-wrap items-start justify-between gap-3"><div className="min-w-0 flex-1"><h4 className="font-medium">{lesson.title}</h4><p className="mt-1 text-xs leading-5 text-slate-400">{lesson.description}</p><p className="mt-2 text-[11px] text-slate-500">{lesson.lesson_format.replaceAll("_"," ")} · {lesson.estimated_minutes} min · {lesson.learning_objective}</p></div><button onClick={() => void generateLessonPackage(mi,li)} disabled={Boolean(packageBusy[key]) || Boolean(createdCourseId) || batchBusy} className="shrink-0 rounded-lg border border-[#d7ad35]/30 px-3 py-2 text-xs font-semibold text-[#e7c76d] disabled:opacity-50">{packageBusy[key] ? "Generating…" : pkg ? "Regenerate package" : "Generate lesson package"}</button></div>{packageErrors[key] && <p role="alert" className="mt-3 text-xs text-red-200">{packageErrors[key]}</p>}{pkg && <div className="mt-4 border-t border-white/10 pt-4"><div className="flex flex-wrap items-center justify-between gap-2"><p className="text-xs font-bold uppercase tracking-wider text-[#d7ad35]">Teaching package</p><span className="text-[11px] text-slate-500">{formatDuration(pkg.estimated_duration_seconds)}</span></div><h5 className="mt-3 text-sm font-semibold">Teaching script</h5><p className="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-300">{pkg.teaching_script}</p><h5 className="mt-4 text-sm font-semibold">Short learner note</h5><p className="mt-2 whitespace-pre-wrap rounded-lg bg-white/[.035] p-3 text-sm leading-6 text-slate-300">{pkg.concise_note}</p>{pkg.practice_activity && <><h5 className="mt-4 text-sm font-semibold">Practical activity</h5><p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-300">{pkg.practice_activity}</p></>}{pkg.video_plan?.length>0 && <><h5 className="mt-4 text-sm font-semibold">Video storyboard</h5><div className="mt-2 grid gap-2">{pkg.video_plan.map((scene,i)=><div key={i} className="rounded-lg border border-white/[.07] p-3"><p className="text-[10px] uppercase tracking-wider text-slate-500">Scene {i+1} · {scene.visual_type.replaceAll("_"," ")}</p><p className="mt-2 text-xs leading-5 text-slate-300">{scene.visual_direction}</p><p className="mt-1 text-xs leading-5 text-slate-500">Narration: {scene.narration}</p>{scene.on_screen_text?.length>0 && <p className="mt-1 text-xs text-slate-400">On screen: {scene.on_screen_text.join(" · ")}</p>}</div>)}</div></>}{pkg.knowledge_check?.length>0 && <><h5 className="mt-4 text-sm font-semibold">Knowledge check draft</h5><ol className="mt-2 list-decimal space-y-3 pl-5 text-sm text-slate-300">{pkg.knowledge_check.map((q,i)=><li key={i}><p>{q.question}</p><ul className="mt-1 list-disc pl-5 text-xs text-slate-400">{q.options.map((option,j)=><li key={j}>{option}{j===q.correct_option?" — answer":""}</li>)}</ul><p className="mt-1 text-xs text-slate-500">{q.explanation}</p></li>)}</ol></>}{pkg.fact_check_notes?.length>0 && <div className="mt-4 rounded-lg border border-amber-300/20 bg-amber-300/[.04] p-3"><p className="text-xs font-semibold text-amber-200">Needs fact-checking</p><ul className="mt-2 list-disc space-y-1 pl-5 text-xs text-amber-100/80">{pkg.fact_check_notes.map((x,i)=><li key={i}>{x}</li>)}</ul></div>}</div>}</div>})}</div></article>)}
              {curriculum.quality_review?.length>0 && <div className="rounded-2xl border border-amber-300/20 bg-amber-300/[.04] p-5"><h3 className="font-semibold text-amber-200">Curriculum review notes</h3><ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-amber-100/80">{curriculum.quality_review.map((x,i)=><li key={i}>{x}</li>)}</ul></div>}
              <div className="rounded-2xl border border-white/10 bg-white/[.025] p-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div><h3 className="font-semibold">Create the course draft</h3><p className="mt-1 text-xs leading-5 text-slate-500">Generate and review every lesson package first. This action creates unpublished course, module and lesson records; it does not publish to learners.</p></div>
                  <button onClick={() => void createDraftCourse()} disabled={!jobId || Object.keys(packages).length !== lessonCount || lessonCount === 0 || Object.values(packageBusy).some(Boolean) || batchBusy || createDraftBusy || Boolean(createdCourseId)} className="rounded-xl bg-[#d7ad35] px-4 py-3 text-sm font-semibold text-black disabled:cursor-not-allowed disabled:opacity-40">{createDraftBusy ? "Creating draft…" : "I have reviewed the packages — create draft course"}</button>
                </div>
                {createDraftError && <p role="alert" className="mt-3 rounded-lg border border-red-400/20 bg-red-400/5 p-3 text-sm text-red-200">{createDraftError}</p>}
                {createdCourseId && <div className="mt-4 rounded-lg border border-emerald-400/20 bg-emerald-400/[.04] p-3"><p className="text-sm font-semibold text-emerald-200">{publishedCourse ? "Course published" : "Draft course created"}</p><p className="mt-1 text-xs text-slate-400">Course ID: {createdCourseId}. Selected track: {targetTrackId ? (tracks.find(track => track.id === targetTrackId)?.name || "Learnora ME track") + (publishedCourse ? "" : " · linked on publication") : "Standalone course"}.</p><p className="mt-2 text-xs text-slate-300">{publishedCourse ? "The course is now published and available according to its course and track access settings." : "The course remains unpublished until an authorised staff member completes the final review and publication step."}</p><p className="mt-2 text-xs text-slate-300">{renderJobsQueued ?? renderJobs.filter(job => job.status === "queued" || job.status === "processing").length} video render job(s) still queued or processing.</p><div className="mt-3 flex flex-wrap items-center gap-2"><button type="button" onClick={async()=>{try{const latest=await internalRequest("/course-studio/jobs/"+jobId);setRenderJobs(latest.render_jobs||[]);setRenderJobsQueued((latest.render_jobs||[]).filter((job:any) => job.status === "queued" || job.status === "processing").length);}catch(error:any){setCreateDraftError(error.message||"Could not refresh video status.");}}} className="rounded-lg border border-white/10 px-3 py-2 text-xs font-semibold text-slate-300">Refresh video status</button>{renderJobs.map(job=><span key={job.id} className="rounded-full border border-white/10 px-2.5 py-1 text-[10px] uppercase tracking-wide text-slate-400">{job.status}</span>)}</div>{renderJobs.some(job=>job.status==="failed")&&<p className="mt-2 text-xs text-amber-200">One or more videos need attention. Retry the failed video before publication.</p>}{canPublish && !publishedCourse && <div className="mt-4 border-t border-white/10 pt-4"><button type="button" onClick={() => void publishCourse()} disabled={publishBusy || renderJobs.some(job => job.status !== "completed")} className="rounded-xl bg-[#d7ad35] px-4 py-3 text-sm font-semibold text-black disabled:cursor-not-allowed disabled:opacity-40">{publishBusy ? "Publishing course…" : "Publish course"}</button>{publishError && <p role="alert" className="mt-3 text-xs text-red-200">{publishError}</p>}</div>}{publishedCourse && <p className="mt-3 text-xs font-semibold text-emerald-200">Published successfully.</p>}{publishedCourse && canPublish && targetTrackId && tracks.find(track => track.id === targetTrackId)?.status !== "published" && <div className="mt-4 border-t border-white/10 pt-4"><button type="button" onClick={() => void publishSelectedTrack()} disabled={trackPublishBusy} className="rounded-xl border border-[#d7ad35]/40 px-4 py-3 text-sm font-semibold text-[#e7c76d] disabled:opacity-40">{trackPublishBusy ? "Publishing track…" : "Publish learning track"}</button>{trackPublishError && <p role="alert" className="mt-3 text-xs text-red-200">{trackPublishError}</p>}</div>}</div>}
              </div>
            </section>}
          </div>

          <aside className="h-fit rounded-2xl border border-white/10 bg-white/[.025] p-5 lg:sticky lg:top-6">
            <p className="text-xs font-bold uppercase tracking-[.16em] text-[#d7ad35]">Production rules</p>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-400"><li>One lesson should teach one manageable idea.</li><li>Videos should usually be 1–3 minutes and never exceed 5 minutes.</li><li>The script teaches; the short note reinforces. They are not the same thing.</li><li>Use a real screen demonstration for software and code where appropriate.</li><li>Do not force video into lessons better taught through text or practice.</li><li>AI output is a draft. A human review and explicit publication step are required.</li></ul>
            <div className="mt-5 border-t border-white/10 pt-4"><p className="text-xs font-bold uppercase tracking-wider text-slate-500">Current status</p><p className="mt-2 text-sm text-slate-300">{createdCourseId ? "Draft course created — awaiting publication" : curriculum ? "Curriculum proposal saved as a private draft" : "Waiting for course brief"}</p><p className="mt-1 text-xs leading-5 text-slate-500">Course outlines and lesson packages are saved privately. Creating a draft course requires explicit staff approval; video rendering and publication are separate later steps.</p></div>
          </aside>
        </section>
      </div>
    </main>
  );
}
