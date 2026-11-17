export default function TracksLoading() {
  return <main className="min-h-screen bg-[#0b1017] px-5 pb-24 pt-32" aria-label="Loading learning tracks">
    <div className="mx-auto max-w-7xl animate-pulse"><div className="h-4 w-40 bg-white/[.08]"/><div className="mt-6 h-16 max-w-2xl bg-white/[.08]"/><div className="mt-4 h-5 max-w-xl bg-white/[.05]"/><div className="mt-10 h-14 bg-white/[.05]"/><div className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-3">{Array.from({length:6}).map((_,i)=><div key={i} className="min-h-72 border border-white/[.08] bg-[#10151b] p-6"><div className="h-4 w-1/3 bg-white/[.08]"/><div className="mt-7 h-7 w-3/4 bg-white/[.08]"/><div className="mt-4 h-16 bg-white/[.05]"/><div className="mt-8 h-10 w-1/2 bg-white/[.06]"/></div>)}</div></div>
  </main>;
}
