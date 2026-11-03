"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { currentUser } from "../../lib/api";
import Skeleton from "../../components/feedback/Skeleton";

export default function Layout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [authorised, setAuthorised] = useState(false);
  useEffect(() => {
    let active = true;
    setAuthorised(false);
    const validate = () => currentUser().then(() => {
      if (active) setAuthorised(true);
    }).catch(() => {
      if (active) window.location.replace("/");
    });
    void validate();
    const onPageShow = () => {
      if (sessionStorage.getItem("phx_logged_out") === "1" || localStorage.getItem("phx_logged_out") === "1") window.location.replace("/");
      else void validate();
    };
    window.addEventListener("pageshow", onPageShow);
    const onStorage = (event: StorageEvent) => { if (event.key === "phx_logged_out" && event.newValue === "1") window.location.replace("/"); };
    window.addEventListener("storage", onStorage);
    return () => { active = false; window.removeEventListener("pageshow", onPageShow); window.removeEventListener("storage", onStorage); };
  }, [pathname]);
  if (!authorised) return <main className="min-h-screen bg-[var(--bg)] p-6"><div className="mx-auto max-w-5xl pt-12"><Skeleton label="Checking your Learnora session"/></div></main>;
  return children;
}
