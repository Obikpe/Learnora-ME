"use client";

import { useState } from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import LearningSessionTracker from "./LearningSessionTracker";
import NotificationPanel from "./NotificationPanel";

export default function Shell({ children, admin, role, active, hideTutor = false, restricted = false, trackLearning = true }: {
  children: React.ReactNode; admin?: boolean; role?: string; active: string; hideTutor?: boolean; restricted?: boolean; trackLearning?: boolean;
}) {
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [selectedNotificationId, setSelectedNotificationId] = useState<string | undefined>(undefined);
  const openNotifications = (id?: string) => {
    setSelectedNotificationId(id);
    setNotificationsOpen(true);
  };

  return <div className="min-h-screen bg-[var(--bg)] text-[var(--text-body)]">
    {!admin && trackLearning && <LearningSessionTracker/>}
    <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-[var(--bg)]/95 backdrop-blur-xl">
      <div className="relative mx-auto flex h-[4.5rem] max-w-[1280px] items-center gap-3 px-4 sm:px-6 lg:px-8">
        <Sidebar admin={admin} role={role} active={active} hideTutor={hideTutor} restricted={restricted}/>
        <Topbar admin={admin} onOpenNotification={openNotifications}/>
      </div>
    </header>
    <main className="mx-auto w-full max-w-[1180px] px-4 pb-12 pt-7 sm:px-6 sm:pt-9 lg:px-8 lg:pt-10">
      {children}
    </main>
    <NotificationPanel open={notificationsOpen} initialSelectedId={selectedNotificationId} onClose={() => setNotificationsOpen(false)}/>
  </div>;
}
