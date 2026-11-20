"use client";
import { useEffect, useRef, useState } from "react";

/** Counts up once near the viewport. Server HTML contains the final number. */
export default function CountUp({ value, suffix = "", duration = 1400 }: { value: number; suffix?: string; duration?: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const [shown, setShown] = useState(value);
  useEffect(() => {
    const el = ref.current;
    if (!el || window.matchMedia("(prefers-reduced-motion: reduce)").matches || !("IntersectionObserver" in window)) return;
    let raf = 0;
    let started = false;
    const io = new IntersectionObserver(([entry]) => {
      if (!entry.isIntersecting || started) return;
      started = true;
      io.disconnect();
      const t0 = performance.now();
      setShown(0);
      const tick = (now: number) => {
        const p = Math.min(1, (now - t0) / duration);
        setShown(Math.round(value * (1 - Math.pow(1 - p, 3))));
        if (p < 1) raf = requestAnimationFrame(tick);
      };
      raf = requestAnimationFrame(tick);
    }, { rootMargin:"0px 0px 8% 0px" });
    io.observe(el);
    return () => { io.disconnect(); cancelAnimationFrame(raf); };
  }, [value,duration]);
  return <span ref={ref}><span aria-hidden="true">{shown.toLocaleString("en")}{suffix}</span><span className="sr-only">{value.toLocaleString("en")}{suffix}</span></span>;
}
