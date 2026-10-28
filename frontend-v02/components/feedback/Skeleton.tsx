"use client";

type SkeletonProps = {
  variant?: "workspace" | "course" | "compact";
  label?: string;
};

/** Layout-shaped placeholders used while the authenticated workspace is being verified. */
export default function Skeleton({ variant = "workspace", label = "Verifying your account" }: SkeletonProps) {
  const bar = (className: string) => <div className={"animate-pulse rounded-md bg-white/[.07] " + className} />;

  if (variant === "compact") {
    return <div role="status" aria-label={label} className="mt-8 rounded-2xl border border-white/[.08] bg-[#0e1319] p-5">
      <span className="sr-only">{label}</span>
      {bar("h-4 w-40")}
      <div className="mt-5 grid gap-3 sm:grid-cols-2">{bar("h-16 w-full")}{bar("h-16 w-full")}</div>
      {bar("mt-5 h-3 w-full")}
      {bar("mt-2 h-3 w-4/5")}
    </div>;
  }

  if (variant === "course") {
    return <div role="status" aria-label={label} className="space-y-5">
      <span className="sr-only">{label}</span>
      {bar("h-3 w-28")}
      {bar("mt-4 h-9 w-3/4 max-w-lg")}
      {bar("h-4 w-full max-w-2xl")}
      <div className="grid gap-5 pt-3 xl:grid-cols-[17rem_minmax(0,1fr)]">
        <div className="space-y-3 rounded-2xl border border-white/[.08] bg-[#0e1319] p-5">{bar("h-5 w-2/3")}{bar("h-10 w-full")}{bar("h-10 w-full")}{bar("h-10 w-full")}{bar("h-10 w-full")}</div>
        <div className="space-y-4 rounded-2xl border border-white/[.08] bg-[#0e1319] p-5 sm:p-7">{bar("h-5 w-1/3")}{bar("h-56 w-full")}{bar("h-4 w-full")}{bar("h-4 w-5/6")}</div>
      </div>
    </div>;
  }

  return <div role="status" aria-label={label} className="space-y-7">
    <span className="sr-only">{label}</span>
    <div className="space-y-3">{bar("h-3 w-32")}{bar("h-9 w-3/4 max-w-xl")}{bar("h-4 w-full max-w-2xl")}</div>
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{bar("h-28 w-full rounded-2xl")}{bar("h-28 w-full rounded-2xl")}{bar("h-28 w-full rounded-2xl")}{bar("h-28 w-full rounded-2xl")}</div>
    <div className="grid gap-5 xl:grid-cols-[1.2fr_.8fr]">
      <section className="space-y-5 rounded-2xl border border-white/[.08] bg-[#0e1319] p-5 sm:p-6">{bar("h-5 w-44")}{bar("h-4 w-64")}{bar("h-16 w-full")}{bar("h-16 w-full")}{bar("h-16 w-full")}</section>
      <section className="space-y-5 rounded-2xl border border-white/[.08] bg-[#0e1319] p-5 sm:p-6">{bar("h-5 w-40")}{bar("h-4 w-full")}{bar("h-20 w-full")}{bar("h-20 w-full")}</section>
    </div>
    <section className="space-y-4 rounded-2xl border border-white/[.08] bg-[#0e1319] p-5 sm:p-6">{bar("h-5 w-52")}{bar("h-4 w-2/3")}{bar("h-32 w-full")}</section>
  </div>;
}
