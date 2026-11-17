import "./globals.css";
import "./landing.css";
import "./organisation.css";
import type { Metadata, Viewport } from "next";
import { getSiteUrl } from "../lib/server/catalogue";

export const metadata: Metadata = {
  metadataBase: new URL(getSiteUrl()),
  title: {
    default: "Learnora ME — Learn. Practise. Build. Prove.",
    template: "%s | Learnora ME",
  },
  description: "Explore practical courses and structured learning tracks. Learn useful skills, practise, build real projects and keep evidence of your progress.",
  applicationName: "Learnora ME",
  icons: { icon: "/icon.svg", shortcut: "/icon.svg" },
  openGraph: {
    type: "website",
    siteName: "Learnora ME",
    title: "Learnora ME — Learn. Practise. Build. Prove.",
    description: "Connect learning with practice, projects, feedback and skills evidence.",
    url: "/",
    images: [{ url: "/og?title=Learn%20skills.%20Build%20real%20projects.&kind=Learnora%20ME", width: 1200, height: 630, alt: "Learnora ME — Learn, practise, build and prove" }],
  },
  twitter: {
    card: "summary_large_image",
    images: ["/og?title=Learn%20Learnora%20ME&kind=Learnora%20ME"],
    title: "Learnora ME — Learn. Practise. Build. Prove.",
    description: "Connect learning with practice, projects, feedback and skills evidence.",
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: "#0f1020",
  colorScheme: "light dark",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
