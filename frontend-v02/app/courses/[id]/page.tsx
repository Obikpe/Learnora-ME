import type { Metadata } from "next";
import CourseDetailClient from "./CourseDetailClient";
import { getSiteUrl } from "../../../lib/server/catalogue";
import { getPublicCourse } from "../../../lib/server/catalogue";

export const revalidate = 60;

type Props = { params: { id: string }; searchParams: { enrol?: string } };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { item } = await getPublicCourse<any>(params.id);
  if (!item) {
    return {
      title: "Course unavailable",
      description: "This Learnora course could not be found or is no longer published.",
      alternates: { canonical: `/courses/${encodeURIComponent(params.id)}` },
      robots: { index: false, follow: true },
    };
  }
  const title = String(item.title || "Learnora course");
  const description = String(item.short_description || item.description || `Explore ${title} on Learnora ME. Review the course outline and available learning access.`).slice(0, 300);
  const image = item.thumbnail_url || `/og?title=${encodeURIComponent(title)}&kind=${encodeURIComponent("Learnora course")}`;
  const canonical = `/courses/${encodeURIComponent(params.id)}`;
  return {
    title,
    description,
    alternates: { canonical },
    openGraph: {
      type: "article",
      url: canonical,
      title: `${title} | Learnora ME`,
      description,
      images: [{ url: image, width: 1200, height: 630, alt: title }],
    },
    twitter: { card: "summary_large_image", title, description, images: [image] },
  };
}

export default async function CourseDetailPage({ params, searchParams }: Props) {
  const { item } = await getPublicCourse<any>(params.id);
  const { data: initialStructure } = await getPublicCourseStructure<any>(params.id);
  const siteUrl = getSiteUrl();
  const jsonLd = item ? {
    "@context": "https://schema.org",
    "@type": "Course",
    name: item.title,
    description: item.short_description || item.description || undefined,
    provider: { "@type": "Organization", name: "Learnora ME", url: siteUrl },
    url: siteUrl + "/courses/" + encodeURIComponent(String(item.id)),
    educationalLevel: item.level || undefined,
    courseMode: "online",
  } : null;
  return <>
    {jsonLd && <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }} />}
    <CourseDetailClient params={params} searchParams={searchParams} initialCourse={item} initialStructure={initialStructure} />
  </>;
}
