export default function EmptyState({title,message,action}:{title:string;message:string;action?:React.ReactNode}) {
  return <section className="py-8 text-left" aria-live="polite">
    <h3 className="text-base font-semibold text-[var(--text-heading)]">{title}</h3>
    <p className="mt-2 max-w-lg text-sm leading-7 text-[var(--text-body)]">{message}</p>
    {action&&<div className="mt-4">{action}</div>}
  </section>;
}
