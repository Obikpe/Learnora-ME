"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  BookOpen, Compass, Target, FolderKanban, Sparkles, FileCheck2, Award,
  MessageCircle, BrainCircuit, LayoutDashboard, Users, Building2,
  Activity, ShieldCheck, CircleDollarSign, Layers3, LineChart, LockKeyhole, Settings,
  Menu, X, ChevronDown, Route, Search, GraduationCap, CalendarDays
} from "lucide-react";
import { currentUser } from "../../lib/api";

type NavItem = { key: string; label: string; href: string; icon: any };

const learnerItems: NavItem[] = [
  { key: "discover", label: "Discover courses", href: "/courses", icon: Compass },
  { key: "learning", label: "My learning", href: "/dashboard", icon: BookOpen },
  { key: "tracks", label: "Learning tracks", href: "/dashboard/tracks", icon: Route },
  { key: "practice", label: "Practise", href: "/dashboard/practice", icon: Target },
  { key: "projects", label: "Projects", href: "/dashboard/projects", icon: FolderKanban },
  { key: "skills", label: "Skills", href: "/dashboard/skills", icon: Sparkles },
  { key: "portfolio", label: "Portfolio", href: "/dashboard/portfolio", icon: FolderKanban },
  { key: "evidence", label: "Evidence", href: "/dashboard/evidence", icon: FileCheck2 },
  { key: "certificates", label: "Certificates", href: "/dashboard/certificates", icon: Award },
  { key: "community", label: "Community", href: "/dashboard/community", icon: MessageCircle },
  { key: "ai", label: "AI tutor", href: "/dashboard/ai", icon: BrainCircuit },
  { key: "calendar", label: "Learning calendar", href: "/dashboard/calendar", icon: CalendarDays },
];
const adminItems: NavItem[] = [
  { key: "overview", label: "Overview", href: "/dashboard/admin/overview", icon: LayoutDashboard },
  { key: "users", label: "Users", href: "/dashboard/admin/users", icon: Users },
  { key: "organisations", label: "Organisations", href: "/dashboard/admin/organisations", icon: Building2 },
  { key: "courses", label: "Courses", href: "/dashboard/admin/courses", icon: BookOpen },
  { key: "content", label: "Content", href: "/dashboard/admin/content", icon: Layers3 },
  { key: "commercial", label: "Commerce", href: "/dashboard/admin/commercial", icon: CircleDollarSign },
  { key: "creators", label: "Creators", href: "/dashboard/admin/creators", icon: Users },
  { key: "analytics", label: "Analytics", href: "/dashboard/admin/analytics", icon: LineChart },
  { key: "ai", label: "AI operations", href: "/dashboard/admin/ai", icon: BrainCircuit },
  { key: "activity", label: "Activity", href: "/dashboard/admin/activity", icon: Activity },
  { key: "security", label: "Security", href: "/dashboard/admin/security", icon: LockKeyhole },
  { key: "admins", label: "Admins", href: "/dashboard/admin/admins", icon: ShieldCheck },
  { key: "settings", label: "Settings", href: "/dashboard/admin/settings", icon: Settings },
];

export default function Sidebar({ admin = false, role = "", active, hideTutor = false, restricted = false }: {
  admin?: boolean; role?: string; active: string; hideTutor?: boolean; restricted?: boolean;
}) {
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [canTeach, setCanTeach] = useState(false);
  const [assignedLearner, setAssignedLearner] = useState(restricted || role === "assigned");
  const [identityResolved, setIdentityResolved] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    let cancelled = false;
    currentUser().then((me: any) => {
      if (cancelled) return;
      const memberships = me.organisation_memberships || [];
      setCanTeach(memberships.some((membership: any) =>
        membership.role === "instructor" && membership.status === "active"
      ));
      setAssignedLearner(Boolean(
        restricted ||
        me.account_type === "cohort" ||
        me.role === "witstart" ||
        me.cohort_id ||
        me.organisation_role === "learner" ||
        memberships.some((membership: any) => ["learner", "member"].includes(membership.role) && membership.status === "active")
      ));
    }).catch(() => {}).finally(() => {
      if (!cancelled) setIdentityResolved(true);
    });

    return () => { cancelled = true; };
  }, [restricted, role]);

  const isRestrictedLearner = restricted || assignedLearner || role === "assigned" || !identityResolved;
  const items = (admin ? adminItems : learnerItems).filter(item =>
    !(hideTutor && item.key === "ai") &&
    !(isRestrictedLearner && ["discover", "tracks"].includes(item.key))
  );
  const extraItems = canTeach && !admin
    ? [...items, { key: "instructor", label: "Teaching", href: "/dashboard/instructor", icon: GraduationCap }]
    : items;
  const primaryItems = admin ? extraItems.slice(0, 3) : extraItems.filter(item =>
    ["discover", "learning", "tracks"].includes(item.key)
  );
  const moreItems = extraItems.filter(item => !primaryItems.some(primary => primary.key === item.key));
  const mobileItems = extraItems.filter(item => !["notifications", "settings"].includes(item.key));
  const isActive = (item: NavItem) => active === item.key || (item.key === "learning" && active === "overview");
  const navLink = (item: NavItem, mobile = false) => {
    const Icon = item.icon;
    return <Link key={item.key} href={item.href} onClick={() => setMobileOpen(false)}
      aria-current={isActive(item) ? "page" : undefined}
      className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${isActive(item)
        ? "bg-[var(--primary-tint)] text-[var(--primary)]"
        : "text-[var(--text-body)] hover:bg-[var(--bg-soft)] hover:text-[var(--text-heading)]"} ${mobile ? "w-full" : "whitespace-nowrap"}`}>
      <Icon size={16} strokeWidth={1.8}/><span>{item.label}</span>
    </Link>;
  };

  function submitSearch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = search.trim();
    router.push(value ? "/courses?search=" + encodeURIComponent(value) : "/courses");
    setMobileOpen(false);
  }

  return <div className="flex min-w-0 flex-1 items-center gap-5">
    <div className="flex shrink-0 items-center xl:hidden">
      <button type="button" onClick={() => setMobileOpen(value => !value)} aria-label={mobileOpen ? "Close navigation" : "Open navigation"} aria-expanded={mobileOpen}
        className="grid size-10 place-items-center rounded-lg border border-[var(--border)] text-[var(--text-body)] hover:bg-[var(--bg-soft)]">
        {mobileOpen ? <X size={19}/> : <Menu size={19}/>}
      </button>
    </div>
    <Link href={admin ? "/dashboard/admin/overview" : "/dashboard"} className="flex shrink-0 items-center gap-2 text-lg font-bold tracking-tight text-[var(--text-heading)]" aria-label="Learnora ME home">
      <span>Learnora <span className="text-[var(--primary)]">ME</span></span>
    </Link>

    <nav aria-label="Main navigation" className="hidden items-center gap-1 xl:flex">
      {primaryItems.map(item => navLink(item))}
      {moreItems.length > 0 && <details className="group relative">
        <summary className="flex cursor-pointer list-none items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-[var(--text-body)] hover:bg-[var(--bg-soft)] hover:text-[var(--text-heading)]">
          More <ChevronDown size={14} className="transition-transform group-open:rotate-180"/>
        </summary>
        <div className="absolute left-0 top-full z-50 mt-2 max-h-[min(70vh,34rem)] w-64 overflow-y-auto rounded-xl border border-[var(--border)] bg-[var(--card)] p-2 shadow-xl">
          {moreItems.map(item => navLink(item, true))}
        </div>
      </details>}
    </nav>

    {!isRestrictedLearner && <form onSubmit={submitSearch} role="search" className="hidden min-w-40 max-w-xs flex-1 items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--bg-soft)] px-3.5 py-2 lg:flex">
      <Search size={16} className="shrink-0 text-[var(--text-muted)]"/>
      <input aria-label="Search courses" name="search" value={search} onChange={event => setSearch(event.target.value)}
        placeholder="What do you want to learn?" className="min-w-0 w-full bg-transparent text-xs text-[var(--text-body)] outline-none placeholder:text-[var(--text-muted)]"/>
    </form>}



    {mobileOpen && <div className="fixed inset-0 z-[80] xl:hidden">
      <button type="button" aria-label="Close navigation" onClick={() => setMobileOpen(false)} className="absolute inset-0 bg-black/45"/>
      <section role="dialog" aria-modal="true" aria-label="Learning navigation" className="absolute inset-y-0 left-0 flex w-[min(21rem,88vw)] flex-col border-r border-[var(--border)] bg-[var(--card)] p-4 shadow-2xl">
        <div className="mb-5 flex items-center justify-between border-b border-[var(--border)] pb-4">
          <span className="font-bold text-[var(--text-heading)]">Learnora <span className="text-[var(--primary)]">ME</span></span>
          <button type="button" onClick={() => setMobileOpen(false)} aria-label="Close navigation" className="grid size-9 place-items-center rounded-lg hover:bg-[var(--bg-soft)]"><X size={18}/></button>
        </div>
        {!isRestrictedLearner && <form onSubmit={submitSearch} role="search" className="mb-4 flex items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--bg-soft)] px-3 py-2">
          <Search size={16} className="text-[var(--text-muted)]"/>
          <input aria-label="Search courses" value={search} onChange={event => setSearch(event.target.value)} placeholder="What do you want to learn?" className="w-full bg-transparent py-1 text-sm outline-none"/>
          <button type="submit" className="text-xs font-semibold text-[var(--primary)]">Search</button>
        </form>}
        <nav aria-label="Learning destinations" className="flex-1 space-y-1 overflow-y-auto">
          {mobileItems.map(item => navLink(item, true))}
        </nav>
      </section>
    </div>}
  </div>;
}
