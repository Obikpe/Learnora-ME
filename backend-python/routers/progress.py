"""Persistent Learnora learning progress API.

Progress is stored in Supabase, never in the ephemeral Vercel filesystem.
All writes are scoped to the authenticated learner and an actual enrolment.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .auth import CurrentUser, get_current_user, supabase
from services.free_access import is_individual_learner

router = APIRouter(
    prefix="/api/progress",
    tags=["Progress"],
)


class LessonProgressIn(BaseModel):
    progress_percent: int = Field(default=0, ge=0, le=100)
    completed: bool = False
    last_position_seconds: int = Field(default=0, ge=0)


class LessonNoteIn(BaseModel):
    content: str = Field(default="", max_length=20000)


class QuizAttemptIn(BaseModel):
    answers: dict[str, Any] = Field(default_factory=dict)
    session_id: UUID | None = None


class AssignmentSubmissionIn(BaseModel):
    submission_text: str = Field(default="", max_length=20000)
    file_url: Optional[str] = Field(default=None, max_length=2000)


def _course_for_lesson(lesson_id: str):
    result = (
        supabase
        .table("learnora_lessons")
        .select(
            "id,module_id,course_modules!inner(course_id)"
        )
        .eq("id", lesson_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Lesson not found.")

    row = result.data[0]
    return str(row["course_modules"]["course_id"])


def _enrolment(user_id: str, course_id: str):
    result = (
        supabase
        .table("learnora_enrolments")
        .select(
            "id,user_id,course_id,organisation_id,cohort_id,status,"
            "enrolled_at,completed_at"
        )
        .eq("user_id", user_id)
        .eq("course_id", course_id)
        .in_("status", ["active", "completed"])
        .order("enrolled_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def effective_passing_score(quiz: dict) -> float:
    """A quiz's configured threshold may be stricter, never below 70%."""
    return max(70.0, float(quiz.get("passing_score") or 70))


def _module_for_lesson(lesson_id: str):
    result = (
        supabase.table("learnora_lessons")
        .select("id,module_id")
        .eq("id", lesson_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Lesson not found.")
    return str(result.data[0]["module_id"])


def _assert_module_unlocked(user_id: str, module_id: str, include_archived: bool = False):
    """Require a passed >=70% assessment for every earlier module."""
    current = (
        supabase.table("course_modules")
        .select("id,course_id,order_index")
        .eq("id", module_id)
        .limit(1)
        .execute()
    ).data or []
    if not current:
        raise HTTPException(404, "Module not found.")
    module = current[0]
    previous_query = (
        supabase.table("course_modules")
        .select("id,title,order_index")
        .eq("course_id", module["course_id"])
        .lt("order_index", module["order_index"])
    )
    previous_query = (
        previous_query.in_("status", ["published", "archived"])
        if include_archived
        else previous_query.eq("status", "published")
    )
    previous_modules = previous_query.order("order_index").execute().data or []

    for previous in previous_modules:
        quizzes = (
            supabase.table("quizzes")
            .select("id,title,passing_score")
            .eq("module_id", previous["id"])
            .eq("is_published", True)
            .execute()
        ).data or []
        if not quizzes:
            continue
        for quiz in quizzes:
            threshold = effective_passing_score(quiz)
            attempts = (
                supabase.table("quiz_attempts")
                .select("id,score,passed")
                .eq("quiz_id", quiz["id"])
                .eq("user_id", user_id)
                .eq("passed", True)
                .gte("score", threshold)
                .limit(1)
                .execute()
            ).data or []
            if not attempts:
                raise HTTPException(
                    423,
                    f'Pass the assessment for "{previous.get("title") or "the previous module"}" with at least {threshold:g}% to unlock the next module.',
                )


def _course_assessment_summary(user_id: str, course_id: str):
    """Completion gates for published quizzes and manually graded assignments."""
    quizzes = (
        supabase.table("quizzes")
        .select("id,title,passing_score")
        .eq("course_id", course_id)
        .eq("is_published", True)
        .execute()
    ).data or []
    quiz_ids = [str(row["id"]) for row in quizzes if row.get("id")]
    attempts = []
    if quiz_ids:
        attempts = (
            supabase.table("quiz_attempts")
            .select("quiz_id,score,passed,submitted_at")
            .eq("user_id", user_id)
            .in_("quiz_id", quiz_ids)
            .execute()
        ).data or []
    passed_quiz_ids = set()
    for quiz in quizzes:
        threshold = effective_passing_score(quiz)
        if any(
            str(attempt.get("quiz_id")) == str(quiz["id"])
            and attempt.get("passed") is True
            and float(attempt.get("score") or 0) >= threshold
            for attempt in attempts
        ):
            passed_quiz_ids.add(str(quiz["id"]))

    assignments = (
        supabase.table("assignments")
        .select("id,title,max_score")
        .eq("course_id", course_id)
        .eq("is_published", True)
        .execute()
    ).data or []
    assignment_ids = [str(row["id"]) for row in assignments if row.get("id")]
    submissions = []
    if assignment_ids:
        submissions = (
            supabase.table("assignment_submissions")
            .select("id,assignment_id,status,score,submitted_at,graded_at")
            .eq("user_id", user_id)
            .in_("assignment_id", assignment_ids)
            .order("submitted_at", desc=True)
            .execute()
        ).data or []
    latest_by_assignment = {}
    for submission in submissions:
        key = str(submission.get("assignment_id"))
        if key and key not in latest_by_assignment:
            latest_by_assignment[key] = submission
    passed_assignment_ids = set()
    for assignment in assignments:
        submission = latest_by_assignment.get(str(assignment["id"]))
        if not submission or submission.get("status") != "graded" or not submission.get("graded_at"):
            continue
        maximum = float(assignment.get("max_score") or 100)
        threshold = maximum * 0.7
        if float(submission.get("score") or 0) >= threshold:
            passed_assignment_ids.add(str(assignment["id"]))

    total = len(quizzes) + len(assignments)
    completed = len(passed_quiz_ids) + len(passed_assignment_ids)
    return {
        "total_quizzes": len(quizzes),
        "passed_quizzes": len(passed_quiz_ids),
        "total_assignments": len(assignments),
        "passed_assignments": len(passed_assignment_ids),
        "total_assessments": total,
        "completed_assessments": completed,
        "completed": total == completed,
    }


def _course_summary(user_id: str, course_id: str, include_archived: bool = False):
    enrolment = _enrolment(user_id, course_id)
    if not enrolment:
        raise HTTPException(
            403,
            "You are not enrolled in this course.",
        )

    module_query = (
        supabase
        .table("course_modules")
        .select("id,title,order_index,status")
        .eq("course_id", course_id)
    )
    module_query = (
        module_query.in_("status", ["published", "archived"])
        if include_archived
        else module_query.eq("status", "published")
    )
    modules = module_query.order("order_index").execute().data or []

    module_ids = [row["id"] for row in modules]

    lessons = []
    if module_ids:
        lesson_query = (
            supabase
            .table("learnora_lessons")
            .select(
                "id,module_id,title,order_index,lesson_type,"
                "content,duration_minutes,status"
            )
            .in_("module_id", module_ids)
        )
        lesson_query = (
            lesson_query.in_("status", ["published", "archived"])
            if include_archived
            else lesson_query.eq("status", "published")
        )
        lessons = lesson_query.order("order_index").execute().data or []

    progress = (
        supabase
        .table("learnora_lesson_progress")
        .select(
            "lesson_id,progress_percent,completed,"
            "last_position_seconds,first_started_at,"
            "last_accessed_at,completed_at"
        )
        .eq("user_id", user_id)
        .execute()
    ).data or []

    progress_map = {
        str(row["lesson_id"]): row
        for row in progress
    }

    completed = sum(
        1
        for lesson in lessons
        if progress_map.get(str(lesson["id"]), {}).get("completed")
    )

    total = len(lessons)
    assessment_summary = _course_assessment_summary(user_id, course_id)
    total_units = total + assessment_summary["total_assessments"]
    completed_units = completed + assessment_summary["completed_assessments"]
    percent = round((completed_units / total_units) * 100) if total_units else 0

    module_views = []
    for module in modules:
        locked = False
        try:
            _assert_module_unlocked(
                user_id,
                str(module["id"]),
                include_archived=include_archived,
            )
        except HTTPException as exc:
            if exc.status_code in (409, 423):
                locked = True
            else:
                raise
        module_lessons = []
        for lesson in lessons:
            if str(lesson["module_id"]) != str(module["id"]):
                continue
            lesson_view = {
                **lesson,
                "progress": progress_map.get(str(lesson["id"])),
            }
            if locked:
                lesson_view["content"] = None
            module_lessons.append(lesson_view)
        module_views.append({**module, "locked": locked, "lessons": module_lessons})

    return {
        "course_id": course_id,
        "enrolment": enrolment,
        "total_lessons": total,
        "completed_lessons": completed,
        "progress_percent": percent,
        "completed": total_units > 0 and completed_units == total_units,
        "total_assessments": assessment_summary["total_assessments"],
        "completed_assessments": assessment_summary["completed_assessments"],
        "assessment_summary": assessment_summary,
        "modules": module_views,
    }


@router.get("/lessons/{lesson_id}/notes")
def get_lesson_note(lesson_id: str, user: CurrentUser = Depends(get_current_user)):
    course_id = _course_for_lesson(lesson_id)
    if not _enrolment(str(user.id), course_id):
        raise HTTPException(403, "You are not enrolled in this course.")
    _assert_module_unlocked(str(user.id), _module_for_lesson(lesson_id))
    result = supabase.table("learner_lesson_notes").select(
        "id,content,created_at,updated_at"
    ).eq("user_id", user.id).eq("lesson_id", lesson_id).limit(1).execute()
    return {"success": True, "note": result.data[0] if result.data else None}


@router.put("/lessons/{lesson_id}/notes")
def save_lesson_note(lesson_id: str, body: LessonNoteIn, user: CurrentUser = Depends(get_current_user)):
    course_id = _course_for_lesson(lesson_id)
    if not _enrolment(str(user.id), course_id):
        raise HTTPException(403, "You are not enrolled in this course.")
    _assert_module_unlocked(str(user.id), _module_for_lesson(lesson_id))
    now = datetime.now(timezone.utc).isoformat()
    result = supabase.table("learner_lesson_notes").upsert({
        "user_id": user.id,
        "course_id": course_id,
        "lesson_id": lesson_id,
        "content": body.content,
        "updated_at": now,
    }, on_conflict="user_id,lesson_id").execute()
    if not result.data:
        raise HTTPException(500, "Unable to save lesson note.")
    return {"success": True, "note": result.data[0]}


@router.get("/courses/{course_id}/activities")
def course_activities(course_id: str, user: CurrentUser = Depends(get_current_user)):
    if not _enrolment(str(user.id), course_id):
        raise HTTPException(403, "You are not enrolled in this course.")
    quizzes = (supabase.table("quizzes")
        .select("id,lesson_id,title,description,passing_score,max_attempts")
        .eq("course_id", course_id).eq("is_published", True)
        .order("created_at").execute()).data or []
    assignments = (supabase.table("assignments")
        .select("id,lesson_id,title,description,instructions,due_date,max_score")
        .eq("course_id", course_id).eq("is_published", True)
        .order("created_at").execute()).data or []
    projects = (supabase.table("projects")
        .select("id,course_id,title,description,instructions,skills")
        .eq("course_id", course_id).eq("is_published", True)
        .order("created_at").execute()).data or []
    return {"success": True, "quizzes": quizzes, "assignments": assignments, "projects": projects}


@router.get("/quizzes/{quiz_id}")
def get_quiz(quiz_id: str, user: CurrentUser = Depends(get_current_user)):
    result = (supabase.table("quizzes")
        .select("id,lesson_id,module_id,course_id,title,description,passing_score,max_attempts,is_published")
        .eq("id", quiz_id).eq("is_published", True).limit(1).execute())
    if not result.data:
        raise HTTPException(404, "Published quiz not found.")
    quiz = result.data[0]
    if not _enrolment(str(user.id), str(quiz["course_id"])):
        raise HTTPException(403, "You are not enrolled in this course.")
    if quiz.get("module_id"):
        _assert_module_unlocked(str(user.id), str(quiz["module_id"]))
    questions = (supabase.table("quiz_questions")
        .select("id,question,question_type,options,points,order_index")
        .eq("quiz_id", quiz_id).order("order_index").execute()).data or []
    attempts = (supabase.table("quiz_attempts")
        .select("id,score,passed,submitted_at")
        .eq("quiz_id", quiz_id).eq("user_id", user.id)
        .order("submitted_at", desc=True).execute()).data or []
    now = datetime.now(timezone.utc)
    try:
        session_rows = supabase.table("quiz_active_sessions").insert({
            "user_id": str(user.id),
            "quiz_id": str(quiz_id),
            "course_id": str(quiz["course_id"]),
            "lesson_id": str(quiz.get("lesson_id")) if quiz.get("lesson_id") else None,
            "started_at": now.isoformat(),
            "expires_at": (now + timedelta(hours=2)).isoformat(),
        }).select("id").execute().data or []
        if not session_rows:
            raise RuntimeError("Active quiz session ID was not returned")
    except Exception as exc:
        print(f"Quiz session protection could not be established: {type(exc).__name__}")
        raise HTTPException(503, "Quiz protection is temporarily unavailable. Please retry.") from None
    return {"success": True, "quiz": quiz, "questions": questions, "attempts": attempts, "session_id": session_rows[0]["id"]}


@router.post("/quizzes/{quiz_id}/attempts", status_code=201)
def submit_quiz_attempt(quiz_id: str, body: QuizAttemptIn, user: CurrentUser = Depends(get_current_user)):
    result = (supabase.table("quizzes")
        .select("id,lesson_id,module_id,course_id,title,passing_score,max_attempts,is_published")
        .eq("id", quiz_id).eq("is_published", True).limit(1).execute())
    if not result.data:
        raise HTTPException(404, "Published quiz not found.")
    quiz = result.data[0]
    if not _enrolment(str(user.id), str(quiz["course_id"])):
        raise HTTPException(403, "You are not enrolled in this course.")
    if quiz.get("module_id"):
        _assert_module_unlocked(str(user.id), str(quiz["module_id"]))
    if not body.session_id:
        raise HTTPException(409, "Open the quiz again before submitting this attempt.")
    try:
        active_session = (supabase.table("quiz_active_sessions")
            .select("id")
            .eq("id", str(body.session_id))
            .eq("user_id", str(user.id))
            .eq("quiz_id", str(quiz_id))
            .gt("expires_at", datetime.now(timezone.utc).isoformat())
            .limit(1)
            .execute()).data or []
    except Exception as exc:
        print(f"Quiz submission session check failed: {type(exc).__name__}")
        raise HTTPException(503, "Quiz protection is temporarily unavailable. Please retry.") from None
    if not active_session:
        raise HTTPException(409, "This quiz session has expired. Reopen the quiz to continue.")
    previous = (supabase.table("quiz_attempts")
        .select("id,score,passed,submitted_at")
        .eq("quiz_id", quiz_id).eq("user_id", user.id)
        .order("submitted_at", desc=True).execute()).data or []
    max_attempts = quiz.get("max_attempts")
    if max_attempts is not None and len(previous) >= int(max_attempts):
        raise HTTPException(409, "You have reached the maximum number of attempts for this quiz.")
    questions = (supabase.table("quiz_questions")
        .select("id,question,question_type,correct_answer,explanation,points,order_index")
        .eq("quiz_id", quiz_id).order("order_index").execute()).data or []
    if not questions:
        raise HTTPException(409, "This quiz has no published questions.")
    supported = {"multiple_choice", "single_choice", "mcq", "true_false", "boolean"}
    if any(str(q.get("question_type") or "").lower() not in supported for q in questions):
        raise HTTPException(409, "This quiz includes question types that require instructor grading and cannot be auto-scored yet.")
    def normalise(value):
        if isinstance(value, dict):
            value = value.get("value", value.get("answer", value.get("label", "")))
        if isinstance(value, list):
            return {str(item).strip().casefold() for item in value}
        return str(value).strip().casefold()
    total_points = sum(float(q.get("points") or 1) for q in questions)
    earned = 0.0
    review = []
    for question in questions:
        answer = body.answers.get(str(question["id"]))
        expected = question.get("correct_answer")
        correct = normalise(answer) == normalise(expected)
        points = float(question.get("points") or 1)
        if correct:
            earned += points
        review.append({
            "question_id": question["id"],
            "correct": correct,
            "correct_answer": expected,
            "explanation": question.get("explanation"),
            "points_earned": points if correct else 0,
            "points_possible": points,
        })
    score = round((earned / total_points) * 100, 2) if total_points else 0
    passing_score = effective_passing_score(quiz)
    passed = score >= passing_score
    now = datetime.now(timezone.utc).isoformat()
    inserted = (supabase.table("quiz_attempts").insert({
        "quiz_id": quiz_id,
        "user_id": user.id,
        "score": score,
        "passed": passed,
        "answers": body.answers,
        "started_at": now,
        "submitted_at": now,
    }).execute())
    if not inserted.data:
        raise HTTPException(500, "Unable to save quiz attempt.")
    try:
        supabase.table("quiz_active_sessions").delete().eq("id", str(body.session_id)).eq("user_id", str(user.id)).eq("quiz_id", str(quiz_id)).execute()
    except Exception as exc:
        print(f"Completed quiz session cleanup deferred: {type(exc).__name__}")
    return {"success": True, "attempt": inserted.data[0], "review": review, "passing_score": passing_score}


@router.delete("/quizzes/{quiz_id}/session/{session_id}")
def close_quiz_session(quiz_id: str, session_id: str, user: CurrentUser = Depends(get_current_user)):
    supabase.table("quiz_active_sessions").delete().eq("id", str(session_id)).eq("user_id", str(user.id)).eq("quiz_id", str(quiz_id)).execute()
    return {"success": True}


@router.get("/assignments/{assignment_id}")
def get_assignment(assignment_id: str, user: CurrentUser = Depends(get_current_user)):
    result = (supabase.table("assignments")
        .select("id,lesson_id,course_id,title,description,instructions,due_date,max_score,is_published")
        .eq("id", assignment_id).eq("is_published", True).limit(1).execute())
    if not result.data:
        raise HTTPException(404, "Published assignment not found.")
    assignment = result.data[0]
    if not _enrolment(str(user.id), str(assignment["course_id"])):
        raise HTTPException(403, "You are not enrolled in this course.")
    if assignment.get("lesson_id"):
        _assert_module_unlocked(str(user.id), _module_for_lesson(str(assignment["lesson_id"])))
    submissions = (supabase.table("assignment_submissions")
        .select("id,submission_text,file_url,status,score,feedback,submitted_at,graded_at")
        .eq("assignment_id", assignment_id).eq("user_id", user.id)
        .order("submitted_at", desc=True).limit(10).execute()).data or []
    return {"success": True, "assignment": assignment, "submissions": submissions}


@router.post("/assignments/{assignment_id}/submissions", status_code=201)
def submit_assignment(assignment_id: str, body: AssignmentSubmissionIn, user: CurrentUser = Depends(get_current_user)):
    result = (supabase.table("assignments")
        .select("id,lesson_id,course_id,is_published")
        .eq("id", assignment_id).eq("is_published", True).limit(1).execute())
    if not result.data:
        raise HTTPException(404, "Published assignment not found.")
    assignment = result.data[0]
    if not _enrolment(str(user.id), str(assignment["course_id"])):
        raise HTTPException(403, "You are not enrolled in this course.")
    if assignment.get("lesson_id"):
        _assert_module_unlocked(str(user.id), _module_for_lesson(str(assignment["lesson_id"])))
    file_url = body.file_url.strip() if body.file_url else None
    if file_url and not file_url.startswith("https://"):
        raise HTTPException(400, "Submission links must use HTTPS.")
    if not body.submission_text.strip() and not file_url:
        raise HTTPException(400, "Add a written response or an HTTPS link before submitting.")
    now = datetime.now(timezone.utc).isoformat()
    inserted = (supabase.table("assignment_submissions").insert({
        "assignment_id": assignment_id,
        "user_id": user.id,
        "submission_text": body.submission_text,
        "file_url": file_url,
        "status": "submitted",
        "submitted_at": now,
    }).execute())
    if not inserted.data:
        raise HTTPException(500, "Unable to save assignment submission.")
    return {"success": True, "submission": inserted.data[0]}


@router.get("/me")
def my_progress(
    user: CurrentUser = Depends(get_current_user),
):
    enrolments = (
        supabase
        .table("learnora_enrolments")
        .select(
            "id,course_id,organisation_id,cohort_id,status,"
            "enrolled_at,completed_at"
        )
        .eq("user_id", user.id)
        .in_("status", ["active", "completed"])
        .order("enrolled_at", desc=True)
        .execute()
    ).data or []

    course_ids = [row["course_id"] for row in enrolments]

    courses = []
    if course_ids:
        courses = (
            supabase
            .table("learnora_courses")
            .select(
                "id,title,slug,short_description,level,status,"
                "ownership,thumbnail_url,estimated_hours"
            )
            .in_("id", course_ids)
            .execute()
        ).data or []

    course_map = {
        str(row["id"]): row
        for row in courses
    }

    progress_rows = (
        supabase
        .table("learnora_lesson_progress")
        .select(
            "lesson_id,progress_percent,completed,"
            "last_accessed_at"
        )
        .eq("user_id", user.id)
        .execute()
    ).data or []

    lesson_ids = [row["lesson_id"] for row in progress_rows]

    lesson_course_map = {}
    if lesson_ids:
        lessons = (
            supabase
            .table("learnora_lessons")
            .select(
                "id,course_modules!inner(course_id)"
            )
            .in_("id", lesson_ids)
            .execute()
        ).data or []

        lesson_course_map = {
            str(row["id"]): str(row["course_modules"]["course_id"])
            for row in lessons
        }

    summaries = []
    for enrolment in enrolments:
        course_id = str(enrolment["course_id"])
        rows = [
            row
            for row in progress_rows
            if lesson_course_map.get(str(row["lesson_id"])) == course_id
        ]
        completed = sum(1 for row in rows if row.get("completed"))

        summaries.append({
            "enrolment": enrolment,
            "course": course_map.get(course_id),
            "completed_lessons": completed,
            "tracked_lessons": len(rows),
        })

    return {
        "success": True,
        "courses": summaries,
    }


@router.get("/courses/{course_id}")
def course_progress(
    course_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    return {
        "success": True,
        "progress": _course_summary(
            str(user.id),
            course_id,
        ),
    }


@router.get("/lessons/{lesson_id}/media")
def lesson_media(
    lesson_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    course_id = _course_for_lesson(lesson_id)
    if not _enrolment(str(user.id), course_id):
        raise HTTPException(403, "You are not enrolled in this course.")
    _assert_module_unlocked(str(user.id), _module_for_lesson(lesson_id))

    videos = (
        supabase.table("lesson_videos")
        .select("*")
        .eq("lesson_id", lesson_id)
        .order("created_at", desc=True)
        .execute()
    ).data or []

    for video in videos:
        video["signed_url"] = None
        if video.get("provider") == "supabase" and video.get("storage_path"):
            try:
                signed = supabase.storage.from_("learnora-course-media").create_signed_url(
                    video["storage_path"],
                    3600,
                )
                data = getattr(signed, "data", None) or signed
                if isinstance(data, dict):
                    video["signed_url"] = data.get("signedUrl") or data.get("signed_url")
            except Exception:
                video["signed_url"] = None

    resources = (
        supabase.table("lesson_resources")
        .select("*")
        .eq("lesson_id", lesson_id)
        .order("created_at", desc=True)
        .execute()
    ).data or []

    for resource in resources:
        resource["signed_url"] = None
        if resource.get("storage_path"):
            try:
                signed = supabase.storage.from_("learnora-course-media").create_signed_url(
                    resource["storage_path"],
                    3600,
                )
                data = getattr(signed, "data", None) or signed
                if isinstance(data, dict):
                    resource["signed_url"] = data.get("signedUrl") or data.get("signed_url")
            except Exception:
                resource["signed_url"] = None

    return {
        "success": True,
        "lesson_id": lesson_id,
        "videos": videos,
        "resources": resources,
    }


@router.put("/lessons/{lesson_id}")
def update_lesson_progress(
    lesson_id: str,
    body: LessonProgressIn,
    user: CurrentUser = Depends(get_current_user),
):
    course_id = _course_for_lesson(lesson_id)
    enrolment = _enrolment(str(user.id), course_id)

    if not enrolment:
        raise HTTPException(
            403,
            "You are not enrolled in this course.",
        )
    _assert_module_unlocked(str(user.id), _module_for_lesson(lesson_id))

    now = datetime.now(timezone.utc).isoformat()

    completed = bool(
        body.completed
        or body.progress_percent >= 100
    )
    percent = 100 if completed else body.progress_percent

    existing = (
        supabase
        .table("learnora_lesson_progress")
        .select("id,first_started_at")
        .eq("user_id", user.id)
        .eq("lesson_id", lesson_id)
        .limit(1)
        .execute()
    )

    payload = {
        "user_id": user.id,
        "lesson_id": lesson_id,
        "enrolment_id": enrolment["id"],
        "progress_percent": percent,
        "completed": completed,
        "last_position_seconds": body.last_position_seconds,
        "last_accessed_at": now,
        "completed_at": now if completed else None,
    }

    if not existing.data:
        payload["first_started_at"] = now
        result = (
            supabase
            .table("learnora_lesson_progress")
            .insert(payload)
            .execute()
        )
    else:
        result = (
            supabase
            .table("learnora_lesson_progress")
            .update(payload)
            .eq("id", existing.data[0]["id"])
            .execute()
        )

    if not result.data:
        raise HTTPException(
            500,
            "Unable to save lesson progress.",
        )

    summary = _course_summary(
        str(user.id),
        course_id,
    )

    if summary["completed"] and enrolment["status"] == "active":
        completed_at = datetime.now(timezone.utc).isoformat()
        updated = (
            supabase
            .table("learnora_enrolments")
            .update({
                "status": "completed",
                "completed_at": completed_at,
            })
            .eq("id", enrolment["id"])
            .eq("status", "active")
            .execute()
        )
        if updated.data:
            summary["enrolment"] = updated.data[0]

    return {
        "success": True,
        "progress": result.data[0],
        "course_progress": summary,
    }



@router.get("/tracks/{track_id}")
def track_progress(
    track_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    """Calculate public track progress from required course completions."""
    if not is_individual_learner(user.role, user.account_type, getattr(user, "organisation_id", None)):
        raise HTTPException(403, "Public track progress is available to individual learner accounts.")
    try:
        track_id = str(UUID(track_id))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(404, "Track not found.") from None

    track_result = (
        supabase.table("learnora_learning_paths")
        .select("id,name,slug,description,status,owner_user_id,organisation_id")
        .eq("id", track_id)
        .is_("owner_user_id", "null")
        .is_("organisation_id", "null")
        .limit(1)
        .execute()
    )
    if not track_result.data:
        raise HTTPException(404, "Track not found.")
    track = track_result.data[0]

    links = (
        supabase.table("learnora_learning_path_courses")
        .select("id,course_id,order_index,required")
        .eq("path_id", track_id)
        .order("order_index")
        .execute()
    ).data or []
    course_ids = list(dict.fromkeys(
        str(row["course_id"]) for row in links if row.get("course_id")
    ))
    if not course_ids:
        raise HTTPException(404, "Track not found.")

    course_rows = (
        supabase.table("learnora_courses")
        .select("id,title,slug,short_description,level,status,ownership,organisation_id,thumbnail_url,estimated_hours")
        .in_("id", course_ids)
        .eq("ownership", "learnora")
        .is_("organisation_id", "null")
        .execute()
    ).data or []
    course_map = {str(row["id"]): row for row in course_rows}
    if not course_map:
        raise HTTPException(404, "Track not found.")
    if any(
        link.get("required") is not False
        and str(link.get("course_id")) not in course_map
        for link in links
    ):
        raise HTTPException(404, "Track not found.")

    enrolments = (
        supabase.table("learnora_enrolments")
        .select("id,course_id,status,enrolled_at,completed_at,source_type")
        .eq("user_id", str(user.id))
        .in_("course_id", list(course_map.keys()))
        .in_("status", ["active", "completed"])
        .execute()
    ).data or []
    if track.get("status") != "published":
        track_source = f"track_enrolment:{track_id}"
        enrolments = [row for row in enrolments if row.get("source_type") == track_source]
    enrolment_map = {str(row.get("course_id")): row for row in enrolments}

    course_progress = []
    required_progress = []
    for link in links:
        course_id = str(link.get("course_id"))
        course = course_map.get(course_id)
        if not course:
            continue
        enrolment = enrolment_map.get(course_id)
        summary = _course_summary(str(user.id), course_id, include_archived=course.get("status") != "published") if enrolment else {
            "total_lessons": 0,
            "completed_lessons": 0,
            "progress_percent": 0,
            "completed": False,
        }
        is_required = link.get("required") is not False
        course_completed = bool(
            enrolment
            and (
                enrolment.get("status") == "completed"
                or summary["completed"]
            )
        )
        item = {
            **link,
            "required": is_required,
            "course": course,
            "enrolment": enrolment,
            "enrolled": bool(enrolment),
            "progress": {
                "total_lessons": summary["total_lessons"],
                "completed_lessons": summary["completed_lessons"],
                "progress_percent": 100 if course_completed else summary["progress_percent"],
                "completed": course_completed,
            },
        }
        course_progress.append(item)
        if is_required:
            required_progress.append(item)

    required_count = len(required_progress)
    if track.get("status") != "published" and not any(item["enrolled"] for item in required_progress):
        raise HTTPException(404, "Track not found.")
    completed_required = sum(
        1 for item in required_progress if item["progress"]["completed"]
    )
    progress_percent = (
        round(sum(item["progress"]["progress_percent"] for item in required_progress) / required_count)
        if required_count else 0
    )
    enrolled = bool(required_count) and all(
        item["enrolled"] for item in required_progress
    )
    if track.get("status") != "published":
        enrolled = any(item["enrolled"] for item in required_progress)
    completed = bool(required_count) and completed_required == required_count

    return {
        "success": True,
        "track": track,
        "enrolled": enrolled,
        "completed": completed,
        "progress_percent": progress_percent,
        "completed_required_courses": completed_required,
        "required_courses": required_count,
        "courses": course_progress,
    }


# Legacy-compatible route retained for existing clients. The authenticated
# user's identity is authoritative; a caller cannot request another user's
# progress by changing the email in the URL.
@router.get("/{user_email}/{track_id}")
def legacy_user_progress(
    user_email: str,
    track_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    if user_email.lower().strip() != str(user.email).lower().strip():
        raise HTTPException(
            403,
            "You can only view your own progress.",
        )

    if track_id.lower() == "all":
        return my_progress(user)

    courses = (
        supabase
        .table("learnora_courses")
        .select(
            "id,title,slug,short_description,level,status,ownership"
        )
        .eq("status", "published")
        .execute()
    ).data or []

    selected = [
        course
        for course in courses
        if str(course.get("slug", "")).lower() == track_id.lower()
    ]

    if not selected:
        selected = [
            course
            for course in courses
            if track_id.lower()
            in str(course.get("title", "")).lower()
        ]

    results = []
    for course in selected:
        try:
            summary = _course_summary(
                str(user.id),
                str(course["id"]),
            )
        except HTTPException:
            continue
        results.append(summary)

    return {
        "success": True,
        "track": track_id,
        "courses": results,
    }
