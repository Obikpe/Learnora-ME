"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { clearToken, setToken, teamMe, token } from "../lib/api";

const IDLE_LIMIT_MS = 10 * 60 * 1000;

export default function SessionGuard() {
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (pathname === "/login") return;
    let active = true;
    let timer: number | undefined;
    const events = ["pointerdown", "keydown", "mousemove", "touchstart", "scroll"];
    let lastWrite = 0;

    const markActivity = () => {
      if (!token()) return;
      const now = Date.now();
      if (now - lastWrite >= 5000) {
        sessionStorage.setItem("learnora_team_last_activity", String(now));
        lastWrite = now;
      }
    };

    const checkIdle = () => {
      if (!token()) {
        router.replace("/login");
        return;
      }
      const raw = sessionStorage.getItem("learnora_team_last_activity");
      const last = raw ? Number(raw) : Date.now();
      if (!Number.isFinite(last) || Date.now() - last >= IDLE_LIMIT_MS) {
        void clearToken().then(() => router.replace("/login?reason=idle"));
      }
    };

    const restoreCookieSession = async () => {
      try {
        // Verify the HttpOnly cookie with the backend. This also restores the
        // non-secret tab marker when a valid cookie is opened in a new tab.
        await teamMe();
        if (!active) return;
        if (!token()) setToken("cookie-session");
        if (!sessionStorage.getItem("learnora_team_last_activity")) {
          sessionStorage.setItem("learnora_team_last_activity", String(Date.now()));
        }
        markActivity();
        checkIdle();
        timer = window.setInterval(checkIdle, 15000);
        events.forEach((event) => window.addEventListener(event, markActivity, { passive: true }));
        document.addEventListener("visibilitychange", checkIdle);
      } catch {
        if (active) {
          sessionStorage.removeItem("learnora_team_token");
          sessionStorage.removeItem("learnora_team_last_activity");
          router.replace("/login");
        }
      }
    };

    void restoreCookieSession();
    return () => {
      active = false;
      if (timer !== undefined) window.clearInterval(timer);
      events.forEach((event) => window.removeEventListener(event, markActivity));
      document.removeEventListener("visibilitychange", checkIdle);
    };
  }, [pathname, router]);

  return null;
}
