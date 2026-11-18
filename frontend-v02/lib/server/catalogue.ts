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
  let lastError: unknown = null;

  for (let attempt = 0; attempt < 3; attempt += 1) {
    let response: Response;
    try {
      const baseUrl = `${API_ORIGIN}/api${path}`;
      // A unique query string bypasses a cached 5xx response without using
      // no-store, which would force a statically generated page to become dynamic.
      const retryUrl = attempt === 0
        ? baseUrl
        : `${baseUrl}${baseUrl.includes("?") ? "&" : "?"}__catalogue_retry=${attempt}`;
      response = await fetch(retryUrl, {
        headers: { Accept: "application/json" },
        next: { revalidate: 60, tags: [`public-catalogue-${key}`] },
      });
    } catch (error) {
      lastError = error;
      if (attempt < 2) {
        await new Promise(resolve => setTimeout(resolve, 250 * (attempt + 1)));
        continue;
      }
      break;
    }

    if (!response.ok) {
      lastError = new Error(`Catalogue request failed (${response.status}).`);
      if (response.status >= 500 && attempt < 2) {
        await new Promise(resolve => setTimeout(resolve, 250 * (attempt + 1)));
        continue;
      }
      break;
    }

    try {
      const body = await response.json();
      const value = body?.[key];
      if (!Array.isArray(value)) {
        lastError = new Error("The catalogue returned an unexpected response.");
        break;
      }
      return { items: value as T[], error: null };
    } catch (error) {
      lastError = error;
      break;
    }
  }

  console.error(`[public-catalogue] ${key} fetch failed after retries`, lastError);
  const message = "We couldn't load the catalogue right now. Please try again in a moment.";

  // A production build must never silently publish an empty course/track
  // catalogue. Throwing also makes ISR revalidation fail safely, preserving
  // the previous generated page rather than replacing it with empty content.
  if (process.env.NODE_ENV === "production") {
    throw new Error(`Public ${key} catalogue is unavailable; refusing to publish an empty catalogue.`, {
      cause: lastError,
    });
  }

  return { items: [], error: message };
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

export async function getPublicCoursePreview<T = any>(id: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_ORIGIN}/api/public/courses/${encodeURIComponent(id)}/preview`, {
      headers: { Accept: "application/json" },
      next: { revalidate: 60, tags: [`public-course-preview-${id}`] },
    });
    if (!response.ok) return null;
    const body = await response.json();
    return body?.preview || null;
  } catch (error) {
    console.error("[public-catalogue] course preview fetch failed", error);
    return null;
  }
}

export async function getPublicCourseStructure<T = any>(id: string): Promise<{ data: T | null; error: string | null }> {
  try {
    const response = await fetch(`${API_ORIGIN}/api/public/courses/${encodeURIComponent(id)}/structure`, {
      headers: { Accept: "application/json" },
      next: { revalidate: 60, tags: [`public-course-structure-${id}`] },
    });
    if (!response.ok) return { data: null, error: "The course outline is temporarily unavailable." };
    const body = await response.json();
    return { data: body as T, error: null };
  } catch (error) {
    console.error("[public-catalogue] course structure fetch failed", error);
    return { data: null, error: "The course outline is temporarily unavailable." };
  }
}

export async function getPublicTrack<T = any>(id: string): Promise<{ item: T | null; error: string | null }> {
  try {
    const response = await fetch(`${API_ORIGIN}/api/public/tracks/${encodeURIComponent(id)}`, {
      headers: { Accept: "application/json" },
      next: { revalidate: 60, tags: [`public-track-${id}`] },
    });
    if (!response.ok) return { item: null, error: response.status === 404 ? "Track not found." : "Track details are temporarily unavailable." };
    const body = await response.json();
    const item = body?.track || body;
    if (!item || typeof item !== "object" || !item.id) return { item: null, error: "Track not found." };
    return { item: item as T, error: null };
  } catch (error) {
    console.error("[public-catalogue] track fetch failed", error);
    return { item: null, error: "Track details are temporarily unavailable." };
  }
}

export function getPublicTracks<T = any>() {
  return fetchPublic<T>("/public/tracks", "tracks");
}

export function getSiteUrl() {
  const configured = process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL;
  return (configured || "https://learnora-me-v02.vercel.app").replace(/\/+$/, "");
}
