"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, ArrowRight, Eye, EyeOff, LockKeyhole } from "lucide-react";
import Logo from "../../components/brand/Logo";
import Image from "next/image";
import { IMAGES } from "../../lib/constants";
import Toast from "../../components/feedback/Toast";
import { login,setToken,currentUser,request,organisationContext,setOrganisationContext,clearOrganisationContext,clearToken } from "../../lib/api";

export default function Login() {
  const [email,setEmail]=useState(""),[password,setPassword]=useState(""),[error,setError]=useState(""),[busy,setBusy]=useState(false),[showPassword,setShowPassword]=useState(false);
  const [busyLabel,setBusyLabel]=useState("Signing in…");
  const router=useRouter();
  async function warmDashboard() {
    // Fetch the learner's core dashboard payload before navigation. The API
    // client caches this session-scoped response so the dashboard can render
    // immediately instead of starting a second request after the redirect.
    setBusyLabel("Preparing your dashboard…");
    try { await request<any>("/progress/me"); } catch {}
  }
  async function submit(e:any) {
    e.preventDefault();setError("");setBusy(true);setBusyLabel("Signing in…");
    try {
      const result:any=await login(email,password);setToken(result.token||result.access_token||"cookie-session");
      let me:any;
      try {
        // Never trust the login response alone as proof that the browser
        // received and can use the HttpOnly session cookie.
        me=await currentUser();
      } catch {
        clearToken();
        throw new Error("Your sign-in could not be confirmed. Please try again.");
      }
      if(me.account_type==="admin"){if(["super_admin","staff_admin"].includes(me.role)){clearOrganisationContext();router.push("https://teamslearnora.vercel.app/login");return;}clearToken();setError("This administrator account is not configured for learner sign-in. Please contact your organisation administrator.");return;}
      if(me.account_type==="cohort"){clearOrganisationContext();router.push("/dashboard/cohort");return;}
      const memberships=me.organisation_memberships||[];
      const activeMemberships=memberships.filter((membership:any)=>membership.status==="active");
      const organisationIds=Array.from(new Set(activeMemberships.map((membership:any)=>String(membership.organisation_id||"")).filter(Boolean)));
      if(organisationIds.length>1){clearToken();throw new Error("This account is linked to more than one active organisation. Contact Learnora support to resolve the account before continuing.");}
      const privilegedMembership=activeMemberships.find((m:any)=>["owner","admin"].includes(m.role));
      const privileged=privilegedMembership?[privilegedMembership]:[];
      const savedId=organisationContext();
      const selected=(me.organisation_id?(activeMemberships.find((m:any)=>String(m.organisation_id)===String(me.organisation_id)&&["owner","admin"].includes(m.role))||activeMemberships.find((m:any)=>String(m.organisation_id)===String(me.organisation_id))):null)||(savedId?activeMemberships.find((m:any)=>String(m.organisation_id)===String(savedId)&&["owner","admin"].includes(m.role)):null)||(privileged.length===1?privileged[0]:null);
      const requestedNext = new URLSearchParams(window.location.search).get("next") || "";
      let safeNext = "";
      if (requestedNext.startsWith("/") && !requestedNext.startsWith("//") && !requestedNext.includes("\\")) {
        try {
          const nextUrl = new URL(requestedNext, window.location.origin);
          if (nextUrl.origin === window.location.origin) safeNext = nextUrl.pathname + nextUrl.search + nextUrl.hash;
        } catch {}
      }
      const assignedLearner = Boolean(
        me.account_type === "cohort" ||
        me.cohort_id ||
        me.organisation_id ||
        me.organisation_role ||
        me.role === "witstart" ||
        activeMemberships.length > 0
      );
      // Course links must never turn sign-in into an enrolment or access grant
      // for learners whose learning is controlled by a cohort or organisation.
      if (me.role === "normal" && me.account_type === "learner" && !assignedLearner && safeNext) {
        clearOrganisationContext();
        if (safeNext === "/dashboard" || safeNext.startsWith("/dashboard/")) await warmDashboard();
        router.push(safeNext);
        return;
      }
      if(selected&&["owner","admin"].includes(selected.role))setOrganisationContext(String(selected.organisation_id));else clearOrganisationContext();
      const destination = me.role==="organisation_prospect"
        ? "/organisation-portal"
        : selected&&["owner","admin"].includes(selected.role)
          ? "/dashboard/organisation"
          : "/dashboard";
      if (destination === "/dashboard") await warmDashboard();
      router.push(destination);
    } catch(e:any) {
      const message=e.message||"We could not sign you in. Check your details and try again.";
      if(message.startsWith("ACCOUNT_DEACTIVATED:")){
        router.push("/reactivate-account?email="+encodeURIComponent(email.trim().toLowerCase()));
        return;
      }
      setError(message);
    }
    finally {setBusy(false);}
  }
  return <main id="main-content" tabIndex={-1} className="grid min-h-screen bg-[var(--bg)] lg:grid-cols-[1fr_.92fr]">
    <a href="#main-content" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[70] focus:bg-[var(--card)] focus:px-4 focus:py-3 focus:text-[var(--text-heading)]">Skip to content</a>
    <aside className="relative hidden min-h-screen overflow-hidden border-r border-white/[.1] bg-[#11171e] lg:block">
      <Image src={IMAGES.login} alt="A quiet study space ready for focused learning" fill sizes="(max-width: 1024px) 100vw, 50vw" priority className="object-cover"/>
      <div className="absolute inset-0 bg-[#090b0e]/65"/>
      <div className="absolute inset-x-0 bottom-0 p-12 xl:p-16"><p className="text-[10px] font-bold uppercase tracking-[.22em] text-[var(--gold-light)]">Learnora ME</p><h2 className="mt-5 max-w-xl font-display text-5xl leading-[1.04] xl:text-6xl">Make the work you do to learn count.</h2><p className="mt-5 max-w-md text-sm leading-7 text-slate-300">Pick up where you left off. Keep practising, building and collecting evidence of your progress.</p><div className="mt-8 flex items-center gap-3 text-xs text-slate-400"><span className="grid size-9 place-items-center border border-white/20"><LockKeyhole size={15}/></span><span>Secure access to your learning workspace</span></div></div>
    </aside>
    <section className="flex min-h-screen items-center px-5 py-12 sm:px-8 lg:px-12 xl:px-20">
      <form onSubmit={submit} className="mx-auto w-full max-w-md">
        <a href="/" className="inline-flex items-center gap-2 text-xs text-slate-500 transition-colors hover:text-slate-200"><ArrowLeft size={14}/> Back to Learnora</a>
        <div className="mt-8"><Logo/></div>
        <p className="mt-12 text-xs font-bold uppercase tracking-[.2em] text-[var(--gold-light)]">Your learning workspace</p>
        <h1 className="mt-4 font-display text-5xl leading-tight tracking-[-.04em] sm:text-6xl">Welcome back.</h1>
        <p className="mt-4 text-sm leading-7 text-slate-400">Sign in to continue with the courses, people and work connected to your account.</p>
        <div className="mt-8 grid gap-5">
          <label htmlFor="login-email" className="grid gap-2 text-xs font-medium text-slate-300">Email address<input id="login-email" value={email} onChange={e=>setEmail(e.target.value)} type="email" required autoComplete="email" aria-invalid={Boolean(error)} aria-describedby={error ? "login-form-error" : undefined} className="field" placeholder="you@example.com"/></label>
          <label htmlFor="login-password" className="grid gap-2 text-xs font-medium text-slate-300">Password<span className="relative block"><input id="login-password" value={password} onChange={e=>setPassword(e.target.value)} type={showPassword?"text":"password"} required autoComplete="current-password" aria-invalid={Boolean(error)} aria-describedby={error ? "login-form-error" : undefined} className="field pr-12" placeholder="Enter your password"/><button type="button" aria-label={showPassword?"Hide password":"Show password"} aria-pressed={showPassword} onClick={()=>setShowPassword(v=>!v)} className="absolute inset-y-0 right-0 grid w-12 place-items-center text-slate-500 hover:text-slate-200">{showPassword?<EyeOff size={17}/>:<Eye size={17}/>}</button></span></label>
          <button disabled={busy} className="mt-1 inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-[var(--accent)] px-5 text-sm font-bold text-[var(--on-accent)] transition-colors hover:bg-[var(--accent-hover)] disabled:cursor-wait disabled:opacity-60">{busy?busyLabel:"Sign in"}{!busy&&<ArrowRight size={16}/>}</button>
        </div>
        <div className="mt-6 text-xs text-slate-500"><a className="gold hover:underline" href="/forgot-password">Forgot password?</a></div>
        <div className="mt-8 border-t border-white/[.1] pt-6 text-sm text-slate-500">New to Learnora? <a className="ml-1 font-semibold gold hover:underline" href="/register">Create an account</a></div>
        <div className="mt-4 text-xs text-slate-500">Joining through an organisation cohort? <a className="ml-1 font-semibold gold hover:underline" href="/cohort-login">Cohort learner sign in</a></div>
        <p className="mt-8 text-xs leading-5 text-slate-500">Use only your own account. Access to organisation and internal workspaces depends on your assigned permissions.</p>
      </form>
    </section>
    {error&&<Toast title="Sign in failed" message={error} type="error" onClose={()=>setError("")}/>}
  </main>;
}
