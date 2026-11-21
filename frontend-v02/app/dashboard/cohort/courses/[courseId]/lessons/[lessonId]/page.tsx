"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, CheckCircle2, LoaderCircle, Save } from "lucide-react";
import Shell from "../../../../../../../components/dashboard/Shell";
import Skeleton from "../../../../../../../components/feedback/Skeleton";
import RichContent from "../../../../../../../components/course/RichContent";
import { request } from "../../../../../../../lib/api/client";

export default function CohortLessonPage() {
  const params = useParams();
  const courseId = String(params.courseId || "");
  const lessonId = String(params.lessonId || "");
  const [lesson, setLesson] = useState<any>(null);
  const [videos, setVideos] = useState<any[]>([]);
  const lastVideoSave = useRef(0);
  const [progress, setProgress] = useState<any>({ progress_percent: 0, completed: false, last_position_seconds: 0 });
  const [percent, setPercent] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    setNotice("");
    try {
      const [lessonResult, progressResult]: any[] = await Promise.all([
        request("/cohort-learning/me/courses/" + encodeURIComponent(courseId) + "/lessons/" + encodeURIComponent(lessonId)),
        request("/cohort-learning/me/courses/" + encodeURIComponent(courseId) + "/progress"),
      ]);
      setLesson(lessonResult.lesson);
      setVideos(lessonResult.videos || []);
      lastVideoSave.current = 0;
      const saved = (progressResult.progress || []).find((row: any) => String(row.lesson_id) === lessonId) || { progress_percent: 0, completed: false, last_position_seconds: 0 };
      setProgress(saved);
      setPercent(Number(saved.progress_percent || 0));
    } catch (e: any) {
      setError(e?.message || "This lesson could not be loaded. It may no longer be assigned to your account.");
    } finally {
      setLoading(false);
    }
  }, [courseId, lessonId]);

  useEffect(() => { if (courseId && lessonId) void load(); }, [load, courseId, lessonId]);

  async function saveProgress(completed = false, videoPercent?: number, positionSeconds?: number) {
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const result: any = await request("/cohort-learning/me/courses/" + encodeURIComponent(courseId) + "/lessons/" + encodeURIComponent(lessonId) + "/progress", {
        method: "PUT",
        body: JSON.stringify({
          progress_percent: completed ? 100 : Math.max(0, Math.min(100, Math.floor(videoPercent ?? percent))),
          completed,
          last_position_seconds: Math.max(0, Math.floor(positionSeconds ?? Number(progress.last_position_seconds || 0))),
        }),
      });
      const saved = result.progress || { progress_percent: completed ? 100 : percent, completed };
      setProgress(saved);
      setPercent(Number(saved.progress_percent || 0));
      setNotice(saved.completed ? "Lesson marked complete. Your progress is saved." : "Your progress has been saved.");
    } catch (e: any) {
      setError(e?.message || "Progress could not be saved. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Shell active="learning" restricted role="assigned" trackLearning={false}><Skeleton variant="course" label="Loading your assigned lesson"/></Shell>;

  return <Shell active="learning" restricted role="assigned" trackLearning={false}>
    <div className="mb-6">
      <Link href={"/dashboard/cohort/courses/" + encodeURIComponent(courseId)} className="inline-flex items-center gap-2 text-xs font-semibold text-[var(--text-muted)] hover:text-[var(--primary)]"><ArrowLeft size={14}/> Back to course lessons</Link>
    </div>

    {error && !lesson ? <section role="alert" className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
      <h1 className="text-lg font-bold text-[var(--text-heading)]">Lesson unavailable</h1>
      <p className="mt-2 text-sm text-[var(--text-muted)]">{error}</p>
      <button type="button" onClick={() => void load()} className="mt-4 text-sm font-semibold text-[var(--primary)]">Try again</button>
    </section> : lesson && <>
      <section className="border-b border-[var(--border)] pb-6">
        <p className="text-xs font-semibold uppercase tracking-wide text-[var(--primary)]">{lesson.module?.title || "Assigned lesson"}</p>
        <h1 className="mt-2 max-w-4xl text-2xl font-bold tracking-tight text-[var(--text-heading)] sm:text-3xl">{lesson.title}</h1>
        {lesson.description && <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--text-muted)]">{lesson.description}</p>}
      </section>

      {videos[0]?.signed_url ? <video
        key={videos[0].id}
        className="mt-6 aspect-video w-full rounded-xl bg-black object-contain"
        controls
        crossOrigin="anonymous"
        playsInline
        preload="metadata"
        src={videos[0].signed_url}
        onLoadedMetadata={event => {
          const player = event.currentTarget;
          const resumeAt = Number(progress.last_position_seconds || 0);
          if (resumeAt > 0 && resumeAt < Math.max(0, player.duration - 3)) {
            player.currentTime = resumeAt;
            lastVideoSave.current = resumeAt;
          }
        }}
        onTimeUpdate={event => {
          const player = event.currentTarget;
          if (player.duration && player.currentTime - lastVideoSave.current >= 30) {
            lastVideoSave.current = player.currentTime;
            void saveProgress(false, player.currentTime / player.duration * 100, player.currentTime);
          }
        }}
        onPause={event => {
          const player = event.currentTarget;
          if (player.duration && !player.ended) {
            lastVideoSave.current = player.currentTime;
            void saveProgress(false, player.currentTime / player.duration * 100, player.currentTime);
          }
        }}
        onEnded={event => {
          const player = event.currentTarget;
          lastVideoSave.current = player.currentTime;
          void saveProgress(true, 100, player.currentTime);
        }}
      /> : videos[0]?.provider === "youtube" && videos[0]?.external_video_id
        ? <iframe title={lesson.title || "Lesson video"} className="mt-6 aspect-video w-full rounded-xl bg-black" src={"https://www.youtube.com/embed/" + encodeURIComponent(videos[0].external_video_id)} allowFullScreen/>
        : videos[0]?.provider === "vimeo" && videos[0]?.external_video_id
          ? <iframe title={lesson.title || "Lesson video"} className="mt-6 aspect-video w-full rounded-xl bg-black" src={"https://player.vimeo.com/video/" + encodeURIComponent(videos[0].external_video_id)} allowFullScreen/>
          : null}

      {lesson.content
        ? <article className="mt-6 rounded-xl border border-[var(--border)] bg-[var(--card)] p-5 sm:p-8">
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-[var(--text-muted)]">Lesson notes and key ideas</h2>
            <RichContent content={typeof lesson.content === "string" ? lesson.content : JSON.stringify(lesson.content, null, 2)}/>
          </article>
        : !videos.length ? <article className="mt-6 rounded-xl border border-[var(--border)] bg-[var(--card)] p-5 sm:p-8">
            <p className="py-6 text-center font-semibold text-[var(--text-heading)]">Lesson material is not available yet.</p>
          </article> : null}

      <section className="mt-6 rounded-xl border border-[var(--border)] bg-[var(--card)] p-5 sm:p-7">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div><h2 className="font-semibold text-[var(--text-heading)]">Your progress</h2><p className="mt-1 text-xs leading-5 text-[var(--text-muted)]">Progress is saved against your cohort account and this assigned lesson.</p></div>
          {progress.completed && <span className="inline-flex items-center gap-1 rounded-full bg-[var(--success-tint)] px-3 py-1.5 text-xs font-semibold text-[var(--success)]"><CheckCircle2 size={13}/> Completed</span>}
        </div>
        <label className="mt-6 block text-xs text-[var(--text-muted)]">Completion: <strong className="text-[var(--text-heading)]">{percent}%</strong>
          <input aria-label="Lesson completion percentage" type="range" min="0" max="100" step="5" value={percent} onChange={event => setPercent(Number(event.target.value))} className="mt-3 w-full accent-[var(--primary)]"/>
        </label>
        <div className="mt-4 h-2 overflow-hidden rounded-full bg-[var(--bg-soft)]"><div className="h-full rounded-full bg-[var(--primary)] transition-all" style={{ width: percent + "%" }}/></div>
        {error && <p role="alert" className="mt-4 text-sm text-[var(--warning)]">{error}</p>}
        {notice && <p role="status" className="mt-4 text-sm text-[var(--success)]">{notice}</p>}
        <div className="mt-6 flex flex-wrap gap-3">
          <button type="button" disabled={saving} onClick={() => void saveProgress(false)} className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-[var(--border)] px-4 py-3 text-sm font-semibold text-[var(--text-body)] hover:bg-[var(--bg-soft)] disabled:opacity-50">
            {saving ? <LoaderCircle className="animate-spin" size={15}/> : <Save size={15}/>} Save progress
          </button>
          <button type="button" disabled={saving} onClick={() => void saveProgress(true)} className="inline-flex min-h-11 items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-3 text-sm font-semibold text-[var(--on-primary)] hover:bg-[var(--primary-hover)] disabled:opacity-50">
            <CheckCircle2 size={15}/> Mark complete
          </button>
        </div>
      </section>
    </>}
  </Shell>;
}
