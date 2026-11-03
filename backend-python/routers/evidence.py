"""Learning evidence, skills and project submissions API."""

from datetime import datetime, timezone
from uuid import UUID
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .auth import CurrentUser, get_current_user, supabase
from .progress import _enrolment
from services.free_access import is_individual_learner

router = APIRouter(
    prefix="/api/evidence",
    tags=["Learning Evidence"],
)


class EvidenceIn(BaseModel):
    skill_id: UUID
    evidence_type: str = Field(..., min_length=2, max_length=50)
    source_id: UUID | None = None
    score: float | None = Field(default=None, ge=0, le=100)
    notes: str | None = Field(default=None, max_length=5000)


class ProjectSubmissionIn(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    repository_url: str | None = Field(default=None, max_length=1000)
    live_url: str | None = Field(default=None, max_length=1000)
    submission_url: str | None = Field(default=None, max_length=1000)


ALLOWED_EVIDENCE_TYPES = {
    "manual",
}


def _enrolled(user_id, course_id):
    # Reuse the central scope-aware enrolment resolver. A personal enrolment
    # must not authorise an organisation/cohort learner's project access.
    return _enrolment(str(user_id), str(course_id))


def _is_assigned_learner(user: CurrentUser) -> bool:
    if (
        user.account_type == "cohort"
        or user.role == "witstart"
        or getattr(user, "organisation_id", None)
        or getattr(user, "cohort_id", None)
    ):
        return True
    try:
        organisation_memberships = (
            supabase.table("organisation_members")
            .select("id")
            .eq("user_id", str(user.id))
            .in_("role", ["learner", "member"])
            .eq("status", "active")
            .limit(1)
            .execute()
        ).data or []
        cohort_memberships = (
            supabase.table("cohort_members")
            .select("id")
            .eq("user_id", str(user.id))
            .eq("status", "active")
            .limit(1)
            .execute()
        ).data or []
    except Exception:
        raise HTTPException(503, "Learner access could not be verified. Please retry.") from None
    return bool(organisation_memberships or cohort_memberships)


@router.get("/me")
def my_evidence(
    user: CurrentUser = Depends(get_current_user),
):
    evidence = (
        supabase
        .table("skill_evidence")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .execute()
    )

    badges = (
        supabase
        .table("learner_badges")
        .select("*")
        .eq("user_id", user.id)
        .execute()
    )

    certificates = (
        supabase
        .table("certificates")
        .select("*")
        .eq("user_id", user.id)
        .order("issued_at", desc=True)
        .execute()
    )

    evidence_rows = evidence.data or []
    certificate_rows = certificates.data or []
    definitions = (
        supabase.table("skills")
        .select("id,name,category,description")
        .order("name")
        .execute()
    ).data or []
    skill_map = {str(row["id"]): row for row in definitions}
    project_source_ids = list({
        str(row["source_id"])
        for row in evidence_rows
        if row.get("evidence_type") == "project" and row.get("source_id")
    })
    verified_project_map = {}
    verified_project_skill_pairs = set()
    if project_source_ids:
        verified_projects = (
            supabase.table("project_submissions")
            .select("id,user_id,status,score,project_id")
            .in_("id", project_source_ids)
            .eq("user_id", user.id)
            .eq("status", "approved")
            .execute()
        ).data or []
        verified_project_map = {str(row["id"]): row for row in verified_projects}
        project_ids = list({str(row["project_id"]) for row in verified_projects if row.get("project_id")})
        if project_ids:
            project_rows = (
                supabase.table("projects")
                .select("id,skills")
                .in_("id", project_ids)
                .execute()
            ).data or []
            project_skill_map = {
                str(project["id"]): {str(value) for value in (project.get("skills") or [])}
                for project in project_rows
            }
            for submission in verified_projects:
                allowed_skills = project_skill_map.get(str(submission.get("project_id")), set())
                for skill_id in allowed_skills:
                    verified_project_skill_pairs.add((str(submission["id"]), skill_id))
    mastery_scores = {}
    for row in evidence_rows:
        source_id = str(row.get("source_id") or "")
        skill_id = str(row.get("skill_id") or "")
        if (
            row.get("evidence_type") != "project"
            or source_id not in verified_project_map
            or (source_id, skill_id) not in verified_project_skill_pairs
        ):
            continue
        score = verified_project_map[source_id].get("score", row.get("score"))
        if score is not None:
            mastery_scores.setdefault(skill_id, []).append(float(score))
    enriched_skill_rows = []
    for definition in definitions:
        values = mastery_scores.get(str(definition["id"]), [])
        proficiency = round(sum(values) / len(values), 1) if values else 0
        status = "advanced" if proficiency >= 85 else "competent" if proficiency >= 70 else "developing" if values else "not_started"
        enriched_skill_rows.append({
            **definition,
            "skill_id": str(definition["id"]),
            "skill_name": definition.get("name"),
            "proficiency": proficiency,
            "status": status,
            "verified_evidence_count": len(values),
        })
    course_ids = list({
        str(row["course_id"])
        for row in certificate_rows
        if row.get("course_id")
    })
    course_map = {}
    if course_ids:
        course_rows = (
            supabase.table("learnora_courses")
            .select("id,title")
            .in_("id", course_ids)
            .execute()
        ).data or []
        course_map = {str(row["id"]): row for row in course_rows}

    enriched_evidence = [
        {
            **row,
            "skill": skill_map.get(str(row.get("skill_id"))),
            "skill_name": (skill_map.get(str(row.get("skill_id"))) or {}).get("name"),
            "verification_state": (
                "verified"
                if row.get("evidence_type") == "project"
                and str(row.get("source_id") or "") in verified_project_map
                and (str(row.get("source_id") or ""), str(row.get("skill_id") or "")) in verified_project_skill_pairs
                else "not_verified"
            ),
        }
        for row in evidence_rows
    ]
    enriched_certificates = [
        {
            **row,
            "course_title": (course_map.get(str(row.get("course_id"))) or {}).get("title"),
        }
        for row in certificate_rows
    ]

    return {
        "success": True,
        "skills": enriched_skill_rows,
        "evidence": enriched_evidence,
        "badges": badges.data or [],
        "certificates": enriched_certificates,
    }


@router.post("/me", status_code=201)
def add_evidence(
    body: EvidenceIn,
    user: CurrentUser = Depends(get_current_user),
):
    evidence_type = body.evidence_type.strip().lower()

    if evidence_type not in ALLOWED_EVIDENCE_TYPES:
        raise HTTPException(
            400,
            "Only personal notes may be added manually. Verified project and assessment evidence is created by Learnora after review.",
        )
    if body.score is not None or body.source_id is not None:
        raise HTTPException(422, "Manual evidence cannot claim a score or attach an unverified source.")

    skill = (
        supabase
        .table("skills")
        .select("id,name")
        .eq("id", str(body.skill_id))
        .limit(1)
        .execute()
    )
    if not skill.data:
        raise HTTPException(
            404,
            "Skill not found.",
        )

    payload = {
        "user_id": user.id,
        "skill_id": str(body.skill_id),
        "evidence_type": evidence_type,
        "source_id": (
            str(body.source_id)
            if body.source_id
            else None
        ),
        "score": body.score,
        "notes": body.notes.strip() if body.notes else None,
    }

    result = (
        supabase
        .table("skill_evidence")
        .insert(payload)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            500,
            "Unable to save skill evidence.",
        )

    return {
        "success": True,
        "evidence": result.data[0],
    }


@router.get("/projects")
def available_projects(user: CurrentUser = Depends(get_current_user)):
    """Published practice projects available to the authenticated learner."""
    rows = (
        supabase.table("projects")
        .select("id,course_id,title,description,instructions,skills,created_at")
        .eq("is_published", True)
        .order("created_at", desc=True)
        .execute()
    ).data or []
    course_ids = list({str(row["course_id"]) for row in rows if row.get("course_id")})
    course_map = {}
    assigned_learner = _is_assigned_learner(user)
    if course_ids:
        course_rows = (
            supabase.table("learnora_courses")
            .select("id,title,status,ownership,organisation_id")
            .in_("id", course_ids)
            .eq("status", "published")
            .execute()
        ).data or []
        course_map = {str(row["id"]): row for row in course_rows}
    skill_ids = list({str(value) for row in rows for value in (row.get("skills") or [])})
    skill_map = {}
    if skill_ids:
        skill_rows = supabase.table("skills").select("id,name,category").in_("id", skill_ids).execute().data or []
        skill_map = {str(row["id"]): row for row in skill_rows}
    available = []
    for row in rows:
        course_id = str(row.get("course_id") or "")
        if course_id:
            if course_id not in course_map or not _enrolled(user.id, course_id):
                continue
        elif assigned_learner or not is_individual_learner(
            user.role,
            user.account_type,
            getattr(user, "organisation_id", None),
        ):
            # Course-less open challenges are part of the individual public
            # practice catalogue, not organisation/cohort assigned learning.
            continue
        available.append({
            **row,
            "course": course_map.get(course_id) if course_id else None,
            "skill_records": [skill_map[str(value)] for value in (row.get("skills") or []) if str(value) in skill_map],
        })
    project_ids = [str(row["id"]) for row in available]
    latest_submissions = {}
    if project_ids:
        submission_rows = (
            supabase.table("project_submissions")
            .select("id,project_id,status,score,feedback,submitted_at,reviewed_at")
            .eq("user_id", str(user.id))
            .in_("project_id", project_ids)
            .order("submitted_at", desc=True)
            .execute()
        ).data or []
        for submission in submission_rows:
            latest_submissions.setdefault(str(submission["project_id"]), submission)
    return {
        "success": True,
        "projects": [
            {**project, "latest_submission": latest_submissions.get(str(project["id"]))}
            for project in available
        ],
    }


@router.get("/projects/me")
def my_project_submissions(
    user: CurrentUser = Depends(get_current_user),
):
    """Return only the authenticated learner's own project submissions."""
    submissions = (
        supabase
        .table("project_submissions")
        .select(
            "id,project_id,title,description,repository_url,live_url,"
            "submission_url,status,feedback,score,submitted_at,reviewed_at"
        )
        .eq("user_id", user.id)
        .order("submitted_at", desc=True)
        .execute()
    ).data or []

    project_ids = list({
        str(row["project_id"])
        for row in submissions
        if row.get("project_id")
    })
    project_map = {}
    if project_ids:
        projects = (
            supabase
            .table("projects")
            .select("id,title,description,skills")
            .in_("id", project_ids)
            .execute()
        ).data or []
        project_map = {
            str(row["id"]): row
            for row in projects
        }

    return {
        "success": True,
        "submissions": [
            {
                **row,
                "project": project_map.get(str(row.get("project_id"))),
                "review_state": (
                    "approved" if row.get("status") == "approved"
                    else "returned" if row.get("status") == "returned"
                    else "reviewed" if row.get("status") == "reviewed"
                    else "awaiting_review"
                ),
            }
            for row in submissions
        ],
    }


@router.post(
    "/projects/{project_id}/submissions",
    status_code=201,
)
def submit_project(
    project_id: str,
    body: ProjectSubmissionIn,
    user: CurrentUser = Depends(get_current_user),
):
    project = (
        supabase
        .table("projects")
        .select(
            "id,course_id,title,is_published"
        )
        .eq("id", project_id)
        .limit(1)
        .execute()
    )

    if not project.data:
        raise HTTPException(
            404,
            "Project not found.",
        )

    project_row = project.data[0]

    if not project_row.get("is_published"):
        raise HTTPException(
            409,
            "This project is not published.",
        )

    course_id = project_row.get("course_id")

    if course_id:
        course_rows = (
            supabase.table("learnora_courses")
            .select("id,status,ownership,organisation_id")
            .eq("id", str(course_id))
            .limit(1)
            .execute()
        ).data or []
        if not course_rows or course_rows[0].get("status") != "published":
            raise HTTPException(409, "This project is not attached to a published course.")
        if not _enrolled(user.id, str(course_id)):
            raise HTTPException(
                403,
                "You must have an active assignment or enrolment for this course before submitting this project.",
            )
    elif _is_assigned_learner(user) or not is_individual_learner(
        user.role,
        user.account_type,
        getattr(user, "organisation_id", None),
    ):
        raise HTTPException(403, "Open practice projects are available to individual learner accounts only.")

    for field_name in ("repository_url", "live_url", "submission_url"):
        value = getattr(body, field_name)
        if value:
            parsed = urlparse(value.strip())
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise HTTPException(422, f"{field_name.replace('_', ' ').title()} must be a valid HTTP or HTTPS URL.")

    existing = (
        supabase
        .table("project_submissions")
        .select("id,status")
        .eq("project_id", project_id)
        .eq("user_id", user.id)
        .in_("status", ["submitted", "reviewed", "approved"])
        .limit(1)
        .execute()
    )

    if existing.data:
        raise HTTPException(
            409,
            "You already have an active submission for this project.",
        )

    now = datetime.now(timezone.utc).isoformat()

    try:
        result = (
            supabase
            .table("project_submissions")
            .insert({
                "project_id": project_id,
                "user_id": user.id,
                **body.model_dump(),
                "status": "submitted",
                "submitted_at": now,
            })
            .execute()
        )
    except Exception as exc:
        if "23505" in str(exc) or "project_submissions_one_active_per_learner_idx" in str(exc):
            raise HTTPException(409, "You already have an active submission for this project.") from None
        print(f"Project submission insert failed: {type(exc).__name__}")
        raise HTTPException(500, "Unable to save project submission.") from None

    if not result.data:
        raise HTTPException(500, "Unable to save project submission.")

    return {
        "success": True,
        "submission": result.data[0],
    }
