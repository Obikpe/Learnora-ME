import type { Metadata } from "next";
export const metadata: Metadata = { title: "Organisation workspace", robots: { index: false, follow: false } };
export default function OrganisationPortalLayout({children}:{children:React.ReactNode}) { return children; }
