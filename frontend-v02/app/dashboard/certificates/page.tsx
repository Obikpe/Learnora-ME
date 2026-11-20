"use client";
import {useCallback,useEffect,useState} from "react";
import {Award,RefreshCw,ShieldCheck,XCircle} from "lucide-react";
import CertificateArtwork from "../../../components/dashboard/CertificateArtwork";
import {request} from "../../../lib/api/client";
import Shell from "../../../components/dashboard/Shell";
import Skeleton from "../../../components/feedback/Skeleton";

export default function CertificatesPage(){
 const [data,setData]=useState<any>(null),[loading,setLoading]=useState(true),[busy,setBusy]=useState(""),[error,setError]=useState(""),[notice,setNotice]=useState("");
 const load=useCallback(async()=>{setLoading(true);setError("");try{setData(await request<any>("/credentials/me"));}catch(e:any){setError(e.message||"Certificates could not be loaded.");}finally{setLoading(false);}},[]);
 useEffect(()=>{void load();},[load]);
 async function issue(courseId:string){setBusy(courseId);setError("");setNotice("");try{await request("/credentials/courses/"+encodeURIComponent(courseId)+"/issue",{method:"POST"});setNotice("Your course-completion certificate is ready.");await load();}catch(e:any){setError(e.message||"Certificate could not be issued.");}finally{setBusy("");}}
 return <Shell active="certificates">
 {error&&<div role="alert" className="mt-5 text-sm text-[var(--error)]">{error}</div>}{notice&&<div role="status" className="mt-5 text-sm text-[var(--success)]">{notice}</div>}
 {loading?<div className="mt-7"><Skeleton label="Loading certificates and completed courses"/></div>:<div className="grid gap-7 xl:grid-cols-[1fr_1fr]">
  <section><div className="flex items-center justify-between gap-3"><div><h2 className="text-lg font-semibold">Issued certificates</h2><p className="mt-1 text-xs text-[var(--text-muted)]">Credentials already attached to your account.</p></div><button type="button" onClick={()=>void load()} className="mini" aria-label="Refresh certificates"><RefreshCw size={14}/></button></div>
   <div className="mt-4 space-y-3">{(data?.certificates||[]).map((cert:any)=><article key={cert.id} className="flex flex-wrap items-center gap-4 rounded-xl border border-[var(--border)] bg-[var(--card)] p-4"><CertificateArtwork certificate={cert}/><div className="min-w-0 flex-1"><h3 className="font-semibold text-[var(--text-heading)]">{cert.course_title}</h3><p className="mt-1 break-all text-[11px] text-[var(--text-muted)]">{cert.certificate_number}</p><p className="mt-2 text-xs text-[var(--text-muted)]">Issued {cert.issued_at?new Date(cert.issued_at).toLocaleDateString():"—"}</p>{cert.valid===false&&<p className="mt-2 text-xs font-medium text-[var(--error)]">Revoked {cert.revoked_at?new Date(cert.revoked_at).toLocaleDateString():""}</p>}</div>{cert.valid===false?<XCircle className="shrink-0 text-[var(--error)]" size={18}/>:<ShieldCheck className="shrink-0 text-[var(--success)]" size={18}/>}</article>)}{!data?.certificates?.length&&<div className="py-6 text-sm text-[var(--text-muted)]"><p>No certificates issued yet.</p><p className="mt-1 text-xs">Finish a course and meet its published assessment requirements to become eligible.</p></div>}</div>
  </section>
  <section><h2 className="text-lg font-semibold">Ready to claim</h2><p className="mt-1 text-xs text-[var(--text-muted)]">Courses appear here when you have completed all required lessons and assessments.</p><div className="mt-4 space-y-3">{(data?.eligible_courses||[]).map((course:any)=><article key={course.course_id} className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5"><h3 className="font-semibold">{course.course_title}</h3><p className="mt-2 text-xs text-[var(--success)]">Completion confirmed</p><button type="button" disabled={busy===course.course_id||!!busy} onClick={()=>void issue(course.course_id)} className="action mt-4 inline-flex items-center gap-2"><Award size={14}/>{busy===course.course_id?"Issuing…":"Claim certificate"}</button></article>)}{!data?.eligible_courses?.length&&<div className="py-6 text-sm text-[var(--text-muted)]"><p>No unclaimed certificates.</p><p className="mt-1 text-xs">Completed eligible courses will appear here.</p></div>}</div></section>
 </div>}
 </Shell>;
}
