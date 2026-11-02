"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, AlertCircle } from "lucide-react";

export default function Toast({ title, message, type = "success", onClose }: { title: string; message: string; type?: "success" | "error"; onClose?: () => void }) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      setVisible(false);
      onClose?.();
    }, 5000);
    return () => window.clearTimeout(timeout);
  }, []);

  if (!visible) return null;

  return (
    <div
      role={type === "error" ? "alert" : "status"}
      aria-live={type === "error" ? "assertive" : "polite"}
      className="fixed bottom-5 right-5 z-[100] w-[min(92vw,390px)] overflow-hidden rounded-2xl border border-white/10 bg-[#111820]/95 p-4 text-white shadow-[0_18px_60px_rgba(0,0,0,.45)] backdrop-blur-xl animate-in slide-in-from-bottom-3 fade-in duration-200"
    >
      <div className="flex items-start gap-3">
        <span className={`mt-0.5 grid size-9 shrink-0 place-items-center rounded-full ${type === "success" ? "bg-emerald-300/10 text-emerald-200" : "bg-rose-300/10 text-rose-200"}`}>
          {type === "success" ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold tracking-tight">{title}</p>
          <p className="mt-1 text-sm leading-6 text-slate-300">{message}</p>
        </div>
      </div>
      <div className="absolute inset-x-0 bottom-0 h-[2px] bg-white/5">
        <div className="h-full origin-left animate-[toast-shrink_5s_linear_forwards] bg-[var(--gold)]" />
      </div>
    </div>
  );
}
