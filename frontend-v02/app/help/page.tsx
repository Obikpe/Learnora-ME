import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, Mail, BookOpen, ShieldCheck } from "lucide-react";
import PublicNav from "../../components/public/PublicNav";
import PublicFooter from "../../components/public/PublicFooter";

export const metadata: Metadata = {
  title: "Help and support",
  description: "Find help with Learnora ME accounts, courses, enrolment and learning progress.",
  alternates: { canonical: "/help" },
  openGraph: {
    title: "Help and support | Learnora ME",
    description: "Get help with your Learnora ME account and learning.",
    url: "/help",
    images: [{ url: "/og?title=Help%20and%20support&kind=Learnora%20ME", width: 1200, height: 630 }],
  },
};

const topics = [
  { icon: BookOpen, title: "Finding a course", body: "Browse published courses and learning tracks. Course pages explain the curriculum and whether individual enrolment is available." },
  { icon: ShieldCheck, title: "Account and access", body: "If you cannot sign in, use the password reset or account recovery options on the sign-in page. Organisation and cohort learners should use the learning access assigned to them." },
  { icon: Mail, title: "Contact support", body: "Tell us the email address on your account, the page you were using and what happened. Never send your password or verification code." },
];

export default function HelpPage() {
  return <>
    <PublicNav />
    <main id="main-content" className="mx-auto max-w-5xl px-5 pb-24 pt-36 lg:px-8">
      <Link href="/" className="inline-flex min-h-11 items-center gap-2 text-sm text-slate-400 hover:text-white"><ArrowLeft size={15}/> Back to Learnora</Link>
      
      
      <p className="mt-6 max-w-2xl text-base leading-8 text-slate-400">Find guidance for common questions or contact the Learnora team. For account security, never share your password or one-time verification codes.</p>
      <div className="mt-12 grid gap-4 md:grid-cols-3">
        {topics.map(({icon:Icon,title,body})=><article key={title} className="border border-white/[.1] bg-[#10151b] p-6"><Icon className="gold" size={22}/><h2 className="mt-5 text-lg font-semibold">{title}</h2><p className="mt-3 text-sm leading-7 text-slate-400">{body}</p></article>)}
      </div>
      <section className="mt-10 border border-white/[.12] bg-[#11171e] p-7 sm:p-9">
        <h2 className="font-display text-3xl">Contact Learnora</h2>
        <p className="mt-3 text-sm leading-7 text-slate-400">Email our support team and include enough detail for us to understand the issue.</p>
        <a href="mailto:learnorame@gmail.com?subject=Learnora%20ME%20Support" className="mt-6 inline-flex min-h-12 items-center gap-2 rounded-lg bg-[var(--accent)] px-5 text-sm font-semibold text-[var(--on-accent)]"><Mail size={16}/> Email learnorame@gmail.com</a>
      </section>
    </main>
    <PublicFooter />
  </>;
}
