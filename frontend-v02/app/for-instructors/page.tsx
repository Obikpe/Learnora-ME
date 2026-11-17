import { publicPageMetadata } from "../../lib/seo";

export const metadata = publicPageMetadata("Teach on Learnora", "Learn how instructors can contribute practical learning, support learners and review work on Learnora ME.", "/for-instructors");

import PublicNav from"../../components/public/PublicNav";import PublicFooter from"../../components/public/PublicFooter";import AudiencePage from"../../components/public/AudiencePage";export default function Page(){return <><PublicNav/><AudiencePage type="instructor"/><PublicFooter/></>}