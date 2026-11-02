"""Platform-managed global tracks built on the canonical learning-path tables.

Global tracks are learning paths with both owner_user_id and organisation_id
NULL. Personal and organisation learning paths remain isolated.
"""
import re
from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .auth import supabase
from .internal_auth import InternalStaffContext, require_internal_permission

router = APIRouter(prefix="/api/internal/tracks", tags=["Internal Tracks"])


class TrackCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    slug: str = Field(..., min_length=2, max_length=140)
    description: Optional[str] = Field(None, max_length=5000)


class TrackWrite(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=120)
    slug: Optional[str] = Field(None, min_length=2, max_length=140)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[Literal["draft", "published", "archived"]] = None


class TrackCourseIn(BaseModel):
    course_id: str
    required: bool = True
    order_index: Optional[int] = Field(None, ge=0)


class TrackCourseOrder(BaseModel):
    id: str
    order_index: int = Field(..., ge=0)


def _uuid(value: str, label: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=404, detail=f"{label} not found.") from None


def _global_track(track_id: str) -> dict:
    track_id = _uuid(track_id, "Track")
    result = (
        supabase.table("learnora_learning_paths")
        .select("id,owner_user_id,organisation_id,name,slug,description,status,created_by,created_at,updated_at")
        .eq("id", track_id)
        .is_("owner_user_id", "null")
        .is_("organisation_id", "null")
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Global Learnora track not found.")
    return result.data[0]


def _track_courses(track_id: str) -> list[dict]:
    return (
        supabase.table("learnora_learning_path_courses")
        .select("id,path_id,course_id,order_index,required")
        .eq("path_id", track_id)
        .order("order_index")
        .execute()
    ).data or []


def _course_map(course_ids: list[str]) -> dict:
    if not course_ids:
        return {}
    rows = (
        supabase.table("learnora_courses")
        .select("id,title,slug,short_description,description,level,status,ownership,organisation_id,thumbnail_url,estimated_hours")
        .in_("id", course_ids)
        .execute()
    ).data or []
    return {str(row["id"]): row for row in rows}


def _track_curriculum_locked(track_id: str) -> bool:
    course_ids = list({
        str(row["course_id"])
        for row in _track_courses(track_id)
        if row.get("course_id")
    })
    if not course_ids:
        return False
    enrolments = (
        supabase.table("learnora_enrolments")
        .select("id")
        .in_("course_id", course_ids)
        .eq("source_type", f"track_enrolment:{track_id}")
        .in_("status", ["active", "completed"])
        .limit(1)
        .execute()
    ).data or []
    return bool(enrolments)


def _track_payload(track: dict, links: list[dict]) -> dict:
    course_map = _course_map([str(row["course_id"]) for row in links if row.get("course_id")])
    courses = []
    for link in links:
        course = course_map.get(str(link.get("course_id")))
        courses.append({**link, "course": course})
    return {**track, "courses": courses, "course_count": len(courses), "curriculum_locked": _track_curriculum_locked(str(track["id"]))}


def _assert_track_curriculum_editable(track_id: str):
    links = _track_courses(track_id)
    course_ids = list({str(row["course_id"]) for row in links if row.get("course_id")})
    if not course_ids:
        return
    enrolments = (
        supabase.table("learnora_enrolments")
        .select("id")
        .in_("course_id", course_ids)
        .eq("source_type", f"track_enrolment:{track_id}")
        .in_("status", ["active", "completed"])
        .limit(1)
        .execute()
    ).data or []
    if enrolments:
        raise HTTPException(
            status_code=409,
            detail="This track has learner course enrolments. Its curriculum is frozen to preserve learner progress; create a new track for a different course sequence.",
        )


def _normalise_slug(value: str) -> str:
    slug = value.strip().lower()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise HTTPException(status_code=422, detail="Use lowercase letters, numbers and single hyphens in the track slug.")
    return slug


def _ensure_unique_slug(slug: str, exclude_id: Optional[str] = None):
    query = (
        supabase.table("learnora_learning_paths")
        .select("id")
        .eq("slug", slug)
        .is_("owner_user_id", "null")
        .is_("organisation_id", "null")
    )
    if exclude_id:
        query = query.neq("id", exclude_id)
    if query.limit(1).execute().data:
        raise HTTPException(status_code=409, detail="A global track with this slug already exists.")


def _assert_publishable(track_id: str):
    links = _track_courses(track_id)
    if not links:
        raise HTTPException(status_code=409, detail="Add at least one course before publishing this track.")
    if not any(row.get("required") is not False for row in links):
        raise HTTPException(status_code=409, detail="A published track must contain at least one required course.")
    course_map = _course_map([str(row["course_id"]) for row in links if row.get("course_id")])
    for link in links:
        course = course_map.get(str(link.get("course_id")))
        if (
            not course
            or course.get("status") != "published"
            or course.get("ownership") != "learnora"
            or course.get("organisation_id") is not None
        ):
            raise HTTPException(status_code=409, detail="Every track course must be a published, global Learnora-owned course before the track can be published.")
        modules = (
            supabase.table("course_modules")
            .select("id,order_index")
            .eq("course_id", str(course["id"]))
            .eq("status", "published")
            .order("order_index")
            .execute()
        ).data or []
        module_ids = [str(row["id"]) for row in modules if row.get("id")]
        if not module_ids:
            raise HTTPException(status_code=409, detail="Every track course must contain at least one published module.")
        lessons = (
            supabase.table("learnora_lessons")
            .select("id")
            .in_("module_id", module_ids)
            .eq("status", "published")
            .limit(1)
            .execute()
        ).data or []
        if not lessons:
            raise HTTPException(status_code=409, detail="Every track course must contain at least one published lesson.")
        ordered_modules = sorted(modules, key=lambda row: int(row.get("order_index") or 0))
        for previous_module in ordered_modules[:-1]:
            quizzes = (
                supabase.table("quizzes")
                .select("id")
                .eq("module_id", str(previous_module["id"]))
                .eq("is_published", True)
                .execute()
            ).data or []
            if not quizzes:
                raise HTTPException(status_code=409, detail="Every published module before the final module must have a published assessment so learners can unlock the next module.")
            for quiz in quizzes:
                questions = (
                    supabase.table("quiz_questions")
                    .select("id,question_type,options,correct_answer")
                    .eq("quiz_id", str(quiz["id"]))
                    .execute()
                ).data or []
                if not questions or any(
                    question.get("correct_answer") is None
                    or (str(question.get("question_type")) not in {"true_false", "boolean"} and not question.get("options"))
                    or str(question.get("question_type")) not in {"multiple_choice", "single_choice", "mcq", "true_false", "boolean"}
                    for question in questions
                ):
                    raise HTTPException(status_code=409, detail="Every published module assessment must contain supported, answerable questions before the track can be published.")


@router.get("")
def list_tracks(staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    tracks = (
        supabase.table("learnora_learning_paths")
        .select("id,name,slug,description,status,created_at,updated_at")
        .is_("owner_user_id", "null")
        .is_("organisation_id", "null")
        .order("created_at", desc=True)
        .execute()
    ).data or []
    track_ids = [str(row["id"]) for row in tracks if row.get("id")]
    links = []
    if track_ids:
        links = (
            supabase.table("learnora_learning_path_courses")
            .select("id,path_id,course_id,order_index,required")
            .in_("path_id", track_ids)
            .order("order_index")
            .execute()
        ).data or []
    counts = {}
    for link in links:
        key = str(link.get("path_id"))
        counts[key] = counts.get(key, 0) + 1
    return {
        "success": True,
        "tracks": [
            {**track, "course_count": counts.get(str(track.get("id")), 0)}
            for track in tracks
        ],
    }


@router.post("")
def create_track(
    payload: TrackCreate,
    staff: InternalStaffContext = Depends(require_internal_permission("content.manage")),
):
    slug = _normalise_slug(payload.slug)
    _ensure_unique_slug(slug)
    supabase.table("learnora_learning_paths").insert({
        "owner_user_id": None,
        "organisation_id": None,
        "name": payload.name.strip(),
        "slug": slug,
        "description": payload.description.strip() if payload.description else None,
        "status": "draft",
        "created_by": staff.user_id,
    }).execute()
    created = (
        supabase.table("learnora_learning_paths")
        .select("id,name,slug,description,status,created_at,updated_at")
        .eq("slug", slug)
        .is_("owner_user_id", "null")
        .is_("organisation_id", "null")
        .limit(1)
        .execute()
    )
    if not created.data:
        raise HTTPException(status_code=500, detail="Track creation could not be confirmed.")
    return {"success": True, "track": created.data[0]}


@router.get("/{track_id}")
def get_track(
    track_id: str,
    staff: InternalStaffContext = Depends(require_internal_permission("courses.view")),
):
    track = _global_track(track_id)
    return {"success": True, "track": _track_payload(track, _track_courses(str(track["id"])))}


@router.patch("/{track_id}")
def update_track(
    track_id: str,
    payload: TrackWrite,
    staff: InternalStaffContext = Depends(require_internal_permission("content.manage")),
):
    track = _global_track(track_id)
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No track changes supplied.")
    for required_field in ("name", "slug", "status"):
        if required_field in data and data[required_field] is None:
            raise HTTPException(status_code=422, detail=f"{required_field} cannot be null.")
    if "name" in data and data["name"] is not None:
        data["name"] = data["name"].strip()
        if len(data["name"]) < 2:
            raise HTTPException(status_code=422, detail="Track name must contain at least two characters.")
    if "slug" in data and data["slug"] is not None:
        data["slug"] = _normalise_slug(data["slug"])
        _ensure_unique_slug(data["slug"], str(track["id"]))
    if "description" in data and data["description"] is not None:
        data["description"] = data["description"].strip() or None
    if data.get("status") == "published":
        _assert_publishable(str(track["id"]))
    (
        supabase.table("learnora_learning_paths")
        .update(data)
        .eq("id", str(track["id"]))
        .is_("owner_user_id", "null")
        .is_("organisation_id", "null")
        .execute()
    )
    return {"success": True, "track": _global_track(str(track["id"]))}


@router.post("/{track_id}/courses")
def add_track_course(
    track_id: str,
    payload: TrackCourseIn,
    staff: InternalStaffContext = Depends(require_internal_permission("content.manage")),
):
    track = _global_track(track_id)
    if track.get("status") == "archived":
        raise HTTPException(status_code=409, detail="Archived tracks cannot be edited.")
    if track.get("status") == "published":
        raise HTTPException(status_code=409, detail="Unpublish the track before changing its course list.")
    _assert_track_curriculum_editable(str(track["id"]))
    course_id = _uuid(payload.course_id, "Course")
    course_result = (
        supabase.table("learnora_courses")
        .select("id,status,ownership,organisation_id")
        .eq("id", course_id)
        .limit(1)
        .execute()
    )
    if not course_result.data:
        raise HTTPException(status_code=404, detail="Course not found.")
    course = course_result.data[0]
    if course.get("ownership") != "learnora" or course.get("organisation_id") is not None:
        raise HTTPException(status_code=403, detail="Only global Learnora-owned courses can be added to a public track.")

    links = _track_courses(str(track["id"]))
    existing = next((row for row in links if str(row.get("course_id")) == course_id), None)
    order_index = payload.order_index
    if order_index is None:
        order_index = max((int(row.get("order_index") or 0) for row in links), default=-1) + 1
    collision = next((
        row for row in links
        if int(row.get("order_index") or 0) == order_index
        and str(row.get("course_id")) != course_id
    ), None)
    if collision:
        raise HTTPException(status_code=409, detail="That course order is already occupied. Choose another position.")

    values = {
        "path_id": str(track["id"]),
        "course_id": course_id,
        "order_index": order_index,
        "required": payload.required,
    }
    if existing:
        (
            supabase.table("learnora_learning_path_courses")
            .update({"order_index": order_index, "required": payload.required})
            .eq("id", existing["id"])
            .execute()
        )
    else:
        supabase.table("learnora_learning_path_courses").insert(values).execute()
    saved = (
        supabase.table("learnora_learning_path_courses")
        .select("id,path_id,course_id,order_index,required")
        .eq("path_id", str(track["id"]))
        .eq("course_id", course_id)
        .limit(1)
        .execute()
    )
    if not saved.data:
        raise HTTPException(status_code=500, detail="Track course save could not be confirmed.")
    return {"success": True, "course_link": saved.data[0]}


@router.patch("/{track_id}/courses/reorder")
def reorder_track_courses(
    track_id: str,
    items: list[TrackCourseOrder],
    staff: InternalStaffContext = Depends(require_internal_permission("content.manage")),
):
    track = _global_track(track_id)
    if track.get("status") == "archived":
        raise HTTPException(status_code=409, detail="Archived tracks cannot be edited.")
    if track.get("status") == "published":
        raise HTTPException(status_code=409, detail="Unpublish the track before changing course order.")
    _assert_track_curriculum_editable(str(track["id"]))
    current = _track_courses(str(track["id"]))
    current_by_id = {str(row["id"]): row for row in current}
    submitted_ids = [str(item.id) for item in items]
    if (
        len(submitted_ids) != len(set(submitted_ids))
        or set(submitted_ids) != set(current_by_id)
        or len(items) != len(current)
    ):
        raise HTTPException(status_code=409, detail="Reorder must include every current track course exactly once.")
    if len({item.order_index for item in items}) != len(items):
        raise HTTPException(status_code=422, detail="Course order positions must be unique.")
    if {item.order_index for item in items} != set(range(len(items))):
        raise HTTPException(status_code=422, detail="Course order positions must be contiguous starting at zero.")

    old_positions = {key: int(row.get("order_index") or 0) for key, row in current_by_id.items()}
    temp_start = max(old_positions.values(), default=0) + len(items) + 100
    try:
        for index, item in enumerate(items):
            supabase.table("learnora_learning_path_courses").update(
                {"order_index": temp_start + index}
            ).eq("id", item.id).eq("path_id", str(track["id"])).execute()
        for item in items:
            (
                supabase.table("learnora_learning_path_courses")
                .update({"order_index": item.order_index})
                .eq("id", item.id)
                .eq("path_id", str(track["id"]))
                .execute()
            )
            # The PostgREST update can return an empty representation on a
            # successful write; execute() raising is the failure signal.
    except Exception as exc:
        # Best-effort compensation first moves every row out of the target
        # positions, then restores the previous unique positions.
        for index, link_id in enumerate(old_positions):
            try:
                supabase.table("learnora_learning_path_courses").update(
                    {"order_index": temp_start + len(items) + index}
                ).eq("id", link_id).eq("path_id", str(track["id"])).execute()
            except Exception:
                pass
        for link_id, old_index in old_positions.items():
            try:
                supabase.table("learnora_learning_path_courses").update(
                    {"order_index": old_index}
                ).eq("id", link_id).eq("path_id", str(track["id"])).execute()
            except Exception:
                pass
        raise HTTPException(status_code=500, detail="Track course reorder failed; original order restoration was attempted.") from exc

    return {"success": True, "courses": _track_courses(str(track["id"]))}


@router.delete("/{track_id}/courses/{course_id}")
def remove_track_course(
    track_id: str,
    course_id: str,
    staff: InternalStaffContext = Depends(require_internal_permission("content.manage")),
):
    track = _global_track(track_id)
    if track.get("status") == "archived":
        raise HTTPException(status_code=409, detail="Archived tracks cannot be edited.")
    if track.get("status") == "published":
        raise HTTPException(status_code=409, detail="Unpublish the track before removing a course.")
    _assert_track_curriculum_editable(str(track["id"]))
    course_id = _uuid(course_id, "Course")
    existing = (
        supabase.table("learnora_learning_path_courses")
        .select("id,path_id,course_id,order_index,required")
        .eq("path_id", str(track["id"]))
        .eq("course_id", course_id)
        .limit(1)
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Track course link not found.")
    (
        supabase.table("learnora_learning_path_courses")
        .delete()
        .eq("id", existing.data[0]["id"])
        .execute()
    )
    return {"success": True, "removed": existing.data[0]}
