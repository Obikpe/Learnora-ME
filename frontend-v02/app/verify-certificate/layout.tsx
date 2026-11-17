import type { Metadata } from "next";
export const metadata: Metadata = { title: "Verify certificate", description: "Check the validity of a Learnora ME certificate.", robots: { index: false, follow: false } };
export default function CertificateVerificationLayout({children}:{children:React.ReactNode}) { return children; }
