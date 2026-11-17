import type { MetadataRoute } from "next";
import { getSiteUrl } from "../lib/server/catalogue";

export default function robots(): MetadataRoute.Robots {
  const base = getSiteUrl();
  return {
    rules: [
      { userAgent: "*", allow: "/", disallow: ["/dashboard/", "/organisation-portal/", "/cohort-login/", "/cohort-activate/", "/api/"] },
    ],
    sitemap: base + "/sitemap.xml",
    host: base,
  };
}
