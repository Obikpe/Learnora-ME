"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowRight, BookOpen, Clock3, LockKeyhole, Check, ChevronDown } from "lucide-react";
import { course, structure } from "../../../lib/api/learning";
import { request } from "../../../lib/api/client";
import { currentUser, getCachedCurrentUser, organisationContext } from "../../../lib/api";
import PublicNav from "../../../components/public/PublicNav";
import PublicFooter from "../../../components/public/PublicFooter";
import Shell from "../../../components/dashboard/Shell";
import EmptyState from "../../../components/feedback/EmptyState";
import Skeleton from "../../../components/feedback/Skeleton";
import CourseWorkspace from "../../../components/course/CourseWorkspace";

export default function CourseDetail({params,searchParams}:{params:{id:string};searchParams:{enrol?:string}}) {
  const enrolIntent=searchParams?.enrol==="1";
  const [c,setC]=useState<any>(),[s,setS]=useState<any>(),[structureLoading,setStructureLoading]=useState(true),[freeMode,setFreeMode]=useState(false),[user,setUser]=useState<any>(()=>getCachedCurrentUser()),[authResolved,setAuthResolved]=useState(Boolean(getCachedCurrentUser())),[hasOrganisationContext,setHasOrganisationContext]=useState(false),[error,setError]=useState(""),[enrolError,setEnrolError]=useState(""),[enrolling,setEnrolling]=useState(false),[enrolled,setEnrolled]=useState(false);
  const autoEnrolStarted=useRef(false);
  const [showWorkspace,setShowWorkspace]=useState(false),[enrolmentResolved,setEnrolmentResolved]=useState(false);
  const explicitlyFree=Boolean(c?.settings?.is_free===true||c?.settings?.access_type==="free"||c?.settings?.price===0);
  const freeLaunchCourse=Boolean(freeMode&&c?.ownership==="learnora"&&!c?.organisation_id);
  const isFree=freeLaunchCourse||explicitlyFree;
  const assignedLearner=Boolean(user?.account_type==="cohort"||user?.cohort_id||user?.organisation_id||user?.organisation_role||user?.role==="witstart"||(user?.organisation_memberships||[]).some((membership:any)=>["learner","member"].includes(membership.role)&&membership.status==="active"));
  const individualLearner=user?.role==="normal"&&user?.account_type==="learner"&&!hasOrganisationContext&&!assignedLearner;
  const canEnrol=Boolean(user)&&!assignedLearner&&((freeLaunchCourse&&individualLearner)||(explicitlyFree&&user.role === "normal"));
  useEffect(()=>{let active=true;autoEnrolStarted.current=false;setC(undefined);setS(undefined);setError("");setEnrolError("");setEnrolled(false);setShowWorkspace(false);setEnrolmentResolved(false);setStructureLoading(true);setHasOrganisationContext(Boolean(organisationContext()));currentUser().then(me=>{if(!active)return;if(me.account_type==="cohort"){setUser(me);window.location.replace("/dashboard/cohort");return;}setUser(me)}).catch(()=>{if(active)setUser(null)}).finally(()=>{if(active)setAuthResolved(true)});course(params.id).then(result=>{if(active)setC(result.course||result)}).catch(x=>{if(active)setError(x.message||"Course could not be loaded.")});request<any>("/access/mode").then(mode=>{if(active)setFreeMode(Boolean(mode.free_access_mode))}).catch(()=>{});structure(params.id).then(result=>{if(active)setS(result)}).catch(()=>{}).finally(()=>{if(active)setStructureLoading(false)});return()=>{active=false}},[params.id]);
  async function enrol(){setEnrolError("");if(!user){window.location.assign("/login?next="+encodeURIComponent("/courses/"+encodeURIComponent(params.id)+"?enrol=1"));return;}setEnrolling(true);try{await request<any>("/courses/"+encodeURIComponent(params.id)+"/enrol",{method:"POST"});setEnrolled(true);setShowWorkspace(true)}catch(e:any){setEnrolError(e.message||"Enrolment is not available for this course.")}finally{setEnrolling(false)}}
  useEffect(()=>{if(!authResolved||user||!enrolIntent||typeof window==="undefined")return;{const next="/courses/"+encodeURIComponent(params.id)+"?enrol=1";window.location.replace("/login?next="+encodeURIComponent(next));}},[authResolved,user,params.id,enrolIntent]);
  useEffect(()=>{if(!authResolved||!user||!c)return;let active=true;request<any>("/progress/me").then(result=>{if(!active)return;const existing=(result.courses||[]).some((row:any)=>String(row.course?.id||row.enrolment?.course_id)===String(params.id));if(assignedLearner&&!existing){window.location.replace(user?.account_type==="cohort"?"/dashboard/cohort":"/dashboard");return;}setEnrolled(existing);setEnrolmentResolved(true);if(existing){setShowWorkspace(true);return;}if(canEnrol&&enrolIntent&&!autoEnrolStarted.current){autoEnrolStarted.current=true;void enrol();}}).catch(()=>{if(assignedLearner)window.location.replace(user?.account_type==="cohort"?"/dashboard/cohort":"/dashboard");else setEnrolmentResolved(true)});return()=>{active=false}},[authResolved,user,c,params.id,canEnrol,enrolIntent]);
  const signedIn=Boolean(user);
  if(enrolIntent&&!authResolved)return <main className="min-h-screen bg-[var(--bg)] px-5 pt-28"><div className="mx-auto max-w-[82rem]"><Skeleton variant="course" label="Checking sign-in"/></div></main>;
  if(enrolIntent&&authResolved&&!user)return <main className="min-h-screen bg-[var(--bg)] px-5 pt-28"><div className="mx-auto max-w-[82rem]"><Skeleton variant="course" label="Redirecting to sign-in"/></div></main>;
  if(showWorkspace&&user)return <CourseWorkspace params={{courseId:params.id}} courseTitle={c?.title}/>;
  const pageContent=error?<main className={`mx-auto max-w-5xl px-5 pb-24 ${signedIn?"pt-12":"pt-36"}`}><EmptyState title="Course unavailable" message={error}/><a href="/courses" className="mt-5 inline-flex items-center gap-2 text-sm font-semibold gold">Back to courses <ArrowRight size={15}/></a></main>:!c?<main className="mx-auto max-w-[82rem] px-5 pb-24 pt-12 lg:px-8"><Skeleton variant="course" label="Loading course details"/></main>:null;
  if(!c&&!error)return <main className="min-h-screen bg-[var(--bg)] px-5 pt-28"><div className="mx-auto max-w-[82rem]"><Skeleton variant="course" label="Loading course details"/></div></main>;
  if(pageContent)return signedIn?<Shell active="discover">{pageContent}</Shell>:<><PublicNav/>{pageContent}<PublicFooter/></>;
  const modules=s?.modules||s?.structure?.modules||[];
  const lessonCount=modules.reduce((n:number,m:any)=>n+(m.lessons||[]).length,0);
  const pageBody=<main className={`mx-auto max-w-[82rem] px-5 pb-24 ${signedIn?"pt-8":"pt-32"} lg:px-8`}>
      <nav aria-label="Breadcrumb" className="mb-8 flex flex-wrap items-center gap-2 text-xs text-slate-600"><a href="/" className="hover:text-slate-300">Home</a><span>/</span><a href="/courses" className="hover:text-slate-300">Courses</a><span>/</span><span className="max-w-[18rem] truncate text-slate-400">{c.title}</span></nav>
      <section className="grid gap-10 xl:grid-cols-[minmax(0,1fr)_23rem] xl:gap-16">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-3"><span className="section-kicker">{c.level||"Learnora course"}</span><span className="h-px w-8 bg-white/20"/><span className="text-xs text-slate-500">{c.ownership==="organisation"?"Organisation programme":c.ownership==="creator"?"Creator course":"Learnora learning"}</span></div>
          <h1 className="mt-6 max-w-4xl font-display text-5xl leading-[1.02] tracking-[-.05em] sm:text-6xl lg:text-7xl">{c.title}</h1>
          <p className="mt-7 max-w-3xl text-lg leading-8 text-slate-300">{c.description||c.short_description||"Explore the curriculum and course objectives."}</p>
          <div className="mt-8 flex flex-wrap gap-x-6 gap-y-3 border-y border-white/[.1] py-5 text-sm text-slate-400">
            <span className="inline-flex items-center gap-2"><Clock3 size={16} className="text-[var(--gold-light)]"/>{c.estimated_hours?c.estimated_hours+" estimated hours":"Self-paced"}</span>
            <span className="inline-flex items-center gap-2"><BookOpen size={16} className="text-[var(--gold-light)]"/>{structureLoading?"…":modules.length} modules</span>
            <span className="inline-flex items-center gap-2"><Check size={16} className="text-[var(--gold-light)]"/>{structureLoading?"…":lessonCount} lessons listed</span>
          </div>
          <div className="mt-10 grid gap-4 sm:grid-cols-2">
            <div className="border-l border-[var(--gold)]/60 pl-4"><p className="text-sm font-semibold">Learn with structure</p><p className="mt-2 text-sm leading-6 text-slate-500">Follow the published curriculum in sequence, with clear lesson context.</p></div>
            <div className="border-l border-[var(--gold)]/60 pl-4"><p className="text-sm font-semibold">Build a record of progress</p><p className="mt-2 text-sm leading-6 text-slate-500">Your activity can help you see what you have completed and what comes next.</p></div>
          </div>
        </div>

        <aside className="h-fit border border-white/[.12] bg-[#11171e] xl:sticky xl:top-28">
          <div className="border-b border-white/[.1] px-6 py-5"><p className="text-[10px] font-bold uppercase tracking-[.2em] text-slate-500">Course access</p><h2 className="mt-2 font-display text-3xl">{isFree?"Your next step starts here":"Access by arrangement"}</h2></div>
          <div className="p-6">
            <p className="text-sm leading-7 text-slate-400">{isFree?(freeMode&&c.ownership==="learnora"?"Learnora is currently free for individual learners. Enrol to start learning and keep your progress with your account.":"This published course is marked as free. Enrol to start learning and keep your progress with your account."):"Self-enrolment is not enabled for this course. Access may depend on an organisation assignment or another access policy; Learnora will not bypass that requirement."}</p>
            <div className="my-5 border-y border-white/[.09] py-4"><div className="flex items-center justify-between py-1.5 text-sm"><span className="text-slate-500">Modules</span><span className="tabular-nums">{structureLoading?"…":modules.length}</span></div><div className="flex items-center justify-between py-1.5 text-sm"><span className="text-slate-500">Lessons</span><span className="tabular-nums">{structureLoading?"…":lessonCount}</span></div><div className="flex items-center justify-between py-1.5 text-sm"><span className="text-slate-500">Pace</span><span>{c.estimated_hours?c.estimated_hours+" hours":"Flexible"}</span></div></div>
            {canEnrol&&!enrolled?<button onClick={enrol} disabled={enrolling} className="flex min-h-12 w-full items-center justify-center gap-2 rounded-lg bg-[var(--gold)] px-5 text-sm font-bold text-[#17140d] transition-colors hover:bg-[var(--gold-light)] disabled:cursor-not-allowed disabled:opacity-50">{enrolling?"Enrolling…":"Enrol for free"}<ArrowRight size={16}/></button>:canEnrol&&enrolled?<a href={"/courses/"+encodeURIComponent(params.id)} className="flex min-h-12 w-full items-center justify-center gap-2 rounded-lg bg-[var(--gold)] px-5 text-sm font-bold text-[#17140d]">Continue learning <ArrowRight size={15}/></a>:isFree&&!user?<a href={"/login?next="+encodeURIComponent("/courses/"+params.id+"?enrol=1")} className="flex min-h-12 items-center justify-center gap-2 rounded-lg bg-[var(--gold)] px-5 text-sm font-bold text-[#17140d]">Enrol for free <ArrowRight size={15}/></a>:freeLaunchCourse&&!individualLearner&&user?.role==="normal"?<a href={"/login?next="+encodeURIComponent("/courses/"+params.id)} className="flex min-h-12 items-center justify-center gap-2 rounded-lg border border-white/[.16] px-5 text-sm font-semibold">Switch to individual learning <ArrowRight size={15}/></a>:isFree?<a href="/dashboard" className="flex min-h-12 items-center justify-center gap-2 rounded-lg border border-white/[.16] px-5 text-sm font-semibold">Go to My Learning <ArrowRight size={15}/></a>:<a href="/get-started" className="flex min-h-12 items-center justify-center gap-2 rounded-lg border border-white/[.16] px-5 text-sm font-semibold transition-colors hover:border-white/30 hover:bg-white/[.03]">Ask about access <ArrowRight size={15}/></a>}
            {enrolError&&<div role="alert" className="mt-4 rounded-lg border border-amber-300/15 bg-amber-300/[.04] p-3 text-xs leading-5 text-amber-100/80">{enrolError} <a href="/login" className="font-semibold gold">Sign in</a></div>}
          </div>
        </aside>
      </section>

      <section className="mt-20 grid gap-10 lg:grid-cols-[.72fr_1.28fr] lg:gap-16">
        <div><p className="section-kicker">Course outline</p><h2 className="mt-4 max-w-md font-display text-4xl leading-tight sm:text-5xl">What you will work through.</h2></div>
        <div className="min-w-0">
          {structureLoading ? <div className="space-y-4 border-y border-white/[.1] py-8"><div className="h-4 w-2/3 animate-pulse bg-white/[.06]"/><div className="h-4 w-full animate-pulse bg-white/[.04]"/><div className="h-4 w-5/6 animate-pulse bg-white/[.04]"/></div> : modules.length? <div className="divide-y divide-white/[.1] border-y border-white/[.1]">{modules.map((m:any,i:number)=><details key={m.id} open={i===0} className="group">
            <summary className="flex min-h-20 cursor-pointer list-none items-center justify-between gap-4 py-5 [&::-webkit-details-marker]:hidden"><div className="flex min-w-0 items-start gap-4"><span className="pt-1 text-xs tabular-nums text-[var(--gold-light)]">{String(i+1).padStart(2,"0")}</span><div className="min-w-0"><h3 className="font-semibold text-slate-100">{m.title}</h3>{m.description&&<p className="mt-1 text-sm leading-6 text-slate-500">{m.description}</p>}<p className="mt-2 text-xs text-slate-600">{(m.lessons||[]).length} lessons</p></div></div><ChevronDown size={17} className="shrink-0 text-slate-500 transition-transform group-open:rotate-180"/></summary>
            <div className="pb-5 pl-8 sm:pl-10"><div className="divide-y divide-white/[.06]">{(m.lessons||[]).map((l:any)=><div key={l.id} className="flex items-start justify-between gap-4 py-3"><div><p className="text-sm text-slate-300">{l.title}</p>{l.description&&<p className="mt-1 text-xs leading-5 text-slate-500">{l.description}</p>}</div><span className="shrink-0 pt-0.5 text-xs text-slate-600">{l.duration_minutes?l.duration_minutes+" min":l.lesson_type||""}</span></div>)}</div></div>
          </details>)}</div>:<EmptyState title="Curriculum not published" message="This course has no published modules or lessons available yet."/>}
        </div>
      </section>

      
    </main>;
  return signedIn?<Shell active="discover">{pageBody}</Shell>:<><PublicNav/>{pageBody}<PublicFooter/></>;
}
