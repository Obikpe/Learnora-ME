"use client";

import { useState } from "react";

function calculateAge(value: string): number {
  const [year, month, day] = value.split("-").map(Number);
  const today = new Date();
  let age = today.getFullYear() - year;
  if (today.getMonth() + 1 < month || (today.getMonth() + 1 === month && today.getDate() < day)) age -= 1;
  return age;
}
import { useRouter } from "next/navigation";
import { ArrowLeft, ArrowRight, Eye, EyeOff, Layers3, Target, FolderKanban } from "lucide-react";
import Logo from "../../components/brand/Logo";
import Toast from "../../components/feedback/Toast";
import { register } from "../../lib/api";

export default function Register() {
  const [name,setName]=useState(""),[email,setEmail]=useState(""),[password,setPassword]=useState(""),[dateOfBirth,setDateOfBirth]=useState(""),[ageConfirmed,setAgeConfirmed]=useState(false),[truthConfirmed,setTruthConfirmed]=useState(false),[error,setError]=useState(""),[acceptedTerms,setAcceptedTerms]=useState(false),[marketingEmailOptIn,setMarketingEmailOptIn]=useState(false),[busy,setBusy]=useState(false),[showPassword,setShowPassword]=useState(false);
  const maxBirthDate = (() => { const date = new Date(); date.setFullYear(date.getFullYear() - 13); return [date.getFullYear(),String(date.getMonth()+1).padStart(2,"0"),String(date.getDate()).padStart(2,"0")].join("-"); })();
  const ageIsValid = Boolean(dateOfBirth && calculateAge(dateOfBirth) >= 13 && dateOfBirth <= maxBirthDate);
  const router=useRouter();
  function openVerification(){router.push("/check-email?email="+encodeURIComponent(email.trim().toLowerCase()));}
  async function submit(e:any) {
    e.preventDefault();setError("");
    if (!dateOfBirth || !ageConfirmed || !truthConfirmed) { setError("Enter your date of birth and confirm both age and accuracy statements."); return; }
    if (!ageIsValid) { setError("Learnora accounts are available only to people aged 13 or older."); return; }
    setBusy(true);
    try { await register(name,email,password,marketingEmailOptIn,dateOfBirth,ageConfirmed,truthConfirmed,Intl.DateTimeFormat().resolvedOptions().timeZone || "Africa/Lagos");openVerification(); }
    catch(e:any) {
      const message=e.message||"Your account could not be created.";
      const lower=message.toLowerCase();
      if(message.startsWith("ACCOUNT_DEACTIVATED:")){
        router.push("/reactivate-account?email="+encodeURIComponent(email.trim().toLowerCase()));
      } else {
        const accountNeedsVerification=(lower.includes("account was created")&&lower.includes("verification email"))||(lower.includes("already exists")&&(lower.includes("not been verified")||lower.includes("not verified")||lower.includes("unverified")));
        if(accountNeedsVerification){openVerification();}else{setError(message);}
      }
    } finally { setBusy(false); }
  }
  return <main id="main-content" tabIndex={-1} className="grid min-h-screen bg-[var(--bg)] lg:grid-cols-[.92fr_1.08fr]">
    <a href="#main-content" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[70] focus:bg-[var(--card)] focus:px-4 focus:py-3 focus:text-[var(--text-heading)]">Skip to content</a>
    <aside className="relative hidden min-h-screen flex-col justify-between border-r border-white/[.1] bg-[#0e141a] p-10 lg:flex xl:p-16">
      <a href="/" className="inline-flex w-fit"><Logo/></a>
      <div className="max-w-xl">
        
        
        <p className="mt-5 max-w-lg text-sm leading-7 text-slate-400">Learnora is designed to connect learning with practice, projects and feedback—so your progress becomes something you can reflect on and build from.</p>
        <div className="mt-10 divide-y divide-white/[.1] border-y border-white/[.1]">
          {[{icon:Layers3,title:"Learn with structure",text:"Follow clear lessons and outcomes."},{icon:Target,title:"Practise with purpose",text:"Try ideas and improve with feedback."},{icon:FolderKanban,title:"Keep evidence",text:"Build a record of projects and progress."}].map(({icon:Icon,title,text})=><div key={title} className="flex items-center gap-4 py-4"><span className="grid size-10 shrink-0 place-items-center border border-white/[.1] text-[var(--gold-light)]"><Icon size={18}/></span><div><p className="text-sm font-semibold">{title}</p><p className="mt-1 text-xs text-slate-500">{text}</p></div></div>)}
        </div>
      </div>
      <p className="text-xs leading-5 text-slate-500">Learnora ME · Learn. Practise. Build. Prove.</p>
    </aside>

    <section className="flex min-h-screen items-center px-5 py-10 sm:px-8 lg:px-12 xl:px-20">
      <div className="mx-auto w-full max-w-lg">
        <a href="/" className="inline-flex items-center gap-2 text-xs text-slate-500 transition-colors hover:text-slate-200 lg:hidden"><ArrowLeft size={14}/> Back to Learnora</a>
        <div className="mt-8 lg:mt-0"><a href="/" className="hidden lg:inline-flex"><Logo/></a></div>
          
          <h1 className="mt-3 font-display text-4xl leading-tight tracking-[-.04em] sm:text-5xl">Create account</h1>
          <p className="mt-4 max-w-md text-sm leading-7 text-slate-400">Create your Learnora account. You can explore the learning experiences and access available to your account.</p>
          <form onSubmit={submit} className="mt-8 grid gap-5">
            <label htmlFor="register-name" className="grid gap-2 text-xs font-medium text-slate-300">Your name<input id="register-name" value={name} onChange={e=>setName(e.target.value)} required autoComplete="name" className="field" placeholder="Full name"/></label>
            <label htmlFor="register-email" className="grid gap-2 text-xs font-medium text-slate-300">Email address<input id="register-email" value={email} onChange={e=>setEmail(e.target.value)} type="email" required autoComplete="email" aria-invalid={Boolean(error && /email|already exists|registered/i.test(error))} aria-describedby={error && /email|already exists|registered/i.test(error) ? "register-form-error" : undefined} className="field" placeholder="you@example.com"/></label>
            <label htmlFor="register-password" className="grid gap-2 text-xs font-medium text-slate-300">Create a password<span className="relative block"><input id="register-password" value={password} onChange={e=>setPassword(e.target.value)} type={showPassword?"text":"password"} required minLength={12} autoComplete="new-password" aria-describedby={error && /password/i.test(error) ? "register-password-hint register-form-error" : "register-password-hint"} aria-invalid={Boolean(error && /password/i.test(error))} className="field pr-12" placeholder="At least 12 characters"/><button type="button" aria-label={showPassword?"Hide password":"Show password"} aria-pressed={showPassword} onClick={()=>setShowPassword(v=>!v)} className="absolute inset-y-0 right-0 grid w-12 place-items-center text-slate-500 hover:text-slate-200">{showPassword?<EyeOff size={17}/>:<Eye size={17}/>}</button></span><span id="register-password-hint" className="text-xs leading-5 text-slate-500">Use at least 12 characters. A longer, unique passphrase is recommended.</span></label>
            <label htmlFor="register-date-of-birth" className="grid gap-2 text-xs font-medium text-slate-300">Date of birth<input id="register-date-of-birth" type="date" value={dateOfBirth} onChange={e=>setDateOfBirth(e.target.value)} max={maxBirthDate} required autoComplete="bday" className="field"/></label>
            {dateOfBirth && !ageIsValid && <p className="text-xs leading-5 text-red-400" role="alert">You must be at least 13 years old to create a Learnora account.</p>}
            <label className="flex min-h-11 items-start gap-3 py-1 text-xs leading-6 text-slate-400"><input type="checkbox" checked={ageConfirmed} onChange={e=>setAgeConfirmed(e.target.checked)} required className="mt-1 size-6 shrink-0 accent-[#d5b15b]"/><span>I confirm that I am at least 13 years old. Learnora does not allow account registration by anyone under 13.</span></label>
            <label className="flex min-h-11 items-start gap-3 py-1 text-xs leading-6 text-slate-400"><input type="checkbox" checked={truthConfirmed} onChange={e=>setTruthConfirmed(e.target.checked)} required className="mt-1 size-6 shrink-0 accent-[#d5b15b]"/><span>I confirm that my date of birth and the other information I have provided are accurate and truthful.</span></label>
            <label className="flex min-h-11 items-start gap-3 py-1 text-xs leading-6 text-slate-400"><input type="checkbox" checked={acceptedTerms} onChange={e=>setAcceptedTerms(e.target.checked)} required className="mt-1 size-6 shrink-0 accent-[#d5b15b]"/><span>I agree to the <a className="gold underline underline-offset-2" href="/terms" target="_blank" rel="noreferrer">Terms of Use</a> and acknowledge the <a className="gold underline underline-offset-2" href="/privacy" target="_blank" rel="noreferrer">Privacy Policy</a>, including how account and learning data are processed.</span></label>
            <label className="flex items-start gap-3 text-xs leading-6 text-slate-400"><input type="checkbox" checked={marketingEmailOptIn} onChange={e=>setMarketingEmailOptIn(e.target.checked)} className="mt-1 size-4 shrink-0 accent-[#d5b15b]"/><span>Yes, I would like to receive Learnora marketing emails about new learning tracks, learning opportunities, offers and discounts. This is optional. I can unsubscribe at any time. This does not affect in-app notifications or essential account emails.</span></label>
            <button disabled={!acceptedTerms||!ageConfirmed||!truthConfirmed||!ageIsValid||busy} className="mt-1 inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-[var(--accent)] px-5 text-sm font-bold text-[var(--on-accent)] transition-colors hover:bg-[var(--accent-hover)] disabled:cursor-not-allowed disabled:opacity-40">{busy?"Creating account…":"Create account"}{!busy&&<ArrowRight size={16}/>}</button>
          </form>
          {error && <p id="register-form-error" className="sr-only" role="alert">{error}</p>}
          <p className="mt-5 text-xs leading-5 text-slate-500">Learnora uses essential browser storage to operate securely. Read the <a className="gold underline underline-offset-2" href="/cookies">Cookies & Storage Notice</a>.</p>
          <div className="mt-7 border-t border-white/[.1] pt-5 text-sm text-slate-500">Already have an account? <a className="ml-1 font-semibold gold hover:underline" href="/login">Sign in</a></div>
        {error&&<Toast title="Could not create account" message={error} type="error" onClose={()=>setError("")}/>}
      </div>
    </section>
  </main>;
}
