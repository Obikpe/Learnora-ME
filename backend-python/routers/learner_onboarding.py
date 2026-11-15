"""Learner onboarding profile and course recommendations."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from .auth import CurrentUser, get_current_user, supabase
from .public_directory import _is_public_course, _public_course_payload
from services.free_access import is_individual_learner

router = APIRouter(prefix="/api/learner", tags=["Learner onboarding"])

class OnboardingIn(BaseModel):
    goal: str = Field(..., min_length=3, max_length=1000)
    experience_level: str = Field(..., pattern="^(beginner|some_experience|experienced|career_changer)$")
    preferred_track: str = Field(..., min_length=2, max_length=120)
    interests: list[str] = Field(default_factory=list, max_length=12)
    weekly_time_minutes: int = Field(default=180, ge=15, le=3000)

def _assert_individual(user: CurrentUser):
    if not is_individual_learner(user.role, user.account_type, getattr(user, "organisation_id", None)):
        raise HTTPException(403, "Personal learning preferences are only available to individual learner accounts.")

def _profile(user_id):
    result = supabase.table("learner_onboarding_profiles").select("*").eq("user_id", user_id).limit(1).execute()
    return result.data[0] if result.data else None

@router.get("/onboarding")
def get_onboarding(user: CurrentUser = Depends(get_current_user)):
    _assert_individual(user)
    profile = _profile(str(user.id))
    return {"success": True, "profile": profile, "completed": bool(profile and profile.get("onboarding_completed"))}

@router.put("/onboarding")
def save_onboarding(body: OnboardingIn, user: CurrentUser = Depends(get_current_user)):
    _assert_individual(user)
    now = datetime.now(timezone.utc).isoformat()
    existing_profile = _profile(str(user.id))
    first_completion = not bool((existing_profile or {}).get("onboarding_completed"))
    completed_at = (existing_profile or {}).get("onboarding_completed_at") or now
    result = supabase.table("learner_onboarding_profiles").upsert({
        "user_id": str(user.id),
        "goal": body.goal.strip(),
        "experience_level": body.experience_level,
        "preferred_track": body.preferred_track.strip(),
        "interests": [x.strip() for x in body.interests if x.strip()][:12],
        "weekly_time_minutes": body.weekly_time_minutes,
        "onboarding_completed": True,
        "onboarding_completed_at": completed_at,
        "updated_at": now,
    }, on_conflict="user_id").execute()
    if not result.data:
        raise HTTPException(500, "Unable to save your learning preferences.")
    # The welcome is a one-time onboarding event. Delivery is idempotent and
    # best-effort so an email-provider outage cannot undo a completed setup.
    if first_completion:
        try:
            from services.notification_service import send_post_setup_welcome
            send_post_setup_welcome(str(user.id))
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Post-setup welcome delivery could not be started")
    return {"success": True, "profile": result.data[0]}

@router.get("/recommendations")
def recommendations(user: CurrentUser = Depends(get_current_user)):
    _assert_individual(user)
    profile = _profile(str(user.id))
    enrolments = supabase.table("learnora_enrolments").select("course_id,status").eq("user_id", str(user.id)).in_("status", ["active","completed"]).execute().data or []
    enrolled_ids = {str(x.get("course_id")) for x in enrolments}
    course_rows = (
        supabase.table("learnora_courses")
        .select("id,organisation_id,creator_id,title,slug,short_description,description,level,status,ownership,thumbnail_url,estimated_hours,settings")
        .eq("status", "published")
        .limit(500)
        .execute()
    ).data or []
    organisation_ids = list({str(row["organisation_id"]) for row in course_rows if row.get("organisation_id")})
    creator_ids = list({str(row["creator_id"]) for row in course_rows if row.get("creator_id")})
    organisation_map = {}
    creator_map = {}
    if organisation_ids:
        organisations = (
            supabase.table("organisations")
            .select("id,is_active,settings")
            .in_("id", organisation_ids)
            .execute()
        ).data or []
        organisation_map = {str(row["id"]): row for row in organisations}
    if creator_ids:
        creators = (
            supabase.table("learnora_creator_accounts")
            .select("id,status")
            .in_("id", creator_ids)
            .execute()
        ).data or []
        creator_map = {str(row["id"]): row for row in creators}
    courses = [
        _public_course_payload(row)
        for row in course_rows
        if _is_public_course(row, organisation_map, creator_map)
    ]
    interests = [x.lower() for x in (profile or {}).get("interests", [])]
    track = ((profile or {}).get("preferred_track") or "").lower()
    goal = ((profile or {}).get("goal") or "").lower()
    level = (profile or {}).get("experience_level") or "beginner"
    ranked = []
    for course in courses:
        cid = str(course.get("id"))
        if cid in enrolled_ids:
            continue
        text = " ".join(str(course.get(k) or "") for k in ("title","short_description","description","level")).lower()
        score = sum(3 for item in interests if item and item in text)
        score += 4 if track and track in text else 0
        score += 2 if goal and any(word in text for word in goal.split() if len(word) > 4) else 0
        score += 1 if str(course.get("level") or "").lower() in {level, "mixed"} else 0
        ranked.append((score, course))
    ranked.sort(key=lambda x: (x[0], str(x[1].get("title") or "").lower()), reverse=True)
    return {
        "success": True,
        "onboarding_required": not bool(profile and profile.get("onboarding_completed")),
        "recommended": [{"course": c, "reason": "Matched to your goals and learning interests." if score else "A course to explore next.", "score": score} for score,c in ranked[:6]],
        "other_courses": [{"course": c} for _,c in ranked[6:18]],
        "tracks": sorted({str(c.get("level")) for _,c in ranked if c.get("level")}),
    }
