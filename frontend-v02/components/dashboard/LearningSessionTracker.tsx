"use client";

import { useEffect, useRef } from "react";
import { request } from "../../lib/api/client";
import { currentUser } from "../../lib/api/auth";

type SessionStart = { session?: { id?: string } };

export default function LearningSessionTracker() {
  const sessionId = useRef<string | null>(null);
  const lastActivityAt = useRef(Date.now());
  const starting = useRef(false);

  useEffect(() => {
    let disposed = false;
    let heartbeatTimer: ReturnType<typeof setInterval> | null = null;

    const recentInteraction = () => Date.now() - lastActivityAt.current <= 300_000;
    const activeNow = () => document.visibilityState === "visible" && recentInteraction();

    const end = (keepalive = false) => {
      const id = sessionId.current;
      if (!id) return;
      sessionId.current = null;
      const body = JSON.stringify({ active: recentInteraction() });
      if (keepalive) {
        try {
          const payload = new Blob([body], { type: "application/json" });
          if (navigator.sendBeacon("/api/progress/learning-sessions/" + id + "/end", payload)) return;
        } catch {}
        void fetch("/api/progress/learning-sessions/" + id + "/end", {
          method: "POST", credentials: "same-origin", keepalive: true,
          headers: { "Content-Type": "application/json" }, body,
        }).catch(() => {});
        return;
      }
      void request("/progress/learning-sessions/" + id + "/end", {
        method: "POST", body,
      }).catch(() => {});
    };

    let eligibleLearner = false;
    const start = async () => {
      if (disposed || !eligibleLearner || starting.current || sessionId.current || document.visibilityState !== "visible") return;
      starting.current = true;
      try {
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "Africa/Lagos";
        const result = await request<SessionStart>("/progress/learning-sessions/start", {
          method: "POST", body: JSON.stringify({ timezone }),
        });
        if (disposed) {
          const id = result.session?.id;
          if (id) void fetch("/api/progress/learning-sessions/" + id + "/end", {
            method: "POST", credentials: "same-origin", keepalive: true,
            headers: { "Content-Type": "application/json" }, body: JSON.stringify({ active: false }),
          }).catch(() => {});
          return;
        }
        sessionId.current = result.session?.id || null;
      } catch {
        // Session tracking is supplementary and must not interrupt learning.
      } finally {
        starting.current = false;
      }
    };

    const heartbeat = () => {
      const id = sessionId.current;
      if (!id || document.visibilityState !== "visible") return;
      void request("/progress/learning-sessions/" + id + "/heartbeat", {
        method: "POST", body: JSON.stringify({ active: activeNow() }),
      }).catch(() => {});
    };

    const markActivity = () => { lastActivityAt.current = Date.now(); };
    const onVisibility = () => {
      if (document.visibilityState === "hidden") end(true);
      else { markActivity(); void start(); }
    };
    const onPageHide = () => end(true);

    ["pointerdown", "pointermove", "keydown", "scroll", "touchstart"].forEach(event =>
      window.addEventListener(event, markActivity, { passive: true })
    );
    document.addEventListener("visibilitychange", onVisibility);
    window.addEventListener("pagehide", onPageHide);
    void currentUser().then(me => {
      const role = String(me?.role || "").toLowerCase();
      const accountType = String(me?.account_type || "").toLowerCase();
      const organisationRole = String(me?.organisation_role || "").toLowerCase();
      const hasPrivilegedMembership = (me?.organisation_memberships || []).some((membership: any) =>
        membership.status === "active" && ["owner", "admin", "team_manager"].includes(String(membership.role || "").toLowerCase())
      );
      eligibleLearner = accountType === "cohort" ||
        (role === "normal" && !hasPrivilegedMembership && !["owner", "admin", "team_manager"].includes(organisationRole));
      if (eligibleLearner) void start();
    }).catch(() => {});
    heartbeatTimer = window.setInterval(heartbeat, 30_000);

    return () => {
      disposed = true;
      if (heartbeatTimer) window.clearInterval(heartbeatTimer);
      ["pointerdown", "keydown", "scroll", "touchstart"].forEach(event =>
        window.removeEventListener(event, markActivity)
      );
      document.removeEventListener("visibilitychange", onVisibility);
      window.removeEventListener("pagehide", onPageHide);
      end(true);
    };
  }, []);

  return null;
}
