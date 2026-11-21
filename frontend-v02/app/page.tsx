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
    images: [{ url: "/og?title=Learn%20practical%20skills%20and%20build%20real%20projects&kind=Learnora%20ME", width: 1200, height: 630, alt: "Learnora ME — Learn, practise, build and prove" }],
  },
  twitter: { card: "summary_large_image", images: ["/og?title=Learn%20practical%20skills%20and%20build%20real%20projects&kind=Learnora%20ME"] },
};

export default async function Home() {
  const [courseResult, trackResult] = await Promise.all([getPublicCourses(), getPublicTracks()]);
  const initialError = courseResult.error && trackResult.error
    ? "The course and track catalogues are temporarily unavailable."
    : courseResult.error || trackResult.error;
  const siteUrl = getSiteUrl();
  const organizationJsonLd = { "@context": "https://schema.org", "@type": "Organization", name: "Learnora ME", url: siteUrl };
  const faqJsonLd = { "@context": "https://schema.org", "@type": "FAQPage", mainEntity: [
    { "@type": "Question", name: "What makes Learnora different from a course library?", acceptedAnswer: { "@type": "Answer", text: "A course is one part of the journey. Learnora connects lessons with practice, projects, feedback and a record of what you have demonstrated." } },
    { "@type": "Question", name: "Can I browse courses before creating an account?", acceptedAnswer: { "@type": "Answer", text: "Yes. You can browse published courses and learning tracks before creating an account. You will need an account to enrol and save your progress." } },
    { "@type": "Question", name: "Do I need to pay to get started?", acceptedAnswer: { "@type": "Answer", text: "Many courses are free to start. If a course has a fee, you will see its price before you enrol." } },
    { "@type": "Question", name: "Does completing a course mean a skill is verified?", acceptedAnswer: { "@type": "Answer", text: "Not automatically. Course progress, assessment results and instructor-reviewed evidence are different things." } },
  ] };
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationJsonLd).replace(/</g, "\\u003c") }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd).replace(/</g, "\\u003c") }} />
      <PublicNav hideBrand={false} />
      <LandingPage initialCourses={courseResult.items} initialTracks={trackResult.items} initialError={initialError} />
      <PublicFooter />
    </>
  );
}
