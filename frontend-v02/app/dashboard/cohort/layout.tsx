import { usePathname } from "next/navigation";
import LearningSessionTracker from "../../../components/dashboard/LearningSessionTracker";

"use client";

export default function CohortLearningLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLearningContent = pathname.startsWith("/dashboard/cohort/courses/");
  return <>{isLearningContent && <LearningSessionTracker/>}{children}</>;
}
