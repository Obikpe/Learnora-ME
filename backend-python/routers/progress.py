"""Persistent Learnora learning progress API.

Progress is stored in Supabase, never in the ephemeral Vercel filesystem.
All writes are scoped to the authenticated learner and an actual enrolment.
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from .auth import CurrentUser, get_current_user, supabase
from .course_content import _has_active_scoped_course_source, _organisation_has_course_entitlement
from services.free_access import is_individual_learner

router = APIRouter(
    prefix="/api/progress",
    tags=["Progress"],
)


class LessonProgressIn(BaseModel):
    progress_percent: int = Field(default=0, ge=0, le=100)
    completed: bool = False
    last_position_seconds: int = Field(default=0, ge=0)


class LearningSessionStartIn(BaseModel):
    timezone: str = Field(default="Africa/Lagos", min_length=1, max_length=64)


class LearningSessionHeartbeatIn(BaseModel):
    active: bool = False


class LessonNoteIn(BaseModel):
    content: str = Field(default="", max_length=20000)


class QuizAttemptIn(BaseModel):
    answers: dict[str, Any] = Field(default_factory=dict)
    session_id: UUID | None = None


class AssignmentSubmissionIn(BaseModel):
    submission_text: str = Field(default="", max_length=20000)
    file_url: Optional[str] = Field(default=None, max_length=2000)


def _lesson_context(lesson_id: str, user_id: str):
    rows = (
        supabase.table("learnora_lessons")
        .select("id,module_id,content,course_modules!inner(course_id)")
        .eq("id", lesson_id)
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        raise HTTPException(404, "Lesson not found.")
    lesson = rows[0]
    course_id = str(lesson["course_modules"]["course_id"])
    if not _enrolment(user_id, course_id):
        raise HTTPException(403, "You are not enrolled in this course.")
    _assert_module_unlocked(user_id, str(lesson["module_id"]))
    return lesson, course_id


def _sign_lesson_assets(rows: list[dict], require_supabase_provider: bool = False):
    for row in rows:
        row["signed_url"] = None
        if not row.get("storage_path"):
            continue
        if require_supabase_provider and row.get("provider") != "supabase":
            continue
        try:
            signed = supabase.storage.from_("learnora-course-media").create_signed_url(
                row["storage_path"],
                3600,
            )
            data = getattr(signed, "data", None) or signed
            if isinstance(data, dict):
                row["signed_url"] = data.get("signedUrl") or data.get("signed_url")
        except Exception:
            row["signed_url"] = None
    return rows


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
    """Return only an enrolment valid for the learner's current access scope.

    Cohort identities use the dedicated cohort-learning API. Organisation
    learners must have an active tenant membership and an active scoped
    assignment or organisation-wide assigned-course grant. A personal
    enrolment must never become an organisation learner's access token.
    """
    try:
        cohort_account = (
            supabase.table("cohort_accounts")
            .select("id")
            .eq("id", user_id)
            .eq("status", "active")
            .limit(1)
            .execute()
        ).data or []
        if cohort_account:
            return None

        active_memberships = (
            supabase.table("organisation_members")
            .select("organisation_id,role")
            .eq("user_id", user_id)
            .eq("status", "active")
            .execute()
        ).data or []
        if any(str(row.get("role") or "").lower() in {"owner", "admin", "team_manager"} for row in active_memberships):
            return None
        memberships = [
            row for row in active_memberships
            if str(row.get("role") or "").lower() in {"learner", "member"}
        ]

        cohort_memberships = (
            supabase.table("cohort_members")
            .select("id,cohort_id")
            .eq("user_id", user_id)
            .eq("status", "active")
            .limit(10)
            .execute()
        ).data or []
        identity = (
            supabase.table("users")
            .select("role")
            .eq("id", user_id)
            .limit(1)
            .execute()
        ).data or []
        legacy_cohort_learner = bool(cohort_memberships) or bool(
            identity and str(identity[0].get("role") or "").strip().lower() == "witstart"
        )

        query = (
            supabase.table("learnora_enrolments")
            .select(
                "id,user_id,course_id,organisation_id,cohort_id,status,"
                "enrolled_at,completed_at,source_type"
            )
            .eq("user_id", user_id)
            .eq("course_id", course_id)
            .in_("status", ["active", "completed"])
            .order("enrolled_at", desc=True)
        )
        enrolments = query.execute().data or []
    except Exception as exc:
        print(f"Course enrolment scope lookup failed: {type(exc).__name__}")
        raise HTTPException(503, "Course access could not be verified. Please retry.") from None

    if legacy_cohort_learner:
        # Legacy cohort learners are backed by public.users + cohort_members.
        # Their organisation-wide course grants must not bypass the cohort's
        # explicit course assignment.
        for membership in memberships:
            organisation_id = str(membership.get("organisation_id") or "")
            if not organisation_id:
                continue
            for enrolment in enrolments:
                if str(enrolment.get("organisation_id") or "") != organisation_id:
                    continue
                if _has_active_scoped_course_source(user_id, organisation_id, course_id, enrolment):
                    return enrolment
        return None

    if memberships:
        for membership in memberships:
            organisation_id = str(membership.get("organisation_id") or "")
            if not organisation_id:
                continue
            for enrolment in enrolments:
                if str(enrolment.get("organisation_id") or "") != organisation_id:
                    continue
                if _has_active_scoped_course_source(user_id, organisation_id, course_id, enrolment):
                    return enrolment
                try:
                    assigned_grant = (
                        supabase.table("course_access")
                        .select("id")
                        .eq("course_id", course_id)
                        .eq("organisation_id", organisation_id)
                        .eq("status", "active")
                        .eq("access_type", "assigned")
                        .limit(1)
                        .execute()
                    ).data or []
                    active_organisation = (
                        supabase.table("organisations")
                        .select("id")
                        .eq("id", organisation_id)
                        .eq("is_active", True)
                        .limit(1)
                        .execute()
                    ).data or []
                except Exception as exc:
                    print(f"Organisation course grant lookup failed: {type(exc).__name__}")
                    raise HTTPException(503, "Organisation course access could not be verified. Please retry.") from None
                if assigned_grant and active_organisation and _organisation_has_course_entitlement(organisation_id):
                    return enrolment
        return None

    # A learner without an active organisation membership may use only a
    # global individual enrolment. Legacy cohort identities and cohort
    # members without an active organisation learner membership must use
    # their assigned cohort access path instead.
    if cohort_memberships:
        return None
    if not identity or not is_individual_learner(identity[0].get("role"), "learner", None):
        return None
    return next((
        row for row in enrolments
        if row.get("organisation_id") is None and row.get("cohort_id") is None
    ), None)


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


def _module_for_quiz(quiz: dict):
    """Resolve a quiz's module from its explicit module or lesson association."""
    if quiz.get("module_id"):
        return str(quiz["module_id"])
    if quiz.get("lesson_id"):
        return _module_for_lesson(str(quiz["lesson_id"]))
    return None


def _module_unlock_states(user_id: str, modules: list[dict], lessons: list[dict], quiz_rows: list[dict] | None = None, attempt_rows: list[dict] | None = None):
    """Calculate module locks with bounded queries instead of querying once per module/quiz."""
    ordered = sorted(modules, key=lambda row: int(row.get("order_index") or 0))
    module_ids = [str(row["id"]) for row in ordered if row.get("id")]
    if not module_ids:
        return {}, {}

    module_by_lesson = {
        str(row["id"]): str(row["module_id"])
        for row in lessons
        if row.get("id") and row.get("module_id")
    }
    lesson_ids = list(module_by_lesson)
    if quiz_rows is None:
        module_quizzes = (
            supabase.table("quizzes")
            .select("id,title,passing_score,module_id,lesson_id")
            .in_("module_id", module_ids)
            .eq("is_published", True)
            .execute()
        ).data or []
        lesson_quizzes = []
        if lesson_ids:
            lesson_quizzes = (
                supabase.table("quizzes")
                .select("id,title,passing_score,module_id,lesson_id")
                .in_("lesson_id", lesson_ids)
                .eq("is_published", True)
                .execute()
            ).data or []
        quiz_source = module_quizzes + lesson_quizzes
    else:
        quiz_source = quiz_rows

    quiz_by_id = {str(row["id"]): row for row in quiz_source if row.get("id")}
    quiz_ids = list(quiz_by_id)
    if attempt_rows is None:
        attempts = []
        if quiz_ids:
            attempts = (
                supabase.table("quiz_attempts")
                .select("quiz_id,score,passed")
                .eq("user_id", user_id)
                .in_("quiz_id", quiz_ids)
                .eq("passed", True)
                .execute()
            ).data or []
    else:
        attempts = attempt_rows
    passed_ids = {
        str(attempt["quiz_id"])
        for attempt in attempts
        if attempt.get("quiz_id")
    }

    quizzes_by_module: dict[str, dict[str, dict]] = {}
    valid_modules = set(module_ids)
    for quiz in quiz_by_id.values():
        module_id = str(quiz.get("module_id") or module_by_lesson.get(str(quiz.get("lesson_id") or "")) or "")
        if module_id in valid_modules:
            quizzes_by_module.setdefault(module_id, {})[str(quiz["id"])] = quiz

    locked: dict[str, bool] = {}
    blocked_by: dict[str, dict] = {}
    access_available = True
    blocker = None
    for module in ordered:
        module_id = str(module["id"])
        locked[module_id] = not access_available
        if not access_available and blocker:
            blocked_by[module_id] = blocker
            continue
        quizzes = list(quizzes_by_module.get(module_id, {}).values())
        if not quizzes:
            access_available = False
            blocker = {"module": module, "reason": "missing_quiz", "threshold": None}
            continue
        failed = next(
            (
                quiz for quiz in quizzes
                if str(quiz["id"]) not in passed_ids
                or not any(
                    str(attempt.get("quiz_id")) == str(quiz["id"])
                    and attempt.get("passed") is True
                    and float(attempt.get("score") or 0) >= effective_passing_score(quiz)
                    for attempt in attempts
                )
            ),
            None,
        )
        if failed:
            access_available = False
            blocker = {
                "module": module,
                "reason": "failed_quiz",
                "threshold": effective_passing_score(failed),
            }
    return locked, blocked_by


def _assert_module_unlocked(user_id: str, module_id: str, include_archived: bool = False):
    """Require a passed >=70% assessment for every earlier module."""
    current = (
        supabase.table("course_modules")
        .select("id,course_id,title,order_index,status")
        .eq("id", module_id)
        .limit(1)
        .execute()
    ).data or []
    if not current:
        raise HTTPException(404, "Module not found.")
    module = current[0]
    previous_query = (
        supabase.table("course_modules")
        .select("id,title,order_index,status")
        .eq("course_id", module["course_id"])
        .lt("order_index", module["order_index"])
    )
    previous_query = (
        previous_query.in_("status", ["published", "archived"])
        if include_archived
        else previous_query.eq("status", "published")
    )
    previous_modules = previous_query.order("order_index").execute().data or []
    if not previous_modules:
        return

    previous_ids = [str(row["id"]) for row in previous_modules]
    lessons = (
        supabase.table("learnora_lessons")
        .select("id,module_id")
        .in_("module_id", previous_ids)
        .execute()
    ).data or []
    ordered = previous_modules + [module]
    locked, blocked_by = _module_unlock_states(user_id, ordered, lessons)
    if not locked.get(str(module_id)):
        return

    blocker = blocked_by.get(str(module_id)) or {}
    previous = blocker.get("module") or previous_modules[-1]
    title = previous.get("title") or "the previous module"
    if blocker.get("reason") == "missing_quiz":
        raise HTTPException(
            423,
            f'Complete the published assessment for "{title}" before moving on. The module is not unlocked because it has no published quiz yet.',
        )
    threshold = float(blocker.get("threshold") or 70)
    raise HTTPException(
        423,
        f'Pass the assessment for "{title}" with at least {threshold:g}% to unlock the next module.',
    )


def _course_assessment_summary(user_id: str, course_id: str):
    """Completion gates for published quizzes and manually graded assignments."""
    quizzes = (
        supabase.table("quizzes")
        .select("id,title,passing_score,module_id,lesson_id")
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
        "_quiz_rows": quizzes,
        "_quiz_attempt_rows": attempts,
    }


def _sync_enrolment_completion(user_id: str, course_id: str, include_archived: bool = False, include_lesson_content: bool = True):
    """Persist verified course completion on the learner's enrolment row."""
    summary = _course_summary(user_id, course_id, include_archived=include_archived, include_lesson_content=include_lesson_content)
    enrolment = summary.get("enrolment") or {}
    if summary.get("completed") and enrolment.get("status") == "active":
        completed_at = datetime.now(timezone.utc).isoformat()
        saved = (
            supabase.table("learnora_enrolments")
            .update({"status": "completed", "completed_at": completed_at})
            .eq("id", str(enrolment["id"]))
            .eq("user_id", user_id)
            .eq("status", "active")
            .execute()
        ).data or []
        if saved:
            summary["enrolment"] = saved[0]
        else:
            latest = (
                supabase.table("learnora_enrolments")
                .select("id,status,enrolled_at,completed_at")
                .eq("id", str(enrolment["id"]))
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            ).data or []
            if latest:
                summary["enrolment"] = {**enrolment, **latest[0]}
    return summary


def _course_summary(user_id: str, course_id: str, include_archived: bool = False, include_lesson_content: bool = True):
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
                + ("content," if include_lesson_content else "")
                + "duration_minutes,status"
            )
            .in_("module_id", module_ids)
        )
        lesson_query = (
            lesson_query.in_("status", ["published", "archived"])
            if include_archived
            else lesson_query.eq("status", "published")
        )
        lessons = lesson_query.order("order_index").execute().data or []

    lesson_ids = [str(row["id"]) for row in lessons if row.get("id")]
    progress = []
    if lesson_ids:
        progress = (
            supabase
            .table("learnora_lesson_progress")
            .select(
                "lesson_id,progress_percent,completed,"
                "last_position_seconds,first_started_at,"
                "last_accessed_at,completed_at"
            )
            .eq("user_id", user_id)
            .in_("lesson_id", lesson_ids)
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
    quiz_rows = assessment_summary.pop("_quiz_rows", [])
    quiz_attempt_rows = assessment_summary.pop("_quiz_attempt_rows", [])
    total_units = total + assessment_summary["total_assessments"]
    completed_units = completed + assessment_summary["completed_assessments"]
    percent = round((completed_units / total_units) * 100) if total_units else 0

    module_locks, _ = _module_unlock_states(user_id, modules, lessons, quiz_rows, quiz_attempt_rows)
    module_views = []
    for module in modules:
        locked = bool(module_locks.get(str(module["id"]), False))
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


def _learning_account_type(user: CurrentUser) -> str:
    return "cohort" if getattr(user, "account_type", "") == "cohort" else "individual"


def _validated_timezone(value: str | None) -> str:
    candidate = (value or "Africa/Lagos").strip()
    try:
        ZoneInfo(candidate)
        return candidate
    except (ZoneInfoNotFoundError, ValueError):
        return "Africa/Lagos"


def _record_learning_day(user: CurrentUser, activity_type: str) -> None:
    """Record only server-verified learning events; never trust a browser date."""
    account_type = _learning_account_type(user)
    timezone_name = "Africa/Lagos"
    try:
        sessions = (
            supabase.table("learning_sessions")
            .select("timezone")
            .eq("learner_id", str(user.id))
            .eq("account_type", account_type)
            .order("started_at", desc=True)
            .limit(1)
            .execute()
        ).data or []
        if sessions:
            timezone_name = _validated_timezone(sessions[0].get("timezone"))
        now = datetime.now(timezone.utc)
        activity_date = now.astimezone(ZoneInfo(timezone_name)).date().isoformat()
        supabase.rpc("record_learner_learning_day", {
            "p_learner_id": str(user.id),
            "p_account_type": account_type,
            "p_activity_date": activity_date,
            "p_timezone": timezone_name,
            "p_activity_type": activity_type,
            "p_activity_at": now.isoformat(),
        }).execute()
    except Exception as exc:
        # Tracking failure must never prevent a learner from completing learning.
        print(f"Learning-day record failed: {type(exc).__name__}")


def _rpc_integer(result, default: int = 0) -> int:
    value = getattr(result, "data", default)
    if isinstance(value, list):
        value = value[0] if value else default
    if isinstance(value, dict):
        value = next(iter(value.values()), default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@router.post("/learning-sessions/start", status_code=201)
def start_learning_session(body: LearningSessionStartIn, user: CurrentUser = Depends(get_current_user)):
    account_type = _learning_account_type(user)
    timezone_name = _validated_timezone(body.timezone)
    try:
        result = supabase.rpc("start_learner_learning_session", {
            "p_learner_id": str(user.id),
            "p_account_type": account_type,
            "p_timezone": timezone_name,
        }).execute()
        session = getattr(result, "data", None)
        if isinstance(session, list):
            session = session[0] if session else None
        if not isinstance(session, dict) or not session.get("id"):
            raise RuntimeError("Session start RPC returned no session")
        return {"success": True, "session": session}
    except Exception as exc:
        print(f"Learning session start failed: {type(exc).__name__}")
        raise HTTPException(503, "Learning-time tracking is temporarily unavailable.") from None


@router.post("/learning-sessions/{session_id}/heartbeat")
def heartbeat_learning_session(session_id: UUID, body: LearningSessionHeartbeatIn, user: CurrentUser = Depends(get_current_user)):
    account_type = _learning_account_type(user)
    try:
        result = supabase.rpc("heartbeat_learner_learning_session", {
            "p_session_id": str(session_id),
            "p_learner_id": str(user.id),
            "p_account_type": account_type,
            "p_active": bool(body.active),
        }).execute()
        counted = _rpc_integer(result, -1)
        if counted < 0:
            raise HTTPException(404, "Learning session not found.")
        return {"success": True, "counted_seconds": counted}
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Learning session heartbeat failed: {type(exc).__name__}")
        raise HTTPException(503, "Learning-time tracking is temporarily unavailable.") from None


@router.post("/learning-sessions/{session_id}/end")
def end_learning_session(session_id: UUID, body: LearningSessionHeartbeatIn, user: CurrentUser = Depends(get_current_user)):
    account_type = _learning_account_type(user)
    try:
        result = supabase.rpc("end_learner_learning_session", {
            "p_session_id": str(session_id),
            "p_learner_id": str(user.id),
            "p_account_type": account_type,
            "p_active": bool(body.active),
        }).execute()
        return {"success": True, "counted_seconds": max(0, _rpc_integer(result))}
    except Exception as exc:
        print(f"Learning session end failed: {type(exc).__name__}")
        raise HTTPException(503, "Learning-time tracking is temporarily unavailable.") from None


@router.get("/learning-summary")
def learning_summary(timezone_name: str = Query(default="Africa/Lagos", alias="timezone"), user: CurrentUser = Depends(get_current_user)):
    timezone_name = _validated_timezone(timezone_name)
    account_type = _learning_account_type(user)
    latest_session = (supabase.table("learning_sessions").select("timezone")
        .eq("learner_id", str(user.id)).eq("account_type", account_type)
        .order("started_at", desc=True).limit(1).execute()).data or []
    if latest_session:
        timezone_name = _validated_timezone(latest_session[0].get("timezone"))
    seconds_result = supabase.rpc("get_learner_learning_seconds", {
        "p_learner_id": str(user.id),
        "p_account_type": account_type,
    }).execute()
    seconds_data = getattr(seconds_result, "data", 0)
    if isinstance(seconds_data, list) and seconds_data:
        seconds_data = next(iter(seconds_data[0].values())) if isinstance(seconds_data[0], dict) else seconds_data[0]
    if isinstance(seconds_data, dict):
        seconds_data = next(iter(seconds_data.values()), 0)
    total_learning_seconds = max(0, int(seconds_data or 0))
    days = (supabase.table("learner_learning_days")
        .select("activity_date,activity_count,activity_types,last_activity_at")
        .eq("learner_id", str(user.id)).eq("account_type", account_type)
        .order("activity_date", desc=True).execute()).data or []
    day_values = {str(row["activity_date"]) for row in days if row.get("activity_date")}
    today = datetime.now(ZoneInfo(timezone_name)).date()
    anchor = today if today.isoformat() in day_values else today - timedelta(days=1)
    streak = 0
    cursor = anchor
    while cursor.isoformat() in day_values:
        streak += 1
        cursor -= timedelta(days=1)
    longest = 0
    run = 0
    previous = None
    for value in sorted(day_values):
        current = datetime.fromisoformat(value).date()
        run = run + 1 if previous and current == previous + timedelta(days=1) else 1
        longest = max(longest, run)
        previous = current
    return {
        "success": True,
        "learning_time_seconds": total_learning_seconds,
        "current_streak": streak,
        "longest_streak": longest,
        "learning_days": days,
        "timezone": timezone_name,
    }


@router.get("/lessons/{lesson_id}/content")
def get_lesson_content(
    lesson_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    lesson, _course_id = _lesson_context(lesson_id, str(user.id))
    return {
        "success": True,
        "lesson_id": str(lesson["id"]),
        "content": lesson.get("content") or "",
    }


@router.get("/lessons/{lesson_id}/workspace")
def get_lesson_workspace(
    lesson_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    lesson, _course_id = _lesson_context(lesson_id, str(user.id))
    note_rows = (
        supabase.table("learner_lesson_notes")
        .select("id,content,created_at,updated_at")
        .eq("user_id", user.id)
        .eq("lesson_id", lesson_id)
        .limit(1)
        .execute()
    ).data or []
    videos = (
        supabase.table("lesson_videos")
        .select("*")
        .eq("lesson_id", lesson_id)
        .order("created_at", desc=True)
        .execute()
    ).data or []
    resources = (
        supabase.table("lesson_resources")
        .select("*")
        .eq("lesson_id", lesson_id)
        .order("created_at", desc=True)
        .execute()
    ).data or []
    _sign_lesson_assets(videos, require_supabase_provider=True)
    _sign_lesson_assets(resources)
    return {
        "success": True,
        "lesson_id": str(lesson["id"]),
        "content": lesson.get("content") or "",
        "note": note_rows[0] if note_rows else None,
        "videos": videos,
        "resources": resources,
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
        .select("id,lesson_id,module_id,title,description,passing_score,max_attempts")
        .eq("course_id", course_id).eq("is_published", True)
        .order("created_at").execute()).data or []
    missing_module_lessons = list({
        str(row["lesson_id"]) for row in quizzes
        if row.get("lesson_id") and not row.get("module_id")
    })
    if missing_module_lessons:
        lesson_rows = (supabase.table("learnora_lessons")
            .select("id,module_id")
            .in_("id", missing_module_lessons)
            .execute()).data or []
        module_by_lesson = {str(row["id"]): str(row["module_id"]) for row in lesson_rows}
        for quiz in quizzes:
            if not quiz.get("module_id") and quiz.get("lesson_id"):
                quiz["module_id"] = module_by_lesson.get(str(quiz["lesson_id"]))
    assignments = (supabase.table("assignments")
        .select("id,lesson_id,title,description,instructions,due_date,max_score")
        .eq("course_id", course_id).eq("is_published", True)
        .order("created_at").execute()).data or []
    projects = (supabase.table("projects")
        .select("id,course_id,title,description,instructions,skills")
        .eq("course_id", course_id).eq("is_published", True)
        .order("created_at").execute()).data or []
    return {"success": True, "quizzes": quizzes, "assignments": assignments, "projects": projects}


@router.get("/quiz-sessions/me")
def my_active_quiz_session(user: CurrentUser = Depends(get_current_user)):
    try:
        rows = (supabase.table("quiz_active_sessions")
            .select("id,quiz_id,course_id,client_session_id,expires_at")
            .eq("user_id", str(user.id))
            .gt("expires_at", datetime.now(timezone.utc).isoformat())
            .order("expires_at", desc=True)
            .limit(50)
            .execute()).data or []
    except Exception as exc:
        print(f"Active quiz session lookup failed: {type(exc).__name__}")
        raise HTTPException(503, "Assessment access could not be verified. Please retry.") from None
    return {"active": bool(rows), "sessions": rows}


@router.get("/quizzes/{quiz_id}")
def get_quiz(quiz_id: str, client_session_id: UUID = Query(...), user: CurrentUser = Depends(get_current_user)):
    result = (supabase.table("quizzes")
        .select("id,lesson_id,module_id,course_id,title,description,passing_score,max_attempts,is_published")
        .eq("id", quiz_id).eq("is_published", True).limit(1).execute())
    if not result.data:
        raise HTTPException(404, "Published quiz not found.")
    quiz = result.data[0]
    if not _enrolment(str(user.id), str(quiz["course_id"])):
        raise HTTPException(403, "You are not enrolled in this course.")
    quiz_module_id = _module_for_quiz(quiz)
    if quiz_module_id:
        _assert_module_unlocked(str(user.id), quiz_module_id)
    questions = (supabase.table("quiz_questions")
        .select("id,question,question_type,options,points,order_index")
        .eq("quiz_id", quiz_id).order("order_index").execute()).data or []
    attempts = (supabase.table("quiz_attempts")
        .select("id,score,passed,submitted_at")
        .eq("quiz_id", quiz_id).eq("user_id", user.id)
        .order("submitted_at", desc=True).execute()).data or []
    now = datetime.now(timezone.utc)
    try:
        session_rows = supabase.table("quiz_active_sessions").upsert({
            "user_id": str(user.id),
            "quiz_id": str(quiz_id),
            "client_session_id": str(client_session_id),
            "course_id": str(quiz["course_id"]),
            "lesson_id": str(quiz.get("lesson_id")) if quiz.get("lesson_id") else None,
            "started_at": now.isoformat(),
            "expires_at": (now + timedelta(hours=2)).isoformat(),
        }, on_conflict="user_id,quiz_id,client_session_id").select("id").execute().data or []
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
    quiz_module_id = _module_for_quiz(quiz)
    if quiz_module_id:
        _assert_module_unlocked(str(user.id), quiz_module_id)
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
    if passed:
        _record_learning_day(user, "quiz_passed")
    course_progress = _sync_enrolment_completion(str(user.id), str(quiz["course_id"]), include_lesson_content=False)
    return {"success": True, "attempt": inserted.data[0], "review": review, "passing_score": passing_score, "course_progress": course_progress}


@router.delete("/quizzes/{quiz_id}/session/{session_id}")
def close_quiz_session(quiz_id: str, session_id: str, user: CurrentUser = Depends(get_current_user)):
    sessions = (
        supabase.table("quiz_active_sessions")
        .select("id,started_at")
        .eq("id", str(session_id))
        .eq("user_id", str(user.id))
        .eq("quiz_id", str(quiz_id))
        .limit(1)
        .execute()
    ).data or []
    if not sessions:
        return {"success": True, "already_closed": True}

    # Only a submitted attempt created after this session started can release
    # the server-side tutor lock. Directly calling this endpoint mid-quiz
    # must not restore access to the AI tutor.
    attempts = (
        supabase.table("quiz_attempts")
        .select("id")
        .eq("user_id", str(user.id))
        .eq("quiz_id", str(quiz_id))
        .gt("submitted_at", str(sessions[0].get("started_at") or ""))
        .limit(1)
        .execute()
    ).data or []
    if not attempts:
        raise HTTPException(409, "Submit the quiz before ending its active session.")

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
    _record_learning_day(user, "assignment_submitted")
    return {"success": True, "submission": inserted.data[0]}


@router.get("/me")
def my_progress(
    user: CurrentUser = Depends(get_current_user),
):
    enrolments = (
        supabase
        .table("learnora_enrolments")
        .select(
            "id,course_id,organisation_id,cohort_id,status,source_type,"
            "enrolled_at,completed_at"
        )
        .eq("user_id", user.id)
        .in_("status", ["active", "completed"])
        .order("enrolled_at", desc=True)
        .execute()
    ).data or []

    # The dashboard list must apply the same server-side access-scope check
    # as lesson, quiz, assignment and media endpoints.
    enrolments = [
        row for row in enrolments
        if row.get("course_id") and _enrolment(str(user.id), str(row["course_id"]))
    ]

    course_ids = list(dict.fromkeys(str(row["course_id"]) for row in enrolments if row.get("course_id")))
    if not course_ids:
        return {"success": True, "courses": [], "in_progress_count": 0, "completed_count": 0}

    course_rows = (
        supabase.table("learnora_courses")
        .select("id,title,slug,short_description,level,status,ownership,thumbnail_url,estimated_hours")
        .in_("id", course_ids)
        .execute()
    ).data or []
    course_map = {str(row["id"]): row for row in course_rows}

    modules = (
        supabase.table("course_modules")
        .select("id,course_id,title,order_index,status")
        .in_("course_id", course_ids)
        .in_("status", ["published", "archived"])
        .order("order_index")
        .execute()
    ).data or []
    modules_by_course: dict[str, list[dict]] = {}
    module_by_id: dict[str, dict] = {}
    for module in modules:
        module_id = str(module["id"])
        module_by_id[module_id] = module
        modules_by_course.setdefault(str(module["course_id"]), []).append(module)

    module_ids = list(module_by_id)
    lessons = []
    if module_ids:
        lessons = (
            supabase.table("learnora_lessons")
            .select("id,module_id,title,order_index,status")
            .in_("module_id", module_ids)
            .in_("status", ["published", "archived"])
            .order("order_index")
            .execute()
        ).data or []
    lessons_by_module: dict[str, list[dict]] = {}
    lesson_module: dict[str, str] = {}
    for lesson in lessons:
        module_id = str(lesson["module_id"])
        lesson_id = str(lesson["id"])
        course = course_map.get(str(module_by_id[module_id]["course_id"]), {})
        if course.get("status") != "archived" and lesson.get("status") != "published":
            continue
        lessons_by_module.setdefault(module_id, []).append(lesson)
        lesson_module[lesson_id] = module_id
    lesson_ids = list(lesson_module)

    progress_rows = []
    if lesson_ids:
        progress_rows = (
            supabase.table("learnora_lesson_progress")
            .select("lesson_id,completed,last_accessed_at")
            .eq("user_id", user.id)
            .in_("lesson_id", lesson_ids)
            .execute()
        ).data or []
    progress_by_lesson = {
        str(row["lesson_id"]): row
        for row in progress_rows
        if row.get("lesson_id")
    }

    quizzes = (
        supabase.table("quizzes")
        .select("id,course_id,module_id,lesson_id,title,passing_score")
        .in_("course_id", course_ids)
        .eq("is_published", True)
        .execute()
    ).data or []
    quiz_ids = [str(row["id"]) for row in quizzes if row.get("id")]
    quiz_attempts = []
    if quiz_ids:
        quiz_attempts = (
            supabase.table("quiz_attempts")
            .select("quiz_id,score,passed")
            .eq("user_id", user.id)
            .in_("quiz_id", quiz_ids)
            .eq("passed", True)
            .execute()
        ).data or []
    best_quiz_scores: dict[str, float] = {}
    for attempt in quiz_attempts:
        quiz_id = str(attempt.get("quiz_id") or "")
        if quiz_id:
            best_quiz_scores[quiz_id] = max(
                best_quiz_scores.get(quiz_id, 0.0),
                float(attempt.get("score") or 0),
            )
    passed_quiz_ids = {
        str(quiz["id"])
        for quiz in quizzes
        if quiz.get("id")
        and best_quiz_scores.get(str(quiz["id"]), 0.0) >= effective_passing_score(quiz)
    }
    quizzes_by_course: dict[str, list[dict]] = {}
    quizzes_by_module: dict[str, dict[str, dict]] = {}
    for quiz in quizzes:
        course_id = str(quiz.get("course_id") or "")
        quizzes_by_course.setdefault(course_id, []).append(quiz)
        module_id = str(quiz.get("module_id") or lesson_module.get(str(quiz.get("lesson_id") or "")) or "")
        if module_id in module_by_id:
            quizzes_by_module.setdefault(module_id, {})[str(quiz["id"])] = quiz

    assignments = (
        supabase.table("assignments")
        .select("id,course_id,title,max_score")
        .in_("course_id", course_ids)
        .eq("is_published", True)
        .execute()
    ).data or []
    assignment_ids = [str(row["id"]) for row in assignments if row.get("id")]
    submissions = []
    if assignment_ids:
        submissions = (
            supabase.table("assignment_submissions")
            .select("id,assignment_id,status,score,submitted_at,graded_at")
            .eq("user_id", user.id)
            .in_("assignment_id", assignment_ids)
            .order("submitted_at", desc=True)
            .execute()
        ).data or []
    latest_by_assignment: dict[str, dict] = {}
    for submission in submissions:
        assignment_id = str(submission.get("assignment_id") or "")
        if assignment_id and assignment_id not in latest_by_assignment:
            latest_by_assignment[assignment_id] = submission
    assignments_by_course: dict[str, list[dict]] = {}
    passed_assignment_ids: set[str] = set()
    for assignment in assignments:
        course_id = str(assignment.get("course_id") or "")
        assignments_by_course.setdefault(course_id, []).append(assignment)
        submission = latest_by_assignment.get(str(assignment.get("id") or ""))
        if not submission or submission.get("status") != "graded" or not submission.get("graded_at"):
            continue
        maximum = float(assignment.get("max_score") or 100)
        if float(submission.get("score") or 0) >= maximum * 0.7:
            passed_assignment_ids.add(str(assignment["id"]))

    summaries = []
    for enrolment in enrolments:
        course_id = str(enrolment["course_id"])
        course = course_map.get(course_id)
        if not course:
            continue
        course_modules = [
            module for module in modules_by_course.get(course_id, [])
            if course.get("status") == "archived" or module.get("status") == "published"
        ]
        course_lessons = [
            lesson
            for module in course_modules
            for lesson in lessons_by_module.get(str(module["id"]), [])
        ]
        completed_lessons = sum(
            1 for lesson in course_lessons
            if (progress_by_lesson.get(str(lesson["id"])) or {}).get("completed")
        )
        course_quizzes = quizzes_by_course.get(course_id, [])
        course_assignments = assignments_by_course.get(course_id, [])
        completed_quizzes = sum(1 for quiz in course_quizzes if str(quiz["id"]) in passed_quiz_ids)
        completed_assignments = sum(1 for assignment in course_assignments if str(assignment["id"]) in passed_assignment_ids)
        total_assessments = len(course_quizzes) + len(course_assignments)
        completed_assessments = completed_quizzes + completed_assignments
        total_lessons = len(course_lessons)
        total_units = total_lessons + total_assessments
        completed_units = completed_lessons + completed_assessments
        calculated_complete = total_units > 0 and completed_units == total_units

        module_access: dict[str, bool] = {}
        access_available = True
        for module in course_modules:
            module_id = str(module["id"])
            module_access[module_id] = access_available
            if not access_available:
                continue
            module_quiz_rows = list(quizzes_by_module.get(module_id, {}).values())
            if not module_quiz_rows or any(str(quiz["id"]) not in passed_quiz_ids for quiz in module_quiz_rows):
                access_available = False

        next_item = None
        for module in course_modules:
            if not module_access.get(str(module["id"]), False):
                continue
            for lesson in lessons_by_module.get(str(module["id"]), []):
                if not (progress_by_lesson.get(str(lesson["id"])) or {}).get("completed"):
                    next_item = {
                        "type": "lesson",
                        "id": str(lesson["id"]),
                        "title": lesson.get("title") or "Continue lesson",
                    }
                    break
            if next_item:
                break
        if not next_item and completed_assessments < total_assessments:
            next_item = {"type": "assessment", "title": "Complete an outstanding assessment"}

        last_activity = max(
            (
                (progress_by_lesson.get(str(lesson["id"])) or {}).get("last_accessed_at")
                for lesson in course_lessons
                if (progress_by_lesson.get(str(lesson["id"])) or {}).get("last_accessed_at")
            ),
            default=None,
        )
        saved_enrolment = enrolment
        if calculated_complete and enrolment.get("status") == "active":
            saved = (
                supabase.table("learnora_enrolments")
                .update({"status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()})
                .eq("id", str(enrolment["id"]))
                .eq("user_id", str(user.id))
                .eq("status", "active")
                .execute()
            ).data or []
            if saved:
                saved_enrolment = saved[0]
            else:
                latest = (
                    supabase.table("learnora_enrolments")
                    .select("id,status,enrolled_at,completed_at")
                    .eq("id", str(enrolment["id"]))
                    .eq("user_id", str(user.id))
                    .limit(1)
                    .execute()
                ).data or []
                if latest:
                    saved_enrolment = {**enrolment, **latest[0]}

        completed = bool(saved_enrolment.get("status") == "completed" or calculated_complete)
        summaries.append({
            "enrolment": saved_enrolment,
            "course": course,
            "completed": completed,
            "progress_percent": 100 if completed else (round((completed_units / total_units) * 100) if total_units else 0),
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "tracked_lessons": total_lessons,
            "completed_assessments": completed_assessments,
            "total_assessments": total_assessments,
            "last_activity_at": last_activity,
            "last_accessed_item": next((
                {
                    "id": str(lesson["id"]),
                    "title": lesson.get("title") or "Continue lesson",
                    "course_id": course_id,
                    "course_title": course.get("title") or "Your course",
                    "last_accessed_at": (progress_by_lesson.get(str(lesson["id"])) or {}).get("last_accessed_at"),
                }
                for lesson in sorted(
                    course_lessons,
                    key=lambda item: (progress_by_lesson.get(str(item["id"])) or {}).get("last_accessed_at") or "",
                    reverse=True,
                )
                if not (progress_by_lesson.get(str(lesson["id"])) or {}).get("completed")
                and module_access.get(str(lesson_module.get(str(lesson["id"]) or "")), False)
                and (progress_by_lesson.get(str(lesson["id"])) or {}).get("last_accessed_at")
            ), None),
            "next_item": None if completed else next_item,
        })

    recent_unfinished = [
        row["last_accessed_item"]
        for row in summaries
        if row.get("last_accessed_item")
    ]
    recent_unfinished.sort(key=lambda row: row.get("last_accessed_at") or "", reverse=True)

    return {
        "success": True,
        "last_accessed_item": recent_unfinished[0] if recent_unfinished else None,
        "courses": summaries,
        "in_progress_count": sum(1 for row in summaries if not row["completed"]),
        "completed_count": sum(1 for row in summaries if row["completed"]),
    }


@router.get("/courses/{course_id}")
def course_progress(
    course_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    return {
        "success": True,
        "progress": _sync_enrolment_completion(
            str(user.id),
            course_id,
            include_lesson_content=False,
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

    existing = (
        supabase
        .table("learnora_lesson_progress")
        .select("id,first_started_at,completed,completed_at")
        .eq("user_id", user.id)
        .eq("lesson_id", lesson_id)
        .limit(1)
        .execute()
    )

    was_completed = bool(existing.data and existing.data[0].get("completed"))
    completed = completed or was_completed
    percent = 100 if completed else body.progress_percent

    payload = {
        "user_id": user.id,
        "lesson_id": lesson_id,
        "enrolment_id": enrolment["id"],
        "progress_percent": percent,
        "completed": completed,
        "last_position_seconds": body.last_position_seconds,
        "last_accessed_at": now,
        "completed_at": (existing.data[0].get("completed_at") if was_completed else now) if completed else None,
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

    if completed and not was_completed:
        _record_learning_day(user, "lesson_completed")
    summary = _sync_enrolment_completion(str(user.id), course_id, include_lesson_content=False) if completed else None

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
        summary = _sync_enrolment_completion(
            str(user.id),
            course_id,
            include_archived=course.get("status") != "published",
            include_lesson_content=False,
        ) if enrolment else {
            "total_lessons": 0,
            "completed_lessons": 0,
            "progress_percent": 0,
            "completed": False,
        }
        if enrolment:
            enrolment = summary.get("enrolment") or enrolment
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
                include_lesson_content=False,
            )
        except HTTPException:
            continue
        results.append(summary)

    return {
        "success": True,
        "track": track_id,
        "courses": results,
    }
