export default function CoursesLoading() {
  return <main className="min-h-screen bg-[#0b1017] px-5 pb-24 pt-32" aria-label="Loading course catalogue">
    <div className="mx-auto max-w-7xl animate-pulse"><div className="h-4 w-40 bg-white/[.08]"/><div className="mt-6 h-16 max-w-2xl bg-white/[.08]"/><div className="mt-4 h-5 max-w-xl bg-white/[.05]"/><div className="mt-10 h-14 bg-white/[.05]"/><div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{Array.from({length:6}).map((_,i)=><div key={i} className="border border-white/[.08] bg-[#10151b]"><div className="aspect-video bg-white/[.06]"/><div className="space-y-3 p-5"><div className="h-4 w-1/3 bg-white/[.08]"/><div className="h-7 w-4/5 bg-white/[.08]"/><div className="h-12 bg-white/[.05]"/></div></div>)}</div></div>
  </main>;
}
