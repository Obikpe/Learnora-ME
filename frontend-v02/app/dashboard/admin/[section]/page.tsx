"use client";
import {useEffect,useState} from "react";
import {currentUser} from "../../../../lib/api";
import Skeleton from "../../../../components/feedback/Skeleton";
import {adminCourses,organisations,organisationRequests,creatorApplications,aiProviders,adminUsers,adminAccountLifecycle,adminActivity} from "../../../../lib/api/admin";
import Shell from "../../../../components/dashboard/Shell";
import SectionHeader from "../../../../components/dashboard/SectionHeader";
import DataTable from "../../../../components/dashboard/DataTable";
import EmptyState from "../../../../components/feedback/EmptyState";

function dateLabel(value:any) {
 if(!value)return "—";
 const date=new Date(value);
 return Number.isNaN(date.getTime())?"—":date.toLocaleString();
}
export default function AdminSection({params}:{params:{section:string}}){
 const[u,setU]=useState<any>(null),[data,setData]=useState<any>(null),[err,setErr]=useState("");
 useEffect(()=>{currentUser().then(x=>{if(x.account_type!=="admin")location.href="/dashboard";else setU(x)}).catch(()=>location.href="/login")},[]);
 useEffect(()=>{
  if(!u)return;
  let fn:Promise<any>;
  switch(params.section){
   case"courses":fn=adminCourses();break;
   case"organisations":fn=organisations();break;
   case"commercial":fn=organisationRequests();break;
   case"creators":fn=creatorApplications();break;
   case"ai":fn=aiProviders();break;
   case"users":fn=Promise.all([adminUsers(),adminAccountLifecycle()]).then(([learners,lifecycle])=>({users:learners.users||[],...lifecycle}));break;
   case"activity":fn=adminActivity();break;
   default:fn=Promise.resolve(null)
  }
  fn.then(setData).catch(e=>setErr(e.message))
 },[u,params.section]);
 if(!u)return <Shell admin active={params.section}><Skeleton label="Verifying administrator access" /></Shell>;
 const s=params.section, rows=data?.courses||data?.organisations||data?.requests||data?.applications||data?.providers||data?.activity||[];
 let columns:any[]=[];
 if(s==="courses")columns=[{key:"title",label:"Course"},{key:"ownership",label:"Ownership"},{key:"status",label:"Status"},{key:"level",label:"Level"}];
 else if(s==="organisations")columns=[{key:"name",label:"Organisation"},{key:"organisation_type",label:"Type"},{key:"template",label:"Template"},{key:"is_active",label:"Status",render:(r:any)=>r.is_active?"Active":"Inactive"}];
 else if(s==="commercial")columns=[{key:"organisation_name",label:"Organisation"},{key:"request_type",label:"Request"},{key:"status",label:"Status"},{key:"created_at",label:"Submitted"}];
 else if(s==="creators")columns=[{key:"status",label:"Status"},{key:"created_at",label:"Submitted"},{key:"user_id",label:"Applicant"}];
 else if(s==="ai")columns=[{key:"display_name",label:"Provider"},{key:"default_model",label:"Model"},{key:"enabled",label:"Enabled"}];
 else if(s==="activity")columns=[{key:"action",label:"Event"},{key:"email",label:"Learner"},{key:"created_at",label:"Date",render:(r:any)=>dateLabel(r.created_at)},{key:"metadata",label:"Details",render:(r:any)=>r.metadata?.deletion_reason||r.details||"—"}];
 const userColumns:any[]=[
  {key:"name",label:"Learner"},
  {key:"email",label:"Email"},
  {key:"created_at",label:"Joined",render:(r:any)=>dateLabel(r.created_at)},
  {key:"account_status",label:"Account status",render:(r:any)=>String(r.account_status||"active").replaceAll("_"," ")},
  {key:"marketing_email_opt_in",label:"Marketing",render:(r:any)=>r.marketing_email_opt_in?"Opted in":"Not opted in"}
 ];
 const lifecycleRows=[
  ...(data?.pending_deletions||[]).map((r:any)=>({...r,id:r.id,event_status:r.account_status,record_email:r.email,occurred_at:r.account_deletion_requested_at})),
  ...(data?.completed_deletions||[]).map((r:any)=>({...r,id:r.original_user_id,event_status:"deleted",record_email:r.original_email,occurred_at:r.deleted_at}))
 ];
 const lifecycleColumns:any[]=[
  {key:"record_email",label:"Learner"},
  {key:"event_status",label:"Status",render:(r:any)=>String(r.event_status||"").replaceAll("_"," ")},
  {key:"deletion_reason",label:"Reason",render:(r:any)=>String(r.deletion_reason||"Not recorded").replaceAll("_"," ")},
  {key:"deletion_reason_details",label:"Additional feedback"},
  {key:"occurred_at",label:"Date",render:(r:any)=>dateLabel(r.occurred_at)},
  {key:"account_deactivation_until",label:"Recovery ends",render:(r:any)=>dateLabel(r.account_deactivation_until||r.deactivation_until)}
 ];
 return <Shell admin role={u.role} active={s}>
  <SectionHeader eyebrow="Learnora administration" title={s==="ai"?"AI operations":s.replaceAll("-"," ")} description="Live operational records from the Learnora backend."/>
  {err?<div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-5 text-red-300">{err}</div>
  :data===null?<EmptyState title="No records to display" message="There are no records available in this section."/>
  :s==="users"?<div className="space-y-8">
    <section><h2 className="mb-3 text-sm font-semibold text-[var(--text-heading)]">Learner accounts</h2><DataTable rows={data?.users||[]} columns={userColumns} emptyTitle="No learner accounts" emptyMessage="Learner accounts will appear here when created."/></section>
    <section><h2 className="mb-3 text-sm font-semibold text-[var(--text-heading)]">Account deletion activity</h2><p className="mb-3 text-xs text-[var(--text-muted)]">Includes accounts in their 30-day recovery period and completed deletions. Deletion reasons are visible to authorised administrators.</p><DataTable rows={lifecycleRows} columns={lifecycleColumns} emptyTitle="No deletion activity" emptyMessage="Deletion requests and completed deletions will appear here."/></section>
   </div>
  :<DataTable rows={rows} columns={columns}/>}
 </Shell>
}
