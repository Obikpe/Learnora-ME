import type { Metadata } from "next";
import TrackDetailClient from "./TrackDetailClient";
import { getPublicTrack } from "../../../lib/server/catalogue";

export const revalidate = 60;

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const { item } = await getPublicTrack<any>(id);
  if (!item) {
    return {
      title: "Learning track unavailable",
      description: "This Learnora learning track could not be found or is no longer published.",
      alternates: { canonical: `/tracks/${encodeURIComponent(id)}` },
      robots: { index: false, follow: true },
    };
  }
  const title = String(item.name || "Learning track");
  const description = String(item.description || `Explore the ${title} learning track on Learnora ME.`).slice(0, 300);
  const canonical = `/tracks/${encodeURIComponent(id)}`;
  const image = `/og?title=${encodeURIComponent(title)}&kind=${encodeURIComponent("Learnora learning track")}`;
  return {
    title,
    description,
    alternates: { canonical },
    openGraph: { type: "website", url: canonical, title: `${title} | Learnora ME`, description, images: [{ url: image, width: 1200, height: 630, alt: title }] },
    twitter: { card: "summary_large_image", title, description, images: [image] },
  };
}

export default async function TrackDetailPage({ params }: Props) {
  const { id } = await params;
  const { item } = await getPublicTrack<any>(id);
  return <TrackDetailClient params={{ id }} initialTrack={item} />;
}
