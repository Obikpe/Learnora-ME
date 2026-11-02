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
  const [publicReviews,setPublicReviews] = useState<any>(null);
  const [myReview,setMyReview] = useState<any>(null);
  const [reviewOpen,setReviewOpen] = useState(false);
  const [reviewDismissed,setReviewDismissed] = useState(false);
  const [reviewRating,setReviewRating] = useState(5);
  const [reviewComment,setReviewComment] = useState("");
  const [reviewConsent,setReviewConsent] = useState(false);
  const [reviewBusy,setReviewBusy] = useState(false);
  const [reviewError,setReviewError] = useState("");
  const [reviewNotice,setReviewNotice] = useState("");

  const loadProgress = useCallback(async () => {
    try {
      const result = await request<any>("/progress/tracks/"+encodeURIComponent(params.id));
      setProgress(result);
    } catch {
      setProgress(null);
    }
  }, [params.id]);

  const loadReviewData = useCallback(async (completed:boolean) => {
    try {
      const publicData = await request<any>("/track-reviews/tracks/"+encodeURIComponent(params.id));
      setPublicReviews(publicData);
    } catch {
      setPublicReviews(null);
    }
    if (completed) {
      try {
        const personal = await request<any>("/track-reviews/tracks/"+encodeURIComponent(params.id)+"/me");
        setMyReview(personal.review||null);
        if (personal.review) {
          setReviewRating(Number(personal.review.rating)||5);
          setReviewComment(personal.review.comment||"");
          setReviewConsent(Boolean(personal.review.public_consent));
        }
      } catch {
        setMyReview(null);
      }
    }
  },[params.id]);

  useEffect(() => {
    let active = true;
    setHasOrganisationContext(Boolean(organisationContext()));
    currentUser().then(me => { if (active) setUser(me); }).catch(() => { if (active) setUser(null); });
    request<any>("/public/tracks/"+encodeURIComponent(params.id))
      .then(async result => {
        if (!active) return;
        setTrack(result.track);
        try {
          const saved = await request<any>("/progress/tracks/"+encodeURIComponent(params.id));
          if (active) {
            setProgress(saved);
            await loadReviewData(Boolean(saved.completed));
          }
        } catch {
          if (active) {
            setProgress(null);
            await loadReviewData(false);
          }
        }
      })
      .catch(async e => {
        try {
          // Existing learners retain access to saved track progress after a
          // track is unpublished or archived from new learner discovery.
          const saved = await request<any>("/progress/tracks/"+encodeURIComponent(params.id));
          if (active) {
            setProgress(saved);
            setTrack({
              ...saved.track,
              courses: saved.courses,
              course_count: saved.courses?.length || 0,
              required_course_count: saved.required_courses || 0,
            });
            await loadReviewData(Boolean(saved.completed));
          }
        } catch {
          if (active) setError(e.message || "Track could not be loaded.");
        }
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [params.id,loadReviewData]);

  const nextCourse = useMemo(() => {
    const courses = progress?.courses || [];
    const enrolledCourses = courses.filter((item:any) => item.enrolled);
    return enrolledCourses.find((item:any) => item.required && !item.progress?.completed)
      || enrolledCourses.find((item:any) => !item.progress?.completed)
      || enrolledCourses[0]
      || courses.find((item:any) => item.required)
      || track?.courses?.[0];
  }, [progress, track]);

  async function saveReview(e:any) {
    e.preventDefault();
    setReviewBusy(true);setReviewError("");setReviewNotice("");
    const path="/track-reviews/tracks/"+encodeURIComponent(params.id)+"/me";
    try {
      const result=await request<any>(path,{
        method:myReview?"PATCH":"POST",
        body:JSON.stringify({rating:reviewRating,comment:reviewComment,public_consent:reviewConsent})
      });
      setMyReview(result.review);
      setReviewOpen(false);
      setReviewDismissed(false);
      setReviewNotice(reviewConsent?"Your review was saved and is awaiting staff approval before public display.":"Your review was saved privately.");
      await loadReviewData(true);
    } catch(e:any) {
      setReviewError(e.message||"Your review could not be saved.");
    } finally {
      setReviewBusy(false);
    }
  }

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

      {publicReviews&&<section className="mt-10 border-y border-white/[.08] py-7"><div className="flex flex-wrap items-end justify-between gap-4"><div><p className="section-kicker">Learner feedback</p><h2 className="mt-2 font-display text-3xl">Track reviews</h2></div>{publicReviews.rating_count>0&&<div className="text-right"><p className="text-2xl font-semibold tabular-nums">{publicReviews.average_rating} / 5</p><p className="text-xs text-slate-500">{publicReviews.rating_count} approved public review(s)</p></div>}</div>{publicReviews.reviews?.length?<div className="mt-5 grid gap-3 md:grid-cols-2">{publicReviews.reviews.map((review:any)=><article key={review.id} className="border border-white/[.08] bg-[#0e1319] p-5"><p className="text-sm gold" aria-label={review.rating+" out of 5 stars"}>{"★".repeat(review.rating)}{"☆".repeat(5-review.rating)}</p>{review.comment&&<p className="mt-3 text-sm leading-7 text-slate-300">{review.comment}</p>}<p className="mt-3 text-[10px] text-slate-600">Learner review · {review.created_at?new Date(review.created_at).toLocaleDateString():""}</p></article>)}</div>:<p className="mt-4 text-sm text-slate-500">No public reviews have been approved for this track yet.</p>}</section>}
      {isCompleted&&individualLearner&&<section className="mt-8 rounded-2xl border border-white/[.1] bg-[#0e1319] p-5 sm:p-6"><div className="flex flex-wrap items-start justify-between gap-4"><div><p className="section-kicker">Optional feedback</p><h2 className="mt-2 text-xl font-semibold">How was this learning track?</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">Your review is optional. It stays private unless you explicitly consent to public display and a staff moderator approves it.</p></div>{myReview&&<span className="text-xs text-slate-500">{myReview.public_consent?(myReview.moderation_status==="approved"?"Approved for public display":myReview.moderation_status==="rejected"?"Not approved for public display":"Awaiting moderation"):"Private review"}</span>}</div>{reviewError&&<p role="alert" className="mt-4 text-sm text-red-200">{reviewError}</p>}{reviewNotice&&<p role="status" className="mt-4 text-sm text-emerald-200">{reviewNotice}</p>}{myReview&&!reviewOpen?<div className="mt-4 flex flex-wrap items-center justify-between gap-3"><p className="text-sm text-slate-300">Your rating: {myReview.rating}/5 {myReview.public_consent?"· Public sharing requested":"· Private"}</p><button type="button" className="mini" onClick={()=>{setReviewOpen(true);setReviewNotice("");}}>Edit review / sharing consent</button></div>:!reviewOpen&&!reviewDismissed?<div className="mt-4 flex flex-wrap gap-3"><button type="button" className="action" onClick={()=>setReviewOpen(true)}>Leave an optional review</button><button type="button" className="mini" onClick={()=>setReviewDismissed(true)}>Not now</button></div>:null}{reviewOpen&&<form onSubmit={saveReview} className="mt-5 grid gap-4 border-t border-white/[.08] pt-5"><label className="grid gap-2 text-xs font-semibold text-slate-300">Your rating<select className="field max-w-xs" value={reviewRating} onChange={e=>setReviewRating(Number(e.target.value))}>{[5,4,3,2,1].map(n=><option key={n} value={n}>{n} / 5</option>)}</select></label><label className="grid gap-2 text-xs font-semibold text-slate-300">Comment (optional)<textarea className="field min-h-24" maxLength={2000} value={reviewComment} onChange={e=>setReviewComment(e.target.value)} placeholder="What worked well, and what could be improved?"/></label><label className="flex items-start gap-3 text-xs leading-6 text-slate-400"><input type="checkbox" className="mt-1" checked={reviewConsent} onChange={e=>setReviewConsent(e.target.checked)}/><span>I agree that Learnora may publish this rating and comment after staff approval. My name and email will not be shown. I can withdraw consent later.</span></label><div className="flex flex-wrap gap-2"><button type="submit" className="action" disabled={reviewBusy}>{reviewBusy?"Saving…":myReview?"Save changes":"Submit review"}</button><button type="button" className="mini" disabled={reviewBusy} onClick={()=>setReviewOpen(false)}>Cancel</button></div></form>}{reviewDismissed&&!myReview&&!reviewOpen&&<button type="button" className="mt-4 text-xs gold underline" onClick={()=>setReviewDismissed(false)}>Show review prompt</button>}</section>}
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
