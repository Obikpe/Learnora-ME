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
    let heartbeatTimer: number | null = null;
    let eligibleLearner = false;

    const recentInteraction = () => Date.now() - lastActivityAt.current <= 300_000;
    const activeNow = () => document.visibilityState === "visible" && recentInteraction();

    // A tab becoming hidden must not end the learner's shared session: another
    // tab may still be active. Pause this tab's accounting and let the database
    // reuse the active session when this tab becomes visible again.
    const pause = (keepalive = false) => {
      const id = sessionId.current;
      if (!id) return;
      sessionId.current = null;
      const body = JSON.stringify({ active: recentInteraction() });
      if (keepalive) {
        void fetch("/api/progress/learning-sessions/" + id + "/heartbeat", {
          method: "POST",
          credentials: "same-origin",
          keepalive: true,
          headers: { "Content-Type": "application/json" },
          body,
        }).catch(() => {});
        return;
      }
      void request("/progress/learning-sessions/" + id + "/heartbeat", {
        method: "POST",
        body,
      }).catch(() => {});
    };

    const start = async () => {
      if (disposed || !eligibleLearner || starting.current || sessionId.current || document.visibilityState !== "visible") return;
      starting.current = true;
      try {
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "Africa/Lagos";
        const result = await request<SessionStart>("/progress/learning-sessions/start", {
          method: "POST",
          body: JSON.stringify({ timezone }),
        });
        const id = result.session?.id || null;
        if (disposed || document.visibilityState !== "visible") {
          if (id) {
            void fetch("/api/progress/learning-sessions/" + id + "/heartbeat", {
              method: "POST",
              credentials: "same-origin",
              keepalive: true,
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ active: false }),
            }).catch(() => {});
          }
          return;
        }
        sessionId.current = id;
      } catch {
        // Tracking is supplementary and must never interrupt a learning session.
      } finally {
        starting.current = false;
      }
    };

    const heartbeat = () => {
      const id = sessionId.current;
      if (!id || document.visibilityState !== "visible") return;
      void request("/progress/learning-sessions/" + id + "/heartbeat", {
        method: "POST",
        body: JSON.stringify({ active: activeNow() }),
      }).catch(() => {
        // A stale session is safely replaced on the next visible start.
        sessionId.current = null;
      });
    };

    const markActivity = () => { lastActivityAt.current = Date.now(); };
    const markMediaActivity = () => { if (document.visibilityState === "visible") markActivity(); };
    const onVisibility = () => {
      if (document.visibilityState === "hidden") pause(true);
      else {
        markActivity();
        void start();
      }
    };
    const onPageHide = () => pause(true);

    const activityEvents = ["pointerdown", "pointermove", "keydown", "scroll", "touchstart"];
    activityEvents.forEach(event => window.addEventListener(event, markActivity, { passive: true }));
    document.addEventListener("visibilitychange", onVisibility);
    document.addEventListener("play", markMediaActivity, true);
    document.addEventListener("playing", markMediaActivity, true);
    document.addEventListener("timeupdate", markMediaActivity, true);
    window.addEventListener("pagehide", onPageHide);

    void currentUser().then(me => {
      const role = String(me?.role || "").toLowerCase();
      const accountType = String(me?.account_type || "").toLowerCase();
      const organisationRole = String(me?.organisation_role || "").toLowerCase();
      const hasPrivilegedMembership = (me?.organisation_memberships || []).some((membership: any) =>
        membership.status === "active" && ["owner", "admin", "team_manager"].includes(String(membership.role || "").toLowerCase())
      );
      const learnerRole = ["normal", "witstart"].includes(role);
      eligibleLearner = accountType === "cohort" ||
        (accountType === "learner" && learnerRole && !hasPrivilegedMembership && !["owner", "admin", "team_manager"].includes(organisationRole));
      if (eligibleLearner) void start();
    }).catch(() => {});

    heartbeatTimer = window.setInterval(heartbeat, 60_000);

    return () => {
      disposed = true;
      if (heartbeatTimer !== null) window.clearInterval(heartbeatTimer);
      activityEvents.forEach(event => window.removeEventListener(event, markActivity));
      document.removeEventListener("visibilitychange", onVisibility);
      document.removeEventListener("play", markMediaActivity, true);
      document.removeEventListener("playing", markMediaActivity, true);
      document.removeEventListener("timeupdate", markMediaActivity, true);
      window.removeEventListener("pagehide", onPageHide);
      pause(true);
    };
  }, []);

  return null;
}
