import type { Metadata } from "next";
export const metadata: Metadata = {
  title: "Verify Email",
  description: "Account access for Learnora ME.",
  robots: { index: false, follow: false },
};
export default function PrivateFlowLayout({children}:{children:React.ReactNode}) { return children; }
