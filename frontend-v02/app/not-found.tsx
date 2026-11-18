import Link from "next/link";
import PublicNav from "../components/public/PublicNav";
import PublicFooter from "../components/public/PublicFooter";

export default function NotFound() {
  return (
    <>
      <PublicNav />
      <main id="main-content" tabIndex={-1} className="mx-auto grid min-h-[65vh] max-w-xl place-content-center gap-5 px-5 pb-16 pt-32 text-center">
        <p className="text-xs font-bold uppercase tracking-[.2em] text-[var(--primary)]">Error 404</p>
        <h1 className="font-display text-3xl leading-tight sm:text-4xl">We couldn’t find that page.</h1>
        <p className="text-base leading-7 text-[var(--text-muted)]">The link may be old or mistyped. You can return home or browse the published courses and learning tracks.</p>
        <div className="flex flex-wrap justify-center gap-3">
          <Link className="inline-flex min-h-11 items-center justify-center rounded-lg bg-[var(--accent)] px-5 text-sm font-bold text-[var(--on-accent)]" href="/courses">Browse courses</Link>
          <Link className="inline-flex min-h-11 items-center justify-center rounded-lg border border-[var(--border)] px-5 text-sm font-semibold text-[var(--text-heading)]" href="/">Go home</Link>
        </div>
      </main>
      <PublicFooter />
    </>
  );
}
