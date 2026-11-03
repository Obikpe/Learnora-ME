import { redirect } from "next/navigation";

export default function LegacyLearnerDashboardRedirect() {
  redirect("/dashboard");
}
