import { publicPageMetadata } from "../../lib/seo";

export const metadata = publicPageMetadata("Learning for organisations", "Explore how Learnora ME can support organisational learning, programmes, teams and learner progress.", "/for-organisations");

import PublicNav from "../../components/public/PublicNav";
import PublicFooter from "../../components/public/PublicFooter";
import OrganisationLandingPage from "../../components/public/OrganisationLandingPage";

export default function ForOrganisationsPage() {
  return (
    <>
      <PublicNav />
      <OrganisationLandingPage />
      <PublicFooter />
    </>
  );
}
