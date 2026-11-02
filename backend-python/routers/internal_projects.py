"""Internal authoring, review and skill mapping for practical projects."""

from datetime import datetime, timezone
from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .auth import log_audit_event, supabase
from .internal_auth import InternalStaffContext, require_internal_permission

router = APIRouter(prefix="/api/internal/projects", tags=["Internal Projects"])


class SkillCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)


class SkillWrite(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=120)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)


class ProjectCreate(BaseModel):
    course_id: Optional[UUID] = None
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    instructions: str = Field(..., min_length=10, max_length=12000)
    skills: list[UUID] = Field(default_factory=list, max_length=20)


class ProjectWrite(BaseModel):
    course_id: Optional[UUID] = None
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    instructions: Optional[str] = Field(None, min_length=10, max_length=12000)
    skills: Optional[list[UUID]] = Field(None, max_length=20)
    is_published: Optional[bool] = None


class ProjectReviewIn(BaseModel):
    score: float = Field(..., ge=0, le=100)
    feedback: Optional[str] = Field(None, max_length=10000)
    decision: Literal["approved", "returned"] = "returned"


def _global_course(course_id: str) -> dict:
    rows = (
        supabase.table("learnora_courses")
        .select("id,title,status,ownership,organisation_id")
        .eq("id", course_id)
        .eq("ownership", "learnora")
        .is_("organisation_id", "null")
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        raise HTTPException(404, "Global Learnora course not found.")
    return rows[0]


def _project(project_id: str) -> dict:
    rows = (
        supabase.table("projects")
        .select("id,course_id,title,description,instructions,skills,is_published,created_at,updated_at")
        .eq("id", project_id)
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        raise HTTPException(404, "Project not found.")
    row = rows[0]
    if row.get("course_id"):
        _global_course(str(row["course_id"]))
    return row


def _skill_ids(values: list[UUID]) -> list[str]:
    ids = list(dict.fromkeys(str(value) for value in values))
    if not ids:
        return []
    found = (
        supabase.table("skills")
        .select("id")
        .in_("id", ids)
        .execute()
    ).data or []
    found_ids = {str(row["id"]) for row in found}
    if found_ids != set(ids):
        raise HTTPException(422, "One or more selected skills do not exist.")
    return ids


@router.get("/skills")
def list_skills(staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    rows = (
        supabase.table("skills")
        .select("id,name,category,description,created_at")
        .order("name")
        .execute()
    ).data or []
    return {"success": True, "skills": rows}


@router.post("/skills", status_code=201)
def create_skill(body: SkillCreate, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    name = body.name.strip()
    if not name:
        raise HTTPException(422, "Skill name is required.")
    existing = (
        supabase.table("skills")
        .select("id")
        .ilike("name", name)
        .limit(1)
        .execute()
    ).data or []
    if existing:
        raise HTTPException(409, "A skill with that name already exists.")
    saved = supabase.table("skills").insert({
        "name": name,
        "category": body.category.strip() if body.category else None,
        "description": body.description.strip() if body.description else None,
    }).execute()
    if not saved.data:
        raise HTTPException(500, "Skill could not be created.")
    log_audit_event(action="learning_skill_created", email=staff.email, account_type="staff", role="staff", metadata={"staff_id": staff.staff_id, "skill_id": saved.data[0]["id"]})
    return {"success": True, "skill": saved.data[0]}


@router.patch("/skills/{skill_id}")
def update_skill(skill_id: str, body: SkillWrite, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    try:
        skill_id = str(UUID(skill_id))
    except ValueError:
        raise HTTPException(404, "Skill not found.") from None
    rows = supabase.table("skills").select("id").eq("id", skill_id).limit(1).execute().data or []
    if not rows:
        raise HTTPException(404, "Skill not found.")
    payload = body.model_dump(exclude_unset=True)
    if "name" in payload and payload["name"] is not None:
        payload["name"] = payload["name"].strip()
        if not payload["name"]:
            raise HTTPException(422, "Skill name is required.")
    for key in ("category", "description"):
        if key in payload and payload[key] is not None:
            payload[key] = payload[key].strip() or None
    saved = supabase.table("skills").update(payload).eq("id", skill_id).execute()
    if not saved.data:
        raise HTTPException(500, "Skill could not be updated.")
    log_audit_event(action="learning_skill_updated", email=staff.email, account_type="staff", role="staff", metadata={"staff_id": staff.staff_id, "skill_id": skill_id})
    return {"success": True, "skill": saved.data[0]}


@router.get("")
def list_projects(staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    rows = (
        supabase.table("projects")
        .select("id,course_id,title,description,instructions,skills,is_published,created_at,updated_at")
        .order("created_at", desc=True)
        .execute()
    ).data or []
    course_ids = list({str(row["course_id"]) for row in rows if row.get("course_id")})
    course_map = {}
    if course_ids:
        course_rows = supabase.table("learnora_courses").select("id,title,status").in_("id", course_ids).execute().data or []
        course_map = {str(row["id"]): row for row in course_rows}
    skill_ids = list({str(skill_id) for row in rows for skill_id in (row.get("skills") or [])})
    skill_map = {}
    if skill_ids:
        skill_rows = supabase.table("skills").select("id,name,category").in_("id", skill_ids).execute().data or []
        skill_map = {str(row["id"]): row for row in skill_rows}
    return {
        "success": True,
        "projects": [
            {
                **row,
                "course": course_map.get(str(row.get("course_id"))),
                "skill_records": [skill_map[str(value)] for value in (row.get("skills") or []) if str(value) in skill_map],
            }
            for row in rows
        ],
    }


@router.post("", status_code=201)
def create_project(body: ProjectCreate, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    course_id = str(body.course_id) if body.course_id else None
    if course_id:
        _global_course(course_id)
    skills = _skill_ids(body.skills)
    saved = supabase.table("projects").insert({
        "course_id": course_id,
        "title": body.title.strip(),
        "description": body.description.strip() if body.description else None,
        "instructions": body.instructions.strip(),
        "skills": skills,
        "is_published": False,
    }).execute()
    if not saved.data:
        raise HTTPException(500, "Project could not be created.")
    log_audit_event(action="learning_project_created", email=staff.email, account_type="staff", role="staff", metadata={"staff_id": staff.staff_id, "project_id": saved.data[0]["id"], "course_id": course_id})
    return {"success": True, "project": saved.data[0]}


@router.patch("/{project_id}")
def update_project(project_id: str, body: ProjectWrite, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    project = _project(project_id)
    payload = body.model_dump(exclude_unset=True)
    if set(payload) - {"is_published"}:
        prior_submissions = (
            supabase.table("project_submissions")
            .select("id")
            .eq("project_id", project_id)
            .limit(1)
            .execute()
        ).data or []
        if prior_submissions:
            raise HTTPException(
                409,
                "Project instructions, course association and skill mapping are frozen after the first learner submission. Create a new project for a changed brief.",
            )
    if project.get("is_published"):
        if payload.get("is_published") is not False or len(payload) != 1:
            raise HTTPException(409, "Unpublish this project before editing its content.")
    if "course_id" in payload:
        course_id = str(payload["course_id"]) if payload["course_id"] else None
        if course_id:
            _global_course(course_id)
        payload["course_id"] = course_id
    if "skills" in payload and payload["skills"] is not None:
        payload["skills"] = _skill_ids(payload["skills"])
    if "title" in payload and payload["title"] is not None:
        payload["title"] = payload["title"].strip()
    if "description" in payload and payload["description"] is not None:
        payload["description"] = payload["description"].strip() or None
    if "instructions" in payload and payload["instructions"] is not None:
        payload["instructions"] = payload["instructions"].strip()
    if payload.get("is_published") is True:
        candidate = {**project, **payload}
        if len(str(candidate.get("instructions") or "").strip()) < 10:
            raise HTTPException(409, "Add clear project instructions before publishing.")
        if not candidate.get("skills"):
            raise HTTPException(409, "Map at least one skill to the project before publishing.")
        if candidate.get("course_id"):
            course = _global_course(str(candidate["course_id"]))
            if course.get("status") != "published":
                raise HTTPException(409, "Publish the course before publishing its project.")
    saved = supabase.table("projects").update(payload).eq("id", project_id).execute()
    if not saved.data:
        raise HTTPException(500, "Project could not be updated.")
    log_audit_event(action="learning_project_updated", email=staff.email, account_type="staff", role="staff", metadata={"staff_id": staff.staff_id, "project_id": project_id, "is_published": saved.data[0].get("is_published")})
    return {"success": True, "project": saved.data[0]}


@router.get("/{project_id}/submissions")
def project_submissions(project_id: str, staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    project = _project(project_id)
    rows = (
        supabase.table("project_submissions")
        .select("id,project_id,user_id,title,description,repository_url,live_url,submission_url,status,feedback,score,submitted_at,reviewed_at,reviewed_by")
        .eq("project_id", project_id)
        .order("submitted_at", desc=True)
        .execute()
    ).data or []
    user_ids = list({str(row["user_id"]) for row in rows if row.get("user_id")})
    users = supabase.table("users").select("id,name,email").in_("id", user_ids).execute().data or [] if user_ids else []
    user_map = {str(row["id"]): row for row in users}
    return {
        "success": True,
        "project": project,
        "submissions": [{**row, "learner": user_map.get(str(row.get("user_id")))} for row in rows],
    }


@router.post("/{project_id}/submissions/{submission_id}/review")
def review_project_submission(
    project_id: str,
    submission_id: str,
    body: ProjectReviewIn,
    staff: InternalStaffContext = Depends(require_internal_permission("content.manage")),
):
    project = _project(project_id)
    rows = (
        supabase.table("project_submissions")
        .select("id,user_id,status")
        .eq("id", submission_id)
        .eq("project_id", project_id)
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        raise HTTPException(404, "Submission not found for this project.")
    if body.decision == "approved" and body.score < 70:
        raise HTTPException(422, "A project must score at least 70% to be approved as skill evidence.")

    learner_id = str(rows[0]["user_id"])
    skill_ids = [str(value) for value in (project.get("skills") or [])]
    if body.decision == "approved" and not skill_ids:
        raise HTTPException(409, "This project has no mapped skills and cannot be approved as verified evidence.")

    # Prepare evidence before marking the submission approved. The learner's
    # mastery view verifies evidence against the submission's approved status,
    # so a failed review update cannot create verified evidence on its own.
    if body.decision == "approved":
        for skill_id in skill_ids:
            existing = (
                supabase.table("skill_evidence")
                .select("id")
                .eq("user_id", learner_id)
                .eq("skill_id", skill_id)
                .eq("evidence_type", "project")
                .eq("source_id", submission_id)
                .limit(1)
                .execute()
            ).data or []
            evidence_payload = {
                "user_id": learner_id,
                "skill_id": skill_id,
                "evidence_type": "project",
                "source_id": submission_id,
                "score": body.score,
                "notes": body.feedback.strip() if body.feedback else "Project approved by Learnora staff.",
            }
            try:
                if existing:
                    saved_evidence = (
                        supabase.table("skill_evidence")
                        .update(evidence_payload)
                        .eq("id", existing[0]["id"])
                        .execute()
                    ).data or []
                else:
                    saved_evidence = supabase.table("skill_evidence").insert(evidence_payload).execute().data or []
            except Exception as exc:
                print(f"Project evidence preparation failed: {type(exc).__name__}")
                raise HTTPException(503, "The project evidence could not be prepared. The submission review was not approved.") from None
            if not saved_evidence:
                raise HTTPException(503, "The project evidence could not be prepared. The submission review was not approved.")

    now = datetime.now(timezone.utc).isoformat()
    saved = (
        supabase.table("project_submissions")
        .update({
            "status": body.decision,
            "score": body.score,
            "feedback": body.feedback.strip() if body.feedback else None,
            "reviewed_at": now,
            "reviewed_by": staff.user_id,
        })
        .eq("id", submission_id)
        .eq("project_id", project_id)
        .execute()
    ).data or []
    if not saved:
        raise HTTPException(500, "Project review could not be saved.")

    if body.decision == "returned":
        # Once the status is returned, mastery verification excludes these
        # records immediately, even if evidence cleanup needs a retry.
        try:
            supabase.table("skill_evidence").delete().eq("user_id", learner_id).eq("evidence_type", "project").eq("source_id", submission_id).execute()
        except Exception as exc:
            print(f"Returned project evidence cleanup failed: {type(exc).__name__}")
            raise HTTPException(503, "The submission was returned, but evidence cleanup needs to be retried.") from None

    log_audit_event(
        action="project_submission_reviewed",
        email=staff.email,
        account_type="staff",
        role="staff",
        metadata={
            "staff_id": staff.staff_id,
            "learner_user_id": learner_id,
            "project_id": project_id,
            "submission_id": submission_id,
            "decision": body.decision,
            "score": body.score,
        },
    )
    return {"success": True, "submission": saved[0]}
