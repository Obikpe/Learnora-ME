import { publicPageMetadata } from "../../lib/seo";
import ApplyToTeach from "./ApplyToTeachClient";

export const metadata = publicPageMetadata("Apply to teach on Learnora", "Learn how to contribute as an instructor or creator on Learnora ME.", "/apply-to-teach");

export default function Page() {
  return <ApplyToTeach />;
}
