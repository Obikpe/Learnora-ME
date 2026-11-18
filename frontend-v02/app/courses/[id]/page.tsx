import type { Metadata } from "next";
import CourseDetailClient from "./CourseDetailClient";
import { getPublicCourse, getPublicCoursePreview, getPublicCourseStructure, getSiteUrl } from "../../../lib/server/catalogue";

export const revalidate = 60;

type Props = { params: Promise<{ id: string }>; searchParams: Promise<{ enrol?: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const { item } = await getPublicCourse<any>(id);
  if (!item) {
    return {
      title: "Course unavailable",
      description: "This Learnora course could not be found or is no longer published.",
      alternates: { canonical: `/courses/${encodeURIComponent(id)}` },
      robots: { index: false, follow: true },
    };
  }
  const title = String(item.title || "Learnora course");
  const description = String(item.short_description || item.description || `Explore ${title} on Learnora ME. Review the course outline and available learning access.`).slice(0, 300);
  const image = `/og?title=${encodeURIComponent(title)}&kind=${encodeURIComponent("Learnora course")}`;
  const canonical = `/courses/${encodeURIComponent(id)}`;
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
  const [{ id }, resolvedSearchParams] = await Promise.all([params, searchParams]);
  const { item } = await getPublicCourse<any>(id);
  const [{ data: initialStructure }, initialPreview] = await Promise.all([getPublicCourseStructure<any>(id), getPublicCoursePreview<any>(id)]);
  const siteUrl = getSiteUrl();
  const jsonLd = item ? {
    "@context": "https://schema.org",
    "@type": "Course",
    name: item.title,
    description: item.short_description || item.description || undefined,
    provider: { "@type": "Organization", name: "Learnora ME", url: siteUrl },
    url: siteUrl + "/courses/" + encodeURIComponent(String(item.id)),
    educationalLevel: item.level || undefined,
    teaches: Array.isArray(item.settings?.learning_outcomes) ? item.settings.learning_outcomes : undefined,
    coursePrerequisites: Array.isArray(item.settings?.requirements) ? item.settings.requirements.join("; ") : undefined,
    courseMode: "online",
  } : null;
  return <>
    {jsonLd && <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }} />}
    <CourseDetailClient params={{ id }} searchParams={resolvedSearchParams} initialCourse={item} initialStructure={initialStructure} initialPreview={initialPreview} />
  </>;
}
