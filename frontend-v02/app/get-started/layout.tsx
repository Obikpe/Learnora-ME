import type { Metadata } from "next";
import { publicPageMetadata } from "../../lib/seo";
export const metadata: Metadata = publicPageMetadata("Choose your path", "Choose whether you are here to learn, teach or bring Learnora to your organisation.", "/get-started");
export default function GetStartedLayout({children}:{children:React.ReactNode}) { return children; }
