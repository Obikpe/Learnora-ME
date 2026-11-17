const API_ORIGIN = (
  process.env.LEARNORA_API_URL ||
  process.env.API_PROXY_TARGET ||
  "https://learnora-backend.vercel.app"
).replace(/\/+$/, "");

export type PublicCatalogueResult<T> = {
  items: T[];
  error: string | null;
};

async function fetchPublic<T>(path: string, key: string): Promise<PublicCatalogueResult<T>> {
  try {
    const response = await fetch(`${API_ORIGIN}/api${path}`, {
      headers: { Accept: "application/json" },
      next: { revalidate: 60, tags: [`public-catalogue-${key}`] },
    });
    if (!response.ok) {
      throw new Error(`Catalogue request failed (${response.status}).`);
    }
    const body = await response.json();
    const value = body?.[key];
    if (!Array.isArray(value)) {
      throw new Error("The catalogue returned an unexpected response.");
    }
    return { items: value as T[], error: null };
  } catch (error) {
    console.error(`[public-catalogue] ${key} fetch failed`, error);
    return {
      items: [],
      error: "We couldn't load the catalogue right now. Please try again in a moment.",
    };
  }
}

export async function getPublicCourse<T = any>(id: string): Promise<{ item: T | null; error: string | null }> {
  try {
    const response = await fetch(`${API_ORIGIN}/api/public/courses/${encodeURIComponent(id)}`, {
      headers: { Accept: "application/json" },
      next: { revalidate: 60, tags: [`public-course-${id}`] },
    });
    if (!response.ok) return { item: null, error: response.status === 404 ? "Course not found." : "Course details are temporarily unavailable." };
    const body = await response.json();
    const item = body?.course || body;
    if (!item || typeof item !== "object" || !item.id) return { item: null, error: "Course not found." };
    return { item: item as T, error: null };
  } catch (error) {
    console.error("[public-catalogue] course fetch failed", error);
    return { item: null, error: "Course details are temporarily unavailable." };
  }
}

export function getPublicCourses<T = any>() {
  return fetchPublic<T>("/public/courses", "courses");
}

export function getPublicTracks<T = any>() {
  return fetchPublic<T>("/public/tracks", "tracks");
}

export function getSiteUrl() {
  const configured = process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL;
  return (configured || "https://learnora-me-v02.vercel.app").replace(/\/+$/, "");
}
