import type { Metadata } from "next";
import TracksClient from "./TracksClient";
import { getPublicTracks } from "../../lib/server/catalogue";

export const revalidate = 60;

export const metadata: Metadata = {
  title: "Explore learning tracks",
  description: "Explore structured learning tracks that connect related courses into a purposeful learning journey on Learnora ME.",
  alternates: { canonical: "/tracks" },
  openGraph: {
    type: "website",
    url: "/tracks",
    title: "Explore learning tracks | Learnora ME",
    description: "Follow structured learning journeys and build connected skills.",
    images: [{ url: "/og?title=Explore%20structured%20learning%20tracks&kind=Learnora%20learning%20journeys", width: 1200, height: 630, alt: "Explore learning tracks on Learnora ME" }],
  },
  twitter: { card: "summary_large_image", images: ["/og?title=Explore%20structured%20learning%20tracks&kind=Learnora%20learning%20journeys"] },
};

export default async function TracksPage() {
  const result = await getPublicTracks();
  return <TracksClient initialTracks={result.items} initialError={result.error} />;
}
