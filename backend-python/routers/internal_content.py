from fastapi import APIRouter, Depends, HTTPException
import re
import secrets
from html import escape as html_escape
from html.parser import HTMLParser
from .auth import supabase
from .internal_auth import InternalStaffContext, require_internal_permission
from pydantic import BaseModel, Field
from typing import Optional, Literal

class _LessonHTMLSanitizer(HTMLParser):
    allowed_tags = {"p", "br", "h1", "h2", "h3", "h4", "h5", "h6", "strong", "b", "em", "i", "u", "ul", "ol", "li", "blockquote", "pre", "code", "a", "hr"}
    void_tags = {"br", "hr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "div":
            self.parts.append("<p>")
            return
        if tag == "span":
            return
        if tag not in self.allowed_tags:
            return
        if tag == "a":
            href = next((value or "" for key, value in attrs if key.lower() == "href"), "").strip()
            safe = href.startswith(("https://", "http://", "mailto:", "/", "#"))
            self.parts.append(f'<a href="{html_escape(href, quote=True)}" rel="noopener noreferrer">' if safe else "<a>")
            return
        self.parts.append(f"<{tag}>")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "div":
            self.parts.append("</p>")
            return
        if tag == "span":
            return
        if tag in self.allowed_tags and tag not in self.void_tags:
            self.parts.append(f"</{tag}>")

    def handle_data(self, data):
        self.parts.append(html_escape(data))


def _sanitise_lesson_content(value):
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return ""
    has_html = re.search(r"<\s*[a-z][^>]*>", raw, re.IGNORECASE)
    if not has_html:
        is_legacy_markdown = re.search(
            r"(^\s{0,3}#{1,6}\s|^\s*[-*+]\s|^\s*\d+[.)]\s|^\s*>|^\s*\x60{3}|\*\*|__)",
            raw,
            re.MULTILINE,
        )
        if is_legacy_markdown:
            return raw
        return "".join(f"<p>{html_escape(part)}</p>" for part in raw.split("\n\n") if part.strip())
    parser = _LessonHTMLSanitizer()
    parser.feed(raw)
    parser.close()
    return "".join(parser.parts)


router = APIRouter(prefix="/api/internal/content", tags=["Internal Content"])

def _global_learnora_course(course_id: str):
    result = (
        supabase.table("learnora_courses")
        .select("id,title,slug,ownership,organisation_id,status")
        .eq("id", course_id)
        .eq("ownership", "learnora")
        .is_("organisation_id", "null")
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Global Learnora course not found.")
    return result.data[0]


def _assert_course_publishable(course_id: str):
    modules = (
        supabase.table("course_modules")
        .select("id,order_index")
        .eq("course_id", course_id)
        .eq("status", "published")
        .order("order_index")
        .execute()
    ).data or []
    if not modules:
        raise HTTPException(status_code=409, detail="Add at least one published module before publishing this course.")
    module_ids = [str(row["id"]) for row in modules if row.get("id")]
    lessons = (
        supabase.table("learnora_lessons")
        .select("id")
        .in_("module_id", module_ids)
        .eq("status", "published")
        .limit(1)
        .execute()
    ).data or []
    if not lessons:
        raise HTTPException(status_code=409, detail="Add at least one published lesson before publishing this course.")
    for module in modules[:-1]:
        quizzes = (
            supabase.table("quizzes")
            .select("id,module_id,lesson_id")
            .eq("module_id", str(module["id"]))
            .eq("is_published", True)
            .execute()
        ).data or []
        if not quizzes:
            raise HTTPException(
                status_code=409,
                detail="Every published module before the final module must have a published assessment so learners can unlock the next module.",
            )
        for quiz in quizzes:
            if quiz.get("lesson_id"):
                lesson_rows = (
                    supabase.table("learnora_lessons")
                    .select("id,module_id,status")
                    .eq("id", str(quiz["lesson_id"]))
                    .limit(1)
                    .execute()
                ).data or []
                if not lesson_rows or lesson_rows[0].get("status") != "published" or str(lesson_rows[0].get("module_id")) != str(module["id"]):
                    raise HTTPException(409, "A published module quiz must be attached to a published lesson in the same module.")
            questions = (
                supabase.table("quiz_questions")
                .select("id,question_type,options,correct_answer")
                .eq("quiz_id", str(quiz["id"]))
                .execute()
            ).data or []
            if not questions:
                raise HTTPException(409, "Every published module assessment needs at least one question before the course can be published.")
            from .internal_assessments import _validate_question_payload
            for question in questions:
                try:
                    _validate_question_payload(question)
                except HTTPException as exc:
                    raise HTTPException(409, "Every published module assessment must contain supported, answerable questions before the course can be published.") from None

    assignments = (
        supabase.table("assignments")
        .select("id,lesson_id,description,instructions,max_score")
        .eq("course_id", course_id)
        .eq("is_published", True)
        .execute()
    ).data or []
    for assignment in assignments:
        if not (assignment.get("instructions") or assignment.get("description")):
            raise HTTPException(409, "Every published assignment must include learner instructions before the course can be published.")
        if assignment.get("max_score") is not None and float(assignment["max_score"]) <= 0:
            raise HTTPException(409, "Every published assignment must have a positive maximum score.")
        if assignment.get("lesson_id"):
            lesson_rows = (
                supabase.table("learnora_lessons")
                .select("id,module_id,status")
                .eq("id", str(assignment["lesson_id"]))
                .limit(1)
                .execute()
            ).data or []
            if not lesson_rows or lesson_rows[0].get("status") != "published" or str(lesson_rows[0].get("module_id")) not in {str(row["id"]) for row in modules}:
                raise HTTPException(409, "A published assignment must be attached to a published lesson in this course.")


def _assert_course_not_in_published_global_track(course_id: str):
    links = (
        supabase.table("learnora_learning_path_courses")
        .select("path_id")
        .eq("course_id", course_id)
        .execute()
    ).data or []
    path_ids = list({str(row["path_id"]) for row in links if row.get("path_id")})
    if not path_ids:
        return
    published = (
        supabase.table("learnora_learning_paths")
        .select("id")
        .in_("id", path_ids)
        .eq("status", "published")
        .is_("owner_user_id", "null")
        .is_("organisation_id", "null")
        .limit(1)
        .execute()
    ).data or []
    if published:
        raise HTTPException(
            status_code=409,
            detail="Unpublish or update the global track before changing this course's publication or ownership.",
        )


@router.get("/courses")
def courses(staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    rows = supabase.table("learnora_courses").select("id,title,slug,organisation_id,ownership,status,created_at,updated_at").eq("ownership", "learnora").is_("organisation_id", "null").order("created_at", desc=True).execute()
    return {"success": True, "courses": rows.data or []}

class CourseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    short_description: Optional[str] = Field(None, max_length=1000)
    description: Optional[str] = Field(None, max_length=10000)
    level: Optional[str] = Field(None, max_length=40)
    status: Literal["draft", "published", "archived"] = "draft"
    ownership: str = Field("learnora", min_length=1, max_length=40)
    organisation_id: Optional[str] = None
    thumbnail_url: Optional[str] = Field(None, max_length=2000)
    estimated_hours: Optional[float] = Field(None, ge=0)

class CourseWrite(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    short_description: Optional[str] = Field(None, max_length=1000)
    description: Optional[str] = Field(None, max_length=10000)
    level: Optional[str] = Field(None, max_length=40)
    status: Optional[Literal["draft", "published", "archived"]] = None
    ownership: Optional[str] = Field(None, max_length=40)
    thumbnail_url: Optional[str] = Field(None, max_length=2000)
    estimated_hours: Optional[float] = Field(None, ge=0)

@router.post("/courses")
def create_course(payload: CourseCreate, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    if payload.status != "draft":
        raise HTTPException(status_code=409, detail="Create courses as drafts, then publish after the curriculum passes validation.")
    if payload.ownership.strip().lower() != "learnora" or payload.organisation_id:
        raise HTTPException(status_code=403, detail="This workspace manages global Learnora-owned courses only.")
    slug = payload.slug.strip().lower().replace(" ", "-")
    if supabase.table("learnora_courses").select("id").eq("slug", slug).limit(1).execute().data:
        raise HTTPException(status_code=400, detail="A course with this slug already exists.")
    if payload.ownership.strip().lower() == "organisation" and not payload.organisation_id:
        raise HTTPException(status_code=400, detail="Organisation-owned courses require an organisation.")
    row = supabase.table("learnora_courses").insert({
        "title": payload.title.strip(),
        "slug": slug,
        "short_description": payload.short_description.strip() if payload.short_description else None,
        "description": payload.description.strip() if payload.description else None,
        "level": payload.level.strip().lower() if payload.level else None,
        "status": payload.status,
        "ownership": payload.ownership.strip().lower(),
        "organisation_id": payload.organisation_id,
        "thumbnail_url": payload.thumbnail_url.strip() if payload.thumbnail_url else None,
        "estimated_hours": payload.estimated_hours,
        "settings": {},
        "created_by": staff.user_id,
    }).execute()
    if not row.data:
        raise HTTPException(status_code=500, detail="Course creation failed.")
    return {"success": True, "course": row.data[0]}

@router.get("/courses/{course_id}")
def get_course(course_id: str, staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    course = _global_learnora_course(course_id)
    row = supabase.table("learnora_courses").select("*").eq("id", course_id).eq("ownership", "learnora").is_("organisation_id", "null").limit(1).execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Global Learnora course not found.")
    return {"success": True, "course": row.data[0]}

@router.patch("/courses/{course_id}")
def update_course(course_id: str, payload: CourseWrite, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    current_result = (
        supabase.table("learnora_courses")
        .select("id,status,ownership,organisation_id")
        .eq("id", course_id)
        .eq("ownership", "learnora")
        .is_("organisation_id", "null")
        .limit(1)
        .execute()
    )
    if not current_result.data:
        raise HTTPException(status_code=404, detail="Course not found.")
    current_course = current_result.data[0]
    data = payload.model_dump(exclude_unset=True)
    resulting_status = data.get("status", current_course.get("status"))
    resulting_ownership = data.get("ownership", current_course.get("ownership"))
    if resulting_ownership != "learnora":
        raise HTTPException(status_code=403, detail="This workspace manages global Learnora-owned courses only.")
    if resulting_status == "published" and current_course.get("status") != "published":
        _assert_course_publishable(course_id)
    if resulting_status != "published" or resulting_ownership != "learnora" or current_course.get("organisation_id") is not None:
        _assert_course_not_in_published_global_track(course_id)
    for key in ("title", "slug", "short_description", "description", "level", "ownership", "thumbnail_url"):
        if key in data and isinstance(data[key], str):
            data[key] = data[key].strip() or None
    if data.get("slug"):
        data["slug"] = data["slug"].lower().replace(" ", "-")
        duplicate = supabase.table("learnora_courses").select("id").eq("slug", data["slug"]).neq("id", course_id).limit(1).execute()
        if duplicate.data:
            raise HTTPException(status_code=400, detail="A course with this slug already exists.")
    if not data:
        raise HTTPException(status_code=400, detail="No changes supplied.")
    row = supabase.table("learnora_courses").update(data).eq("id", course_id).execute()
    if not row.data:
        raise HTTPException(status_code=500, detail="Course update failed.")
    return {"success": True, "course": row.data[0]}

@router.post("/courses/{course_id}/archive")
def archive_course(course_id: str, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    _global_learnora_course(course_id)
    _assert_course_not_in_published_global_track(course_id)
    row = supabase.table("learnora_courses").update({"status": "archived"}).eq("id", course_id).execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Course not found.")
    return {"success": True, "course": row.data[0]}

@router.get("/courses/{course_id}/structure")
def course_structure(course_id: str, staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    _global_learnora_course(course_id)
    course = supabase.table("learnora_courses").select("*").eq("id", course_id).eq("ownership", "learnora").is_("organisation_id", "null").limit(1).execute()
    if not course.data:
        raise HTTPException(status_code=404, detail="Global Learnora course not found.")

    modules = (
        supabase.table("course_modules")
        .select("*")
        .eq("course_id", course_id)
        .order("order_index")
        .execute()
    ).data or []

    module_ids = [str(m["id"]) for m in modules]
    lessons = []
    if module_ids:
        lessons = (
            supabase.table("learnora_lessons")
            .select("*")
            .in_("module_id", module_ids)
            .order("order_index")
            .execute()
        ).data or []

    by_module = {str(m["id"]): [] for m in modules}
    for lesson in lessons:
        by_module.setdefault(str(lesson["module_id"]), []).append(lesson)

    structured = [{**module, "lessons": by_module.get(str(module["id"]), [])} for module in modules]
    return {
        "success": True,
        "course": course.data[0],
        "modules": structured,
        "module_count": len(structured),
        "lesson_count": sum(len(module["lessons"]) for module in structured),
    }

@router.get("/courses/{course_id}/modules")
def modules(course_id: str, staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    _global_learnora_course(course_id)
    rows = supabase.table("course_modules").select("*").eq("course_id", course_id).order("order_index").execute()
    return {"success": True, "modules": rows.data or []}

@router.get("/modules/{module_id}/lessons")
def lessons(module_id: str, staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    _course_for_module(module_id)
    rows = supabase.table("learnora_lessons").select("*").eq("module_id", module_id).order("order_index").execute()
    return {"success": True, "lessons": rows.data or []}

@router.get("/lessons/{lesson_id}")
def lesson(lesson_id: str, staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    _module_for_lesson(lesson_id)
    row = supabase.table("learnora_lessons").select("*").eq("id", lesson_id).limit(1).execute()
    return {"success": True, "lesson": (row.data or [None])[0]}

@router.get("/lessons/{lesson_id}/media")
def lesson_media(lesson_id: str, staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    _module_for_lesson(lesson_id)
    videos = supabase.table("lesson_videos").select("*").eq("lesson_id", lesson_id).order("created_at", desc=True).execute()
    resources = supabase.table("lesson_resources").select("*").eq("lesson_id", lesson_id).order("created_at", desc=True).execute()
    return {"success": True, "videos": videos.data or [], "resources": resources.data or []}


from pydantic import BaseModel, Field
from typing import Optional, Literal

class ModuleWrite(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)
    status: Optional[Literal["draft", "published", "archived"]] = None

class LessonWrite(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)
    lesson_type: Optional[Literal["video", "article", "text", "practice", "quiz", "assignment", "project", "mixed"]] = None
    content: Optional[str] = Field(None, max_length=100000)
    duration_minutes: Optional[int] = Field(None, ge=0)
    is_preview: Optional[bool] = None
    status: Optional[Literal["draft", "published", "archived"]] = None

class ReorderItem(BaseModel):
    id: str
    order_index: int = Field(..., ge=0)

class VideoUploadRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: Literal["video/mp4", "video/webm", "video/quicktime", "video/mpeg", "video/x-msvideo"]
    file_size_bytes: int = Field(..., gt=0, le=2147483648)
    title: Optional[str] = Field(None, max_length=200)

class ResourceUploadRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: Literal[
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/csv",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "text/plain",
        "application/zip",
        "application/json",
    ]
    file_size_bytes: int = Field(..., gt=0, le=104857600)
    title: Optional[str] = Field(None, max_length=200)


class VideoWrite(BaseModel):
    provider: Literal["supabase", "cloudflare", "mux", "bunny", "vimeo", "youtube", "external", "other"] = "supabase"
    storage_path: Optional[str] = None
    external_video_id: Optional[str] = None
    title: Optional[str] = None
    duration_seconds: Optional[int] = Field(None, ge=0)
    file_size_bytes: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = None
    thumbnail_url: Optional[str] = None
    transcript_text: Optional[str] = Field(None, max_length=200000)
    status: str = "pending"
    is_private: bool = True

class ResourceWrite(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    resource_type: str = Field(..., min_length=1, max_length=80)
    storage_path: Optional[str] = None
    external_url: Optional[str] = None
    file_size_bytes: Optional[int] = Field(None, ge=0)

def _course_for_module(module_id: str):
    row = supabase.table("course_modules").select("id,course_id").eq("id", module_id).limit(1).execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Module not found.")
    module = row.data[0]
    _global_learnora_course(str(module["course_id"]))
    return module

def _module_for_lesson(lesson_id: str):
    row = supabase.table("learnora_lessons").select("id,module_id").eq("id", lesson_id).limit(1).execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Lesson not found.")
    lesson = row.data[0]
    _course_for_module(str(lesson["module_id"]))
    return lesson

@router.post("/courses/{course_id}/modules")
def create_module(course_id: str, payload: ModuleWrite, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    if not payload.title:
        raise HTTPException(status_code=400, detail="title is required")
    _global_learnora_course(course_id)
    row = supabase.table("course_modules").insert({"course_id": course_id, "title": payload.title.strip(), "description": payload.description, "order_index": payload.order_index or 0, "status": payload.status or "draft"}).execute()
    if not row.data:
        raise HTTPException(status_code=500, detail="Module creation returned no record.")
    return {"success": True, "module": row.data[0]}

@router.patch("/modules/{module_id}")
def update_module(module_id: str, payload: ModuleWrite, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    _course_for_module(module_id)
    data = payload.model_dump(exclude_unset=True)
    if "title" in data and data["title"]:
        data["title"] = data["title"].strip()
    if not data:
        raise HTTPException(status_code=400, detail="No changes supplied.")
    row = supabase.table("course_modules").update(data).eq("id", module_id).execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Module not found.")
    return {"success": True, "module": row.data[0]}

@router.post("/modules/{module_id}/lessons")
def create_lesson(module_id: str, payload: LessonWrite, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    if not payload.title:
        raise HTTPException(status_code=400, detail="title is required")
    _course_for_module(module_id)
    row = supabase.table("learnora_lessons").insert({"module_id": module_id, "title": payload.title.strip(), "slug": payload.slug, "description": payload.description, "order_index": payload.order_index or 0, "lesson_type": payload.lesson_type or "mixed", "content": _sanitise_lesson_content(payload.content), "duration_minutes": payload.duration_minutes, "is_preview": payload.is_preview or False, "status": payload.status or "draft"}).execute()
    if not row.data:
        raise HTTPException(status_code=500, detail="Lesson creation returned no record.")
    return {"success": True, "lesson": row.data[0]}

@router.patch("/lessons/{lesson_id}")
def update_lesson(lesson_id: str, payload: LessonWrite, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    _module_for_lesson(lesson_id)
    data = payload.model_dump(exclude_unset=True)
    if "title" in data and data["title"]:
        data["title"] = data["title"].strip()
    if "content" in data:
        data["content"] = _sanitise_lesson_content(data["content"])
    if not data:
        raise HTTPException(status_code=400, detail="No changes supplied.")
    row = supabase.table("learnora_lessons").update(data).eq("id", lesson_id).execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Lesson not found.")
    return {"success": True, "lesson": row.data[0]}

@router.post("/modules/{module_id}/archive")
def archive_module(module_id: str, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    _course_for_module(module_id)
    row = supabase.table("course_modules").update({"status": "archived"}).eq("id", module_id).execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Module not found.")
    return {"success": True, "module": row.data[0]}

@router.post("/lessons/{lesson_id}/archive")
def archive_lesson(lesson_id: str, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    _module_for_lesson(lesson_id)
    row = supabase.table("learnora_lessons").update({"status": "archived"}).eq("id", lesson_id).execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Lesson not found.")
    return {"success": True, "lesson": row.data[0]}

@router.patch("/courses/{course_id}/modules/reorder")
def reorder_modules(course_id: str, items: list[ReorderItem], staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    _global_learnora_course(course_id)
    for item in items:
        supabase.table("course_modules").update({"order_index": item.order_index}).eq("id", item.id).eq("course_id", course_id).execute()
    return {"success": True}

@router.patch("/modules/{module_id}/lessons/reorder")
def reorder_lessons(module_id: str, items: list[ReorderItem], staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    _course_for_module(module_id)
    for item in items:
        supabase.table("learnora_lessons").update({"order_index": item.order_index}).eq("id", item.id).eq("module_id", module_id).execute()
    return {"success": True}

@router.post("/lessons/{lesson_id}/video-upload")
def create_video_upload(
    lesson_id: str,
    payload: VideoUploadRequest,
    staff: InternalStaffContext = Depends(require_internal_permission("content.video")),
):
    lesson = _module_for_lesson(lesson_id)
    module = _course_for_module(str(lesson["module_id"]))
    course_id = str(module["course_id"])
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", payload.filename.strip()).strip(".-") or "video"
    path = f"courses/{course_id}/lessons/{lesson_id}/{secrets.token_hex(12)}-{safe_name}"
    try:
        response = supabase.storage.from_("learnora-course-media").create_signed_upload_url(
            path,
            options={"upsert": "false"},
        )
        data = getattr(response, "data", None) or response
        if isinstance(data, dict):
            token = data.get("token")
            signed_url = data.get("signedUrl") or data.get("signed_url")
            response_path = data.get("path") or path
        else:
            token = getattr(data, "token", None)
            signed_url = getattr(data, "signed_url", None) or getattr(data, "signedUrl", None)
            response_path = getattr(data, "path", None) or path
        if not token or not signed_url:
            raise RuntimeError("Supabase did not return a signed upload URL.")
        return {
            "success": True,
            "bucket": "learnora-course-media",
            "path": response_path,
            "token": token,
            "signed_url": signed_url,
            "title": payload.title or payload.filename,
            "content_type": payload.content_type,
            "file_size_bytes": payload.file_size_bytes,
        }
    except HTTPException:
        raise
    except Exception as exc:
        print("Video upload URL creation failed:", type(exc).__name__)
        raise HTTPException(status_code=500, detail="Unable to create video upload URL.")

@router.post("/lessons/{lesson_id}/resource-upload")
def create_resource_upload(
    lesson_id: str,
    payload: ResourceUploadRequest,
    staff: InternalStaffContext = Depends(require_internal_permission("content.resources")),
):
    lesson = _module_for_lesson(lesson_id)
    module = _course_for_module(str(lesson["module_id"]))
    course_id = str(module["course_id"])
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", payload.filename.strip()).strip(".-") or "resource"
    path = f"courses/{course_id}/lessons/{lesson_id}/resources/{secrets.token_hex(12)}-{safe_name}"
    try:
        response = supabase.storage.from_("learnora-course-media").create_signed_upload_url(
            path,
            options={"upsert": "false"},
        )
        data = getattr(response, "data", None) or response
        if isinstance(data, dict):
            token = data.get("token")
            signed_url = data.get("signedUrl") or data.get("signed_url")
            response_path = data.get("path") or path
        else:
            token = getattr(data, "token", None)
            signed_url = getattr(data, "signed_url", None) or getattr(data, "signedUrl", None)
            response_path = getattr(data, "path", None) or path
        if not token or not signed_url:
            raise RuntimeError("Supabase did not return a signed resource upload URL.")
        return {
            "success": True,
            "bucket": "learnora-course-media",
            "path": response_path,
            "token": token,
            "signed_url": signed_url,
            "title": payload.title or payload.filename,
            "content_type": payload.content_type,
            "file_size_bytes": payload.file_size_bytes,
        }
    except HTTPException:
        raise
    except Exception as exc:
        print("Resource upload URL creation failed:", type(exc).__name__)
        raise HTTPException(status_code=500, detail="Unable to create resource upload URL.") from exc


@router.post("/lessons/{lesson_id}/videos")
def create_video(lesson_id: str, payload: VideoWrite, staff: InternalStaffContext = Depends(require_internal_permission("content.video"))):
    _module_for_lesson(lesson_id)
    row = supabase.table("lesson_videos").insert({"lesson_id": lesson_id, **payload.model_dump()}).execute()
    if not row.data:
        raise HTTPException(status_code=500, detail="Video metadata could not be saved.")
    return {"success": True, "video": row.data[0]}

@router.patch("/videos/{video_id}")
def update_video(video_id: str, payload: VideoWrite, staff: InternalStaffContext = Depends(require_internal_permission("content.video"))):
    existing = supabase.table("lesson_videos").select("id,lesson_id").eq("id", video_id).limit(1).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Video not found.")
    _module_for_lesson(str(existing.data[0]["lesson_id"]))
    row = supabase.table("lesson_videos").update(payload.model_dump(exclude_unset=True)).eq("id", video_id).execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Video not found.")
    return {"success": True, "video": row.data[0]}

@router.post("/lessons/{lesson_id}/resources")
def create_resource(lesson_id: str, payload: ResourceWrite, staff: InternalStaffContext = Depends(require_internal_permission("content.resources"))):
    _module_for_lesson(lesson_id)
    row = supabase.table("lesson_resources").insert({"lesson_id": lesson_id, **payload.model_dump()}).execute()
    if not row.data:
        raise HTTPException(status_code=500, detail="Resource metadata could not be saved.")
    return {"success": True, "resource": row.data[0]}
