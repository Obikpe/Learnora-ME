"""Track-scoped course and lesson assignments for organisation-managed cohorts.

Cohort learners use cohort_accounts and cohort_members; they are not required
to have a public.users or organisation_members row. Every learner-facing read
checks the active cohort membership and the explicit course/lesson assignment.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from routers.auth import CurrentUser, get_current_user, supabase
from routers.permissions import PermissionContext, require_permission
from services.audit import audit

router = APIRouter(tags=["Cohort learning"])


class TrackCourseIn(BaseModel):
    course_id: UUID


class LearnerCourseAssignmentIn(BaseModel):
    course_id: UUID
    tutor_user_id: Optional[UUID] = None
    lesson_ids: list[UUID] = Field(default_factory=list, max_length=500)


def _scope(context: PermissionContext, organisation_id: str) -> None:
    if context.is_platform_admin:
        return
    if str(context.organisation_id or "") != str(organisation_id):
        raise HTTPException(403, "Organisation access denied.")


def _cohort(organisation_id: str, cohort_id: str) -> dict:
    result = (
        supabase.table("cohorts")
        .select("id,organisation_id,status")
        .eq("id", cohort_id)
        .eq("organisation_id", organisation_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Cohort not found.")
    row = result.data[0]
    if row.get("status") not in {"draft", "upcoming", "active"}:
        raise HTTPException(409, "This cohort is closed to learning assignments.")
    return row


def _published_course(course_id: str, organisation_id: str) -> dict:
    result = (
        supabase.table("learnora_courses")
        .select("id,title,slug,short_description,description,ownership,organisation_id,status,thumbnail_url,estimated_hours,creator_id")
        .eq("id", course_id)
        .limit(1)
        .execute()
    )
    if not result.data or result.data[0].get("status") != "published":
        raise HTTPException(404, "Published course not found.")
    course = result.data[0]
    if course.get("ownership") == "organisation" and str(course.get("organisation_id")) != str(organisation_id):
        raise HTTPException(403, "An organisation cannot assign another organisation's course.")
    if course.get("ownership") not in {"learnora", "creator", "organisation"}:
        raise HTTPException(403, "This course cannot be assigned to a cohort.")
    if course.get("ownership") == "creator":
        creator_id = course.get("creator_id")
        creator = (
            supabase.table("learnora_creator_accounts")
            .select("id,status")
            .eq("id", creator_id)
            .limit(1)
            .execute()
        ) if creator_id else None
        if not creator or not creator.data or creator.data[0].get("status") not in {"approved", "active"}:
            raise HTTPException(403, "This creator is not approved for course distribution.")
    return course


def _member(cohort_id: str, member_id: str) -> dict:
    result = (
        supabase.table("cohort_members")
        .select("id,cohort_id,user_id,cohort_account_id,track_id,status")
        .eq("id", member_id)
        .eq("cohort_id", cohort_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Cohort learner not found.")
    member = result.data[0]
    if member.get("status") != "active":
        raise HTTPException(409, "Only active cohort learners can receive course assignments.")
    if not member.get("track_id"):
        raise HTTPException(409, "The learner has no fixed track assignment.")
    return member


def _validate_lesson_ids(course_id: str, lesson_ids: list[str]) -> None:
    if len(set(lesson_ids)) != len(lesson_ids):
        raise HTTPException(400, "Duplicate lesson IDs are not allowed.")
    if not lesson_ids:
        return
    lessons = (
        supabase.table("learnora_lessons")
        .select("id,module_id,status")
        .in_("id", lesson_ids)
        .execute()
    ).data or []
    if len(lessons) != len(lesson_ids):
        raise HTTPException(400, "One or more lessons do not exist.")
    if any(row.get("status") != "published" for row in lessons):
        raise HTTPException(400, "Only published lessons can be assigned.")
    module_ids = list({str(row["module_id"]) for row in lessons})
    modules = (
        supabase.table("course_modules")
        .select("id,course_id")
        .in_("id", module_ids)
        .execute()
    ).data or []
    course_by_module = {str(row["id"]): str(row["course_id"]) for row in modules}
    if any(course_by_module.get(str(row["module_id"])) != course_id for row in lessons):
        raise HTTPException(400, "Every assigned lesson must belong to the selected course.")


@router.get("/api/organisations/{organisation_id}/cohorts/{cohort_id}/tracks/{track_id}/courses")
def list_track_courses(
    organisation_id: str,
    cohort_id: str,
    track_id: str,
    context: PermissionContext = Depends(require_permission("organisations.view")),
):
    _scope(context, organisation_id)
    _cohort(organisation_id, cohort_id)
    option = (
        supabase.table("cohort_track_options")
        .select("id,status")
        .eq("cohort_id", cohort_id)
        .eq("track_id", track_id)
        .eq("status", "active")
        .limit(1)
        .execute()
    )
    if not option.data:
        raise HTTPException(404, "Track is not enabled for this cohort.")
    rows = (
        supabase.table("cohort_track_courses")
        .select("id,cohort_id,track_id,course_id,status,assigned_by,created_at,updated_at")
        .eq("cohort_id", cohort_id)
        .eq("track_id", track_id)
        .order("created_at")
        .execute()
    ).data or []
    course_ids = list({str(row["course_id"]) for row in rows})
    courses = (
        supabase.table("learnora_courses")
        .select("id,title,slug,short_description,status,thumbnail_url,estimated_hours")
        .in_("id", course_ids)
        .execute()
    ).data or [] if course_ids else []
    course_map = {str(row["id"]): row for row in courses}
    return {"success": True, "courses": [{**row, "course": course_map.get(str(row["course_id"]))} for row in rows]}


@router.get("/api/organisations/{organisation_id}/cohorts/{cohort_id}/tracks/{track_id}/courses/{course_id}/lessons")
def list_track_course_lessons(
    organisation_id: str,
    cohort_id: str,
    track_id: str,
    course_id: str,
    context: PermissionContext = Depends(require_permission("organisations.view")),
):
    """List published lessons available for a course enabled on this cohort track."""
    _scope(context, organisation_id)
    _cohort(organisation_id, cohort_id)
    option = (
        supabase.table("cohort_track_options")
        .select("id")
        .eq("cohort_id", cohort_id)
        .eq("track_id", track_id)
        .eq("status", "active")
        .limit(1)
        .execute()
    )
    if not option.data:
        raise HTTPException(404, "Track is not enabled for this cohort.")
    track_course = (
        supabase.table("cohort_track_courses")
        .select("id")
        .eq("cohort_id", cohort_id)
        .eq("track_id", track_id)
        .eq("course_id", course_id)
        .eq("status", "active")
        .limit(1)
        .execute()
    )
    if not track_course.data:
        raise HTTPException(404, "Course is not enabled for this cohort track.")
    _published_course(course_id, organisation_id)
    modules = (
        supabase.table("course_modules")
        .select("id")
        .eq("course_id", course_id)
        .execute()
    ).data or []
    module_ids = [str(row["id"]) for row in modules]
    lessons = (
        supabase.table("learnora_lessons")
        .select("id,module_id,title,slug,description,order_index,lesson_type,duration_minutes,status")
        .in_("module_id", module_ids)
        .eq("status", "published")
        .order("order_index")
        .execute()
    ).data or [] if module_ids else []
    return {"success": True, "lessons": lessons}


@router.post("/api/organisations/{organisation_id}/cohorts/{cohort_id}/tracks/{track_id}/courses", status_code=201)
def add_course_to_track(
    organisation_id: str,
    cohort_id: str,
    track_id: str,
    body: TrackCourseIn,
    context: PermissionContext = Depends(require_permission("courses.assign")),
):
    _scope(context, organisation_id)
    _cohort(organisation_id, cohort_id)
    option = (
        supabase.table("cohort_track_options")
        .select("id,status")
        .eq("cohort_id", cohort_id)
        .eq("track_id", track_id)
        .eq("status", "active")
        .limit(1)
        .execute()
    )
    if not option.data:
        raise HTTPException(404, "Track is not enabled for this cohort.")
    _published_course(str(body.course_id), organisation_id)
    now = datetime.now(timezone.utc).isoformat()
    try:
        result = supabase.table("cohort_track_courses").upsert({
            "cohort_id": cohort_id,
            "track_id": track_id,
            "course_id": str(body.course_id),
            "status": "active",
            "assigned_by": context.user_id,
            "updated_at": now,
        }, on_conflict="cohort_id,track_id,course_id").execute()
    except Exception:
        raise HTTPException(409, "Course could not be added to this track.")
    if not result.data:
        raise HTTPException(500, "Track course assignment could not be saved.")
    return {"success": True, "course_assignment": result.data[0]}


@router.patch("/api/organisations/{organisation_id}/cohorts/{cohort_id}/tracks/{track_id}/courses/{course_id}")
def update_track_course(
    organisation_id: str,
    cohort_id: str,
    track_id: str,
    course_id: str,
    body: dict,
    context: PermissionContext = Depends(require_permission("courses.assign")),
):
    _scope(context, organisation_id)
    _cohort(organisation_id, cohort_id)
    status = body.get("status")
    if status not in {"active", "inactive"}:
        raise HTTPException(400, "Status must be active or inactive.")
    if status == "inactive":
        assigned = (
            supabase.table("cohort_member_course_assignments")
            .select("id")
            .eq("cohort_id", cohort_id)
            .eq("track_id", track_id)
            .eq("course_id", course_id)
            .eq("status", "active")
            .limit(1)
            .execute()
        )
        if assigned.data:
            raise HTTPException(409, "This course is assigned to learners. Remove or deactivate learner assignments first.")
    result = (
        supabase.table("cohort_track_courses")
        .update({"status": status, "updated_at": datetime.now(timezone.utc).isoformat()})
        .eq("cohort_id", cohort_id)
        .eq("track_id", track_id)
        .eq("course_id", course_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Track course assignment not found.")
    return {"success": True, "course_assignment": result.data[0]}


@router.post("/api/organisations/{organisation_id}/cohorts/{cohort_id}/learners/{member_id}/courses", status_code=201)
def assign_course_to_learner(
    organisation_id: str,
    cohort_id: str,
    member_id: str,
    body: LearnerCourseAssignmentIn,
    context: PermissionContext = Depends(require_permission("courses.assign")),
):
    _scope(context, organisation_id)
    _cohort(organisation_id, cohort_id)
    member = _member(cohort_id, member_id)
    course_id = str(body.course_id)
    _published_course(course_id, organisation_id)
    enabled = (
        supabase.table("cohort_track_courses")
        .select("id")
        .eq("cohort_id", cohort_id)
        .eq("track_id", member["track_id"])
        .eq("course_id", course_id)
        .eq("status", "active")
        .limit(1)
        .execute()
    )
    if not enabled.data:
        raise HTTPException(400, "This course is not enabled for the learner's fixed track.")
    tutor_id = str(body.tutor_user_id) if body.tutor_user_id else None
    if tutor_id:
        tutor = (
            supabase.table("organisation_members")
            .select("id")
            .eq("organisation_id", organisation_id)
            .eq("user_id", tutor_id)
            .eq("status", "active")
            .limit(1)
            .execute()
        )
        if not tutor.data:
            raise HTTPException(400, "The assigned tutor must be an active member of this organisation.")
    lesson_ids = [str(value) for value in body.lesson_ids]
    _validate_lesson_ids(course_id, lesson_ids)
    now = datetime.now(timezone.utc).isoformat()
    try:
        result = supabase.table("cohort_member_course_assignments").upsert({
            "cohort_member_id": member_id,
            "cohort_id": cohort_id,
            "track_id": member["track_id"],
            "course_id": course_id,
            "tutor_user_id": tutor_id,
            "status": "active",
            "assigned_by": context.user_id,
            "updated_at": now,
        }, on_conflict="cohort_member_id,course_id").execute()
    except Exception:
        raise HTTPException(409, "The course assignment failed validation or conflicts with an existing assignment.")
    if not result.data:
        raise HTTPException(500, "Course assignment could not be saved.")
    assignment = result.data[0]
    existing_lessons = (
        supabase.table("cohort_member_lesson_assignments")
        .select("id,lesson_id")
        .eq("course_assignment_id", assignment["id"])
        .execute()
    ).data or []
    if existing_lessons:
        supabase.table("cohort_member_lesson_assignments").update({
            "status": "inactive", "updated_at": now,
        }).eq("course_assignment_id", assignment["id"]).execute()
    for lesson_id in lesson_ids:
        supabase.table("cohort_member_lesson_assignments").upsert({
            "course_assignment_id": assignment["id"],
            "lesson_id": lesson_id,
            "status": "active",
            "updated_at": now,
        }, on_conflict="course_assignment_id,lesson_id").execute()
    audit(
        actor_user_id=context.user_id,
        action="cohort_learner_course_assigned",
        resource_type="cohort_member_course_assignment",
        resource_id=assignment["id"],
        organisation_id=organisation_id,
        metadata={"cohort_id": cohort_id, "track_id": member["track_id"], "course_id": course_id, "lesson_count": len(lesson_ids), "tutor_assigned": bool(tutor_id)},
    )
    return {"success": True, "assignment": assignment, "assigned_lesson_ids": lesson_ids}


@router.get("/api/organisations/{organisation_id}/cohorts/{cohort_id}/learners/{member_id}/courses")
def list_learner_course_assignments(
    organisation_id: str,
    cohort_id: str,
    member_id: str,
    context: PermissionContext = Depends(require_permission("organisations.view")),
):
    _scope(context, organisation_id)
    _cohort(organisation_id, cohort_id)
    _member(cohort_id, member_id)
    rows = (
        supabase.table("cohort_member_course_assignments")
        .select("*")
        .eq("cohort_member_id", member_id)
        .order("assigned_at")
        .execute()
    ).data or []
    course_ids = list({str(row["course_id"]) for row in rows})
    courses = (
        supabase.table("learnora_courses")
        .select("id,title,slug,status,thumbnail_url,estimated_hours")
        .in_("id", course_ids)
        .execute()
    ).data or [] if course_ids else []
    course_map = {str(row["id"]): row for row in courses}
    assignment_ids = [str(row["id"]) for row in rows]
    lessons = (
        supabase.table("cohort_member_lesson_assignments")
        .select("course_assignment_id,lesson_id,status")
        .in_("course_assignment_id", assignment_ids)
        .eq("status", "active")
        .execute()
    ).data or [] if assignment_ids else []
    lessons_by_assignment = {}
    for lesson in lessons:
        lessons_by_assignment.setdefault(str(lesson["course_assignment_id"]), []).append(lesson["lesson_id"])
    return {"success": True, "assignments": [{**row, "course": course_map.get(str(row["course_id"])), "lesson_ids": lessons_by_assignment.get(str(row["id"]), [])} for row in rows]}


def _active_cohort_member(user: CurrentUser) -> tuple[dict, dict]:
    if user.account_type != "cohort" or not user.id:
        raise HTTPException(403, "This endpoint is only available to cohort learners.")
    account_result = (
        supabase.table("cohort_accounts")
        .select("id,cohort_id,organisation_id,status,first_name,last_name,username")
        .eq("id", str(user.id))
        .eq("status", "active")
        .limit(1)
        .execute()
    )
    if not account_result.data:
        raise HTTPException(403, "Cohort learner account is inactive.")
    account = account_result.data[0]
    cohort_result = (
        supabase.table("cohorts")
        .select("id,status,organisation_id")
        .eq("id", account["cohort_id"])
        .eq("organisation_id", account["organisation_id"])
        .limit(1)
        .execute()
    )
    if not cohort_result.data or cohort_result.data[0].get("status") not in {"draft", "upcoming", "active"}:
        raise HTTPException(403, "This cohort is closed.")
    organisation = (
        supabase.table("organisations")
        .select("id,is_active")
        .eq("id", account["organisation_id"])
        .limit(1)
        .execute()
    )
    if not organisation.data or not organisation.data[0].get("is_active"):
        raise HTTPException(403, "This organisation is inactive.")
    member_result = (
        supabase.table("cohort_members")
        .select("id,cohort_id,cohort_account_id,track_id,status")
        .eq("cohort_id", account["cohort_id"])
        .eq("cohort_account_id", account["id"])
        .eq("status", "active")
        .limit(1)
        .execute()
    )
    if not member_result.data:
        raise HTTPException(403, "Active cohort membership was not found.")
    return account, member_result.data[0]


@router.get("/api/cohort-learning/me/courses")
def my_cohort_courses(user: CurrentUser = Depends(get_current_user)):
    account, member = _active_cohort_member(user)
    rows = (
        supabase.table("cohort_member_course_assignments")
        .select("id,course_id,track_id,tutor_user_id,status,assigned_at")
        .eq("cohort_member_id", member["id"])
        .eq("status", "active")
        .order("assigned_at")
        .execute()
    ).data or []
    course_ids = list({str(row["course_id"]) for row in rows})
    courses = (
        supabase.table("learnora_courses")
        .select("id,title,slug,short_description,description,thumbnail_url,estimated_hours,level,status")
        .in_("id", course_ids)
        .eq("status", "published")
        .execute()
    ).data or [] if course_ids else []
    course_map = {str(row["id"]): row for row in courses}
    return {
        "success": True,
        "learner": {"id": account["id"], "first_name": account["first_name"], "last_name": account["last_name"], "username": account["username"], "cohort_id": account["cohort_id"], "track_id": member["track_id"]},
        "courses": [{**row, "course": course_map.get(str(row["course_id"]))} for row in rows if str(row["course_id"]) in course_map],
    }


@router.get("/api/cohort-learning/me/courses/{course_id}/lessons")
def my_cohort_course_lessons(course_id: str, user: CurrentUser = Depends(get_current_user)):
    _, member = _active_cohort_member(user)
    assignment_result = (
        supabase.table("cohort_member_course_assignments")
        .select("id,course_id,status")
        .eq("cohort_member_id", member["id"])
        .eq("course_id", course_id)
        .eq("status", "active")
        .limit(1)
        .execute()
    )
    if not assignment_result.data:
        raise HTTPException(403, "This course has not been assigned to you.")
    assignment = assignment_result.data[0]
    allowed = (
        supabase.table("cohort_member_lesson_assignments")
        .select("lesson_id")
        .eq("course_assignment_id", assignment["id"])
        .eq("status", "active")
        .execute()
    ).data or []
    lesson_ids = [str(row["lesson_id"]) for row in allowed]
    if not lesson_ids:
        return {"success": True, "lessons": []}
    lessons = (
        supabase.table("learnora_lessons")
        .select("id,module_id,title,slug,description,order_index,lesson_type,duration_minutes,is_preview,status")
        .in_("id", lesson_ids)
        .eq("status", "published")
        .order("order_index")
        .execute()
    ).data or []
    module_ids = list({str(row["module_id"]) for row in lessons})
    modules = (
        supabase.table("course_modules")
        .select("id,title,order_index,course_id")
        .in_("id", module_ids)
        .eq("course_id", course_id)
        .execute()
    ).data or [] if module_ids else []
    module_map = {str(row["id"]): row for row in modules}
    return {"success": True, "lessons": [{**row, "module": module_map.get(str(row["module_id"]))} for row in lessons if str(row["module_id"]) in module_map]}


@router.get("/api/cohort-learning/me/courses/{course_id}/lessons/{lesson_id}")
def my_cohort_lesson_content(course_id: str, lesson_id: str, user: CurrentUser = Depends(get_current_user)):
    _, member = _active_cohort_member(user)
    assignment_result = (
        supabase.table("cohort_member_course_assignments")
        .select("id")
        .eq("cohort_member_id", member["id"])
        .eq("course_id", course_id)
        .eq("status", "active")
        .limit(1)
        .execute()
    )
    if not assignment_result.data:
        raise HTTPException(403, "This course has not been assigned to you.")
    assignment_id = assignment_result.data[0]["id"]
    allowed = (
        supabase.table("cohort_member_lesson_assignments")
        .select("id")
        .eq("course_assignment_id", assignment_id)
        .eq("lesson_id", lesson_id)
        .eq("status", "active")
        .limit(1)
        .execute()
    )
    if not allowed.data:
        raise HTTPException(403, "This lesson has not been assigned to you.")
    lesson_result = (
        supabase.table("learnora_lessons")
        .select("id,module_id,title,slug,description,order_index,lesson_type,content,duration_minutes,is_preview,status")
        .eq("id", lesson_id)
        .eq("status", "published")
        .limit(1)
        .execute()
    )
    if not lesson_result.data:
        raise HTTPException(404, "Published lesson not found.")
    lesson = lesson_result.data[0]
    module = (
        supabase.table("course_modules")
        .select("id,course_id,title")
        .eq("id", lesson["module_id"])
        .eq("course_id", course_id)
        .limit(1)
        .execute()
    )
    if not module.data:
        raise HTTPException(403, "Lesson does not belong to the assigned course.")
    return {"success": True, "lesson": lesson, "module": module.data[0]}


class LessonProgressIn(BaseModel):
    progress_percent: int = Field(default=0, ge=0, le=100)
    completed: bool = False
    last_position_seconds: int = Field(default=0, ge=0)


def _active_course_assignment(user: CurrentUser, course_id: str) -> tuple[dict, dict]:
    account, member = _active_cohort_member(user)
    result = (
        supabase.table("cohort_member_course_assignments")
        .select("id,course_id,status")
        .eq("cohort_member_id", member["id"])
        .eq("course_id", course_id)
        .eq("status", "active")
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(403, "This course has not been assigned to you.")
    return account, result.data[0]


@router.get("/api/cohort-learning/me/courses/{course_id}/progress")
def my_cohort_course_progress(course_id: str, user: CurrentUser = Depends(get_current_user)):
    account, assignment = _active_course_assignment(user, course_id)
    rows = (
        supabase.table("cohort_account_lesson_progress")
        .select("lesson_id,progress_percent,completed,last_position_seconds,first_started_at,last_accessed_at,completed_at,updated_at")
        .eq("cohort_account_id", str(account["id"]))
        .eq("course_assignment_id", str(assignment["id"]))
        .order("updated_at", desc=True)
        .execute()
    ).data or []
    return {"success": True, "course_id": course_id, "progress": rows}


@router.put("/api/cohort-learning/me/courses/{course_id}/lessons/{lesson_id}/progress")
def update_my_cohort_lesson_progress(
    course_id: str,
    lesson_id: str,
    body: LessonProgressIn,
    user: CurrentUser = Depends(get_current_user),
):
    account, assignment = _active_course_assignment(user, course_id)
    member = _active_cohort_member(user)[1]
    allowed = (
        supabase.table("cohort_member_lesson_assignments")
        .select("id")
        .eq("course_assignment_id", str(assignment["id"]))
        .eq("lesson_id", lesson_id)
        .eq("status", "active")
        .limit(1)
        .execute()
    )
    if not allowed.data:
        raise HTTPException(403, "This lesson has not been assigned to you.")

    completed = bool(body.completed or body.progress_percent == 100)
    progress_percent = 100 if completed else body.progress_percent
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "cohort_account_id": str(account["id"]),
        "cohort_member_id": str(member["id"]),
        "cohort_id": str(account["cohort_id"]),
        "course_assignment_id": str(assignment["id"]),
        "lesson_id": lesson_id,
        "progress_percent": progress_percent,
        "completed": completed,
        "last_position_seconds": body.last_position_seconds,
        "last_accessed_at": now,
        "updated_at": now,
    }
    try:
        result = supabase.table("cohort_account_lesson_progress").upsert(
            payload, on_conflict="cohort_account_id,lesson_id"
        ).execute()
    except Exception:
        raise HTTPException(409, "Progress could not be saved. Please retry.")
    if not result.data:
        raise HTTPException(500, "Progress could not be saved.")
    return {"success": True, "progress": result.data[0]}


@router.get("/api/instructor/me/assignments")
def my_instructor_assignments(user: CurrentUser = Depends(get_current_user)):
    """Return only active cohort-course assignments explicitly assigned to this instructor."""
    if not user.id or user.account_type == "cohort":
        raise HTTPException(403, "This workspace is only available to organisation instructors.")

    membership_rows = (
        supabase.table("organisation_members")
        .select("organisation_id,role,status")
        .eq("user_id", str(user.id))
        .eq("status", "active")
        .execute()
    ).data or []
    instructor_org_ids = {
        str(row["organisation_id"])
        for row in membership_rows
        if row.get("role") == "instructor" and row.get("organisation_id")
    }
    if not instructor_org_ids:
        raise HTTPException(403, "You do not have an active instructor membership.")

    active_organisations = (
        supabase.table("organisations")
        .select("id,name,is_active")
        .in_("id", list(instructor_org_ids))
        .eq("is_active", True)
        .execute()
    ).data or []
    active_org_map = {
        str(row["id"]): row
        for row in active_organisations
        if row.get("is_active")
    }
    if not active_org_map:
        return {"success": True, "assignments": []}

    assigned_rows = (
        supabase.table("cohort_member_course_assignments")
        .select("id,cohort_member_id,cohort_id,track_id,course_id,status,assigned_at,updated_at")
        .eq("tutor_user_id", str(user.id))
        .eq("status", "active")
        .order("assigned_at", desc=True)
        .execute()
    ).data or []
    if not assigned_rows:
        return {"success": True, "assignments": []}

    cohort_ids = list({str(row["cohort_id"]) for row in assigned_rows if row.get("cohort_id")})
    cohorts = (
        supabase.table("cohorts")
        .select("id,name,organisation_id,status,start_date,end_date")
        .in_("id", cohort_ids)
        .execute()
    ).data or [] if cohort_ids else []
    cohort_map = {
        str(row["id"]): row
        for row in cohorts
        if str(row.get("organisation_id")) in active_org_map
        and row.get("status") in {"draft", "upcoming", "active"}
    }

    member_ids = list({
        str(row["cohort_member_id"])
        for row in assigned_rows
        if row.get("cohort_member_id") and str(row.get("cohort_id")) in cohort_map
    })
    members = (
        supabase.table("cohort_members")
        .select("id,cohort_id,cohort_account_id,user_id,status")
        .in_("id", member_ids)
        .eq("status", "active")
        .execute()
    ).data or [] if member_ids else []
    member_map = {
        str(row["id"]): row
        for row in members
        if str(row.get("cohort_id")) in cohort_map
    }

    account_ids = list({
        str(row["cohort_account_id"])
        for row in members
        if row.get("cohort_account_id")
    })
    accounts = (
        supabase.table("cohort_accounts")
        .select("id,first_name,last_name,username,status")
        .in_("id", account_ids)
        .eq("status", "active")
        .execute()
    ).data or [] if account_ids else []
    account_map = {str(row["id"]): row for row in accounts}

    legacy_user_ids = list({
        str(row["user_id"])
        for row in members
        if row.get("user_id") and not row.get("cohort_account_id")
    })
    legacy_users = (
        supabase.table("users")
        .select("id,name")
        .in_("id", legacy_user_ids)
        .execute()
    ).data or [] if legacy_user_ids else []
    legacy_user_map = {str(row["id"]): row for row in legacy_users}

    course_ids = list({str(row["course_id"]) for row in assigned_rows if row.get("course_id")})
    courses = (
        supabase.table("learnora_courses")
        .select("id,title,slug,status,estimated_hours")
        .in_("id", course_ids)
        .eq("status", "published")
        .execute()
    ).data or [] if course_ids else []
    course_map = {str(row["id"]): row for row in courses}

    assignment_ids = [
        str(row["id"])
        for row in assigned_rows
        if str(row.get("cohort_id")) in cohort_map
        and str(row.get("cohort_member_id")) in member_map
        and str(row.get("course_id")) in course_map
    ]
    lesson_rows = (
        supabase.table("cohort_member_lesson_assignments")
        .select("course_assignment_id,lesson_id")
        .in_("course_assignment_id", assignment_ids)
        .eq("status", "active")
        .execute()
    ).data or [] if assignment_ids else []
    lesson_counts = {}
    active_lessons_by_assignment = {}
    for lesson in lesson_rows:
        key = str(lesson["course_assignment_id"])
        lesson_id = str(lesson["lesson_id"])
        lesson_counts[key] = lesson_counts.get(key, 0) + 1
        active_lessons_by_assignment.setdefault(key, set()).add(lesson_id)

    active_lesson_ids = list({
        lesson_id
        for lesson_ids in active_lessons_by_assignment.values()
        for lesson_id in lesson_ids
    })
    progress_rows = (
        supabase.table("cohort_account_lesson_progress")
        .select("course_assignment_id,lesson_id,progress_percent,completed")
        .in_("course_assignment_id", assignment_ids)
        .in_("lesson_id", active_lesson_ids)
        .execute()
    ).data or [] if assignment_ids and active_lesson_ids else []
    lesson_details = (
        supabase.table("learnora_lessons")
        .select("id,title,order_index,duration_minutes")
        .in_("id", active_lesson_ids)
        .execute()
    ).data or [] if active_lesson_ids else []
    lesson_map = {str(row["id"]): row for row in lesson_details}

    progress_by_assignment = {}
    progress_detail_by_assignment = {}
    for progress in progress_rows:
        key = str(progress.get("course_assignment_id") or "")
        lesson_id = str(progress.get("lesson_id") or "")
        if lesson_id not in active_lessons_by_assignment.get(key, set()):
            continue
        progress_entry = progress_by_assignment.setdefault(
            key, {"completed": set(), "in_progress": set()}
        )
        percent = max(0, min(100, int(progress.get("progress_percent") or 0)))
        completed = bool(progress.get("completed"))
        if completed:
            progress_entry["completed"].add(lesson_id)
            progress_entry["in_progress"].discard(lesson_id)
        elif percent > 0 and lesson_id not in progress_entry["completed"]:
            progress_entry["in_progress"].add(lesson_id)
        details = progress_detail_by_assignment.setdefault(key, {})
        previous = details.get(lesson_id, {"progress_percent": 0, "completed": False})
        details[lesson_id] = {
            "progress_percent": max(percent, int(previous["progress_percent"])),
            "completed": completed or bool(previous["completed"]),
        }

    assignments = []
    for row in assigned_rows:
        cohort = cohort_map.get(str(row.get("cohort_id")))
        member = member_map.get(str(row.get("cohort_member_id")))
        course = course_map.get(str(row.get("course_id")))
        if not cohort or not member or not course:
            continue
        account = account_map.get(str(member.get("cohort_account_id"))) if member.get("cohort_account_id") else None
        legacy_user = legacy_user_map.get(str(member.get("user_id"))) if member.get("user_id") else None
        if member.get("cohort_account_id") and not account:
            continue
        if not account and not legacy_user:
            # Do not display stale assignments whose learner identity no longer exists.
            continue
        learner_name = (
            f"{account.get('first_name', '')} {account.get('last_name', '')}".strip()
            if account else str((legacy_user or {}).get("name") or "Learner")
        )
        assignments.append({
            "id": str(row["id"]),
            "assigned_at": row.get("assigned_at"),
            "updated_at": row.get("updated_at"),
            "cohort": {
                "id": str(cohort["id"]),
                "name": cohort.get("name") or "Cohort",
                "status": cohort.get("status"),
                "start_date": cohort.get("start_date"),
                "end_date": cohort.get("end_date"),
                "organisation_name": active_org_map[str(cohort["organisation_id"])].get("name"),
            },
            "learner": {
                "member_id": str(member["id"]),
                "name": learner_name,
                "username": account.get("username") if account else None,
            },
            "course": {
                "id": str(course["id"]),
                "title": course.get("title") or "Assigned course",
                "slug": course.get("slug"),
                "estimated_hours": course.get("estimated_hours"),
            },
            "assigned_lesson_count": lesson_counts.get(str(row["id"]), 0),
            "completed_lesson_count": len(progress_by_assignment.get(str(row["id"]), {}).get("completed", set())),
            "in_progress_lesson_count": len(progress_by_assignment.get(str(row["id"]), {}).get("in_progress", set())),
            "completion_percent": round(
                100 * len(progress_by_assignment.get(str(row["id"]), {}).get("completed", set()))
                / lesson_counts[str(row["id"])]
            ) if lesson_counts.get(str(row["id"]), 0) else 0,
            "lesson_progress": [
                {
                    "lesson_id": lesson_id,
                    "title": lesson_map.get(lesson_id, {}).get("title") or "Assigned lesson",
                    "order_index": lesson_map.get(lesson_id, {}).get("order_index"),
                    "duration_minutes": lesson_map.get(lesson_id, {}).get("duration_minutes"),
                    "progress_percent": int(progress_detail_by_assignment.get(str(row["id"]), {}).get(lesson_id, {}).get("progress_percent", 0)),
                    "completed": bool(progress_detail_by_assignment.get(str(row["id"]), {}).get(lesson_id, {}).get("completed", False)),
                    "status": "completed" if progress_detail_by_assignment.get(str(row["id"]), {}).get(lesson_id, {}).get("completed", False) else ("in_progress" if int(progress_detail_by_assignment.get(str(row["id"]), {}).get(lesson_id, {}).get("progress_percent", 0)) > 0 else "not_started"),
                }
                for lesson_id in sorted(
                    active_lessons_by_assignment.get(str(row["id"]), set()),
                    key=lambda lesson_id: (
                        lesson_map.get(lesson_id, {}).get("order_index") is None,
                        lesson_map.get(lesson_id, {}).get("order_index") or 0,
                        lesson_map.get(lesson_id, {}).get("title") or "",
                    ),
                )
            ],
        })
    return {"success": True, "assignments": assignments}
