"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  BookOpen, Compass, Target, FolderKanban, Sparkles, FileCheck2, Award,
  MessageCircle, BrainCircuit, Bell, Settings, LayoutDashboard, LogOut,
  Users, Building2, Activity, ShieldCheck, CircleDollarSign, Layers3,
  LineChart, LockKeyhole, CreditCard, Menu, X, ChevronDown, Route,
  Search, GraduationCap
} from "lucide-react";
import { clearToken, currentUser } from "../../lib/api";

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
  { key: "notifications", label: "Notifications", href: "/dashboard/notifications", icon: Bell },
  { key: "subscription", label: "Subscription", href: "/dashboard/subscription", icon: CreditCard },
  { key: "settings", label: "Account settings", href: "/dashboard/settings", icon: Settings },
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

export default function Sidebar({ admin = false, role = "", active, hideTutor = false }: {
  admin?: boolean; role?: string; active: string; hideTutor?: boolean;
}) {
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [canTeach, setCanTeach] = useState(false);
  const [isCohortAccount, setIsCohortAccount] = useState(false);
  const [isFreeAccess, setIsFreeAccess] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    let cancelled = false;
    currentUser().then((me: any) => {
      if (cancelled) return;
      setCanTeach((me.organisation_memberships || []).some((membership: any) =>
        membership.role === "instructor" && membership.status === "active"
      ));
      setIsCohortAccount(me.account_type === "cohort");
      setIsFreeAccess(me.access_state === "free" && me.course_access === true);
    }).catch(() => {});
    return () => { cancelled = true; };
  }, []);

  const items = (admin ? adminItems : learnerItems).filter(item =>
    !(hideTutor && item.key === "ai") &&
    !((isCohortAccount || isFreeAccess) && item.key === "subscription")
  );
  const extraItems = canTeach && !admin
    ? [...items, { key: "instructor", label: "Teaching", href: "/dashboard/instructor", icon: GraduationCap }]
    : items;
  const primaryItems = admin ? extraItems.slice(0, 3) : extraItems.filter(item =>
    ["discover", "learning", "tracks"].includes(item.key)
  );
  const moreItems = extraItems.filter(item => !primaryItems.some(primary => primary.key === item.key));
  const logout = () => { clearToken(); window.location.replace("/"); };
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
    <Link href={admin ? "/dashboard/admin/overview" : "/dashboard"} className="flex shrink-0 items-center gap-2 text-lg font-bold tracking-tight text-[var(--text-heading)]" aria-label="Learnora ME home">
      <span className="grid size-8 place-items-center rounded-lg bg-[var(--primary)] text-sm font-bold text-[var(--on-primary)]">L</span>
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
          <button type="button" onClick={logout} className="mt-1 flex w-full items-center gap-2 rounded-lg border-t border-[var(--border)] px-3 py-3 text-left text-sm text-[var(--text-muted)] hover:bg-[var(--bg-soft)] hover:text-[var(--error)]"><LogOut size={16}/>Sign out</button>
        </div>
      </details>}
    </nav>

    <form onSubmit={submitSearch} role="search" className="hidden min-w-40 max-w-xs flex-1 items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--bg-soft)] px-3.5 py-2 lg:flex">
      <Search size={16} className="shrink-0 text-[var(--text-muted)]"/>
      <input aria-label="Search courses" name="search" value={search} onChange={event => setSearch(event.target.value)}
        placeholder="What do you want to learn?" className="min-w-0 w-full bg-transparent text-xs text-[var(--text-body)] outline-none placeholder:text-[var(--text-muted)]"/>
    </form>

    <div className="ml-auto flex items-center gap-2 xl:hidden">
      <button type="button" onClick={() => setMobileOpen(value => !value)} aria-label={mobileOpen ? "Close navigation" : "Open navigation"} aria-expanded={mobileOpen}
        className="grid size-10 place-items-center rounded-lg border border-[var(--border)] text-[var(--text-body)] hover:bg-[var(--bg-soft)]">
        {mobileOpen ? <X size={19}/> : <Menu size={19}/>}
      </button>
    </div>

    {mobileOpen && <div className="absolute inset-x-0 top-full z-50 max-h-[calc(100dvh-4.5rem)] overflow-y-auto border-b border-[var(--border)] bg-[var(--card)] p-4 shadow-xl xl:hidden">
      <form onSubmit={submitSearch} role="search" className="mb-3 flex items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--bg-soft)] px-3 py-2">
        <Search size={16} className="text-[var(--text-muted)]"/>
        <input aria-label="Search courses" value={search} onChange={event => setSearch(event.target.value)} placeholder="What do you want to learn?" className="w-full bg-transparent py-1 text-sm outline-none"/>
        <button type="submit" className="text-xs font-semibold text-[var(--primary)]">Search</button>
      </form>
      <nav aria-label="Mobile navigation" className="grid gap-1">
        {extraItems.map(item => navLink(item, true))}
        <button type="button" onClick={logout} className="mt-2 flex min-h-11 w-full items-center gap-2 border-t border-[var(--border)] px-3 pt-3 text-left text-sm text-[var(--text-muted)] hover:text-[var(--error)]"><LogOut size={16}/>Sign out</button>
      </nav>
    </div>}
  </div>;
}
