import LearningSessionTracker from "../../../components/dashboard/LearningSessionTracker";

export default function CohortLearningLayout({ children }: { children: React.ReactNode }) {
  return <>{children}<LearningSessionTracker /></>;
}
