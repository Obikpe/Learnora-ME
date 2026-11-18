"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowRight, ChevronDown, Menu, X, Headset, Sun, Moon } from "lucide-react";
import Logo from "../brand/Logo";
import Link from "next/link";
import { hasFunctionalCookieConsent } from "../../lib/cookie-consent";

const audiences = [
  { href: "/for-learners", title: "For learners", detail: "Build skills, projects and evidence." },
  { href: "/for-instructors", title: "For instructors", detail: "Teach, guide and grow your practice." },
  { href: "/for-organisations", title: "For organisations", detail: "Develop people and capability." },
];
const links = [
  { href: "/tracks", title: "Learning tracks" },
  { href: "/courses", title: "Browse courses" },
  { href: "/how-it-works", title: "How it works" },
  { href: "/about", title: "About Learnora" },
];

export default function PublicNav() {
  const [open, setOpen] = useState(false);
  const [audienceOpen, setAudienceOpen] = useState(false);
  const [theme, setTheme] = useState<"dark" | "light">("light");
  const mobileMenuRef = useRef<HTMLDivElement>(null);
  const menuTriggerRef = useRef<HTMLButtonElement>(null);
  const headerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const root = document.documentElement;
    const saved = hasFunctionalCookieConsent() ? window.localStorage.getItem("learnora_theme") : null;
    const nextTheme = saved === "dark" ? "dark" : "light";
    root.dataset.theme = nextTheme;
    setTheme(nextTheme);
  }, []);
  const close = (restoreFocus = false) => {
    setOpen(false);
    setAudienceOpen(false);
    if (restoreFocus) menuTriggerRef.current?.focus();
  };
  const toggleTheme = () => {
    const nextTheme = theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = nextTheme;
    try {
      if (hasFunctionalCookieConsent()) window.localStorage.setItem("learnora_theme", nextTheme);
      else window.localStorage.removeItem("learnora_theme");
    } catch {}
    setTheme(nextTheme);
  };

  useEffect(() => {
    if (!open) return;
    const menu = mobileMenuRef.current;
    if (!menu) return;
    const getFocusable = () => Array.from(menu.querySelectorAll<HTMLElement>('a[href], button:not([disabled])'));
    getFocusable()[0]?.focus();
    function trapFocus(event: KeyboardEvent) {
      if (event.key !== "Tab") return;
      const focusable = getFocusable();
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
    document.addEventListener("keydown", trapFocus);
    return () => document.removeEventListener("keydown", trapFocus);
  }, [open]);

  useEffect(() => {
    if (!open && !audienceOpen) return;
    function closeOnOutsidePointer(event: PointerEvent) {
      if (event.target instanceof Node && !headerRef.current?.contains(event.target)) {
        setOpen(false);
        setAudienceOpen(false);
      }
    }
    document.addEventListener("pointerdown", closeOnOutsidePointer);
    return () => document.removeEventListener("pointerdown", closeOnOutsidePointer);
  }, [open, audienceOpen]);

  useEffect(() => {
    if (!open) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = previousOverflow; };
  }, [open]);

  return (
    <header ref={headerRef} onKeyDown={e=>{if(e.key==="Escape")close(true)}} className="public-nav fixed inset-x-0 top-0 z-50 border-b border-white/[.09] bg-[#090b0e]/95 backdrop-blur-xl">
      <div className="mx-auto flex h-20 max-w-[82rem] items-center justify-between px-5 lg:px-8">
        <Link href="#main-content" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[70] focus:bg-white focus:px-4 focus:py-3 focus:text-black" onClick={close}>Skip to content</Link>
        <Link href="/" aria-label="Learnora ME home" onClick={close} className="shrink-0"><Logo /></Link>

        <nav aria-label="Main navigation" className="hidden items-center gap-7 lg:flex">
          <div className="group relative">
            <button type="button" onClick={() => setAudienceOpen(v => !v)} aria-expanded={audienceOpen} aria-haspopup="true" className="inline-flex min-h-11 items-center gap-2 rounded-lg px-2 text-sm text-slate-300 transition-colors hover:text-white focus-visible:outline-offset-2">
              Who it’s for <ChevronDown size={14} className={audienceOpen ? "rotate-180 transition-transform" : "transition-transform"}/>
            </button>
            <div className={`absolute left-0 top-full w-[340px] pt-2 ${audienceOpen ? "visible opacity-100" : "invisible opacity-0"} transition-opacity duration-150`}>
              <div className="public-nav-panel-content border border-white/[.12] bg-[#11171e] p-2 shadow-2xl shadow-black/40">
                {audiences.map((item) => <Link key={item.href} href={item.href} onClick={close} className="group/item flex items-start justify-between gap-4 border-b border-white/[.06] p-4 last:border-0 hover:bg-white/[.035]">
                  <span><span className="block text-sm font-semibold text-slate-100">{item.title}</span><span className="mt-1 block text-xs leading-5 text-slate-500">{item.detail}</span></span>
                  <ArrowRight size={14} className="mt-1 shrink-0 text-slate-600"/>
                </Link>)}
              </div>
            </div>
          </div>
          {links.map(item => <Link key={item.href} href={item.href} className="rounded-lg px-1 py-3 text-sm text-slate-300 transition-colors hover:text-white focus-visible:outline-offset-2">{item.title}</Link>)}
        </nav>

        <div className="hidden items-center gap-3 lg:flex">
          <button type="button" onClick={toggleTheme} aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"} title={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"} className="grid size-11 place-items-center rounded-lg border border-white/[.12] text-slate-300 hover:bg-white/[.05]">{theme === "dark" ? <Sun size={17}/> : <Moon size={17}/>}</button>
          <Link href="/help" aria-label="Help and support" title="Help and support" className="grid size-11 place-items-center rounded-lg border border-white/[.12] text-slate-300 hover:bg-white/[.05]"><Headset size={17}/></Link>
          <Link href="/login" className="rounded-lg px-2 py-3 text-sm text-slate-300 transition-colors hover:text-white">Sign in</Link>
          <Link href="/register" className="public-nav-primary inline-flex min-h-11 items-center gap-2 rounded-lg bg-[var(--accent)] px-4 text-sm font-semibold text-[var(--on-accent)] transition-colors hover:bg-[var(--accent-hover)]">Get started <ArrowRight size={15}/></Link>
        </div>

        <button ref={menuTriggerRef} type="button" className="grid size-11 place-items-center rounded-xl border border-white/[.12] text-slate-200 transition-colors hover:bg-white/[.05] lg:hidden" aria-label={open ? "Close navigation menu" : "Open navigation menu"} aria-controls="public-mobile-nav" aria-expanded={open} onClick={() => setOpen(v => !v)}>
          {open ? <X size={20}/> : <Menu size={20}/>}
        </button>
      </div>

      {open && <div id="public-mobile-nav" ref={mobileMenuRef} role="dialog" aria-modal="true" aria-label="Mobile navigation" className="public-nav-mobile fixed inset-x-0 top-20 bottom-0 overflow-y-auto overscroll-contain border-t border-white/[.08] bg-[#090b0e] px-5 pb-8 pt-3 lg:hidden">
        <nav aria-label="Mobile navigation" className="mx-auto grid max-w-[82rem]">
          <p className="px-3 pb-2 pt-3 text-[10px] font-bold uppercase tracking-[.18em] text-slate-600">Explore Learnora</p>
          {links.map(item => <Link key={item.href} href={item.href} onClick={close} className="flex min-h-12 items-center justify-between border-b border-white/[.06] px-3 text-sm text-slate-200">{item.title}<ArrowRight size={15} className="text-slate-600"/></Link>)}
          <p className="px-3 pb-2 pt-5 text-[10px] font-bold uppercase tracking-[.18em] text-slate-600">Choose your path</p>
          {audiences.map(item => <Link key={item.href} href={item.href} onClick={close} className="rounded-lg px-3 py-3 hover:bg-white/[.04]"><span className="block text-sm font-semibold">{item.title}</span><span className="mt-1 block text-xs text-slate-500">{item.detail}</span></Link>)}
          <div className="mt-4 flex flex-wrap items-center gap-3 border-t border-white/[.08] pt-4">
            <button type="button" onClick={toggleTheme} className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-white/[.14] px-3 text-sm text-slate-300">{theme === "dark" ? <Sun size={16}/> : <Moon size={16}/>} {theme === "dark" ? "Light theme" : "Dark theme"}</button>
            <Link href="/help" onClick={close} className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-white/[.14] px-3 text-sm text-slate-300"><Headset size={16}/> Support</Link>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3">
            <Link href="/login" onClick={close} className="grid min-h-12 place-items-center rounded-lg border border-white/[.14] text-sm font-semibold">Sign in</Link>
            <Link href="/register" onClick={close} className="public-nav-primary inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-[var(--accent)] text-sm font-semibold text-[var(--on-accent)]">Get started <ArrowRight size={15}/></Link>
          </div>
        </nav>
      </div>}
    </header>
  );
}
