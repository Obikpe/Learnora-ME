import type { Metadata } from "next";

export function publicPageMetadata(title: string, description: string, path: string, kind = "Learnora ME"): Metadata {
  const image = `/og?title=${encodeURIComponent(title)}&kind=${encodeURIComponent(kind)}`;
  return {
    title,
    description,
    alternates: { canonical: path },
    openGraph: {
      type: "website",
      url: path,
      title: `${title} | Learnora ME`,
      description,
      images: [{ url: image, width: 1200, height: 630, alt: title }],
    },
    twitter: { card: "summary_large_image", title, description, images: [image] },
  };
}
