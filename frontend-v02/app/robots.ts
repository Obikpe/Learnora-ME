import type { MetadataRoute } from "next";
import { getSiteUrl } from "../lib/server/catalogue";

export default function robots(): MetadataRoute.Robots {
  const base = getSiteUrl();
  return {
    rules: [
      { userAgent: "*", allow: "/", disallow: ["/dashboard", "/dashboard/", "/organisation-portal", "/organisation-portal/", "/cohort-login/", "/cohort-activate/", "/login", "/register", "/forgot-password", "/reset-password", "/verify-email", "/check-email", "/confirm-account-deletion", "/reactivate-account", "/resend-verification", "/unsubscribe", "/onboarding", "/api/"] },
    ],
    sitemap: base + "/sitemap.xml",
    host: base,
  };
}
