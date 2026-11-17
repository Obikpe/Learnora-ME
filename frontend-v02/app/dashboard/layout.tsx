import type { Metadata } from "next";
import DashboardSessionGuard from "../../components/dashboard/DashboardSessionGuard";

export const metadata: Metadata = { robots: { index: false, follow: false } };

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <DashboardSessionGuard>{children}</DashboardSessionGuard>;
}
