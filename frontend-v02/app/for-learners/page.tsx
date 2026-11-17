import { publicPageMetadata } from "../../lib/seo";

export const metadata = publicPageMetadata("Learning for individuals", "Explore practical courses, structured learning and ways to keep a record of your progress with Learnora ME.", "/for-learners");

import PublicNav from"../../components/public/PublicNav";import PublicFooter from"../../components/public/PublicFooter";import AudiencePage from"../../components/public/AudiencePage";export default function Page(){return <><PublicNav/><AudiencePage type="learner"/><PublicFooter/></>}