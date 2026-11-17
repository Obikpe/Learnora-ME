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
    images: [{ url: "/og?title=Browse%20practical%20courses&kind=Learnora%20course%20catalogue", width: 1200, height: 630, alt: "Browse courses on Learnora ME" }],
  },
  twitter: { card: "summary_large_image", images: ["/og?title=Browse%20practical%20courses&kind=Learnora%20course%20catalogue"] },
};

export default async function CoursesPage() {
  const result = await getPublicCourses<any>();
  const siteUrl = "https://learnora-me-v02.vercel.app";
  const courseListJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: "Learnora ME published courses",
    itemListElement: result.items.map((course: any, index: number) => ({
      "@type": "ListItem",
      position: index + 1,
      item: {
        "@type": "Course",
        name: course.title,
        description: course.short_description || course.description || undefined,
        url: siteUrl + "/courses/" + encodeURIComponent(String(course.id)),
        provider: { "@type": "Organization", name: "Learnora ME", url: siteUrl },
        educationalLevel: course.level || undefined,
      },
    })),
  };
  return <>
    {result.items.length > 0 && <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(courseListJsonLd).replace(/</g, "\\u003c") }} />}
    <CoursesClient initialCourses={result.items} initialError={result.error} />
  </>;
}
