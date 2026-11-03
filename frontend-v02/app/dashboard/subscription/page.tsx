import { redirect } from "next/navigation";

export default function LegacyLearnerRouteRedirect() {
  redirect("/dashboard");
}
