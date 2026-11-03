export default function StatCard({ label, value, detail }: { label: string; value: any; detail?: string }) {
  return <section className="group min-w-0 rounded-xl border border-[var(--border)] bg-[var(--card)] p-4 shadow-[var(--shadow)] transition-colors hover:border-[var(--primary)] sm:p-5">
    <p className="text-xs font-medium text-[var(--text-muted)]">{label}</p>
    <div className="mt-3 break-words text-3xl font-semibold tracking-tight tabular-nums text-[var(--text-heading)] sm:text-4xl">{value ?? "—"}</div>
    {detail && <p className="mt-2 text-xs leading-5 text-[var(--text-muted)]">{detail}</p>}
  </section>;
}
