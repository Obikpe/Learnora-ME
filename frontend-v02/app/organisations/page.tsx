import { publicPageMetadata } from "../../lib/seo";
import DirectoryClient from "./DirectoryClient";

export const metadata = publicPageMetadata("Explore organisations", "Discover organisations and learning communities listed on Learnora ME.", "/organisations");

export default function Page() {
  return <DirectoryClient />;
}
