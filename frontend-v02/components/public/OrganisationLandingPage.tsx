"use client";

import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";
import {
  ArrowRight, ArrowUpRight, BookOpen, Building2, CheckCircle2, Clock3,
  GraduationCap, Layers3, Network, Search, ShieldCheck, Users,
} from "lucide-react";
import { request } from "../../lib/api/client";
import { submitOrganisationRequest } from "../../lib/api/public";
import { IMAGES } from "../../lib/constants";

type Course = {
  id: string;
  title: string;
  slug?: string | null;
  short_description?: string | null;
  description?: string | null;
  level?: string | null;
  thumbnail_url?: string | null;
  estimated_hours?: number | null;
  tracks?: Array<{ id: string; name: string; slug?: string | null }>;
};
type TrackCourse = { id?: string; course_id?: string; order_index?: number; required?: boolean; course?: Course };
type Track = {
  id: string;
  name: string;
  slug?: string | null;
  description?: string | null;
  course_count: number;
  required_course_count: number;
  self_enrol_available?: boolean;
  courses: TrackCourse[];
};
type EnquiryForm = {
  organisation_name: string;
  contact_name: string;
  email: string;
  phone: string;
  country: string;
  website: string;
  organisation_type: string;
  request_type: string;
  organisation_size: string;
  expected_learners: string;
  expected_instructors: string;
  expected_teams: string;
  expected_cohorts: string;
  duration: string;
  notes: string;
  portal_password: string;
  confirm_password: string;
};
const initialForm: EnquiryForm = {
  organisation_name: "", contact_name: "", email: "", phone: "", country: "Nigeria",
  website: "", organisation_type: "business", request_type: "organisation_learning",
  organisation_size: "", expected_learners: "", expected_instructors: "",
  expected_teams: "", expected_cohorts: "", duration: "", notes: "",
  portal_password: "", confirm_password: "",
};
const orgTypes = [
  ["business", "Business / enterprise"], ["school", "School"],
  ["university", "University / higher education"], ["academy", "Academy / training provider"],
  ["nonprofit", "Non-profit organisation"], ["team", "Team / department"],
  ["government", "Government institution"], ["other", "Other"],
] as const;

function countCoursePlacements(items: Track[]) {
  return items.reduce((sum, track) => sum + (Array.isArray(track.courses) ? track.courses.length : 0), 0);
}

function TrackCard({ track, index }: { track: Track; index: number }) {
  const course = track.courses?.find(item => item.course)?.course;
  const images = [IMAGES.practice, IMAGES.projects, IMAGES.workshop];
  return (
    <article className="org-track-card">
      <Link href={"/tracks/" + encodeURIComponent(track.id)} className="org-track-image">
        <img src={course?.thumbnail_url || images[index % images.length]} alt="" loading="lazy"/>
        <span><RouteIcon/> Skills track</span>
      </Link>
      <div className="org-track-copy">
        <p className="org-eyebrow">Published learning track</p>
        <h3><Link href={"/tracks/" + encodeURIComponent(track.id)}>{track.name}</Link></h3>
        <p className="org-card-description">{track.description || "A structured sequence of published courses for developing connected skills."}</p>
        <div className="org-card-meta"><span><BookOpen size={14}/>{track.course_count} courses</span><span><Layers3 size={14}/>{track.required_course_count} required</span></div>
        <Link className="org-inline-link" href={"/tracks/" + encodeURIComponent(track.id)}>Explore track <ArrowRight size={15}/></Link>
      </div>
    </article>
  );
}
function RouteIcon() { return <Network size={13}/>; }

export default function OrganisationLandingPage() {
  const [tracks, setTracks] = useState<Track[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [catalogueError, setCatalogueError] = useState("");
  const [query, setQuery] = useState("");
  const [form, setForm] = useState<EnquiryForm>(initialForm);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState("");
  const [success, setSuccess] = useState<{ id: string; verificationEmailSent: boolean; verificationMessage?: string | null } | null>(null);

  async function loadCatalogue() {
    setLoading(true);
    setCatalogueError("");
    try {
      const [trackResult, courseResult] = await Promise.all([
        request<{ success: boolean; tracks: Track[] }>("/public/tracks"),
        request<{ success: boolean; courses: Course[] }>("/public/courses"),
      ]);
      setTracks(Array.isArray(trackResult.tracks) ? trackResult.tracks : []);
      setCourses(Array.isArray(courseResult.courses) ? courseResult.courses : []);
    } catch (error) {
      setCatalogueError(error instanceof Error ? error.message : "The published catalogue could not be loaded.");
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => { void loadCatalogue(); }, []);

  const filteredTracks = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return tracks;
    return tracks.filter(track => {
      const courseText = (track.courses || []).map(item => [item.course?.title, item.course?.short_description, item.course?.description, item.course?.level].filter(Boolean).join(" ")).join(" ");
      return [track.name, track.description, courseText].filter(Boolean).join(" ").toLowerCase().includes(q);
    });
  }, [tracks, query]);
  const filteredCourses = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return courses.slice(0, 6);
    return courses.filter(course => [course.title, course.short_description, course.description, course.level, ...(course.tracks || []).map(track => track.name)].filter(Boolean).join(" ").toLowerCase().includes(q)).slice(0, 6);
  }, [courses, query]);
  const placements = useMemo(() => countCoursePlacements(tracks), [tracks]);

  function update<K extends keyof EnquiryForm>(key: K, value: EnquiryForm[K]) {
    setForm(current => ({ ...current, [key]: value }));
  }
  function numericOrNull(value: string) { return value.trim() ? Number(value) : null; }
  async function submitEnquiry(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError("");
    if (form.portal_password !== form.confirm_password) {
      setFormError("The portal passwords do not match.");
      return;
    }
    const payload: Record<string, unknown> = { ...form };
    delete payload.confirm_password;
    for (const key of ["organisation_size", "expected_learners", "expected_instructors", "expected_teams", "expected_cohorts"]) {
      payload[key] = numericOrNull(form[key as keyof EnquiryForm] as string);
    }
    payload.requirements = [];
    setSubmitting(true);
    try {
      const result = await submitOrganisationRequest(payload);
      setSuccess({
        id: result.request.id,
        verificationEmailSent: Boolean(result.portal?.verification_email_sent),
        verificationMessage: result.portal?.verification_message,
      });
      setForm(initialForm);
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Your enquiry could not be submitted. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="org-page">
      <div className="org-audience-strip"><div className="org-wrap"><Link href="/for-learners">For individuals</Link><Link href="/for-organisations" aria-current="page">For organisations</Link><Link href="/for-instructors">For instructors</Link><span>Learning built around the people and work that matter</span></div></div>

      <section className="org-hero">
        <div className="org-hero-photo"><img src={IMAGES.organisationPage} alt="Colleagues collaborating in a bright workspace" fetchPriority="high"/><div className="org-photo-overlay"><span>LEARNORA ME · ORGANISATIONS</span><strong>Develop people. Strengthen capability. Make learning useful.</strong></div></div>
        <div className="org-wrap org-hero-inner">
          <div className="org-hero-copy">
            <p className="org-kicker"><span/> Learnora for organisations</p>
            <h1>Build the capabilities your people and work need next.</h1>
            <p>Bring learning, practice and progress into one connected experience. Shape programmes around your organisation, whether you are developing a workforce, supporting a school, running an academy or growing a team.</p>
            <ul className="org-checks">
              <li><CheckCircle2/> Build skills around real roles and priorities</li>
              <li><CheckCircle2/> Organise learning across teams, programmes and cohorts</li>
              <li><CheckCircle2/> Understand participation, progress and practical evidence</li>
            </ul>
            <div className="org-hero-actions"><a className="org-button org-button-primary" href="#org-contact">Discuss your organisation <ArrowRight size={16}/></a><a className="org-button org-button-outline" href="#org-tracks">Explore learning tracks <ArrowUpRight size={15}/></a></div>
            <p className="org-small-note">For businesses, education providers, non-profits, public institutions and teams.</p>
          </div>
        </div>
      </section>

      <section className="org-proof-band" aria-label="Live Learnora catalogue">
        <div className="org-wrap org-proof-grid">
          <div><strong>{loading ? "—" : tracks.length}</strong><span>Published learning tracks</span></div>
          <div><strong>{loading ? "—" : courses.length}</strong><span>Published courses</span></div>
          <div><strong>{loading ? "—" : placements}</strong><span>Course placements across tracks</span></div>
        </div>
        <p className="org-wrap org-proof-caption">Live counts from Learnora's published catalogue. They describe available learning content, not customer or outcome statistics.</p>
      </section>

      <section className="org-wrap org-content-split">
        <div className="org-photo-grid" aria-label="Learning and collaboration photography">
          <img src={IMAGES.workshop} alt="A group taking part in a learning workshop" loading="lazy"/>
          <img src={IMAGES.projects} alt="Colleagues collaborating on a project" loading="lazy"/>
          <img src={IMAGES.practice} alt="A person learning with a laptop" loading="lazy"/>
        </div>
        <div className="org-content-copy">
          <p className="org-eyebrow">Learning that fits your context</p>
          <h2>One platform. Different organisational needs.</h2>
          <p>Not every organisation works in the same way. Learnora's organisation model is designed to support different structures while keeping learning and access organised.</p>
          <ul className="org-checks">
            <li><CheckCircle2/> Businesses developing job-related capabilities across teams</li>
            <li><CheckCircle2/> Schools and universities coordinating structured learning</li>
            <li><CheckCircle2/> Academies and training providers delivering programmes</li>
            <li><CheckCircle2/> Non-profits and public institutions supporting defined learning initiatives</li>
          </ul>
          <a href="#org-contact" className="org-inline-link">Talk through your requirements <ArrowRight size={15}/></a>
        </div>
      </section>

      <section className="org-tracks-section" id="org-tracks">
        <div className="org-wrap">
          <div className="org-section-heading"><div><p className="org-kicker"><span/> Explore the catalogue</p><h2>Choose learning that matches your priorities.</h2><p>Explore published Learnora tracks and courses. The catalogue below is loaded from the live platform, not a sample list.</p></div><Link className="org-inline-link" href="/tracks">View all tracks <ArrowRight size={15}/></Link></div>
          <label className="org-search"><Search size={17}/><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Search skills, tracks or courses" aria-label="Search published skills, tracks or courses"/>{query && <button type="button" onClick={() => setQuery("")}>Clear</button>}</label>
          {catalogueError && <div role="alert" className="org-error"><span>{catalogueError}</span><button type="button" onClick={() => void loadCatalogue()}>Retry</button></div>}
          {loading ? <p className="org-state">Loading published learning tracks and courses…</p> : filteredTracks.length ? <div className="org-track-grid">{filteredTracks.slice(0, 3).map((track, index) => <TrackCard key={track.id} track={track} index={index}/>)}</div> : !catalogueError ? <div className="org-empty"><Layers3 size={25}/><h3>{tracks.length ? "No tracks match that search" : "Published tracks will appear here"}</h3><p>{tracks.length ? "Try a different skill or course title." : "Learnora will display tracks here when they are published to the public catalogue."}</p></div> : null}
          {!loading && filteredCourses.length > 0 && <div className="org-course-results"><div className="org-results-heading"><h3>{query ? "Matching published courses" : "More learning to explore"}</h3><Link href={query ? "/courses?search=" + encodeURIComponent(query) : "/courses"}>Browse courses <ArrowRight size={14}/></Link></div><div className="org-course-grid">{filteredCourses.map(course => <article className="org-course-card" key={course.id}><div className="org-course-image"><img src={course.thumbnail_url || IMAGES.practice} alt="" loading="lazy"/></div><div><span>{course.level || "Published course"}</span><h4><Link href={"/courses/" + encodeURIComponent(course.id)}>{course.title}</Link></h4><p>{course.short_description || course.description || "Explore the published course outline and learning content."}</p>{typeof course.estimated_hours === "number" && course.estimated_hours > 0 && <small><Clock3 size={13}/>{course.estimated_hours} hours</small>}</div></article>)}</div></div>}
          {!loading && !filteredCourses.length && !catalogueError && <p className="org-no-courses">No published courses match this search.</p>}
        </div>
      </section>

      <section className="org-capabilities-band">
        <div className="org-wrap">
          <div className="org-capabilities-intro"><p className="org-kicker"><span/> Designed for real organisational structures</p><h2>Give people the structure and support to keep moving.</h2><p>Use the organisation workspace model to coordinate the people, learning and oversight your programme requires. Access and capacity remain subject to Learnora's approval and agreed entitlements.</p></div>
          <div className="org-capabilities-grid">
            <article><Building2/><h3>Organisation workspace</h3><p>Keep organisational identity, settings, people and learning access within a dedicated workspace.</p></article>
            <article><Users/><h3>Teams and managers</h3><p>Organise people into teams and assign scoped responsibilities to authorised managers.</p></article>
            <article><GraduationCap/><h3>Programmes and cohorts</h3><p>Coordinate instructor-led programmes and cohorts where your organisation needs them.</p></article>
            <article><ShieldCheck/><h3>Progress and evidence</h3><p>Review participation, assessments, practical work and skill evidence without treating attendance as competence.</p></article>
          </div>
        </div>
      </section>

      <section className="org-contact-section" id="org-contact">
        <div className="org-wrap org-contact-grid">
          <div className="org-contact-copy">
            <p className="org-kicker"><span/> Start a conversation</p>
            <h2>Let's understand what your organisation needs.</h2>
            <p>Tell us about your organisation, the people you support and the learning outcomes you are working towards. The Learnora team will review your enquiry before any workspace is provisioned.</p>
            <ul className="org-checks">
              <li><CheckCircle2/> Discuss your structure and learning priorities</li>
              <li><CheckCircle2/> Explore teams, programmes and cohort requirements</li>
              <li><CheckCircle2/> Understand onboarding, review and activation</li>
            </ul>
            <div className="org-contact-image"><img src={IMAGES.organisations} alt="A team collaborating around a table" loading="lazy"/></div>
          </div>
          <div className="org-form-panel">
            {success ? <div className="org-success" role="status"><CheckCircle2 size={30}/><h3>Enquiry submitted</h3><p>Your request reference is <strong>{success.id}</strong>.</p><p>{success.verificationEmailSent ? "A verification email has been sent to your contact address." : "Email delivery was not confirmed. Please check your inbox or contact Learnora support if it does not arrive."}</p>{success.verificationMessage && <p className="org-form-warning">{success.verificationMessage}</p>}<p>Verify your email before signing in to the prospect portal. Your organisation workspace remains inactive until Learnora completes its review, contract and approval process.</p><Link className="org-button org-button-primary" href="/login">Go to sign in <ArrowRight size={15}/></Link><button className="org-reset" type="button" onClick={() => setSuccess(null)}>Submit another enquiry</button></div> : <>
              <h3>Organisation enquiry</h3><p className="org-form-intro">Share a few details so we can understand your requirements.</p>
              <form onSubmit={submitEnquiry} className="org-form">
                <label>Organisation name<input value={form.organisation_name} onChange={e => update("organisation_name", e.target.value)} required minLength={2} autoComplete="organization"/></label>
                <label>Contact person<input value={form.contact_name} onChange={e => update("contact_name", e.target.value)} required minLength={2} autoComplete="name"/></label>
                <label>Work email<input type="email" value={form.email} onChange={e => update("email", e.target.value)} required autoComplete="email"/></label>
                <label>Phone number <span>(optional)</span><input type="tel" value={form.phone} onChange={e => update("phone", e.target.value)} autoComplete="tel"/></label>
                <label>Organisation type<select value={form.organisation_type} onChange={e => update("organisation_type", e.target.value)}>{orgTypes.map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></label>
                <label>Country<input value={form.country} onChange={e => update("country", e.target.value)} autoComplete="country-name"/></label>
                <label>Website <span>(optional)</span><input type="url" value={form.website} onChange={e => update("website", e.target.value)} placeholder="https://"/></label>
                <label>Organisation size <span>(approximate)</span><input type="number" min="1" value={form.organisation_size} onChange={e => update("organisation_size", e.target.value)}/></label>
                <label>Expected learners <span>(optional)</span><input type="number" min="0" value={form.expected_learners} onChange={e => update("expected_learners", e.target.value)}/></label>
                <label>Expected teams <span>(optional)</span><input type="number" min="0" value={form.expected_teams} onChange={e => update("expected_teams", e.target.value)}/></label>
                <label>Expected instructors <span>(optional)</span><input type="number" min="0" value={form.expected_instructors} onChange={e => update("expected_instructors", e.target.value)}/></label>
                <label>Expected cohorts <span>(optional)</span><input type="number" min="0" value={form.expected_cohorts} onChange={e => update("expected_cohorts", e.target.value)}/></label>
                <label className="org-form-full">Expected programme duration <span>(optional)</span><input value={form.duration} onChange={e => update("duration", e.target.value)} placeholder="e.g. 6 months"/></label>
                <label className="org-form-full">What are you looking to achieve?<textarea value={form.notes} onChange={e => update("notes", e.target.value)} rows={4} placeholder="Tell us about your learning priorities, teams and desired outcomes."/></label>
                <div className="org-form-account org-form-full"><h4>Create your enquiry portal password</h4><p>The portal lets you follow your request and review any contract shared with you. Email verification is required before sign-in.</p><div className="org-form-two"><label>Password<input type="password" value={form.portal_password} onChange={e => update("portal_password", e.target.value)} minLength={10} maxLength={72} autoComplete="new-password" required/></label><label>Confirm password<input type="password" value={form.confirm_password} onChange={e => update("confirm_password", e.target.value)} minLength={10} maxLength={72} autoComplete="new-password" required/></label></div></div>
                {formError && <p className="org-form-error org-form-full" role="alert">{formError}</p>}
                <p className="org-form-terms org-form-full">Submitting creates an organisation request and a prospect portal account. It does not activate an organisation workspace or commit either party to a contract. Read our <Link href="/terms">Terms of Use</Link> and <Link href="/privacy">Privacy Notice</Link>.</p>
                <button className="org-button org-button-primary org-submit org-form-full" type="submit" disabled={submitting}>{submitting ? "Submitting enquiry…" : "Submit organisation enquiry"} <ArrowRight size={16}/></button>
              </form>
            </>}
          </div>
        </div>
      </section>

      <section className="org-final-cta"><div className="org-wrap"><div><p className="org-kicker"><span/> Learnora for organisations</p><h2>Start with your people. Build towards what comes next.</h2><p>Explore the catalogue or tell us what your organisation is working towards.</p></div><div><a className="org-button org-button-light" href="#org-tracks">Explore learning <ArrowRight size={15}/></a><a className="org-button org-button-ghost" href="#org-contact">Make an enquiry <ArrowUpRight size={15}/></a></div></div></section>
    </main>
  );
}
