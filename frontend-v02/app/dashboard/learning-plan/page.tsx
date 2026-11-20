"use client";

import {useCallback,useEffect,useState} from "react";
import Link from "next/link";
import {ArrowLeft,ArrowRight,CalendarDays,Clock3,RefreshCw,Sparkles} from "lucide-react";
import Shell from "../../../components/dashboard/Shell";
import Skeleton from "../../../components/feedback/Skeleton";
import {request} from "../../../lib/api/client";

export default function LearningPlanPage(){
 const [tracks,setTracks]=useState<any[]>([]);
 const [trackId,setTrackId]=useState("");
 const [plan,setPlan]=useState<any>(null);
 const [loading,setLoading]=useState(true);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState("");
 const [notice,setNotice]=useState("");

 const load=useCallback(async()=>{
  setLoading(true);setError("");
  try{
   const [saved,catalogue]=await Promise.all([
    request<any>("/learner/learning-plan"),
    request<any>("/public/tracks")
   ]);
   setPlan(saved.plan||null);setTracks(catalogue.tracks||[]);
   if(catalogue.tracks?.length)setTrackId(current=>current||String(catalogue.tracks[0].id));
  }catch(e:any){setError(e.message||"Your learning plan could not be loaded.");}
  finally{setLoading(false);}
 },[]);
 useEffect(()=>{void load()},[load]);

 async function generatePlan(){
  setBusy(true);setError("");setNotice("");
  try{
   const result=await request<any>("/learner/learning-plan/generate",{method:"POST",body:JSON.stringify({track_id:trackId||null})});
   setPlan(result.plan);setNotice("Your optional learning plan is ready.");
  }catch(e:any){setError(e.message||"A learning plan could not be generated.");}
  finally{setBusy(false);}
 }
 async function archivePlan(){
  if(!plan?.id)return;
  setBusy(true);setError("");setNotice("");
  try{await request("/learner/learning-plan/"+encodeURIComponent(plan.id)+"/archive",{method:"POST"});setPlan(null);setNotice("Your plan has been archived. Your course and track enrolments are unchanged.");}
  catch(e:any){setError(e.message||"The plan could not be archived.");}
  finally{setBusy(false);}
 }

 if(loading)return <Shell active="learning"><Skeleton label="Loading your optional learning plan"/></Shell>;
 const data=plan?.plan_data||{};
 return <Shell active="learning">
  <div className="mx-auto max-w-5xl">
   <Link href="/dashboard" className="inline-flex items-center gap-2 text-xs text-slate-500 hover:text-white"><ArrowLeft size={14}/>Learning workspace</Link>
   <header className="mt-7 border-b border-white/[.1] pb-7">
    
    
    <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-400">Choose a published track and let Learnora help organise your study time. The track remains the source of truth: this plan only schedules existing courses and never changes the curriculum.</p>
   </header>
   {error&&<div role="alert" className="notice error mt-5">{error}</div>}
   {notice&&<div role="status" className="notice success mt-5">{notice}</div>}
   {!plan?<section className="mt-8 border border-white/[.08] bg-[#0e1319] p-5 sm:p-7">
    <div className="flex items-start gap-3"><Sparkles size={20} className="mt-1 gold"/><div><h2 className="text-lg font-semibold">Build a personalised study plan</h2><p className="mt-2 text-sm leading-6 text-slate-500">Your saved goal, experience, interests and weekly study time will shape the guidance. Course order and course details come from the published catalogue.</p></div></div>
    <label className="mt-6 block text-xs text-slate-500">Published track<select value={trackId} onChange={e=>setTrackId(e.target.value)} className="field mt-2 w-full"><option value="">Choose a flexible plan from published courses</option>{tracks.map(t=><option key={t.id} value={t.id}>{t.name} · {t.course_count} courses</option>)}</select></label>
    {!tracks.length&&<p className="mt-3 text-xs text-slate-500">No published tracks are available yet. You can still generate a flexible plan from published courses.</p>}
    <button type="button" onClick={()=>void generatePlan()} disabled={busy} className="mt-6 inline-flex min-h-12 items-center gap-2 bg-[#d7ad35] px-5 text-sm font-bold text-black disabled:opacity-50">{busy?"Preparing your plan…":"Generate my learning plan"}<ArrowRight size={15}/></button>
    <p className="mt-4 text-xs leading-5 text-slate-600">This is optional. You can browse and enrol in any available course without generating a plan.</p>
   </section>:<>
    <section className="mt-8 border border-white/[.08] bg-[#0e1319] p-5 sm:p-7">
     <div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-xs uppercase tracking-[.18em] gold">Your current plan</p><h2 className="mt-2 font-display text-2xl">{data.track?.name||"Flexible learning plan"}</h2><p className="mt-2 text-xs text-slate-500">{plan.weekly_time_minutes} minutes per week · {data.weeks?.length||0} planned weeks</p></div><div className="flex gap-2"><button type="button" disabled={busy} onClick={()=>void generatePlan()} className="mini inline-flex items-center gap-2"><RefreshCw size={13}/>Regenerate</button><button type="button" disabled={busy} onClick={()=>void archivePlan()} className="mini">Archive plan</button></div></div>
     <div className="mt-6 border-t border-white/[.07] pt-5"><h3 className="text-sm font-semibold">AI learning guidance</h3><p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-300">{data.ai_guidance||"Work through the scheduled courses in order and record one practical outcome from each study session."}</p><p className="mt-3 text-[10px] uppercase tracking-[.14em] text-slate-600">Generation: {data.generation_mode==="ai_assisted"?"AI-assisted":"Fallback guidance"}</p></div>
    </section>
    <section className="mt-8"><div className="flex items-center gap-3"><CalendarDays size={19} className="gold"/><div><h2 className="font-semibold">Your weekly schedule</h2><p className="mt-1 text-xs text-slate-500">Follow the order of the published track. You can adjust your own pace.</p></div></div>
     <div className="mt-5 space-y-3">{(data.weeks||[]).map((week:any)=><article key={week.week} className="border border-white/[.08] bg-[#0e1319] p-5"><div className="flex items-center justify-between gap-3"><h3 className="font-semibold">Week {week.week}</h3><span className="inline-flex items-center gap-1 text-xs text-slate-500"><Clock3 size={13}/>{Math.round((week.minutes||0)/60*10)/10} hours</span></div>{week.guidance&&<div className="mt-4 grid gap-3 border border-white/[.06] bg-black/10 p-4 sm:grid-cols-3"><div><p className="text-[10px] uppercase tracking-[.14em] gold">Focus</p><p className="mt-2 text-xs leading-6 text-slate-300">{week.guidance.focus}</p></div><div><p className="text-[10px] uppercase tracking-[.14em] gold">Practice</p><p className="mt-2 text-xs leading-6 text-slate-300">{week.guidance.practice}</p></div><div><p className="text-[10px] uppercase tracking-[.14em] gold">Reflect</p><p className="mt-2 text-xs leading-6 text-slate-300">{week.guidance.reflection}</p></div></div>}<div className="mt-4 divide-y divide-white/[.06]">{(week.tasks||[]).map((task:any,i:number)=><div key={task.course_id+"-"+i} className="flex flex-wrap items-center justify-between gap-3 py-3 first:pt-0 last:pb-0"><div className="min-w-0"><p className="text-sm font-medium">{task.course_title}</p><p className="mt-1 text-xs leading-5 text-slate-500">{task.focus}</p></div><Link href={"/courses/"+encodeURIComponent(task.course_id)} className="shrink-0 text-xs font-semibold gold">View course <ArrowRight size={12} className="inline"/></Link></div>)}</div></article>)}</div>
    </section>
   </>}
   <p className="mt-8 text-xs leading-6 text-slate-600">A learning plan is a planning aid, not a completion record. Learnora&apos;s course and assessment records remain authoritative for progress and completion.</p>
  </div>
 </Shell>;
}
