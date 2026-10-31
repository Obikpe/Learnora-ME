"""Public, deliberately minimal discovery endpoints for Learnora.

Only approved creator accounts are listed. Organisations must explicitly opt
in through settings.public_directory=true; active status alone is not consent
to be discoverable.
"""
from fastapi import APIRouter, HTTPException
from urllib.parse import urlparse
from uuid import UUID

from .auth import supabase
from services.free_access import free_access_mode_enabled

router = APIRouter(prefix="/api/public", tags=["Public discovery"])


def _is_public_course(course: dict, organisation_map: dict, creator_map: dict) -> bool:
    if course.get("status") != "published":
        return False
    settings = course.get("settings") or {}
    ownership = course.get("ownership")
    if ownership == "learnora":
        return course.get("organisation_id") is None
    if ownership == "creator":
        creator = creator_map.get(str(course.get("creator_id")))
        return bool(creator and creator.get("status") in {"approved", "active"})
    if ownership == "organisation":
        if settings.get("public_catalogue") is not True:
            return False
        organisation = organisation_map.get(str(course.get("organisation_id")))
        org_settings = (organisation or {}).get("settings") or {}
        return bool(organisation and organisation.get("is_active") and org_settings.get("public_directory") is True)
    return False


def _public_course_payload(course: dict) -> dict:
    settings = course.get("settings") or {}
    topics = settings.get("topics") if isinstance(settings.get("topics"), list) else []
    is_free = ((free_access_mode_enabled() and course.get("ownership") == "learnora" and not course.get("organisation_id")) or settings.get("is_free") is True or settings.get("access_type") == "free" or settings.get("price") == 0)
    return {
        "id": course.get("id"),
        "organisation_id": course.get("organisation_id"),
        "creator_id": course.get("creator_id"),
        "title": course.get("title"),
        "slug": course.get("slug"),
        "short_description": course.get("short_description"),
        "description": course.get("description"),
        "level": course.get("level"),
        "status": course.get("status"),
        "ownership": course.get("ownership"),
        "thumbnail_url": course.get("thumbnail_url"),
        "estimated_hours": course.get("estimated_hours"),
        "created_at": course.get("created_at"),
        "settings": {
            "public_catalogue": True,
            "is_free": bool(is_free),
            "access_type": "free" if is_free else "restricted",
            "track": str(settings.get("track") or "").strip() or None,
            "topics": [topic.strip()[:100] for topic in topics if isinstance(topic, str) and topic.strip()][:20],
        },
    }


def _public_course_lookup(course_id: str) -> dict:
    # Course primary keys are UUIDs. Legacy local identifiers such as "ws_03"
    # are not database IDs and should return a clean 404, not a Postgres 500.
    try:
        UUID(course_id)
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(404, "Course not found.") from None

    result = (
        supabase.table("learnora_courses")
        .select("id,organisation_id,creator_id,title,slug,short_description,description,level,status,ownership,thumbnail_url,estimated_hours,settings,created_at")
        .eq("id", course_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Course not found.")
    course = result.data[0]
    organisation_map = {}
    creator_map = {}
    if course.get("organisation_id"):
        org_result = supabase.table("organisations").select("id,is_active,settings").eq("id", course["organisation_id"]).limit(1).execute()
        if org_result.data:
            organisation_map[str(course["organisation_id"])] = org_result.data[0]
    if course.get("creator_id"):
        creator_result = supabase.table("learnora_creator_accounts").select("id,status").eq("id", course["creator_id"]).limit(1).execute()
        if creator_result.data:
            creator_map[str(course["creator_id"])] = creator_result.data[0]
    if not _is_public_course(course, organisation_map, creator_map):
        raise HTTPException(404, "Course not found.")
    return course




def _global_track_lookup(track_id: str) -> dict:
    try:
        track_id = str(UUID(track_id))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(404, "Track not found.") from None
    result = (
        supabase.table("learnora_learning_paths")
        .select("id,name,slug,description,status,owner_user_id,organisation_id,created_at,updated_at")
        .eq("id", track_id)
        .is_("owner_user_id", "null")
        .is_("organisation_id", "null")
        .eq("status", "published")
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Track not found.")
    return result.data[0]


def _public_track_payload_from_rows(track: dict, links: list[dict], course_map: dict) -> dict:
    courses = []
    for link in links:
        course = course_map.get(str(link.get("course_id")))
        if course:
            courses.append({**link, "course": course})
        elif link.get("required") is True:
            # A published track is hidden if a required course is no longer
            # a published global Learnora course.
            raise HTTPException(404, "Track not found.")
    if not courses:
        raise HTTPException(404, "Track not found.")
    required_courses = [row["course"] for row in courses if row.get("required") is not False]
    required_count = len(required_courses)
    if required_count == 0:
        raise HTTPException(404, "Track not found.")
    self_enrol_available = all(
        free_access_mode_enabled()
        or (course.get("settings") or {}).get("is_free") is True
        or (course.get("settings") or {}).get("access_type") == "free"
        or (course.get("settings") or {}).get("price") == 0
        for course in required_courses
    )
    return {
        "id": track.get("id"),
        "name": track.get("name"),
        "slug": track.get("slug"),
        "description": track.get("description"),
        "status": track.get("status"),
        "created_at": track.get("created_at"),
        "courses": courses,
        "course_count": len(courses),
        "required_course_count": required_count,
        "self_enrol_available": self_enrol_available,
    }


def _public_track_payload(track: dict) -> dict:
    links = (
        supabase.table("learnora_learning_path_courses")
        .select("id,course_id,order_index,required")
        .eq("path_id", str(track["id"]))
        .order("order_index")
        .execute()
    ).data or []
    course_ids = list({str(row["course_id"]) for row in links if row.get("course_id")})
    course_map = {}
    if course_ids:
        rows = (
            supabase.table("learnora_courses")
            .select("id,title,slug,short_description,level,status,ownership,organisation_id,thumbnail_url,estimated_hours,settings")
            .in_("id", course_ids)
            .eq("status", "published")
            .eq("ownership", "learnora")
            .is_("organisation_id", "null")
            .execute()
        ).data or []
        course_map = {str(row["id"]): row for row in rows}
    return _public_track_payload_from_rows(track, links, course_map)


@router.get("/tracks")
def public_tracks():
    tracks = (
        supabase.table("learnora_learning_paths")
        .select("id,name,slug,description,status,owner_user_id,organisation_id,created_at")
        .is_("owner_user_id", "null")
        .is_("organisation_id", "null")
        .eq("status", "published")
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
    course_ids = list({str(row["course_id"]) for row in links if row.get("course_id")})
    course_map = {}
    if course_ids:
        rows = (
            supabase.table("learnora_courses")
            .select("id,title,slug,short_description,level,status,ownership,organisation_id,thumbnail_url,estimated_hours,settings")
            .in_("id", course_ids)
            .eq("status", "published")
            .eq("ownership", "learnora")
            .is_("organisation_id", "null")
            .execute()
        ).data or []
        course_map = {str(row["id"]): row for row in rows}
    links_by_track = {}
    for link in links:
        links_by_track.setdefault(str(link.get("path_id")), []).append(link)

    visible = []
    for track in tracks:
        try:
            visible.append(_public_track_payload_from_rows(
                track,
                links_by_track.get(str(track.get("id")), []),
                course_map,
            ))
        except HTTPException as exc:
            if exc.status_code != 404:
                raise
    return {"success": True, "count": len(visible), "tracks": visible}


@router.get("/tracks/{track_id}")
def public_track(track_id: str):
    track = _global_track_lookup(track_id)
    return {"success": True, "track": _public_track_payload(track)}

@router.get("/courses")
def public_courses():
    result = (
        supabase.table("learnora_courses")
        .select("id,organisation_id,creator_id,title,slug,short_description,description,level,status,ownership,thumbnail_url,estimated_hours,settings,created_at")
        .eq("status", "published")
        .order("created_at", desc=True)
        .execute()
    )
    course_rows = result.data or []
    organisation_ids = list({str(row["organisation_id"]) for row in course_rows if row.get("organisation_id")})
    creator_ids = list({str(row["creator_id"]) for row in course_rows if row.get("creator_id")})
    organisation_map = {}
    creator_map = {}
    if organisation_ids:
        organisations = (supabase.table("organisations").select("id,is_active,settings").in_("id", organisation_ids).execute()).data or []
        organisation_map = {str(row["id"]): row for row in organisations}
    if creator_ids:
        creators = (supabase.table("learnora_creator_accounts").select("id,status").in_("id", creator_ids).execute()).data or []
        creator_map = {str(row["id"]): row for row in creators}
    visible = [_public_course_payload(row) for row in course_rows if _is_public_course(row, organisation_map, creator_map)]
    return {"success": True, "count": len(visible), "courses": visible}


@router.get("/courses/{course_id}")
def public_course(course_id: str):
    course = _public_course_lookup(course_id)
    return {"success": True, "course": _public_course_payload(course)}


@router.get("/courses/{course_id}/structure")
def public_course_structure(course_id: str):
    course = _public_course_lookup(course_id)
    modules = (
        supabase.table("course_modules")
        .select("id,course_id,title,description,order_index,status")
        .eq("course_id", course_id)
        .eq("status", "published")
        .order("order_index")
        .execute()
    ).data or []
    module_ids = [str(row["id"]) for row in modules]
    lessons = []
    if module_ids:
        lessons = (
            supabase.table("learnora_lessons")
            .select("id,module_id,title,slug,description,order_index,lesson_type,duration_minutes,is_preview,status")
            .in_("module_id", module_ids)
            .eq("status", "published")
            .order("order_index")
            .execute()
        ).data or []
    by_module = {}
    for lesson in lessons:
        by_module.setdefault(str(lesson["module_id"]), []).append(lesson)
    shaped = [{**module, "lessons": by_module.get(str(module["id"]), [])} for module in modules]
    return {"success": True, "course": _public_course_payload(course), "modules": shaped}


@router.get("/tutors")
def public_tutors():
    result = (
        supabase
        .table("learnora_creator_accounts")
        .select("id,display_name,bio,created_at,application_id")
        .eq("status", "approved")
        .order("display_name")
        .limit(100)
        .execute()
    )
    tutors = result.data or []
    application_ids = list({str(row["application_id"]) for row in tutors if row.get("application_id")})
    applications = []
    if application_ids:
        applications = (
            supabase.table("learnora_creator_applications")
            .select("id,application_data")
            .in_("id", application_ids)
            .execute()
        ).data or []
    application_map = {str(row["id"]): (row.get("application_data") or {}) for row in applications}
    public_tutors = []
    for tutor in tutors:
        application = application_map.get(str(tutor.get("application_id")), {})
        portfolio_url = str(application.get("portfolio_url") or "").strip()
        parsed = urlparse(portfolio_url) if portfolio_url else None
        if not parsed or parsed.scheme not in {"http", "https"} or not parsed.netloc:
            portfolio_url = None
        public_tutors.append({
            "id": tutor.get("id"),
            "display_name": tutor.get("display_name"),
            "bio": tutor.get("bio"),
            "expertise": str(application.get("expertise") or "").strip()[:200] or None,
            "portfolio_url": portfolio_url,
            "sample_course": str(application.get("sample_course") or "").strip()[:200] or None,
            "created_at": tutor.get("created_at"),
        })
    return {"success": True, "tutors": public_tutors}


@router.get("/organisations")
def public_organisations():
    result = (
        supabase
        .table("organisations")
        .select(
            "id,name,slug,organisation_type,description,logo_url,"
            "brand_primary,brand_secondary,template"
        )
        .eq("is_active", True)
        .contains("settings", {"public_directory": True})
        .order("name")
        .limit(100)
        .execute()
    )
    return {"success": True, "organisations": result.data or []}
