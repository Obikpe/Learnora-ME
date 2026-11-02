"use client";

import { useCallback, useEffect, useState } from "react";
import { MessageSquareText, RefreshCw, ShieldCheck, XCircle } from "lucide-react";
import Shell from "../../components/Shell";
import { request, teamMe } from "../../lib/api";

type Review = {
  id:string;
  rating:number;
  comment?:string|null;
  public_consent:boolean;
  moderation_status:"pending"|"approved"|"rejected";
  created_at:string;
  learner?:{name?:string|null;email?:string|null};
  track?:{name?:string|null;slug?:string|null};
};

export default function TrackReviewsWorkspace(){
  const [roles,setRoles]=useState<string[]>([]);
  const [reviews,setReviews]=useState<Review[]>([]);
  const [filter,setFilter]=useState("pending");
  const [loading,setLoading]=useState(true);
  const [busy,setBusy]=useState("");
  const [error,setError]=useState("");
  const [notice,setNotice]=useState("");

  const load=useCallback(async()=>{
    setLoading(true);setError("");
    try{
      const path="/track-reviews"+(filter?"?status="+encodeURIComponent(filter):"");
      const result=await request<any>(path);
      setReviews(result.reviews||[]);
    }catch(e:any){setError(e.message||"Track reviews could not be loaded.");}
    finally{setLoading(false);}
  },[filter]);

  useEffect(()=>{teamMe().then(x=>setRoles(x.roles||[])).catch(()=>{});},[]);
  useEffect(()=>{void load();},[load]);

  async function moderate(id:string,status:"approved"|"rejected"){
    setBusy(id);setError("");setNotice("");
    try{
      await request("/track-reviews/"+encodeURIComponent(id)+"/moderate",{method:"POST",body:JSON.stringify({status})});
      setNotice(status==="approved"?"Review approved. It will appear publicly only if the learner consented to sharing.":"Review rejected. It will remain private.");
      await load();
    }catch(e:any){setError(e.message||"Review moderation could not be saved.");}
    finally{setBusy("");}
  }

  return <Shell roles={roles} active="track-reviews">
    <header className="border-b border-white/[.1] pb-7"><p className="section-kicker">Learning operations / Learner feedback</p><h1 className="mt-3 font-display text-4xl sm:text-5xl">Track reviews</h1><p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">Moderate feedback submitted by learners who have completed a track. Only approved reviews with explicit public-sharing consent are displayed publicly.</p></header>
    <div className="mt-6 flex flex-wrap items-center justify-between gap-3"><label className="grid gap-1 text-xs text-slate-500">Moderation status<select className="field min-w-44" value={filter} onChange={e=>setFilter(e.target.value)}><option value="pending">Pending</option><option value="approved">Approved</option><option value="rejected">Rejected</option><option value="">All reviews</option></select></label><button type="button" className="mini inline-flex items-center gap-2" disabled={loading} onClick={()=>void load()}><RefreshCw size={14}/>Refresh</button></div>
    {error&&<p role="alert" className="notice error mt-4">{error}</p>}{notice&&<p role="status" className="notice ok mt-4">{notice}</p>}
    {loading?<div className="mt-5 h-48 animate-pulse border border-white/[.08] bg-[#11171e] motion-reduce:animate-none"/>:reviews.length?<section className="mt-5 grid gap-3">{reviews.map(review=><article key={review.id} className="panel">
      <div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-xs text-slate-500">{review.track?.name||"Learning track"}</p><h2 className="mt-1 font-semibold">{review.learner?.name||"Learner"}</h2><p className="mt-1 text-[11px] text-slate-600">{review.learner?.email||"No email"} · {review.created_at?new Date(review.created_at).toLocaleString():""}</p></div><span className="text-xs text-[var(--gold2)]">{"★".repeat(review.rating)}{"☆".repeat(5-review.rating)} · {review.rating}/5</span></div>
      {review.comment?<p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-300">{review.comment}</p>:<p className="mt-4 text-xs italic text-slate-500">No written comment.</p>}
      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-white/[.08] pt-4"><div className="text-xs text-slate-500">{review.public_consent?"Learner consented to public display":"Private feedback only"} · {review.moderation_status}</div>{review.moderation_status==="pending"&&<div className="flex flex-wrap gap-2"><button type="button" className="mini inline-flex items-center gap-2 text-emerald-200" disabled={busy===review.id} onClick={()=>void moderate(review.id,"approved")}><ShieldCheck size={14}/>{busy===review.id?"Saving…":"Approve"}</button><button type="button" className="mini inline-flex items-center gap-2 text-red-200" disabled={busy===review.id} onClick={()=>void moderate(review.id,"rejected")}><XCircle size={14}/>Reject</button></div>}</div>
      {!review.public_consent&&<p className="mt-3 text-[11px] leading-5 text-slate-600">Approval does not publish this review because the learner has not given public-sharing consent.</p>}
    </article>)}</section>:<div className="panel mt-5 py-12 text-center"><MessageSquareText className="mx-auto text-slate-600" size={24}/><p className="mt-3 text-sm text-slate-400">No reviews match this filter.</p></div>}
  </Shell>;
}
