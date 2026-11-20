"use client";
import { useState } from "react";
import { createPortal } from "react-dom";
import { Award, Download, X } from "lucide-react";

export default function CertificateArtwork({ certificate }: { certificate: any }) {
  const [open, setOpen] = useState(false);
  const issued = certificate.issued_at ? new Date(certificate.issued_at) : null;
  const date = issued && !Number.isNaN(issued.getTime()) ? issued.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" }) : "Date unavailable";
  const artwork = <div className="certificate-artwork flex aspect-[1.414/1] w-full flex-col items-center justify-center border-[8px] border-double border-[#b99a52] bg-[#fffdf6] px-[7%] py-[5%] text-center text-[#24233b]">
    <div className="grid size-9 place-items-center rounded-full border border-[#b99a52] text-[#9b7b35]"><Award size={20}/></div>
    <p className="mt-2 text-[clamp(8px,1vw,13px)] font-bold uppercase tracking-[.25em] text-[#92783e]">Learnora ME</p>
    <h2 className="mt-2 font-serif text-[clamp(20px,3vw,42px)]">Certificate of Completion</h2>
    <p className="mt-3 text-[clamp(8px,1vw,13px)] uppercase tracking-widest text-[#77715f]">Presented to</p>
    <p className="mt-1 max-w-full truncate font-serif text-[clamp(17px,2.4vw,34px)] font-semibold">{certificate.recipient_name || certificate.user_name || "Learnora Learner"}</p>
    <p className="mt-2 text-[clamp(8px,1vw,13px)] text-[#77715f]">For successfully completing</p>
    <p className="mt-1 max-w-[85%] text-[clamp(14px,1.8vw,24px)] font-semibold">{certificate.course_title || "Course completion"}</p>
    <div className="mt-5 flex w-full justify-between text-[clamp(7px,.85vw,11px)] text-[#77715f]"><span>Learnora ME</span><span>{date}</span></div>
    <p className="mt-2 text-[clamp(6px,.75vw,10px)] text-[#8b805f]">Certificate No. {certificate.certificate_number || "Pending"}</p>
  </div>;

  return <>
    <button type="button" onClick={() => setOpen(true)} className="h-24 w-36 shrink-0 overflow-hidden rounded-md border border-[var(--border)] hover:border-[var(--primary)]" aria-label={"Open certificate for " + certificate.course_title}><span className="block w-[222%] origin-top-left scale-[.45]">{artwork}</span></button>
    {open && typeof document !== "undefined" && createPortal(
      <div className="certificate-print-overlay fixed inset-0 z-[10000] flex items-center justify-center overflow-y-auto bg-black/75 p-3 sm:p-6" onMouseDown={(event) => { if (event.target === event.currentTarget) setOpen(false); }}>
        <section role="dialog" aria-modal="true" aria-label={"Certificate for " + certificate.course_title} className="my-auto w-full max-w-[1100px] rounded-xl bg-[var(--card)] p-3 shadow-2xl sm:p-6">
          <div className="mb-4 flex items-center justify-between gap-4 print:hidden"><div><h3 className="font-semibold">Your certificate</h3><p className="text-xs text-[var(--text-muted)]">Full-size preview. Print or save as PDF.</p></div><button type="button" onClick={() => setOpen(false)} aria-label="Close certificate" className="grid size-9 shrink-0 place-items-center rounded-full hover:bg-[var(--bg-soft)]"><X size={18}/></button></div>
          {artwork}
          <div className="mt-4 flex justify-end print:hidden"><button type="button" onClick={() => window.print()} className="inline-flex items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-[var(--on-primary)]"><Download size={15}/> Download / Print</button></div>
        </section>
      </div>,
      document.body
    )}
    <style jsx global>{`@media print { body * { visibility:hidden !important; } .certificate-print-overlay,.certificate-print-overlay * { visibility:visible !important; } .certificate-print-overlay { position:absolute !important; inset:0 !important; display:block !important; padding:0 !important; background:#fff !important; } .certificate-print-overlay>section { width:100% !important; max-width:none !important; margin:0 !important; padding:0 !important; box-shadow:none !important; } .certificate-artwork { width:100% !important; aspect-ratio:1.414/1 !important; -webkit-print-color-adjust:exact; print-color-adjust:exact; } @page { size:landscape; margin:10mm; } }`}</style>
  </>;
}
