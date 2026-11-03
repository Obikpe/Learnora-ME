"use client";

import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";
import {
  ArrowRight, ArrowUpRight, BookOpen, CheckCircle2, Clock3, Compass,
  GraduationCap, Layers3, RefreshCw, Search, Sparkles, Route,
} from "lucide-react";
import { request } from "../../lib/api/client";
import { IMAGES } from "../../lib/constants";

type PublicCourse = {
  id: string;
  title: string;
  ownership?: string;
  slug?: string | null;
  short_description?: string | null;
  description?: string | null;
  level?: string | null;
  thumbnail_url?: string | null;
  estimated_hours?: number | null;
  created_at?: string | null;
  tracks?: Array<{ id: string; name: string; slug?: string | null }>;
  settings?: {
    is_free?: boolean;
    access_type?: string;
    topics?: string[];
  };
};

type PublicTrackCourse = {
  id?: string;
  course_id?: string;
  order_index?: number;
  required?: boolean;
  course?: PublicCourse;
};

type PublicTrack = {
  id: string;
  name: string;
  slug?: string | null;
  description?: string | null;
  course_count: number;
  required_course_count: number;
  self_enrol_available?: boolean;
  courses: PublicTrackCourse[];
};

const heroSlides = [
  {
    eyebrow: "Learn · Practise · Build · Prove",
    title: <>Make learning <span className="landing-accent">count</span> beyond the classroom.</>,
    body: "Connect lessons to practice, projects and feedback. Build skills you can use, explain and keep developing.",
    image: IMAGES.hero,
    alt: "Learners collaborating around a table",
    action: "Explore courses",
    href: "/courses",
  },
  {
    eyebrow: "A clearer learning journey",
    title: <>Turn what you learn into <span className="landing-accent">work you can show.</span></>,
    body: "Learning is more meaningful when you can apply an idea, build something and reflect on what the work taught you.",
    image: IMAGES.practice,
    alt: "A learner working through material on a laptop",
    action: "Explore learning tracks",
    href: "/tracks",
  },
  {
    eyebrow: "Progress with context",
    title: <>Keep moving from curiosity to <span className="landing-accent">capability.</span></>,
    body: "Follow structured learning, practise deliberately and keep a clearer record of the work behind your progress.",
    image: IMAGES.projects,
    alt: "A team collaborating on a practical project",
    action: "How Learnora works",
    href: "/how-it-works",
  },
];

const imageFallbacks = [IMAGES.practice, IMAGES.projects, IMAGES.library, IMAGES.workshop];

function courseImage(course: PublicCourse, index: number) {
  return course.thumbnail_url || imageFallbacks[index % imageFallbacks.length];
}

function courseHref(course: PublicCourse) {
  return "/courses/" + encodeURIComponent(course.id);
}

function TrackCard({ track, index }: { track: PublicTrack; index: number }) {
  const firstCourse = track.courses?.find(item => item.course)?.course;
  const image = firstCourse?.thumbnail_url || [IMAGES.practice, IMAGES.projects, IMAGES.library][index % 3];
  return (
    <article className="landing-track-card">
      <Link href={"/tracks/" + encodeURIComponent(track.id)} className="landing-image-link" aria-label={"View " + track.name + " track"}>
        <img src={image} alt="" loading="lazy" />
        <span className="landing-image-label"><Route size={13}/> Learning track</span>
      </Link>
      <div className="landing-card-content">
        <h3><Link href={"/tracks/" + encodeURIComponent(track.id)}>{track.name}</Link></h3>
        <p>{track.description || "A structured sequence of published courses."}</p>
        <div className="landing-meta">
          <span><BookOpen size={14}/> {track.course_count} {track.course_count === 1 ? "course" : "courses"}</span>
          <span><Layers3 size={14}/> {track.required_course_count} required</span>
        </div>
        {track.self_enrol_available && <span className="landing-availability">Available for self-enrolment</span>}
        <Link className="landing-text-link" href={"/tracks/" + encodeURIComponent(track.id)}>Explore track <ArrowRight size={15}/></Link>
      </div>
    </article>
  );
}

function CourseCard({ course, index }: { course: PublicCourse; index: number }) {
  const free = course.settings?.is_free === true || course.settings?.access_type === "free";
  const selfEnrolAvailable = free || course.ownership === "learnora";
  return (
    <article className="landing-course-card">
      <Link href={courseHref(course)} className="landing-course-image" aria-label={"View " + course.title}>
        <img src={courseImage(course, index)} alt="" loading="lazy" />
        {free && <span className="landing-free-label">Free access</span>}
      </Link>
      <div className="landing-course-copy">
        <div className="landing-course-overline">{course.level || "Published course"}</div>
        <h3><Link href={courseHref(course)}>{course.title}</Link></h3>
        <p>{course.short_description || course.description || "Explore the course outline and learning content."}</p>
        <div className="landing-meta">
          {typeof course.estimated_hours === "number" && course.estimated_hours > 0
            ? <span><Clock3 size={14}/> {course.estimated_hours} hours</span>
            : null}
          {course.tracks?.slice(0, 1).map(track => <span key={track.id}><Route size={14}/>{track.name}</span>)}
        </div>
        <Link className="landing-text-link" href={selfEnrolAvailable ? courseHref(course) + "?enrol=1" : courseHref(course)}>{selfEnrolAvailable ? "Enrol for free" : "View course"} <ArrowRight size={15}/></Link>
      </div>
    </article>
  );
}

export default function LandingPage() {
  const [courses, setCourses] = useState<PublicCourse[]>([]);
  const [tracks, setTracks] = useState<PublicTrack[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeSlide, setActiveSlide] = useState(0);
  const [search, setSearch] = useState("");

  async function loadCatalogue() {
    setLoading(true);
    setError("");
    try {
      const [courseResult, trackResult] = await Promise.all([
        request<{ success: boolean; courses: PublicCourse[] }>("/public/courses"),
        request<{ success: boolean; tracks: PublicTrack[] }>("/public/tracks"),
      ]);
      setCourses(Array.isArray(courseResult.courses) ? courseResult.courses : []);
      setTracks(Array.isArray(trackResult.tracks) ? trackResult.tracks : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "The Learnora catalogue could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void loadCatalogue(); }, []);

  const categories = useMemo(() => {
    const values = new Set<string>();
    courses.forEach(course => {
      course.settings?.topics?.forEach(topic => {
        if (typeof topic === "string" && topic.trim()) values.add(topic.trim());
      });
      course.tracks?.forEach(track => {
        if (track.name?.trim()) values.add(track.name.trim());
      });
    });
    return Array.from(values).sort((a, b) => a.localeCompare(b)).slice(0, 12);
  }, [courses]);

  const newestCourses = useMemo(() => courses.slice(0, 8), [courses]);
  const featuredTracks = useMemo(() => tracks.slice(0, 3), [tracks]);

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = search.trim();
    window.location.href = value ? "/courses?search=" + encodeURIComponent(value) : "/courses";
  }

  const slide = heroSlides[activeSlide];

  return (
    <main className="landing-page">
      <div className="landing-audience-strip">
        <div className="landing-wrap">
          <Link href="/for-learners" aria-current="page">For individuals</Link>
          <Link href="/for-organisations">For organisations</Link>
          <Link href="/for-instructors">For instructors</Link>
          <span>Learning that connects to real work</span>
        </div>
      </div>

      <section className="landing-wrap landing-hero" aria-label="Discover Learnora">
        <div className="landing-hero-copy">
          <p className="landing-kicker"><span/> {slide.eyebrow}</p>
          <h1>{slide.title}</h1>
          <p className="landing-hero-description">{slide.body}</p>
          <div className="landing-actions">
            <Link className="landing-button landing-button-primary" href={slide.href}>{slide.action} <ArrowRight size={16}/></Link>
            <Link className="landing-button landing-button-outline" href="/how-it-works">How it works <ArrowUpRight size={16}/></Link>
          </div>
          <form className="landing-search" onSubmit={submitSearch}>
            <Search size={18} aria-hidden="true"/>
            <input aria-label="Search courses and skills" value={search} onChange={event => setSearch(event.target.value)} placeholder="What do you want to learn?"/>
            <button type="submit">Search</button>
          </form>
          <div className="landing-hero-points">
            <span><BookOpen size={17}/> Learn clearly</span>
            <span><Compass size={17}/> Practise deeply</span>
            <span><CheckCircle2 size={17}/> Show your work</span>
          </div>
        </div>
        <div className="landing-hero-visual">
          <div className="landing-hero-image">
            <img src={slide.image} alt={slide.alt} fetchPriority="high" />
            <div className="landing-image-caption">
              <span>THE LEARNORA APPROACH</span>
              <strong>A course is a beginning. What you do with it is the story.</strong>
            </div>
          </div>
          <div className="landing-slide-controls" aria-label="Featured messages">
            <span>{String(activeSlide + 1).padStart(2, "0")} / 03</span>
            <div>{heroSlides.map((item, index) => <button key={item.eyebrow} type="button" aria-label={"Show slide " + (index + 1)} aria-pressed={activeSlide === index} onClick={() => setActiveSlide(index)} className={activeSlide === index ? "active" : ""}/>)}</div>
            <button type="button" className="landing-next" aria-label="Next featured message" onClick={() => setActiveSlide(value => (value + 1) % heroSlides.length)}><ArrowRight size={17}/></button>
          </div>
        </div>
      </section>

      <section className="landing-section landing-soft-section">
        <div className="landing-wrap">
          <div className="landing-section-heading">
            <div><p className="landing-kicker"><span/> The catalogue</p><h2>New and available to explore</h2></div>
            <Link className="landing-text-link" href="/courses">Browse all courses <ArrowRight size={15}/></Link>
          </div>
          {error && <div role="alert" className="landing-error"><span>{error}</span><button type="button" onClick={() => void loadCatalogue()}><RefreshCw size={14}/> Try again</button></div>}
          {loading ? <div className="landing-loading" role="status">Loading published courses and tracks…</div> : newestCourses.length ? (
            <div className="landing-course-grid">{newestCourses.slice(0, 4).map((course, index) => <CourseCard key={course.id} course={course} index={index}/>)}</div>
          ) : !error ? <div className="landing-empty"><BookOpen size={24}/><h3>New courses are on the way</h3><p>Published courses will appear here when they are available in the Learnora catalogue.</p></div> : null}
        </div>
      </section>

      <section className="landing-wrap landing-tracks-section">
        <div className="landing-section-heading">
          <div><p className="landing-kicker"><span/> Structured learning</p><h2>Follow a path, not just a playlist</h2><p>Tracks bring related courses together in an intentional sequence.</p></div>
          <Link className="landing-text-link" href="/tracks">Explore all tracks <ArrowRight size={15}/></Link>
        </div>
        {loading ? <div className="landing-loading" role="status">Loading published tracks…</div> : featuredTracks.length ? (
          <div className="landing-track-grid">{featuredTracks.map((track, index) => <TrackCard key={track.id} track={track} index={index}/>)}</div>
        ) : !error ? <div className="landing-empty"><Route size={24}/><h3>No published tracks yet</h3><p>Structured learning tracks will appear here once they are published.</p></div> : null}
      </section>

      <section className="landing-image-band">
        <div className="landing-wrap landing-image-band-inner">
          <div className="landing-band-image"><img src={IMAGES.workshop} alt="A group learning together in a workshop" loading="lazy"/></div>
          <div><p className="landing-kicker"><span/> More than course completion</p><h2>Progress should mean more than a percentage.</h2><p>Finishing a course tells you that you reached the end of its material. Practice, projects, assessment and feedback help tell a fuller story of what you can do.</p><Link className="landing-button landing-button-light" href="/how-it-works">See how it works <ArrowRight size={16}/></Link></div>
        </div>
      </section>

      <section className="landing-wrap landing-categories-section">
        <div className="landing-section-heading">
          <div><p className="landing-kicker"><span/> Explore the catalogue</p><h2>Explore learning areas</h2><p>These topics are drawn from the published course catalogue.</p></div>
        </div>
        {categories.length ? <div className="landing-category-list">{categories.map(category => <Link key={category} href={"/courses?search=" + encodeURIComponent(category)}><span/>{category}<ArrowUpRight size={14}/></Link>)}</div> : <div className="landing-empty"><Compass size={24}/><h3>Learning areas will appear here</h3><p>As courses are published with topics and track relationships, you can explore them here.</p></div>}
      </section>

      <section className="landing-career-band">
        <div className="landing-wrap landing-career-inner">
          <div><p className="landing-kicker"><span/> Find your starting point</p><h2>Build a learning journey around what you want to do next.</h2><p>Start with a published track, explore its courses and decide whether the sequence fits your goals.</p><Link className="landing-button landing-button-light" href="/tracks">Explore learning tracks <ArrowRight size={16}/></Link></div>
          <div className="landing-career-list">
            {featuredTracks.length ? featuredTracks.slice(0, 3).map(track => <Link key={track.id} href={"/tracks/" + encodeURIComponent(track.id)}><span><Layers3 size={18}/></span><strong>{track.name}</strong><small>{track.course_count} {track.course_count === 1 ? "course" : "courses"}</small><ArrowUpRight size={17}/></Link>) : <div className="landing-career-placeholder"><GraduationCap size={28}/><p>Published learning tracks will be shown here.</p></div>}
          </div>
        </div>
      </section>

      <section className="landing-wrap landing-principles-section">
        <div className="landing-section-heading"><div><p className="landing-kicker"><span/> The Learnora difference</p><h2>Learning should lead somewhere useful.</h2></div></div>
        <div className="landing-principles-grid">
          <article><span>01</span><h3>Practice matters</h3><p>Understanding grows when people use ideas, make decisions and learn from feedback.</p></article>
          <article><span>02</span><h3>Evidence should be honest</h3><p>Course completion, assessment results and instructor-reviewed evidence are different things.</p></article>
          <article><span>03</span><h3>People learn together</h3><p>Tutors, peers and teams can make learning more supported and connected to real needs.</p></article>
        </div>
      </section>

      <section className="landing-wrap landing-audience-section">
        <div className="landing-section-heading"><div><p className="landing-kicker"><span/> One connected ecosystem</p><h2>Different journeys. One shared foundation.</h2></div></div>
        <div className="landing-audience-grid">
          <Link href="/for-learners"><img src={IMAGES.learners} alt="Learners working together" loading="lazy"/><div><GraduationCap size={20}/><h3>For learners</h3><p>Build useful skills through lessons, practice, projects and an honest record of progress.</p><span>Explore this path <ArrowRight size={14}/></span></div></Link>
          <Link href="/for-instructors"><img src={IMAGES.instructors} alt="An instructor supporting a class" loading="lazy"/><div><BookOpen size={20}/><h3>For instructors</h3><p>Create practical learning, support learners and review work.</p><span>Explore this path <ArrowRight size={14}/></span></div></Link>
          <Link href="/for-organisations"><img src={IMAGES.organisations} alt="Colleagues collaborating in a meeting" loading="lazy"/><div><Layers3 size={20}/><h3>For organisations</h3><p>Shape learning around your people, programmes, teams and agreed outcomes.</p><span>Explore this path <ArrowRight size={14}/></span></div></Link>
        </div>
      </section>

      <section className="landing-wrap landing-faq-section">
        <div className="landing-faq-intro"><p className="landing-kicker"><span/> Questions, answered</p><h2>Before you begin.</h2><p>Know what you can explore and how learning works on Learnora.</p></div>
        <div className="landing-faq-list">
          <details><summary>What makes Learnora different from a course library?</summary><p>A course is one part of the journey. Learnora connects lessons with practice, projects, feedback and a record of what you have demonstrated.</p></details>
          <details><summary>Can I browse courses before creating an account?</summary><p>Yes. Published courses and tracks can be explored from the public catalogue. Enrolment and learning activities follow the access rules returned by the platform.</p></details>
          <details><summary>Do I need to pay to get started?</summary><p>Course and track availability is determined by the live catalogue and your account permissions. The course page shows the access information supplied by Learnora before you enrol.</p></details>
          <details><summary>Does completing a course mean a skill is verified?</summary><p>Not automatically. Course progress, assessment results and instructor-reviewed evidence are different things. Learnora is designed to keep that distinction clear.</p></details>
          <details><summary>Can my school or organisation use Learnora?</summary><p>Organisations can enquire about a workspace shaped around their people, programmes, courses and agreed outcomes.</p></details>
          <details><summary>I teach or have expertise to share. Can I contribute?</summary><p>Instructors and creators can explore the teaching pathway and apply to contribute. Access to creator tools follows the approval and permission process.</p></details>
        </div>
      </section>

      <section className="landing-wrap landing-final-cta">
        <div><p className="landing-kicker"><span/> Start where you are</p><h2>Your next step does not have to be your whole future.</h2><p>Explore a course, follow a learning track or find out how Learnora can support your teaching or organisation.</p></div>
        <div className="landing-final-actions"><Link className="landing-button landing-button-primary" href="/courses">Explore courses <ArrowRight size={16}/></Link><Link className="landing-button landing-button-outline" href="/get-started">Get started <ArrowUpRight size={16}/></Link></div>
      </section>
    </main>
  );
}
