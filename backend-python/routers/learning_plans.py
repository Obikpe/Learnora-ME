"""Optional personalised learning plans layered over published catalogue tracks.

The track remains the authoritative curriculum. A learner plan only schedules
and contextualises real published courses; it cannot create, remove or reorder
track curriculum.
"""
from datetime import datetime, timezone
import json
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .auth import CurrentUser, get_current_user, supabase
from services.ai_profiles import generate

router = APIRouter(prefix="/api/learner", tags=["Learner plans"])


class GeneratePlanIn(BaseModel):
    track_id: Optional[str] = Field(default=None, max_length=80)


def _assert_individual(user: CurrentUser):
    if (
        str(getattr(user, "role", "") or "").lower() != "normal"
        or str(getattr(user, "account_type", "") or "").lower() != "learner"
        or getattr(user, "organisation_id", None)
    ):
        raise HTTPException(403, "Personal learning plans are available to individual learner accounts.")


def _profile(user_id: str):
    rows = (
        supabase.table("learner_onboarding_profiles")
        .select("goal,experience_level,preferred_track,interests,weekly_time_minutes,onboarding_completed")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    ).data or []
    if not rows or not rows[0].get("onboarding_completed"):
        raise HTTPException(409, "Complete your learning preferences before generating a plan.")
    return rows[0]


def _catalogue(track_id: Optional[str], profile: dict):
    tracks = (
        supabase.table("learnora_learning_paths")
        .select("id,name,slug,description")
        .is_("owner_user_id", "null")
        .is_("organisation_id", "null")
        .eq("status", "published")
        .order("created_at", desc=True)
        .execute()
    ).data or []
    preferred = str(profile.get("preferred_track") or "").strip().lower()
    if track_id:
        try:
            UUID(str(track_id))
        except (ValueError, TypeError, AttributeError):
            raise HTTPException(404, "Published global track not found.") from None
    track = next((row for row in tracks if str(row.get("id")) == str(track_id)), None) if track_id else None
    if track_id and not track:
        raise HTTPException(404, "Published global track not found.")
    if not track and preferred:
        track = next((
            row for row in tracks
            if preferred in {str(row.get("name") or "").strip().lower(), str(row.get("slug") or "").strip().lower()}
            or preferred in str(row.get("name") or "").lower()
        ), None)

    links = []
    if track:
        links = (
            supabase.table("learnora_learning_path_courses")
            .select("course_id,order_index,required")
            .eq("path_id", str(track["id"]))
            .order("order_index")
            .execute()
        ).data or []
    course_ids = [str(row["course_id"]) for row in links if row.get("course_id")]
    if track and not course_ids:
        raise HTTPException(409, "The selected published track does not contain any courses.")
    if course_ids:
        courses = (
            supabase.table("learnora_courses")
            .select("id,title,slug,short_description,level,estimated_hours,status,ownership,organisation_id")
            .in_("id", course_ids)
            .eq("status", "published")
            .eq("ownership", "learnora")
            .is_("organisation_id", "null")
            .execute()
        ).data or []
        by_id = {str(row["id"]): row for row in courses}
        unavailable_required = [str(link["course_id"]) for link in links if link.get("required") is not False and str(link.get("course_id")) not in by_id]
        if unavailable_required:
            raise HTTPException(409, "A required course in this published track is not currently available. Contact Learnora support.")
        sequence = [
            {**by_id[str(link["course_id"])], "required": link.get("required") is not False, "order_index": link.get("order_index", 0)}
            for link in links if str(link.get("course_id")) in by_id
        ]
        if not sequence:
            raise HTTPException(409, "The selected track has no currently published global courses.")
        return track, sequence

    # A learner may still receive a useful plan before a matching public track
    # exists. These are standalone course suggestions, not a new curriculum.
    courses = (
        supabase.table("learnora_courses")
        .select("id,title,slug,short_description,level,estimated_hours,status,ownership,organisation_id")
        .eq("status", "published")
        .eq("ownership", "learnora")
        .is_("organisation_id", "null")
        .order("created_at", desc=True)
        .limit(100)
        .execute()
    ).data or []
    if not courses:
        raise HTTPException(409, "There are no published Learnora courses available for a plan yet.")
    return None, [{**course, "required": True, "order_index": index} for index, course in enumerate(courses[:8])]


def _schedule(courses: list[dict], weekly_minutes: int):
    capacity = max(15, int(weekly_minutes))
    week_rows = []
    current_tasks = []
    remaining = capacity
    week_number = 1

    for course in courses:
        hours = course.get("estimated_hours")
        total_minutes = max(60, int(float(hours) * 60)) if hours is not None else 180
        remaining_course = total_minutes
        while remaining_course > 0:
            allocation = min(remaining, remaining_course)
            current_tasks.append({
                "course_id": str(course["id"]),
                "course_title": course.get("title") or "Learnora course",
                "focus": "Study the published lessons, complete the available activities and save one practical takeaway.",
                "minutes": allocation,
                "required": bool(course.get("required", True)),
            })
            remaining -= allocation
            remaining_course -= allocation
            if remaining == 0:
                week_rows.append({"week": week_number, "minutes": capacity, "tasks": current_tasks})
                week_number += 1
                current_tasks = []
                remaining = capacity

    if current_tasks:
        week_rows.append({"week": week_number, "minutes": capacity - remaining, "tasks": current_tasks})
    return week_rows


@router.get("/learning-plan")
def get_learning_plan(user: CurrentUser = Depends(get_current_user)):
    _assert_individual(user)
    rows = (
        supabase.table("learner_learning_plans")
        .select("id,source_track_id,goal,weekly_time_minutes,plan_data,status,generated_by,created_at,updated_at")
        .eq("user_id", str(user.id))
        .eq("status", "active")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    ).data or []
    return {"success": True, "plan": rows[0] if rows else None}


@router.post("/learning-plan/generate", status_code=201)
async def generate_learning_plan(body: GeneratePlanIn, user: CurrentUser = Depends(get_current_user)):
    _assert_individual(user)
    profile = _profile(str(user.id))
    track, courses = _catalogue(body.track_id, profile)
    weekly_minutes = int(profile.get("weekly_time_minutes") or 180)
    weeks = _schedule(courses, weekly_minutes)
    if not weeks:
        raise HTTPException(409, "A learning schedule could not be created from the published catalogue.")

    course_summary = [
        {
            "id": str(course["id"]),
            "title": course.get("title"),
            "level": course.get("level"),
            "estimated_hours": course.get("estimated_hours"),
            "required": bool(course.get("required", True)),
        }
        for course in courses
    ]
    weekly_outline = [
        {
            "week": week["week"],
            "minutes": week["minutes"],
            "courses": [
                {"course_id": task["course_id"], "course_title": task["course_title"], "minutes": task["minutes"]}
                for task in week["tasks"]
            ],
        }
        for week in weeks
    ]
    prompt = (
        "Create a personalised weekly learning plan as strict JSON only. "
        "Use this exact shape: {\"overview\": string, \"weekly_guidance\": "
        "[{\"week\": integer, \"focus\": string, \"practice\": string, "
        "\"reflection\": string}]}. Return exactly one guidance item for "
        "each supplied week, in order. Only refer to the supplied real courses "
        "and their titles. Do not add, remove, rename or reorder courses, invent "
        "lessons, claim the learner completed anything, or alter the supplied "
        "time allocations. Keep each field concise and actionable.\n"
        f"Learner goal: {profile.get('goal')}\n"
        f"Experience level: {profile.get('experience_level')}\n"
        f"Interests: {', '.join(profile.get('interests') or [])}\n"
        f"Weekly time: {weekly_minutes} minutes\n"
        f"Published track: {track.get('name') if track else 'Flexible course plan'}\n"
        f"Fixed catalogue schedule: {json.dumps(weekly_outline, ensure_ascii=False)}"
    )
    guidance = "Work through the scheduled courses in order, practise each concept, and record one practical outcome from every study session."
    generation_mode = "rule_based_fallback"
    try:
        ai_result = await generate(str(user.id), "coach", prompt, None, None)
        raw = str(ai_result.get("content") or "").strip()
        if ai_result.get("provider") not in (None, "rules") and ai_result.get("status") == "success":
            json_start, json_end = raw.find("{"), raw.rfind("}")
            if json_start >= 0 and json_end > json_start:
                parsed = json.loads(raw[json_start:json_end + 1])
                weekly_guidance = parsed.get("weekly_guidance")
                if isinstance(weekly_guidance, list) and len(weekly_guidance) == len(weeks):
                    validated = {}
                    for expected_week, item in zip(weeks, weekly_guidance):
                        if not isinstance(item, dict) or int(item.get("week", -1)) != int(expected_week["week"]):
                            raise ValueError("AI plan week sequence did not match the saved schedule.")
                        fields = {}
                        for key in ("focus", "practice", "reflection"):
                            value = str(item.get(key) or "").strip()
                            if not value:
                                raise ValueError("AI plan guidance was incomplete.")
                            fields[key] = value[:1200]
                        validated[int(expected_week["week"])] = fields
                    for week in weeks:
                        week["guidance"] = validated[int(week["week"])]
                    overview = str(parsed.get("overview") or "").strip()
                    if overview:
                        guidance = overview[:5000]
                    generation_mode = "ai_assisted"
    except Exception as exc:
        print(f"Learning plan guidance generation failed: {type(exc).__name__}")
    if generation_mode != "ai_assisted":
        for week in weeks:
            week["guidance"] = {
                "focus": "Work through the published lessons for the scheduled course or courses.",
                "practice": "Attempt the available practice and assessment activities, then review any feedback.",
                "reflection": "Write down one concept you can now explain or apply and one question to revisit.",
            }

    plan_data = {
        "track": ({"id": str(track["id"]), "name": track.get("name"), "slug": track.get("slug")} if track else None),
        "weeks": weeks,
        "course_sequence": course_summary,
        "ai_guidance": guidance,
        "generation_mode": generation_mode,
        "experience_level": profile.get("experience_level"),
        "interests": profile.get("interests") or [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "curriculum_policy": "The published Learnora track/course catalogue is authoritative. This plan only schedules existing content.",
    }
    saved = supabase.table("learner_learning_plans").insert({
        "user_id": str(user.id),
        "source_track_id": str(track["id"]) if track else None,
        "goal": str(profile.get("goal") or "").strip(),
        "weekly_time_minutes": weekly_minutes,
        "plan_data": plan_data,
        "status": "active",
        "generated_by": "learnora-ai" if generation_mode == "ai_assisted" else "learnora-fallback",
    }).execute()
    if not saved.data:
        raise HTTPException(500, "The learning plan could not be saved.")
    new_plan_id = str(saved.data[0]["id"])
    supabase.table("learner_learning_plans").update({
        "status": "archived",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("user_id", str(user.id)).eq("status", "active").neq("id", new_plan_id).execute()
    return {"success": True, "plan": saved.data[0]}


@router.post("/learning-plan/{plan_id}/archive")
def archive_learning_plan(plan_id: str, user: CurrentUser = Depends(get_current_user)):
    _assert_individual(user)
    updated = supabase.table("learner_learning_plans").update({
        "status": "archived",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", plan_id).eq("user_id", str(user.id)).eq("status", "active").execute()
    if not updated.data:
        raise HTTPException(404, "Active learning plan not found.")
    return {"success": True}
