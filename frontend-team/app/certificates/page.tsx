"use client";
import { useCallback, useEffect, useState } from "react";
import { Award, RefreshCw, ShieldAlert } from "lucide-react";
import Shell from "../../components/Shell";
import { request, teamMe } from "../../lib/api";

export default function CertificatesWorkspace() {
  const [roles,setRoles]=useState<string[]>([]);
  const [items,setItems]=useState<any[]>([]);
  const [loading,setLoading]=useState(true);
  const [busy,setBusy]=useState("");
  const [reason,setReason]=useState<Record<string,string>>({});
  const [error,setError]=useState("");
  const [notice,setNotice]=useState("");
  const load=useCallback(async()=>{
    setLoading(true);setError("");
    try{const result=await request<any>("/credentials/internal");setItems(result.certificates||[]);}
    catch(e:any){setError(e.message||"Certificate register could not be loaded.");}
    finally{setLoading(false);}
  },[]);
  useEffect(()=>{teamMe().then(x=>setRoles(x.roles||[])).catch(e=>setError(e.message||"Staff session unavailable."));void load();},[load]);
  async function revoke(id:string){
    const explanation=(reason[id]||"").trim();
    if(explanation.length<5){setError("Enter a clear reason of at least five characters before revoking.");return;}
    if(!window.confirm("Revoke this certificate? Its public verification result will immediately become invalid."))return;
    setBusy(id);setError("");setNotice("");
    try{await request("/credentials/internal/"+encodeURIComponent(id)+"/revoke",{method:"POST",body:JSON.stringify({reason:explanation})});setNotice("Certificate revoked. Public verification now reports the credential as invalid.");setReason(old=>({...old,[id]:""}));await load();}
    catch(e:any){setError(e.message||"Certificate could not be revoked.");}
    finally{setBusy("");}
  }
  return <Shell roles={roles} active="certificates">
    <header className="border-b border-white/[.1] pb-6"><p className="section-kicker">Learning operations / Credentials</p><h1 className="mt-3 font-display text-4xl sm:text-5xl">Certificates</h1><p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">Review issued course-completion credentials and revoke a credential only when there is a documented reason. Revocation is permanent in this workflow and is written to the audit log.</p></header>
    <div className="mt-5 flex flex-wrap items-center justify-between gap-3"><p className="text-xs text-slate-500">Latest 200 issued certificates</p><button type="button" className="mini inline-flex items-center gap-2" onClick={()=>void load()} disabled={loading}><RefreshCw size={14} className={loading?"animate-spin":""}/>Refresh</button></div>
    {error&&<p role="alert" className="notice error mt-4">{error}</p>}{notice&&<p role="status" className="notice ok mt-4">{notice}</p>}
    <section className="mt-5 grid gap-4">
      {loading&&!items.length?<p className="py-10 text-sm text-slate-500">Loading credential register…</p>:items.map(item=><article key={item.id} className="panel">
        <div className="flex flex-wrap items-start justify-between gap-4"><div className="flex min-w-0 items-start gap-3"><Award size={20} className="mt-1 shrink-0 text-[var(--gold2)]"/><div className="min-w-0"><h2 className="font-semibold">{item.course_title}</h2><p className="mt-1 text-xs text-slate-500">{item.certificate_number}</p><p className="mt-2 text-xs text-slate-400">{item.learner?.name||"Learner"} · {item.learner?.email||"No email"} · Issued {item.issued_at?new Date(item.issued_at).toLocaleDateString():"—"}</p></div></div><span className={"text-xs font-semibold "+(item.valid?"text-emerald-300":"text-red-300")}>{item.valid?"Valid":"Revoked"}</span></div>
        {!item.valid?<p className="mt-4 rounded-lg border border-red-400/15 bg-red-400/[.04] p-3 text-xs leading-6 text-red-200">Revoked {item.revoked_at?new Date(item.revoked_at).toLocaleString():""} · {item.revocation_reason||"No reason recorded"}</p>:<div className="mt-4 grid gap-2 sm:grid-cols-[minmax(0,1fr)_auto]"><label className="sr-only" htmlFor={"reason-"+item.id}>Reason for revocation</label><input id={"reason-"+item.id} className="field" value={reason[item.id]||""} onChange={e=>setReason(old=>({...old,[item.id]:e.target.value}))} placeholder="Documented reason for revocation"/><button type="button" className="mini inline-flex items-center justify-center gap-2 text-red-200" disabled={busy===item.id} onClick={()=>void revoke(item.id)}><ShieldAlert size={14}/>{busy===item.id?"Revoking…":"Revoke certificate"}</button></div>}
      </article>)}
      {!loading&&!items.length&&<div className="panel py-12 text-center text-sm text-slate-500">No course certificates have been issued yet.</div>}
    </section>
  </Shell>;
}
