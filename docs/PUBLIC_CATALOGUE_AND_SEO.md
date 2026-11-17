# Public Catalogue, SEO and Discovery

Last updated: 17 November 2026

## Rendering

- The homepage, `/courses` and `/tracks` are Next.js App Router Server Component routes.
- Published courses and tracks are fetched from the public FastAPI endpoints on the server.
- Server fetches use `next: { revalidate: 60 }` and matching route-level revalidation.
- Search, filters, pagination, current-user state and the learner-specific Continue learning rail remain client-side.
- Course detail pages server-render the public course, published syllabus and explicitly previewable lesson content.
- The preview endpoint returns only a published lesson with `is_preview = true` from a published module belonging to a public course. Preview lesson content is sanitised before browser rendering.
- Route-level `loading.tsx` files provide card-shaped skeletons. API failures have retry controls and empty catalogues have customer-facing empty states.

## Search and catalogue behaviour

- Course filters: text search, topic, level, track, duration and price.
- Rating filtering and rating sorting appear only when real rating data exists.
- Sort options: newest, title, shortest, longest, and top rated when rating data exists.
- Filter state and pagination are reflected in the URL.
- The search field offers native suggestions from real catalogue topics, tracks and levels.
- Pagination displays 12 courses per page.
- No sample, fabricated or draft courses are inserted into the public catalogue.

## Metadata and crawler support

- Site metadata base uses `NEXT_PUBLIC_SITE_URL` or `SITE_URL`, falling back to the active Vercel production domain `https://learnora-me-v02.vercel.app`.
- Homepage, course listing, track listing, public information pages and dynamic course/track detail pages have unique titles, descriptions, canonicals, Open Graph metadata and Twitter card images.
- Dynamic course and track pages use metadata based on their actual published records.
- `/og` generates 1200×630 social preview images.
- `/sitemap.xml` includes public static pages and published courses/tracks.
- `/robots.txt` identifies the sitemap and excludes private account/workspace paths.
- Structured data: Organization and FAQPage on the homepage; ItemList/Course on the course catalogue; Course on course detail pages.
- Account, verification and recovery routes are marked noindex.

## Navigation and homepage

- Removed the second audience-link strip; audience links remain in the main navigation and audience content section.
- The homepage hero states the learner outcome, with search as a prominent action.
- Course and track rails appear immediately after the hero.
- Added a Continue learning rail for signed-in individual learners, using their actual incomplete enrolments.
- Featured track cards show the actual ordered course sequence.
- Added a visual distinction between course progress, assessment results and instructor-reviewed evidence without inventing learner records.
- The lower-page CTA labels `/get-started` as `Choose your path`.
- Support navigation opens a Help page; the support email is shown in the footer.
- FAQ pricing copy explains that many courses are free and any fee is shown before enrolment.

## Production Vercel access

Both `learnora-me-v02` and `learnora-backend` previously had Vercel Authentication protection scoped to `all_except_custom_domains`. Since neither project has a custom domain attached, their production `vercel.app` domains were within the protected scope.

The protection scope has been changed to `preview` for both projects. Production domains are therefore public while preview deployments remain protected. Application-level authentication and API permissions remain responsible for private learner and organisation data.

## Live content inventory snapshot

Queried the connected production Supabase project on 17 November 2026:

- 1 published global Learnora course: **Introduction to Data Analytics**
- 1 published global learning track: **Data Analytics**
- 1 published module and 1 published lesson in that course
- The lesson **What Is Data Analytics?** is explicitly marked as a preview lesson
- 0 approved creator accounts
- 0 skill-evidence records
- No public review/rating/testimonial tables were found in the inspected public schema

This inventory is why the public site does not fabricate 6–12 courses, ratings, learner counts, instructor profiles, testimonials or certificate examples. More real course content and approved instructors must be published before those social-proof sections can be populated honestly.

## Remaining verification

- Run the frontend production build and backend preview tests.
- Inspect rendered HTML and response headers on the public production domains after deployment.
- Test sitemap, robots, Open Graph image, JSON-LD and canonical URLs with external crawler tools.
- Run responsive and accessibility checks at 320, 375, 414, 768, 1024, 1440 and 1920 pixels.
- Run Lighthouse mobile and axe checks.
- Confirm a preview lesson is readable without enrolment while non-preview lesson content remains protected.
- No production deployment was initiated for these repository changes.
