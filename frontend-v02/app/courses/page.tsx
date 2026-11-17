import type { Metadata } from "next";
import CoursesClient from "./CoursesClient";
import { getPublicCourses } from "../../lib/server/catalogue";

export const revalidate = 60;

export const metadata: Metadata = {
  title: "Browse courses",
  description: "Browse Learnora ME's published courses by skill, topic, level and learning track. Find practical learning you can put to work.",
  alternates: { canonical: "/courses" },
  openGraph: {
    type: "website",
    url: "/courses",
    title: "Browse courses | Learnora ME",
    description: "Find practical courses by skill, topic, level and learning track.",
    images: [{ url: "/api/og?title=Browse%20practical%20courses&kind=Learnora%20course%20catalogue", width: 1200, height: 630, alt: "Browse courses on Learnora ME" }],
  },
  twitter: { card: "summary_large_image", images: ["/api/og?title=Browse%20practical%20courses&kind=Learnora%20course%20catalogue"] },
};

export default async function CoursesPage() {
  const result = await getPublicCourses();
  return <CoursesClient initialCourses={result.items} initialError={result.error} />;
}
