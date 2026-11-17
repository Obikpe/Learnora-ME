import type { Metadata } from "next";
import CourseDetailClient from "./CourseDetailClient";
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
  const image = item.thumbnail_url || `/api/og?title=${encodeURIComponent(title)}&kind=${encodeURIComponent("Learnora course")}`;
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
  return <CourseDetailClient params={params} searchParams={searchParams} initialCourse={item} />;
}
