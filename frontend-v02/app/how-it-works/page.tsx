import { publicPageMetadata } from "../../lib/seo";

export const metadata = publicPageMetadata("How Learnora works", "See how Learnora connects structured courses, practice, assessment, guidance and evidence of skills.", "/how-it-works");

import PublicNav from "../../components/public/PublicNav";
import PublicFooter from "../../components/public/PublicFooter";
import Journey from "../../components/public/Journey";
import { ArrowRight, BookOpenCheck, BriefcaseBusiness, ClipboardCheck, Users } from "lucide-react";

const capabilities=[
  {icon:BookOpenCheck,title:"Learning",body:"Courses and lessons provide structure, concepts and clear objectives."},
  {icon:ClipboardCheck,title:"Assessment",body:"Exercises and practical work create opportunities to demonstrate understanding."},
  {icon:Users,title:"Guidance",body:"Instructors, peers and AI support can help people reflect and improve."},
  {icon:BriefcaseBusiness,title:"Evidence",body:"Projects, feedback and assessment records give skills context."}
];

export default function Page() {
  return <>
    <PublicNav/>
    <main id="main-content" className="pt-20">
      <section className="border-b border-white/[.1]">
        <div className="mx-auto max-w-[82rem] px-5 py-16 sm:py-24 lg:px-8 lg:py-28">
          
          <h1 className="mt-6 max-w-5xl font-display text-5xl leading-[1.02] tracking-[-.05em] sm:text-6xl lg:text-7xl">A learning system designed around <span className="gold">capability.</span></h1>
          <div className="mt-8 grid gap-6 md:grid-cols-[1fr_.65fr] md:items-end"><p className="max-w-2xl text-base leading-8 text-slate-300 sm:text-lg">Learnora connects learning material with practice, projects, assessment and feedback—helping people decide what they can do now and what to work on next.</p><p className="border-l border-[var(--gold)]/60 pl-4 text-sm leading-7 text-slate-500">The aim is not simply to record that someone reached the end of a course. It is to help them apply what they learned and keep an honest record of the work.</p></div>
        </div>
      </section>
      <Journey/>
      <section className="border-y border-white/[.1] bg-[#0c1015] py-16 sm:py-20">
        <div className="mx-auto max-w-[82rem] px-5 lg:px-8">
          <div className="grid gap-6 lg:grid-cols-[.8fr_1.2fr] lg:items-end"><div><h2 className="mt-4 max-w-xl font-display text-4xl leading-tight sm:text-5xl">One journey. Different tools, working together.</h2></div><p className="max-w-xl text-sm leading-7 text-slate-400 lg:justify-self-end">The experience can include courses, assessment, human guidance and evidence. The tools available to you depend on your account type and learning programme.</p></div>
          <div className="mt-10 grid gap-0 border-y border-white/[.12] sm:grid-cols-2 xl:grid-cols-4">{capabilities.map(({icon:Icon,title,body})=><article key={title} className="border-b border-white/[.1] py-6 sm:px-5 xl:border-b-0 xl:odd:border-r xl:first:pl-0 xl:last:pr-0"><Icon className="mt-5 gold" size={21} strokeWidth={1.7}/><h3 className="mt-4 font-display text-2xl">{title}</h3><p className="mt-3 text-sm leading-7 text-slate-400">{body}</p></article>)}</div>
        </div>
      </section>
      <section className="mx-auto max-w-[82rem] px-5 py-16 sm:py-20 lg:px-8">
        <div className="grid gap-8 border border-white/[.12] bg-[#11171e] p-7 sm:p-10 lg:grid-cols-[.8fr_1.2fr] lg:items-start">
          <div><h2 className="mt-4 max-w-lg font-display text-4xl leading-tight sm:text-5xl">What you see should reflect what is real.</h2></div>
          <div><p className="text-sm leading-7 text-slate-300">Learnora should not turn an unfinished feature into a promise, course completion into a verified skill, or an AI suggestion into a human review. Dashboards and reports should use live records and clearly distinguish what is self-reported, automatically assessed or instructor-reviewed.</p><a href="/about" className="mt-7 inline-flex min-h-11 items-center gap-2 text-sm font-semibold gold hover:underline">Read our principles <ArrowRight size={16}/></a></div>
        </div>
      </section>
    </main>
    <PublicFooter/>
  </>;
}
