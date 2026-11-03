import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import LearningSessionTracker from "./LearningSessionTracker";

export default function Shell({ children, admin, role, active, hideTutor = false }: {
  children: React.ReactNode; admin?: boolean; role?: string; active: string; hideTutor?: boolean;
}) {
  return <div className="min-h-screen bg-[var(--bg)] text-[var(--text-body)]">
    {!admin && <LearningSessionTracker/>}
    <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-[var(--bg)]/95 backdrop-blur-xl">
      <div className="relative mx-auto flex h-[4.5rem] max-w-[1280px] items-center gap-3 px-4 sm:px-6 lg:px-8">
        <Sidebar admin={admin} role={role} active={active} hideTutor={hideTutor}/>
        <Topbar admin={admin}/>
      </div>
    </header>
    <main className="mx-auto w-full max-w-[1180px] px-4 pb-12 pt-7 sm:px-6 sm:pt-9 lg:px-8 lg:pt-10">
      {children}
    </main>
  </div>;
}
