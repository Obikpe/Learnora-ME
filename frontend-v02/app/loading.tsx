export default function HomeLoading() {
  return <main className="min-h-screen bg-[#0b1017] px-5 pb-20 pt-32" aria-label="Loading Learnora homepage">
    <div className="mx-auto max-w-[82rem] animate-pulse">
      <div className="grid gap-8 lg:grid-cols-2"><div><div className="h-4 w-40 bg-white/[.08]"/><div className="mt-7 h-20 max-w-xl bg-white/[.08]"/><div className="mt-3 h-20 max-w-lg bg-white/[.08]"/><div className="mt-7 h-12 max-w-md bg-white/[.06]"/><div className="mt-6 h-14 max-w-xl bg-white/[.06]"/></div><div className="aspect-[4/3] bg-white/[.06]"/></div>
      <div className="mt-16 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">{Array.from({length:4}).map((_,i)=><div key={i} className="border border-white/[.08] p-5"><div className="aspect-video bg-white/[.06]"/><div className="mt-5 h-5 w-3/4 bg-white/[.08]"/><div className="mt-3 h-12 bg-white/[.05]"/></div>)}</div>
    </div>
  </main>;
}
