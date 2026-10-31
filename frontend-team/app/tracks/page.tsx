"use client";

import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import { Archive, ArrowDown, ArrowUp, BookOpen, Plus, Route, Save, Trash2 } from "lucide-react";
import Shell from "../../components/Shell";
import { request, teamMe } from "../../lib/api";

type Course = { id: string; title: string; slug?: string; status: string; ownership: string; organisation_id?: string | null };
type Track = { id: string; name: string; slug: string; description?: string | null; status: string; course_count: number };

export default function TracksWorkspace() {
  const [me,setMe]=useState<any>(null);
  const [tracks,setTracks]=useState<Track[]>([]);
  const [courses,setCourses]=useState<Course[]>([]);
  const [selectedId,setSelectedId]=useState("");
  const [detail,setDetail]=useState<any>(null);
  const [name,setName]=useState("");
  const [slug,setSlug]=useState("");
  const [description,setDescription]=useState("");
  const [courseId,setCourseId]=useState("");
  const [courseRequired,setCourseRequired]=useState(true);
  const [loading,setLoading]=useState(true);
  const [saving,setSaving]=useState(false);
  const [error,setError]=useState("");
  const [notice,setNotice]=useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [trackResult,courseResult]=await Promise.all([
        request<any>("/tracks"),
        request<any>("/content/courses"),
      ]);
      setTracks(trackResult.tracks||[]);
      setCourses((courseResult.courses||[]).filter((c:Course)=>c.ownership==="learnora"&&!c.organisation_id));
    } catch(e:any) {
      setError(e.message||"Track workspace could not be loaded.");
    } finally {
      setLoading(false);
    }
  },[]);

  const loadTrack = useCallback(async (id:string) => {
    if(!id){setDetail(null);return;}
    setDetail(null);
    try {
      const result=await request<any>("/tracks/"+encodeURIComponent(id));
      setDetail(result.track);
    } catch(e:any) {
      setError(e.message||"Track details could not be loaded.");
    }
  },[]);

  useEffect(()=>{
    teamMe().then(setMe).catch(e=>setError(e.message||"Your staff session could not be loaded."));
    void load();
  },[load]);

  useEffect(()=>{if(selectedId)void loadTrack(selectedId);else setDetail(null)},[selectedId,loadTrack]);

  const availableCourses=useMemo(()=>{
    const linked=new Set((detail?.courses||[]).map((item:any)=>String(item.course_id)));
    return courses.filter(course=>!linked.has(String(course.id)));
  },[courses,detail]);

  async function createTrack(e:FormEvent) {
    e.preventDefault();setError("");setNotice("");setSaving(true);
    try {
      const result=await request<any>("/tracks",{method:"POST",body:JSON.stringify({name,slug,description})});
      await load();
      setSelectedId(result.track.id);
      setName("");setSlug("");setDescription("");
      setNotice("Draft track created.");
    } catch(e:any) {setError(e.message||"Track could not be created.");}
    finally {setSaving(false);}
  }

  async function saveTrack() {
    if(!detail)return;
    setError("");setNotice("");setSaving(true);
    try {
      await request<any>("/tracks/"+encodeURIComponent(detail.id),{method:"PATCH",body:JSON.stringify({name:detail.name,slug:detail.slug,description:detail.description})});
      await load();await loadTrack(detail.id);setNotice("Track details saved.");
    } catch(e:any) {setError(e.message||"Track details could not be saved.");}
    finally {setSaving(false);}
  }

  async function setStatus(status:"published"|"draft"|"archived") {
    if(!detail)return;
    setError("");setNotice("");setSaving(true);
    try {
      await request<any>("/tracks/"+encodeURIComponent(detail.id),{method:"PATCH",body:JSON.stringify({status})});
      await load();await loadTrack(detail.id);setNotice(status==="published"?"Track published to the learner catalogue.":status==="archived"?"Track archived.":"Track returned to draft.");
    } catch(e:any) {setError(e.message||"Track status could not be changed.");}
    finally {setSaving(false);}
  }

  async function addCourse(e:FormEvent) {
    e.preventDefault();if(!detail||!courseId)return;
    setError("");setNotice("");setSaving(true);
    try {
      const order_index=(detail.courses||[]).reduce((max:number,item:any)=>Math.max(max,Number(item.order_index)||0),-1)+1;
      await request<any>("/tracks/"+encodeURIComponent(detail.id)+"/courses",{method:"POST",body:JSON.stringify({course_id:courseId,order_index,required:courseRequired})});
      setCourseId("");setCourseRequired(true);await loadTrack(detail.id);await load();setNotice("Course added to the track.");
    } catch(e:any) {setError(e.message||"Course could not be added.");}
    finally {setSaving(false);}
  }

  async function toggleRequired(item:any) {
    if(!detail)return;
    setSaving(true);setError("");setNotice("");
    try {
      await request<any>("/tracks/"+encodeURIComponent(detail.id)+"/courses",{method:"POST",body:JSON.stringify({course_id:item.course_id,order_index:item.order_index,required:!item.required})});
      await loadTrack(detail.id);setNotice("Course requirement updated.");
    } catch(e:any) {setError(e.message||"Course requirement could not be updated.");}
    finally {setSaving(false);}
  }

  async function moveCourse(index:number,direction:-1|1) {
    if(!detail)return;
    const items=[...(detail.courses||[])];
    const next=index+direction;
    if(next<0||next>=items.length)return;
    [items[index],items[next]]=[items[next],items[index]];
    const payload=items.map((item:any,i:number)=>({id:item.id,order_index:i}));
    setSaving(true);setError("");setNotice("");
    try {
      await request<any>("/tracks/"+encodeURIComponent(detail.id)+"/courses/reorder",{method:"PATCH",body:JSON.stringify(payload)});
      await loadTrack(detail.id);setNotice("Course order updated.");
    } catch(e:any) {setError(e.message||"Course order could not be updated.");}
    finally {setSaving(false);}
  }

  async function removeCourse(course_id:string) {
    if(!detail)return;
    setSaving(true);setError("");setNotice("");
    try {
      await request<any>("/tracks/"+encodeURIComponent(detail.id)+"/courses/"+encodeURIComponent(course_id),{method:"DELETE"});
      await loadTrack(detail.id);setNotice("Course removed from the track. Its course and learner progress were not deleted.");
    } catch(e:any) {setError(e.message||"Course could not be removed.");}
    finally {setSaving(false);}
  }

  if(!me)return <div className="p-10 text-slate-400">Loading secure workspace…</div>;

  return <Shell roles={me.roles||[]} active="tracks">
    <header className="border-b border-white/[.1] pb-6"><p className="section-kicker">Content operations / Tracks</p><h1 className="mt-3 font-display text-4xl tracking-tight sm:text-5xl">Learning tracks</h1><p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">Build global learner journeys from published Learnora courses. Tracks use the existing learning-path structure; personal paths, organisation paths and cohort track assignments remain separate.</p></header>

    {error&&<div role="alert" className="notice error mt-5">{error}</div>}
    {notice&&<div role="status" className="notice success mt-5">{notice}</div>}

    <section className="mt-7 grid gap-6 xl:grid-cols-[minmax(260px,.65fr)_minmax(0,1.35fr)]">
      <div className="space-y-5">
        <form onSubmit={createTrack} className="border border-white/[.08] bg-[#0e1319] p-5">
          <p className="section-kicker">New track</p><h2 className="mt-2 text-lg font-semibold">Create a draft</h2>
          <label className="mt-5 block text-xs text-slate-500">Track name<input required minLength={2} maxLength={120} value={name} onChange={e=>{setName(e.target.value);if(!slug||slug===slugify(name))setSlug(slugify(e.target.value))}} className="field mt-2 w-full" placeholder="e.g. Data Analytics Foundations"/></label>
          <label className="mt-4 block text-xs text-slate-500">URL slug<input required minLength={2} maxLength={140} pattern="[a-z0-9]+(-[a-z0-9]+)*" value={slug} onChange={e=>setSlug(e.target.value)} className="field mt-2 w-full" placeholder="data-analytics-foundations"/></label>
          <label className="mt-4 block text-xs text-slate-500">Description<textarea maxLength={5000} value={description} onChange={e=>setDescription(e.target.value)} className="field mt-2 min-h-24 w-full" placeholder="What will learners build or understand?"/></label>
          <button disabled={saving||!name.trim()||!slug.trim()} className="action mt-5 inline-flex items-center gap-2"><Plus size={15}/>Create draft</button>
        </form>

        <div className="border border-white/[.08] bg-[#0e1319] p-5">
          <div className="flex items-center justify-between"><h2 className="text-sm font-semibold">All tracks</h2><span className="text-xs text-slate-600">{tracks.length}</span></div>
          {loading?<p className="py-8 text-sm text-slate-500">Loading tracks…</p>:<div className="mt-3 divide-y divide-white/[.06]">
            {tracks.map(track=><button type="button" key={track.id} onClick={()=>setSelectedId(track.id)} className={"w-full py-3 text-left "+(selectedId===track.id?"text-[var(--gold2)]":"text-slate-300 hover:text-white")}><span className="flex items-center justify-between gap-3"><span className="font-medium">{track.name}</span><span className="text-[9px] uppercase tracking-[.14em] text-slate-600">{track.status}</span></span><span className="mt-1 block text-xs text-slate-600">{track.course_count} courses · {track.slug}</span></button>)}
            {!tracks.length&&<p className="py-8 text-sm text-slate-500">No global tracks have been created yet.</p>}
          </div>}
        </div>
      </div>

      <div className="min-w-0 border border-white/[.08] bg-[#0e1319] p-5 sm:p-7">
        {!detail?<div className="py-16 text-center"><Route size={26} className="mx-auto text-slate-600"/><h2 className="mt-4 font-semibold">Select a track to manage</h2><p className="mt-2 text-sm text-slate-500">Create a draft or choose an existing track from the list.</p></div>:<>
          <div className="flex flex-wrap items-start justify-between gap-4"><div><p className="section-kicker">Track editor</p><h2 className="mt-2 text-2xl font-semibold">{detail.name}</h2><p className="mt-1 text-xs text-slate-600">{detail.slug} · {detail.course_count} courses</p></div><span className={"rounded-full border px-3 py-1 text-[10px] font-bold uppercase tracking-[.14em] "+(detail.status==="published"?"border-emerald-400/30 text-emerald-300":"border-white/10 text-slate-500")}>{detail.status}</span></div>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <label className="text-xs text-slate-500">Name<input value={detail.name||""} onChange={e=>setDetail((v:any)=>({...v,name:e.target.value}))} className="field mt-2 w-full"/></label>
            <label className="text-xs text-slate-500">Slug<input value={detail.slug||""} onChange={e=>setDetail((v:any)=>({...v,slug:e.target.value}))} className="field mt-2 w-full"/></label>
            <label className="text-xs text-slate-500 md:col-span-2">Description<textarea value={detail.description||""} onChange={e=>setDetail((v:any)=>({...v,description:e.target.value}))} className="field mt-2 min-h-24 w-full"/></label>
          </div>
          <div className="mt-4 flex flex-wrap gap-2"><button type="button" disabled={saving} onClick={()=>void saveTrack()} className="action inline-flex items-center gap-2"><Save size={14}/>Save details</button>{detail.status==="published"?<button type="button" disabled={saving} onClick={()=>void setStatus("draft")} className="mini">Unpublish</button>:detail.status==="archived"?<button type="button" disabled={saving} onClick={()=>void setStatus("draft")} className="mini">Restore to draft</button>:<button type="button" disabled={saving} onClick={()=>void setStatus("published")} className="mini">Publish track</button>}{detail.status!=="archived"&&<button type="button" disabled={saving} onClick={()=>void setStatus("archived")} className="mini inline-flex items-center gap-2"><Archive size={14}/>Archive</button>}</div>

          <div className="mt-9 border-t border-white/[.08] pt-6">
            <div className="flex flex-wrap items-end justify-between gap-3"><div><p className="section-kicker">Curriculum</p><h3 className="mt-2 text-lg font-semibold">Ordered courses</h3></div><span className="text-xs text-slate-600">{(detail.courses||[]).length} linked</span></div>
            <div className="mt-4 divide-y divide-white/[.06]">
              {(detail.courses||[]).map((item:any,index:number)=><div key={item.id} className="flex flex-wrap items-center gap-3 py-3"><span className="grid size-8 shrink-0 place-items-center border border-white/[.1] text-xs tabular-nums text-slate-500">{index+1}</span><div className="min-w-0 flex-1"><p className="truncate text-sm font-medium text-slate-200">{item.course?.title||"Missing course record"}</p><p className="mt-1 text-[10px] uppercase tracking-[.12em] text-slate-600">{item.course?.status||"unknown"}</p></div><div className="flex items-center gap-1"><button type="button" disabled={saving} onClick={()=>void toggleRequired(item)} className="mini text-[10px]">{item.required?"Required":"Optional"}</button><button type="button" title="Move up" aria-label="Move course up" disabled={saving||index===0} onClick={()=>void moveCourse(index,-1)} className="mini-icon disabled:opacity-30"><ArrowUp size={14}/></button><button type="button" title="Move down" aria-label="Move course down" disabled={saving||index===(detail.courses||[]).length-1} onClick={()=>void moveCourse(index,1)} className="mini-icon disabled:opacity-30"><ArrowDown size={14}/></button><button type="button" title="Remove course" aria-label="Remove course" disabled={saving} onClick={()=>void removeCourse(item.course_id)} className="mini-icon text-red-300"><Trash2 size={14}/></button></div></div>)}
              {!detail.courses?.length&&<p className="py-7 text-sm text-slate-500">Add published Learnora courses to build this track.</p>}
            </div>
            <form onSubmit={addCourse} className="mt-5 flex flex-col gap-2 sm:flex-row"><select value={courseId} onChange={e=>setCourseId(e.target.value)} className="field min-h-11 flex-1"><option value="">Choose a global Learnora course</option>{availableCourses.map(course=><option key={course.id} value={course.id}>{course.title} · {course.status}</option>)}</select><label className="inline-flex min-h-11 items-center gap-2 border border-white/[.1] px-3 text-xs text-slate-400"><input type="checkbox" checked={courseRequired} onChange={e=>setCourseRequired(e.target.checked)}/>Required</label><button type="submit" disabled={saving||!courseId} className="mini inline-flex min-h-11 items-center justify-center gap-2"><Plus size={14}/>Add course</button></form>
            <p className="mt-3 text-[11px] leading-5 text-slate-600">Only global Learnora-owned courses can be linked. Publishing requires every linked course to have published modules and lessons, plus assessments before modules that unlock later modules. Once learners have course enrolments, the track curriculum is frozen; create a new track for a different sequence. Unpublished tracks remain available to existing learners with saved enrolments.</p>
          </div>
        </>}
      </div>
    </section>
  </Shell>;
}

function slugify(value:string) {
  return value.toLowerCase().trim().replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"");
}
