"use client";

import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";
import Image from "next/image";
import {
  ArrowRight, ArrowUpRight, BookOpen, CheckCircle2, Clock3, Compass,
  GraduationCap, Layers3, RefreshCw, Search, Route,
} from "lucide-react";
import { request } from "../../lib/api/client";
import { currentUser } from "../../lib/api";
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
    title: <>Learn data, design and tech skills. <span className="landing-accent">Build real projects.</span></>,
    body: "Learn practical skills, practise with guided work and build projects that show what you can do.",
  },
  {
    title: <>Turn what you learn into <span className="landing-accent">work you can show.</span></>,
    body: "Learning is more meaningful when you can apply an idea, build something and reflect on what the work taught you.",
  },
  {
    title: <>Keep moving from curiosity to <span className="landing-accent">capability.</span></>,
    body: "Follow structured learning, practise deliberately and keep a clearer record of the work behind your progress.",
  },
];

const imageFallbacks = [IMAGES.practice, IMAGES.projects, IMAGES.library, IMAGES.workshop];

function courseImage(course: PublicCourse, index: number) {
  const candidate = typeof course.thumbnail_url === "string" ? course.thumbnail_url.trim() : "";
  const trusted = candidate.startsWith("https://images.unsplash.com/") || candidate.startsWith("https://gihfupzvdpyrmynqgukz.supabase.co/");
  return trusted ? candidate : imageFallbacks[index % imageFallbacks.length];
}

function courseHref(course: PublicCourse) {
  return "/courses/" + encodeURIComponent(course.id);
}

function TrackCard({ track, index }: { track: PublicTrack; index: number }) {
  const firstCourse = track.courses?.find(item => item.course)?.course;
  const image = firstCourse ? courseImage(firstCourse, index) : [IMAGES.practice, IMAGES.projects, IMAGES.library][index % 3];
  return (
    <article className="landing-track-card">
      <Link href={"/tracks/" + encodeURIComponent(track.id)} className="landing-image-link" aria-hidden="true" tabIndex={-1}>
        <Image src={image} alt="" width={800} height={450} quality={75} sizes="(max-width: 768px) 100vw, 33vw" />
        <span className="landing-image-label"><Route size={13}/> Learning track</span>
      </Link>
      <div className="landing-card-content">
        <h3><Link href={"/tracks/" + encodeURIComponent(track.id)}>{track.name}</Link></h3>
        <p>{track.description || "A structured sequence of published courses."}</p>
        <div className="landing-meta">
          <span><BookOpen size={14}/> {track.course_count} {track.course_count === 1 ? "course" : "courses"}</span>
          <span><Layers3 size={14}/> {track.required_course_count} required</span>
        </div>
        {track.courses?.length > 0 && <ul aria-label="Courses in this track" className="mt-5 grid gap-2 border-l border-[var(--gold)]/40 pl-4">{track.courses.slice(0,3).map((item,index)=><li key={item.id || item.course_id || index} className="text-xs text-slate-400">{item.course?.title || "Published course"}</li>)}</ul>}
        {track.self_enrol_available && <span className="landing-availability">Open for enrolment</span>}
        <Link className="landing-text-link" aria-label={"Explore " + track.name + " learning track"} href={"/tracks/" + encodeURIComponent(track.id)}>Explore track <ArrowRight size={15}/></Link>
      </div>
    </article>
  );
}

function CourseCard({ course, index }: { course: PublicCourse; index: number }) {
  const free = course.settings?.is_free === true || course.settings?.access_type === "free";
  const selfEnrolAvailable = free;
  return (
    <article className="landing-course-card">
      <Link href={courseHref(course)} className="landing-course-image" aria-hidden="true" tabIndex={-1}>
        <Image src={courseImage(course, index)} alt="" width={800} height={450} quality={75} sizes="(max-width: 768px) 100vw, 33vw" />
        {free && <span className="landing-free-label">Free access</span>}
      </Link>
      <div className="landing-course-copy">
        <div className="landing-course-overline">{course.level || "Published course"}</div>
        <h3><Link href={courseHref(course)}>{course.title}</Link></h3>
        <p>{course.short_description || course.description || "Explore the course outline and learning content."}</p>
        <div className="landing-meta">
          {typeof course.estimated_hours === "number" && course.estimated_hours > 0
            ? <span><Clock3 size={14}/> {course.estimated_hours < 1 ? Math.round(course.estimated_hours * 60) + " min" : course.estimated_hours + " hours"}</span>
            : null}
          {course.tracks?.slice(0, 1).map(track => <span key={track.id}><Route size={14}/>{track.name}</span>)}
        </div>
        <Link className="landing-text-link" aria-label={(selfEnrolAvailable ? "Enrol in " : "View ") + course.title} href={selfEnrolAvailable ? courseHref(course) + "?enrol=1" : courseHref(course)}>{selfEnrolAvailable ? "Enrol for free" : "View course"} <ArrowRight size={15}/></Link>
      </div>
    </article>
  );
}

export default function LandingPage({ initialCourses, initialTracks, initialError }: { initialCourses: PublicCourse[]; initialTracks: PublicTrack[]; initialError?: string | null }) {
  const [courses, setCourses] = useState<PublicCourse[]>(initialCourses);
  const [tracks, setTracks] = useState<PublicTrack[]>(initialTracks);
  const [error, setError] = useState(initialError || "");
  const [retrying, setRetrying] = useState(false);
  const [activeSlide, setActiveSlide] = useState(0);
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const targets = document.querySelectorAll<HTMLElement>(".landing-page .landing-reveal");
    if (!("IntersectionObserver" in window)) {
      targets.forEach(target => target.classList.add("is-visible"));
      return;
    }
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        (entry.target as HTMLElement).classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -48px 0px" });
    targets.forEach(target => observer.observe(target));
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const timer = window.setInterval(() => {
      if (document.visibilityState === "visible") setActiveSlide(value => (value + 1) % heroSlides.length);
    }, 7000);
    return () => window.clearInterval(timer);
  }, []);
  const [search, setSearch] = useState("");
  const [continueCourses, setContinueCourses] = useState<any[]>([]);

  async function loadCatalogue() {
    setRetrying(true);
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
      setRetrying(false);
    }
  }

  useEffect(() => {
    let active = true;
    currentUser().then(async me => {
      if (!active || me.account_type !== "learner" || me.role !== "normal" || me.organisation_id || me.cohort_id || me.organisation_role) return;
      const progress = await request<any>("/progress/me");
      if (!active) return;
      const rows = Array.isArray(progress.courses) ? progress.courses : [];
      setContinueCourses(rows.filter((row: any) => row.course?.id && !row.progress?.completed).slice(0, 4));
    }).catch(() => {});
    return () => { active = false; };
  }, []);

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
    <main id="main-content" className="landing-page">
      <section className="landing-wrap landing-hero landing-hero-motion" aria-label="Discover Learnora">
        <div className="landing-hero-copy">
          <p className="landing-kicker"><span/> Learnora ME</p>
          <h1 key={activeSlide} className="landing-slide-copy" aria-live="polite">{slide.title}</h1>
          <p key={"body-" + activeSlide} className="landing-hero-description landing-slide-copy">{slide.body}</p>
          <div className="landing-actions"><Link className="landing-button landing-button-outline" href="/how-it-works">How Learnora works <ArrowUpRight size={16}/></Link></div>
          <form className="landing-search" onSubmit={submitSearch}>
            <Search size={18} aria-hidden="true"/>
            <input aria-label="Search courses and skills" list="landing-search-suggestions" value={search} onChange={event => setSearch(event.target.value)} placeholder="Search courses"/>
            <button type="submit">Find courses</button>
          </form>
          <datalist id="landing-search-suggestions">{categories.map(topic=><option key={topic} value={topic}/>)}</datalist>
          {categories.length > 0 && <div className="landing-popular-topics"><span>Popular topics</span>{categories.slice(0,5).map(topic=><Link key={topic} href={"/courses?search="+encodeURIComponent(topic)}>{topic}</Link>)}</div>}
          <div className="landing-hero-points">
            <span><BookOpen size={17}/> Learn clearly</span>
            <span><Compass size={17}/> Practise deeply</span>
            <span><CheckCircle2 size={17}/> Show your work</span>
          </div>
          <div className="landing-slide-controls" aria-label="Featured messages">
            <span aria-live="polite">{String(activeSlide + 1).padStart(2, "0")} / {String(heroSlides.length).padStart(2, "0")}</span>
            <div>
              {heroSlides.map((item, index) => <button key={index} type="button" className={activeSlide === index ? "active" : ""} aria-label={"Show featured message " + (index + 1)} aria-pressed={activeSlide === index} onClick={() => setActiveSlide(index)} />)}
            </div>
          </div>
        </div>
        <div className="landing-hero-visual" aria-label="A preview of learning on Learnora">
          <div className="landing-hero-product">
            {courses[0] ? <>
              <div className="landing-hero-product-top"><span>Published course</span><span>{courses[0].settings?.is_free || courses[0].settings?.access_type === "free" ? "Free to start" : "Course details"}</span></div>
              <div className="landing-hero-product-icon"><BookOpen size={28}/></div>
              <p className="landing-hero-product-kicker">{courses[0].tracks?.[0]?.name || courses[0].settings?.topics?.[0] || "Learnora course"}</p>
              <h2>{courses[0].title}</h2>
              <p className="landing-hero-product-description">{courses[0].short_description || courses[0].description || "Explore the published curriculum and available learning access."}</p>
              <div className="landing-hero-product-topics">{(courses[0].settings?.topics || []).slice(0,3).map(topic=><span key={topic}>{topic}</span>)}</div>
              <div className="landing-hero-product-footer"><span>{courses[0].level || "All levels"}</span><span>{courses[0].estimated_hours ? (courses[0].estimated_hours < 1 ? Math.round(courses[0].estimated_hours * 60) + " min" : courses[0].estimated_hours + " hours") : "Self-paced"}</span><Link href={courseHref(courses[0])}>View course <ArrowRight size={15}/></Link></div>
            </> : <><div className="landing-hero-product-icon"><BookOpen size={28}/></div><h2>Explore practical learning.</h2><p className="landing-hero-product-description">Published courses will appear here when they are ready to explore.</p><Link href="/courses">Browse courses <ArrowRight size={15}/></Link></>}
          </div>
        </div>
      </section>

      {continueCourses.length > 0 && <section className="landing-wrap py-10 landing-reveal" aria-labelledby="continue-learning-heading">
        <div className="landing-section-heading"><div><h2 id="continue-learning-heading">Continue learning</h2><p>Pick up where you left off.</p></div><Link className="landing-text-link" href="/dashboard">Open My Learning <ArrowRight size={15}/></Link></div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{continueCourses.map((row:any) => <Link key={row.course.id} href={"/dashboard/learning/"+encodeURIComponent(row.course.id)} className="border border-[var(--border)] bg-[var(--card)] p-5 transition-colors hover:border-[var(--gold)]/50"><p className="text-[10px] uppercase tracking-[.16em] text-slate-500">In progress</p><h3 className="mt-3 font-display text-xl">{row.course.title}</h3><div className="mt-5 h-1.5 overflow-hidden bg-[var(--border)]"><div className="h-full bg-[var(--gold)]" style={{width:Math.max(0,Math.min(100,Number(row.progress?.progress_percent||0)))+"%"}}/></div><p className="mt-2 text-xs text-slate-500">{Number(row.progress?.progress_percent||0)}% complete</p></Link>)}</div>
      </section>}

      <section className="landing-section landing-soft-section landing-reveal">
        <div className="landing-wrap">
          <div className="landing-section-heading">
            <div><h2>New and available to explore</h2></div>
            <Link className="landing-text-link" href="/courses">Browse all courses <ArrowRight size={15}/></Link>
          </div>
          {error && <div role="alert" className="landing-error"><span>{error}</span><button type="button" disabled={retrying} onClick={() => void loadCatalogue()}><RefreshCw size={14}/> {retrying ? "Retrying…" : "Try again"}</button></div>}
          {newestCourses.length ? (
            <div className="landing-course-grid">{newestCourses.slice(0, 4).map((course, index) => <CourseCard key={course.id} course={course} index={index}/>)}</div>
          ) : !error ? <div className="landing-empty"><BookOpen size={24}/><h3>Explore the Learnora catalogue</h3><p>There are no published courses available to browse at the moment. Check back soon.</p></div> : null}
        </div>
      </section>

      <section className="landing-wrap landing-tracks-section landing-reveal">
        <div className="landing-section-heading">
          <div><h2>Follow a path, not just a playlist</h2><p>Tracks bring related courses together in an intentional sequence.</p></div>
          <Link className="landing-text-link" href="/tracks">Explore all tracks <ArrowRight size={15}/></Link>
        </div>
        {featuredTracks.length ? (
          <div className="landing-track-grid">{featuredTracks.map((track, index) => <TrackCard key={track.id} track={track} index={index}/>)}</div>
        ) : !error ? <div className="landing-empty"><Route size={24}/><h3>No tracks available yet</h3><p>There are no published learning tracks to explore right now.</p></div> : null}
      </section>

      <section className="landing-image-band landing-reveal">
        <div className="landing-wrap landing-image-band-inner">
          <div className="landing-evidence-preview" aria-label="How Learnora distinguishes learning progress, assessment and reviewed evidence">
            <article><div><strong>Course progress</strong><p>Records lessons and learning activity.</p></div><span className="landing-evidence-type">Learning record</span></article>
            <article><div><strong>Assessment result</strong><p>Records performance against an assessment.</p></div><span className="landing-evidence-type">Assessment</span></article>
            <article><div><strong>Instructor-reviewed evidence</strong><p>Records work that has been reviewed by an instructor.</p></div><span className="landing-evidence-type">Human review</span></article>
          </div>
          <div><h2>Progress should mean more than a percentage.</h2><p>Finishing a course tells you that you reached the end of its material. Practice, projects, assessment and feedback help tell a fuller story of what you can do.</p><Link className="landing-button landing-button-light" href="/how-it-works">See how it works <ArrowRight size={16}/></Link></div>
        </div>
      </section>

      <section className="landing-wrap landing-categories-section landing-reveal">
        <div className="landing-section-heading">
          <div><h2>Explore learning areas</h2><p>These topics are drawn from the published course catalogue.</p></div>
        </div>
        {categories.length ? <div className="landing-category-list">{categories.map(category => <Link key={category} href={"/courses?search=" + encodeURIComponent(category)}><span/>{category}<ArrowUpRight size={14}/></Link>)}</div> : <div className="landing-empty"><Compass size={24}/><h3>Explore courses by topic</h3><p>Topic collections will appear when published courses include topic information.</p></div>}
      </section>

      <section className="landing-wrap landing-principles-section landing-reveal">
        <div className="landing-principles-grid">
          <article><h3>Practice matters</h3><p>Understanding grows when people use ideas, make decisions and learn from feedback.</p></article>
          <article><h3>Evidence should be honest</h3><p>Course completion, assessment results and instructor-reviewed evidence are different things.</p></article>
          <article><h3>People learn together</h3><p>Tutors, peers and teams can make learning more supported and connected to real needs.</p></article>
        </div>
      </section>

      <section className="landing-wrap landing-audience-section landing-reveal">
        <div className="landing-section-heading"><div><h2>Different journeys. One shared foundation.</h2></div></div>
        <div className="landing-audience-grid">
          <Link href="/for-learners"><Image src={IMAGES.learners} alt="Learners working together" width={700} height={500} quality={75} sizes="(max-width: 768px) 100vw, 33vw"/><div><GraduationCap size={20}/><h3>For learners</h3><p>Build useful skills through lessons, practice, projects and an honest record of progress.</p><span>Explore this path <ArrowRight size={14}/></span></div></Link>
          <Link href="/for-instructors"><Image src={IMAGES.instructors} alt="An instructor supporting a class" width={700} height={500} quality={75} sizes="(max-width: 768px) 100vw, 33vw"/><div><BookOpen size={20}/><h3>For instructors</h3><p>Create practical learning, support learners and review work.</p><span>Explore this path <ArrowRight size={14}/></span></div></Link>
          <Link href="/for-organisations"><Image src={IMAGES.organisations} alt="Colleagues collaborating in a meeting" width={700} height={500} quality={75} sizes="(max-width: 768px) 100vw, 33vw"/><div><Layers3 size={20}/><h3>For organisations</h3><p>Shape learning around your people, programmes, teams and agreed outcomes.</p><span>Explore this path <ArrowRight size={14}/></span></div></Link>
        </div>
      </section>

      <section className="landing-wrap landing-faq-section landing-reveal">
        <div className="landing-faq-intro"><h2>Before you begin.</h2><p>Know what you can explore and how learning works on Learnora.</p></div>
        <div className="landing-faq-list">
          <details><summary>What makes Learnora different from a course library?</summary><p>A course is one part of the journey. Learnora connects lessons with practice, projects, feedback and a record of what you have demonstrated.</p></details>
          <details><summary>Can I browse courses before creating an account?</summary><p>Yes. You can browse published courses and learning tracks before creating an account. You will need an account to enrol and save your progress.</p></details>
          <details><summary>Do I need to pay to get started?</summary><p>Many courses are free to start. If a course has a fee, you will see its price before you enrol.</p></details>
          <details><summary>Does completing a course mean a skill is verified?</summary><p>Not automatically. Course progress, assessment results and instructor-reviewed evidence are different things. Learnora is designed to keep that distinction clear.</p></details>
          <details><summary>Can my school or organisation use Learnora?</summary><p>Organisations can enquire about a workspace shaped around their people, programmes, courses and agreed outcomes.</p></details>
          <details><summary>I teach or have expertise to share. Can I contribute?</summary><p>Instructors and creators can explore the teaching pathway and apply to contribute. Access to creator tools follows the approval and permission process.</p></details>
        </div>
      </section>

      <section className="landing-wrap landing-final-cta landing-reveal">
        <div><h2>Your next step does not have to be your whole future.</h2><p>Explore a course, follow a learning track or find out how Learnora can support your teaching or organisation.</p></div>
        <div className="landing-final-actions"><Link className="landing-button landing-button-primary" href="/courses">Explore courses <ArrowRight size={16}/></Link><Link className="landing-button landing-button-outline" href="/get-started">Choose your path <ArrowUpRight size={16}/></Link></div>
      </section>
    </main>
  );
}
