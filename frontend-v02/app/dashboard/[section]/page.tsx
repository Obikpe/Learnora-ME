"use client";
import { useEffect,useState } from "react";
import { ArrowRight, BookOpen, FileCheck2, Sparkles } from "lucide-react";
import { currentUser } from "../../../lib/api";
import { courses,progress,evidence } from "../../../lib/api/learning";
import { request } from "../../../lib/api/client";
import Shell from "../../../components/dashboard/Shell";
import SectionHeader from "../../../components/dashboard/SectionHeader";
import DataTable from "../../../components/dashboard/DataTable";
import EmptyState from "../../../components/feedback/EmptyState";
import CommunityBoard from "../../../components/dashboard/CommunityBoard";
import AccountSettings from "../../../components/dashboard/AccountSettings";
import Skeleton from "../../../components/feedback/Skeleton";

const labels:any={portfolio:"Portfolio",learning:"My learning",discover:"Discover",practice:"Practise",projects:"Projects",skills:"Skills",evidence:"Evidence",certificates:"Certificates",community:"Community",settings:"Settings"};
const descriptions:any={
 learning:"Return to enrolled courses and continue where you left off.",
 discover:"Explore published courses that are available to your account.",
 practice:"Work on practical projects, submit your work and receive structured feedback.",
 projects:"Review the practical work you have submitted through Learnora.",
 skills:"See the skills recorded in your learning profile and the evidence connected to them.",
 evidence:"Review the work and records attached to your learning journey.",
 certificates:"Claim certificates for completed courses and verify issued credentials.",
 portfolio:"Bring together your credentials, reviewed work and verified skills in one private portfolio.",
 community:"Ask questions and connect learning to the people who can support you.",
 settings:"Manage the profile and preferences currently available to your account."
};
export default function Page({params}:{params:{section:string}}){
 const [u,setU]=useState<any>(null),[data,setData]=useState<any>(null),[err,setErr]=useState(""),[loading,setLoading]=useState(true);
 useEffect(()=>{currentUser().then(me=>{if(me.role==="organisation_prospect"){location.href="/organisation-portal";return;}if(me.organisation_id&&["owner","admin"].includes(me.organisation_role)){location.href="/dashboard/organisation";return;}setU(me);}).catch(()=>location.href="/login")},[]);
 useEffect(()=>{
  if(!u)return;
  let cancelled=false;
  async function load(){
   setLoading(true);setErr("");setData(null);
   try{
    const s=params.section;
    const result=s==="discover"?await courses()
      :s==="learning"?await progress()
      :["evidence","skills"].includes(s)?await evidence()
      :s==="projects"?await request<any>("/evidence/projects/me")
      :s==="practice"?await request<any>("/evidence/projects")
      :s==="portfolio"?await Promise.all([evidence(),request<any>("/evidence/projects/me"),request<any>("/credentials/me")]).then(([ev,pr,cr])=>({evidence:ev.evidence||[],skills:ev.skills||[],certificates:cr.certificates||[],submissions:pr.submissions||[]}))
      :s==="certificates"?await request<any>("/credentials/me")
      :null;
    if(!cancelled)setData(result);
   }catch(e:any){if(!cancelled)setErr(e.message||"This area could not be loaded.");}
   finally{if(!cancelled)setLoading(false);}
  }
  load();return()=>{cancelled=true};
 },[u,params.section]);
 if(!u)return <Shell active={params.section}><Skeleton label="Verifying your account and preparing this section" /></Shell>;
 const section=params.section;
 const courseRows:any[]=(data?.data||data?.courses||[]).map((x:any)=>x.course?{id:x.course.id,title:x.course.title,level:x.course.level,status:x.enrolment?.status,completed_lessons:x.completed_lessons,tracked_lessons:x.tracked_lessons}:x);
 const evidenceRows=data?.evidence||[];
 const skills=data?.skills||[];
 const certs=data?.certificates||[];
 const submissions=data?.submissions||[];
 const eligibleCourses=data?.eligible_courses||[];
 return <Shell active={section}>
  <SectionHeader eyebrow="Your Learnora" title={labels[section]||"Learnora"} description={descriptions[section]||"Your learning workspace."}/>
  {loading?<div className="mt-8"><Skeleton variant="compact" label={"Loading "+(labels[section]||"your Learnora section")} /></div>:err?<div role="alert" className="mt-8 rounded-2xl border border-red-400/20 bg-red-400/[.05] p-5 text-sm text-red-200">{err}</div>:<>
   {section==="discover"&&<div className="mt-7"><DataTable rows={courseRows} emptyTitle="No published courses returned" emptyMessage="The course catalogue only shows courses that the backend has published and made available." columns={[{key:"title",label:"Course",render:r=><a className="font-medium text-white hover:gold" href={"/courses/"+r.id}>{r.title||"Untitled course"}</a>},{key:"level",label:"Level"},{key:"status",label:"Status"},{key:"estimated_hours",label:"Hours"}]}/></div>}
   {section==="learning"&&<div className="mt-7"><DataTable rows={courseRows} emptyTitle="Your learning starts here" emptyMessage="When you enrol in a course, it will appear here with its current progress." columns={[{key:"title",label:"Course",render:r=><a className="font-medium text-white" href={"/dashboard/learning/"+r.id}>{r.title||"Course"}</a>},{key:"status",label:"Enrolment"},{key:"completed_lessons",label:"Completed lessons"},{key:"tracked_lessons",label:"Lessons tracked"}]}/></div>}
   {section==="evidence"&&<div className="mt-7"><DataTable rows={evidenceRows} emptyTitle="No evidence records yet" emptyMessage="Evidence will appear after a supported project, assessment or other learning activity is recorded." columns={[{key:"skill_name",label:"Skill"},{key:"verification_state",label:"Verification"},{key:"evidence_type",label:"Evidence type"},{key:"score",label:"Score"},{key:"created_at",label:"Added",render:r=>r.created_at?new Date(r.created_at).toLocaleDateString():"—"},{key:"notes",label:"Notes"}]}/><p className="mt-4 text-xs leading-6 text-slate-600">A saved evidence record is not automatically a verified skill. Review status is shown only when the backend has a corresponding review record.</p></div>}
   {section==="skills"&&<SkillMastery skills={skills}/>}
   {section==="portfolio"&&<PortfolioOverview data={data}/>}
   {section==="certificates"&&<CertificateCenter certificates={certs} eligibleCourses={eligibleCourses}/> }
   {section==="projects"&&<ProjectSubmissions submissions={submissions}/>}
   {section==="practice"&&<PracticeLab projects={data?.projects||[]}/>}
   {section==="community"&&<CommunityBoard/>}
   {section==="settings"&&<AccountSettings user={u}/>}
  </>}
 </Shell>;
}
function TargetIcon(){return <Sparkles className="gold" size={22}/>}

function PracticeLab({projects}:{projects:any[]}){
 const [items,setItems]=useState(projects);
 const [drafts,setDrafts]=useState<Record<string,any>>({});
 const [busy,setBusy]=useState("");
 const [notice,setNotice]=useState("");
 const [error,setError]=useState("");
 useEffect(()=>setItems(projects),[projects]);
 const value=(id:string)=>drafts[id]||{title:"",description:"",repository_url:"",live_url:"",submission_url:""};
 const update=(id:string,key:string,v:string)=>setDrafts(old=>({...old,[id]:{...value(id),[key]:v}}));
 async function submit(id:string){
  setBusy(id);setError("");setNotice("");
  try{const result=await request<any>("/evidence/projects/"+encodeURIComponent(id)+"/submissions",{method:"POST",body:JSON.stringify(value(id))});setNotice("Your project submission has been sent for review.");setItems(old=>old.map(p=>String(p.id)===String(id)?{...p,latest_submission:result.submission}:p));setDrafts(old=>({...old,[id]:{title:"",description:"",repository_url:"",live_url:"",submission_url:""}}));}
  catch(e:any){setError(e.message||"Your submission could not be saved.");}
  finally{setBusy("");}
 }
 return <div className="mt-7 space-y-4">
  <div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="text-xl font-semibold">Practical projects</h2><p className="mt-1 text-sm text-slate-500">Build something, submit your work and receive a review tied to the skills it demonstrates.</p></div><a href="/dashboard/projects" className="text-sm gold">My submissions <ArrowRight size={14} className="inline"/></a></div>
  {error&&<p role="alert" className="rounded-xl border border-red-400/20 p-3 text-sm text-red-200">{error}</p>}{notice&&<p role="status" className="rounded-xl border border-emerald-400/20 p-3 text-sm text-emerald-200">{notice}</p>}
  {items.length?items.map(p=><article key={p.id} className="rounded-2xl border border-white/[.08] bg-[#0e1319] p-5 sm:p-6"><div className="flex flex-wrap justify-between gap-3"><div><h3 className="text-lg font-semibold">{p.title}</h3><p className="mt-1 text-xs text-slate-500">{p.course?.title||"Independent project"}</p></div><span className="text-xs text-slate-500">{(p.skill_records||[]).map((s:any)=>s.name).join(" · ")}</span></div><p className="mt-3 text-sm leading-7 text-slate-400">{p.description||p.instructions}</p>{p.latest_submission&&<div className="mt-4 rounded-xl border border-white/[.08] bg-black/20 p-4"><p className="text-xs font-semibold">Latest submission: <span className={p.latest_submission.status==="approved"?"text-emerald-200":p.latest_submission.status==="returned"?"text-amber-200":"text-slate-300"}>{p.latest_submission.status}</span></p>{p.latest_submission.score!==null&&p.latest_submission.score!==undefined&&<p className="mt-1 text-xs text-slate-500">Score: {p.latest_submission.score}%</p>}{p.latest_submission.feedback&&<p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-400">{p.latest_submission.feedback}</p>}</div>}{(p.latest_submission?.status==="returned"||!p.latest_submission)&&<details className="mt-4"><summary className="cursor-pointer text-sm font-semibold gold">{p.latest_submission?.status==="returned"?"Revise and resubmit":"View brief and submit work"}</summary><div className="mt-4 grid gap-3"><div className="rounded-xl bg-black/20 p-4 text-sm leading-7 text-slate-300 whitespace-pre-wrap">{p.instructions}</div><input className="field" placeholder="Submission title (optional)" value={value(p.id).title} onChange={e=>update(p.id,"title",e.target.value)}/><textarea className="field min-h-24" placeholder="Describe what you built, your approach and what you learned" value={value(p.id).description} onChange={e=>update(p.id,"description",e.target.value)}/><input className="field" type="url" placeholder="Repository URL (https://…)" value={value(p.id).repository_url} onChange={e=>update(p.id,"repository_url",e.target.value)}/><input className="field" type="url" placeholder="Live project URL (https://…)" value={value(p.id).live_url} onChange={e=>update(p.id,"live_url",e.target.value)}/><input className="field" type="url" placeholder="Other submission URL (https://…)" value={value(p.id).submission_url} onChange={e=>update(p.id,"submission_url",e.target.value)}/><button className="action" disabled={busy===p.id} onClick={()=>submit(p.id)}>{busy===p.id?"Submitting…":"Submit project"}</button></div></details>}</article>):<EmptyState title="No practice projects are available yet" message="Published projects will appear here when Learnora Teams makes them available to learners."/>}
 </div>;
}
function SkillMastery({skills}:{skills:any[]}){
 const levels:any={advanced:"Advanced",competent:"Competent",developing:"Developing",not_started:"Not started"};
 return <div className="mt-7"><div className="grid gap-3 sm:grid-cols-3"><div className="rounded-xl border border-white/[.08] bg-[#0e1319] p-4"><p className="text-xs text-slate-500">Skills mapped</p><p className="mt-2 text-3xl font-semibold">{skills.length}</p></div><div className="rounded-xl border border-white/[.08] bg-[#0e1319] p-4"><p className="text-xs text-slate-500">With verified evidence</p><p className="mt-2 text-3xl font-semibold">{skills.filter(s=>(s.verified_evidence_count||0)>0).length}</p></div><div className="rounded-xl border border-white/[.08] bg-[#0e1319] p-4"><p className="text-xs text-slate-500">Advanced / competent</p><p className="mt-2 text-3xl font-semibold">{skills.filter(s=>["advanced","competent"].includes(s.status)).length}</p></div></div><div className="mt-5 grid gap-3 md:grid-cols-2">{skills.map(s=><article key={s.skill_id||s.id} className="rounded-xl border border-white/[.08] bg-[#0e1319] p-4"><div className="flex items-start justify-between gap-3"><div><h3 className="font-semibold">{s.skill_name||s.name}</h3><p className="mt-1 text-xs text-slate-500">{s.category||"Skill"} · {levels[s.status]||"Not assessed"}</p></div><strong className="text-sm tabular-nums">{s.proficiency||0}%</strong></div><div className="mt-3 h-2 overflow-hidden rounded-full bg-white/[.08]"><div className="h-full rounded-full bg-[var(--gold)]" style={{width:Math.max(0,Math.min(100,Number(s.proficiency)||0))+"%"}}/></div><p className="mt-2 text-xs text-slate-500">{s.verified_evidence_count||0} verified project evidence record(s)</p></article>)}</div><p className="mt-4 text-xs leading-6 text-slate-600">Mastery is calculated only from staff-approved project evidence. Course completion, self-reported skills and unreviewed submissions do not count as verified competence.</p></div>;
}
function ProjectSubmissions({submissions}:{submissions:any[]}){
 return <div className="mt-7 grid gap-4">{submissions.length?submissions.map(s=><article key={s.id} className="rounded-2xl border border-white/[.08] bg-[#0e1319] p-5"><div className="flex flex-wrap items-start justify-between gap-3"><div><h2 className="font-semibold">{s.project?.title||s.title||"Project submission"}</h2><p className="mt-1 text-xs text-slate-500">Submitted {s.submitted_at?new Date(s.submitted_at).toLocaleDateString():"—"}</p></div><span className="text-xs text-slate-400">{s.status||s.review_state||"Submitted"}{s.score!==null&&s.score!==undefined?" · "+s.score+"%":""}</span></div>{s.description&&<p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-400">{s.description}</p>}<div className="mt-3 flex flex-wrap gap-4 text-xs">{s.repository_url&&<a className="gold underline" href={s.repository_url} target="_blank" rel="noreferrer">Repository</a>}{s.live_url&&<a className="gold underline" href={s.live_url} target="_blank" rel="noreferrer">Live project</a>}{s.submission_url&&<a className="gold underline" href={s.submission_url} target="_blank" rel="noreferrer">Submission file</a>}</div>{s.feedback&&<div className="mt-4 rounded-xl border border-white/[.07] bg-black/20 p-4"><p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Reviewer feedback</p><p className="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-300">{s.feedback}</p></div>}</article>):<EmptyState title="Your project record starts with a first submission" message="Submitted projects will appear here with review status, feedback and links to your work. Explore the Practice Lab to find projects."/>}</div>;
}
function PortfolioOverview({data}:any){
 const verified=(data?.evidence||[]).filter((x:any)=>x.verification_state==="verified");
 const skills=data?.skills||[];
 const certs=data?.certificates||[];
 const projects=data?.submissions||[];
 return <div className="mt-7 space-y-5"><section className="rounded-2xl border border-white/[.08] bg-[#0e1319] p-6"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-xs uppercase tracking-widest gold">Learnora portfolio</p><h2 className="mt-3 text-2xl font-semibold">Your learning, practice and evidence</h2><p className="mt-2 max-w-2xl text-sm leading-7 text-slate-400">A private portfolio of credentials, reviewed project work and verified skills. Only reviewed evidence is presented as verified.</p></div><button className="mini" onClick={()=>window.print()}>Print / save as PDF</button></div><div className="mt-5 grid gap-3 sm:grid-cols-3"><div><p className="text-xs text-slate-500">Valid certificates</p><p className="mt-1 text-2xl font-semibold">{certs.filter((c:any)=>c.valid!==false).length}</p><p className="mt-1 text-[11px] text-slate-600">{certs.filter((c:any)=>c.valid===false).length} revoked</p></div><div><p className="text-xs text-slate-500">Reviewed project submissions</p><p className="mt-1 text-2xl font-semibold">{projects.filter((x:any)=>x.reviewed_at).length}</p></div><div><p className="text-xs text-slate-500">Verified skill evidence</p><p className="mt-1 text-2xl font-semibold">{verified.length}</p></div></div></section><section className="rounded-xl border border-white/[.08] bg-[#0e1319] p-5"><h3 className="font-semibold">Verified skills</h3>{skills.filter((s:any)=>(s.verified_evidence_count||0)>0).length?skills.filter((s:any)=>(s.verified_evidence_count||0)>0).map((s:any)=><div key={s.skill_id||s.id} className="border-b border-white/[.06] py-3 last:border-0"><div className="flex justify-between gap-3"><p className="text-sm font-medium">{s.skill_name||s.name}</p><p className="text-xs text-slate-400">{s.proficiency||0}% · {s.status}</p></div><p className="mt-1 text-xs text-slate-500">{s.verified_evidence_count} approved evidence record(s)</p></div>):<p className="mt-3 text-sm text-slate-500">Skills will appear here after practical work has been reviewed and approved.</p>}</section><section className="grid gap-4 md:grid-cols-2"><article className="rounded-xl border border-white/[.08] bg-[#0e1319] p-5"><h3 className="font-semibold">Credentials</h3>{certs.length?certs.map((c:any)=><p key={c.id} className="mt-3 text-sm">{c.course_title||"Course completion"} <span className="block text-xs text-slate-500">{c.certificate_number}</span><span className={"mt-1 block text-xs "+(c.valid===false?"text-red-300":"text-emerald-300")}>{c.valid===false?"Revoked":"Valid"}</span><a className="mt-1 inline-block text-xs gold underline" href={"/verify-certificate/"+encodeURIComponent(c.certificate_number)}>View verification</a></p>):<p className="mt-3 text-sm text-slate-500">No certificates issued yet.</p>}</article><article className="rounded-xl border border-white/[.08] bg-[#0e1319] p-5"><h3 className="font-semibold">Reviewed work</h3>{projects.length?projects.map((p:any)=><div key={p.id} className="mt-3 text-sm">{p.project?.title||p.title||"Project"} <span className="block text-xs text-slate-500">{p.review_state==="approved"?"Approved":p.review_state==="returned"?"Returned":p.review_state==="reviewed"?"Reviewed":"Awaiting review"} · {p.score??"Not scored"}</span><div className="mt-1 flex flex-wrap gap-3 text-xs">{p.repository_url&&<a className="gold underline" href={p.repository_url} target="_blank" rel="noreferrer">Repository</a>}{p.live_url&&<a className="gold underline" href={p.live_url} target="_blank" rel="noreferrer">Live work</a>}</div>{p.feedback&&<p className="mt-1 text-xs leading-5 text-slate-400">{p.feedback}</p>}</div>):<p className="mt-3 text-sm text-slate-500">Your submitted work will appear here.</p>}</article></section><p className="text-xs text-slate-600">This portfolio is private to your signed-in account. Public sharing requires a separate learner-controlled consent feature; this view does not publish personal information.</p></div>;
}
function CertificateCenter({certificates,eligibleCourses}:{certificates:any[];eligibleCourses:any[]}){
 const [busy,setBusy]=useState("");const [error,setError]=useState("");const [notice,setNotice]=useState("");const [items,setItems]=useState(certificates);
 async function claim(id:string){setBusy(id);setError("");setNotice("");try{const r=await request<any>("/credentials/courses/"+encodeURIComponent(id)+"/issue",{method:"POST"});setNotice(r.already_issued?"This certificate was already issued.":"Your certificate has been issued.");const fresh=await request<any>("/credentials/me");setItems(fresh.certificates||[]);}catch(e:any){setError(e.message||"Certificate could not be issued.");}finally{setBusy("");}}
 return <div className="mt-7 space-y-5">{error&&<p role="alert" className="text-sm text-red-200">{error}</p>}{notice&&<p role="status" className="text-sm text-emerald-200">{notice}</p>}<section className="rounded-2xl border border-white/[.08] bg-[#0e1319] p-5"><h2 className="font-semibold">Ready to claim</h2>{eligibleCourses.length?eligibleCourses.map(c=><div key={c.course_id} className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[.06] py-3 last:border-0"><div><p className="text-sm font-medium">{c.course_title}</p><p className="text-xs text-slate-500">Course requirements completed</p></div><button className="action" disabled={!!busy} onClick={()=>claim(c.course_id)}>{busy===c.course_id?"Issuing…":"Claim certificate"}</button></div>):<p className="mt-3 text-sm text-slate-500">Complete a course and its required assessments to become eligible for a certificate.</p>}</section><section className="rounded-2xl border border-white/[.08] bg-[#0e1319] p-5"><h2 className="font-semibold">Issued certificates</h2>{items.length?items.map(c=><div key={c.id} className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[.06] py-3 last:border-0"><div><p className="text-sm font-medium">{c.course_title}</p><p className="text-xs text-slate-500">{c.certificate_number} · {c.issued_at?new Date(c.issued_at).toLocaleDateString():""}</p><p className={"mt-1 text-xs "+(c.valid===false?"text-red-300":"text-emerald-300")}>{c.valid===false?"Revoked":"Valid"}</p></div><a className="text-sm gold underline" href={"/verify-certificate/"+encodeURIComponent(c.certificate_number)}>View verification</a></div>):<p className="mt-3 text-sm text-slate-500">No certificates issued yet.</p>}</section></div>;
}
