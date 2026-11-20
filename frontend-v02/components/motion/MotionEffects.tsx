"use client";
import { useEffect } from "react";

/** One shared observer for reveals, dynamic sections and mouse-only card tilt. */
export default function MotionEffects() {
  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
    const seen = new WeakSet<Element>();
    const io = "IntersectionObserver" in window ? new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const el = entry.target as HTMLElement;
        el.classList.add("is-in","is-visible");
        io!.unobserve(el);
      }
    }, { rootMargin:"0px 0px -12% 0px",threshold:0.01 }) : null;

    const prepareStagger = (root: ParentNode) => {
      root.querySelectorAll<HTMLElement>("[data-stagger]").forEach(parent => {
        Array.from(parent.children).forEach((child,i) => {
          const el = child as HTMLElement;
          if (!el.hasAttribute("data-reveal")) el.setAttribute("data-reveal","up");
          el.style.setProperty("--d",Math.min(i,8)*0.08+"s");
        });
      });
    };
    const scan = (root: ParentNode = document) => {
      prepareStagger(root);
      root.querySelectorAll<HTMLElement>("[data-reveal],.landing-reveal").forEach(el => {
        if (seen.has(el)) return;
        seen.add(el);
        if (!io || reduce.matches) el.classList.add("is-in","is-visible");
        else io.observe(el);
      });
    };
    scan();

    let pending = 0;
    const mutations = new MutationObserver(() => {
      if (pending) return;
      pending = requestAnimationFrame(() => { pending=0; scan(); });
    });
    mutations.observe(document.body,{childList:true,subtree:true});

    let raf = 0;
    const onMove = (event: PointerEvent) => {
      if (event.pointerType !== "mouse" || reduce.matches) return;
      const el = (event.target as Element | null)?.closest?.("[data-tilt],[data-spotlight]") as HTMLElement | null;
      if (!el) return;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const rect = el.getBoundingClientRect();
        if (!rect.width || !rect.height) return;
        const px=(event.clientX-rect.left)/rect.width, py=(event.clientY-rect.top)/rect.height;
        el.style.setProperty("--mx",(px*100).toFixed(1)+"%");
        el.style.setProperty("--my",(py*100).toFixed(1)+"%");
        const max=Number(el.getAttribute("data-tilt"))||5;
        el.style.setProperty("--ry",((px-.5)*2*max).toFixed(2)+"deg");
        el.style.setProperty("--rx",((.5-py)*2*max).toFixed(2)+"deg");
      });
    };
    const onOut = (event: PointerEvent) => {
      const el=(event.target as Element | null)?.closest?.("[data-tilt]") as HTMLElement | null;
      if (!el || el.contains(event.relatedTarget as Node | null)) return;
      el.style.setProperty("--rx","0deg"); el.style.setProperty("--ry","0deg");
    };
    document.addEventListener("pointermove",onMove,{passive:true});
    document.addEventListener("pointerout",onOut,{passive:true});
    return () => {
      io?.disconnect(); mutations.disconnect(); cancelAnimationFrame(raf);
      document.removeEventListener("pointermove",onMove);
      document.removeEventListener("pointerout",onOut);
    };
  },[]);
  return <div className="scroll-progress" aria-hidden="true" />;
}
