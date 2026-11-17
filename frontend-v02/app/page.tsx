import type { Metadata } from "next";
import PublicNav from "../components/public/PublicNav";
import PublicFooter from "../components/public/PublicFooter";
import LandingPage from "../components/public/LandingPage";
import { getPublicCourses, getPublicTracks, getSiteUrl } from "../lib/server/catalogue";

export const revalidate = 60;

export const metadata: Metadata = {
  title: "Learn practical skills and build real projects",
  description: "Explore published courses and learning tracks on Learnora ME. Learn useful skills, practise, build projects and keep evidence of your progress.",
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    url: "/",
    title: "Learn practical skills and build real projects | Learnora ME",
    description: "Explore courses and learning tracks that connect lessons with practice and projects.",
    images: [{ url: "/api/og?title=Learn%20practical%20skills%20and%20build%20real%20projects&kind=Learnora%20ME", width: 1200, height: 630, alt: "Learnora ME — Learn, practise, build and prove" }],
  },
  twitter: { card: "summary_large_image", images: ["/api/og?title=Learn%20practical%20skills%20and%20build%20real%20projects&kind=Learnora%20ME"] },
};

export default async function Home() {
  const [courseResult, trackResult] = await Promise.all([getPublicCourses(), getPublicTracks()]);
  const initialError = courseResult.error && trackResult.error
    ? "The course and track catalogues are temporarily unavailable."
    : courseResult.error || trackResult.error;
  return (
    <>
      <PublicNav />
      <LandingPage initialCourses={courseResult.items} initialTracks={trackResult.items} initialError={initialError} />
      <PublicFooter />
    </>
  );
}
