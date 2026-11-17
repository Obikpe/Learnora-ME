import type { MetadataRoute } from "next";
import { getSiteUrl, getPublicCourses, getPublicTracks } from "../lib/server/catalogue";

export const revalidate = 3600;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = getSiteUrl();
  const [courses, tracks] = await Promise.all([getPublicCourses<any>(), getPublicTracks<any>()]);
  const staticRoutes = ["", "/courses", "/tracks", "/about", "/how-it-works", "/help", "/get-started", "/for-learners", "/for-instructors", "/for-organisations"];
  const entries: MetadataRoute.Sitemap = staticRoutes.map(path => ({
    url: base + path,
    changeFrequency: path === "" ? "daily" : "weekly",
    priority: path === "" ? 1 : path === "/courses" || path === "/tracks" ? 0.9 : 0.6,
  }));
  for (const course of courses.items) {
    if (!course?.id) continue;
    entries.push({
      url: base + "/courses/" + encodeURIComponent(String(course.id)),
      changeFrequency: "weekly",
      priority: 0.8,
      ...(course.updated_at ? { lastModified: new Date(course.updated_at) } : {}),
    });
  }
  for (const track of tracks.items) {
    if (!track?.id) continue;
    entries.push({
      url: base + "/tracks/" + encodeURIComponent(String(track.id)),
      changeFrequency: "weekly",
      priority: 0.7,
      ...(track.updated_at ? { lastModified: new Date(track.updated_at) } : {}),
    });
  }
  return entries;
}
