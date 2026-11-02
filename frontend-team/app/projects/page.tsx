"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import Shell from "../../components/Shell";
import { request, teamMe } from "../../lib/api";

type Project = { id:string; course_id?:string|null; title:string; description?:string|null; instructions:string; skills:string[]; is_published:boolean; course?:any; skill_records?:any[] };
type Skill = { id:string; name:string; category?:string|null; description?:string|null };

export default function ProjectsWorkspace(){
 const [roles,setRoles]=useState<string[]>([]);
 const [projects,setProjects]=useState<Project[]>([]);
 const [skills,setSkills]=useState<Skill[]>([]);
 const [courses,setCourses]=useState<any[]>([]);
 const [selected,setSelected]=useState("");
 const [detail,setDetail]=useState<Project|null>(null);
 const [submissions,setSubmissions]=useState<any[]>([]);
 const [title,setTitle]=useState("");
 const [description,setDescription]=useState("");
 const [instructions,setInstructions]=useState("");
 const [courseId,setCourseId]=useState("");
 const [selectedSkills,setSelectedSkills]=useState<string[]>([]);
 const [newSkill,setNewSkill]=useState("");
 const [newSkillCategory,setNewSkillCategory]=useState("");
 const [score,setScore]=useState("70");
 const [feedback,setFeedback]=useState("");
 const [decision,setDecision]=useState<"approved"|"returned">("returned");
 const [reviewing,setReviewing]=useState("");
 const [loading,setLoading]=useState(true);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState("");
 const [notice,setNotice]=useState("");

 const load=useCallback(async()=>{
  setLoading(true);setError("");
  try{
   const [p,s,c]=await Promise.all([
    request<any>("/projects"),
    request<any>("/projects/skills"),
    request<any>("/content/courses")
   ]);
   setProjects(p.projects||[]);setSkills(s.skills||[]);
   setCourses((c.courses||[]).filter((x:any)=>x.ownership==="learnora"&&!x.organisation_id));
  }catch(e:any){setError(e.message||"Project workspace could not be loaded.");}
  finally{setLoading(false);}
 },[]);
 const loadDetail=useCallback(async(id:string)=>{
  if(!id){setDetail(null);setSubmissions([]);return;}
  try{
   const [s]=await Promise.all([request<any>("/projects/"+encodeURIComponent(id)+"/submissions")]);
   setDetail(projects.find(p=>String(p.id)===String(id))||null);setSubmissions(s.submissions||[]);
  }catch(e:any){setError(e.message||"Project details could not be loaded.");}
 },[projects]);
 useEffect(()=>{teamMe().then(x=>setRoles(x.roles||[])).catch(e=>setError(e.message||"Staff session unavailable."));void load();},[load]);
 useEffect(()=>{if(selected)void loadDetail(selected);else{setDetail(null);setSubmissions([])}},[selected,loadDetail]);

 async function act(fn:()=>Promise<any>,message:string){
  setBusy(true);setError("");setNotice("");
  try{await fn();await load();if(selected)await loadDetail(selected);setNotice(message);}
  catch(e:any){setError(e.message||"The operation could not be completed.");}
  finally{setBusy(false);}
 }
 async function create(e:FormEvent){
  e.preventDefault();
  await act(async()=>{
   const r=await request<any>("/projects",{method:"POST",body:JSON.stringify({title,description,instructions,course_id:courseId||null,skills:selectedSkills})});
   setTitle("");setDescription("");setInstructions("");setCourseId("");setSelectedSkills([]);
   setSelected(r.project.id);
  },"Draft project created.");
 }
 async function save(){
  if(!detail)return;
  await act(()=>request("/projects/"+encodeURIComponent(detail.id),{method:"PATCH",body:JSON.stringify({title:detail.title,description:detail.description,instructions:detail.instructions,course_id:detail.course_id||null,skills:detail.skills||[]})}),"Project saved.");
 }
 async function publish(){
  if(!detail)return;
  await act(()=>request("/projects/"+encodeURIComponent(detail.id),{method:"PATCH",body:JSON.stringify({is_published:!detail.is_published})}),detail.is_published?"Project unpublished.":"Project published.");
 }
 async function addSkill(e:FormEvent){
  e.preventDefault();
  await act(async()=>{await request("/projects/skills",{method:"POST",body:JSON.stringify({name:newSkill,category:newSkillCategory||null})});setNewSkill("");setNewSkillCategory("");},"Skill added.");
 }
 async function review(submissionId:string){
  await act(()=>request("/projects/"+encodeURIComponent(selected)+"/submissions/"+encodeURIComponent(submissionId)+"/review",{method:"POST",body:JSON.stringify({score:Number(score),feedback,decision})}),"Submission review saved.");
  setReviewing("");setFeedback("");
 }
 const toggleSkill=(id:string)=>setSelectedSkills(v=>v.includes(id)?v.filter(x=>x!==id):[...v,id]);
 const projectFrozen=Boolean(detail&&submissions.length>0);
 return <Shell roles={roles} active="projects">
  <header className="border-b border-white/[.1] pb-6"><p className="section-kicker">Learning operations / Practice Lab</p><h1 className="mt-3 font-display text-4xl sm:text-5xl">Projects & skill evidence</h1><p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">Create practical projects, map them to skills, publish learner work and review submissions. Only staff-approved project evidence contributes to verified mastery.</p></header>
  {error&&<p role="alert" className="notice error mt-5">{error}</p>}{notice&&<p role="status" className="notice ok mt-5">{notice}</p>}
  <div className="mt-6 grid gap-5 xl:grid-cols-[.8fr_1.2fr]">
   <section className="panel">
    <h2>Create a practical project</h2>
    <form onSubmit={create} className="mt-4 grid gap-3">
     <input className="field" placeholder="Project title" value={title} onChange={e=>setTitle(e.target.value)} required minLength={3}/>
     <textarea className="field min-h-20" placeholder="Short description" value={description} onChange={e=>setDescription(e.target.value)}/>
     <textarea className="field min-h-32" placeholder="Project brief and submission requirements" value={instructions} onChange={e=>setInstructions(e.target.value)} required minLength={10}/>
     <select className="field" value={courseId} onChange={e=>setCourseId(e.target.value)}><option value="">Standalone project</option>{courses.map(c=><option key={c.id} value={c.id}>{c.title}</option>)}</select>
     <div><p className="label mb-2">Skills this project assesses</p><div className="grid max-h-40 gap-2 overflow-y-auto sm:grid-cols-2">{skills.map(s=><label key={s.id} className="flex items-center gap-2 text-xs text-slate-300"><input type="checkbox" checked={selectedSkills.includes(s.id)} onChange={()=>toggleSkill(s.id)}/>{s.name}</label>)}</div></div>
     <button className="action" disabled={busy||!title.trim()||instructions.trim().length<10||!selectedSkills.length}>Create draft project</button>
    </form>
    <form onSubmit={addSkill} className="mt-6 border-t border-white/[.08] pt-5"><h3 className="text-sm font-semibold">Add a skill to the catalogue</h3><div className="mt-3 grid gap-2"><input className="field" placeholder="Skill name" value={newSkill} onChange={e=>setNewSkill(e.target.value)} required minLength={2}/><input className="field" placeholder="Category (optional)" value={newSkillCategory} onChange={e=>setNewSkillCategory(e.target.value)}/><button className="mini" disabled={busy||newSkill.trim().length<2}>Add skill</button></div></form>
   </section>
   <section className="panel">
    <div className="flex flex-wrap items-center justify-between gap-3"><h2>Project catalogue</h2><span className="text-xs text-slate-500">{projects.length} projects</span></div>
    {loading?<p className="muted mt-4">Loading projects…</p>:projects.length?<div className="mt-4 grid gap-2">{projects.map(p=><button key={p.id} onClick={()=>setSelected(p.id)} className={"w-full border p-4 text-left "+(selected===p.id?"border-[var(--gold)]/60 bg-white/[.04]":"border-white/[.08] hover:border-white/[.2]")}><span className="flex flex-wrap justify-between gap-2"><strong className="text-sm">{p.title}</strong><span className="text-[10px] uppercase tracking-wider text-slate-500">{p.is_published?"Published":"Draft"}</span></span><span className="mt-2 block text-xs text-slate-500">{p.course?.title||"Standalone"} · {(p.skill_records||[]).map((s:any)=>s.name).join(", ")||"No mapped skills"}</span></button>)}</div>:<p className="muted mt-4">No practical projects yet. Create the first project using the form.</p>}
   </section>
  </div>
  {detail&&<section className="panel mt-5">
   <div className="flex flex-wrap items-start justify-between gap-3"><div><p className="section-kicker">Selected project</p><h2 className="mt-2">{detail.title}</h2></div><div className="flex gap-2"><button className="mini" disabled={busy||detail.is_published||projectFrozen} onClick={save}>Save changes</button><button className="action" disabled={busy} onClick={publish}>{detail.is_published?"Unpublish":"Publish"}</button></div></div>
   {projectFrozen&&<p className="mt-3 text-xs leading-6 text-amber-200">Project instructions, course association and skill mapping are locked after the first learner submission. Create a new project if the brief or mapped skills need to change.</p>}<div className="mt-4 grid gap-3 md:grid-cols-2"><input className="field" value={detail.title||""} disabled={detail.is_published||projectFrozen} onChange={e=>setDetail({...detail,title:e.target.value})}/><select className="field" value={detail.course_id||""} disabled={detail.is_published||projectFrozen} onChange={e=>setDetail({...detail,course_id:e.target.value||null})}><option value="">Standalone project</option>{courses.map(c=><option key={c.id} value={c.id}>{c.title}</option>)}</select><textarea className="field min-h-20 md:col-span-2" value={detail.description||""} disabled={detail.is_published||projectFrozen} onChange={e=>setDetail({...detail,description:e.target.value})}/><textarea className="field min-h-32 md:col-span-2" value={detail.instructions||""} disabled={detail.is_published||projectFrozen} onChange={e=>setDetail({...detail,instructions:e.target.value})}/></div>
   <div className="mt-3 flex flex-wrap gap-3">{skills.map(s=><label key={s.id} className="flex items-center gap-2 text-xs text-slate-300"><input type="checkbox" disabled={detail.is_published||projectFrozen} checked={(detail.skills||[]).includes(s.id)} onChange={()=>setDetail({...detail,skills:toggleDetail(detail.skills||[],s.id)})}/>{s.name}</label>)}</div>
   <div className="mt-7 border-t border-white/[.08] pt-5"><h3 className="font-semibold">Learner submissions ({submissions.length})</h3>{submissions.length?<div className="mt-3 grid gap-3">{submissions.map(s=><article key={s.id} className="border border-white/[.08] p-4"><div className="flex flex-wrap justify-between gap-2"><strong className="text-sm">{s.learner?.name||s.learner?.email||"Learner submission"}</strong><span className="text-xs text-slate-500">{s.status} · {s.score??"Not scored"}</span></div><p className="mt-2 text-xs text-slate-400">{s.description||"No description supplied."}</p>{s.feedback&&<p className="mt-2 border-l border-[var(--gold)]/40 pl-3 text-xs leading-6 text-slate-300">Previous feedback: {s.feedback}</p>}<div className="mt-2 flex flex-wrap gap-3 text-xs">{s.repository_url&&<a className="underline" href={s.repository_url} target="_blank" rel="noreferrer">Repository</a>}{s.live_url&&<a className="underline" href={s.live_url} target="_blank" rel="noreferrer">Live project</a>}{s.submission_url&&<a className="underline" href={s.submission_url} target="_blank" rel="noreferrer">Submission</a>}</div>{reviewing===s.id?<div className="mt-4 grid gap-2 md:grid-cols-3"><input className="field" type="number" min="0" max="100" value={score} onChange={e=>setScore(e.target.value)}/><select className="field" value={decision} onChange={e=>setDecision(e.target.value as any)}><option value="returned">Return with feedback</option><option value="approved">Approve as skill evidence (70%+)</option></select><textarea className="field md:col-span-3" placeholder="Feedback for learner" value={feedback} onChange={e=>setFeedback(e.target.value)}/><button className="action" disabled={busy||Number(score)<0||Number(score)>100||(decision==="approved"&&Number(score)<70)} onClick={()=>review(s.id)}>Save review</button></div>:<button className="mini mt-3" onClick={()=>{setReviewing(s.id);setScore(String(s.score??70));setFeedback(s.feedback||"");setDecision(s.status==="approved"?"approved":"returned")}}>Review submission</button>}</article>)}</div>:<p className="muted mt-3">No submissions have been received for this project.</p>}</div>
  </section>}
 </Shell>;
}
function toggleDetail(values:string[],id:string){return values.includes(id)?values.filter(x=>x!==id):[...values,id]}
