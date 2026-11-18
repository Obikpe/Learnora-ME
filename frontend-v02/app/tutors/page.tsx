import { publicPageMetadata } from "../../lib/seo";
import DirectoryClient from "./DirectoryClient";

export const metadata = publicPageMetadata("Find instructors and tutors", "Explore instructor profiles and teaching expertise listed on Learnora ME.", "/tutors");

export default function Page() {
  return <DirectoryClient />;
}
