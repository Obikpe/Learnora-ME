"""Internal assessment authoring and grading for global Learnora content."""
from typing import Any, Optional, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .auth import log_audit_event, supabase
from .internal_auth import InternalStaffContext, require_internal_permission
from .progress import effective_passing_score, _sync_enrolment_completion

router = APIRouter(prefix="/api/internal/assessments", tags=["Internal Assessments"])
def _course(course_id: str) -> dict:
    rows = (
        supabase.table("learnora_courses")
        .select("id,title,ownership,organisation_id,status")
        .eq("id", course_id)
        .eq("ownership", "learnora")
        .is_("organisation_id", "null")
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        raise HTTPException(404, "Global Learnora course not found.")
    return rows[0]


def _quiz(quiz_id: str) -> dict:
    rows = (
        supabase.table("quizzes")
        .select("id,course_id,module_id,lesson_id,title,description,passing_score,max_attempts,is_published")
        .eq("id", quiz_id)
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        raise HTTPException(404, "Quiz not found.")
    quiz = rows[0]
    _course(str(quiz["course_id"]))
    return quiz


def _draft_quiz(quiz_id: str) -> dict:
    quiz = _quiz(quiz_id)
    if quiz.get("is_published"):
        raise HTTPException(409, "Unpublish the quiz before editing its questions or settings.")
    return quiz


class QuizCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    module_id: Optional[str] = Field(None, max_length=80)
    lesson_id: Optional[str] = Field(None, max_length=80)
    passing_score: float = Field(default=70, ge=70, le=100)
    max_attempts: Optional[int] = Field(default=None, ge=1, le=100)


class QuizWrite(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    passing_score: Optional[float] = Field(None, ge=70, le=100)
    max_attempts: Optional[int] = Field(default=None, ge=1, le=100)
    is_published: Optional[bool] = None


class QuestionIn(BaseModel):
    question: str = Field(..., min_length=3, max_length=5000)
    question_type: Literal["multiple_choice", "single_choice", "mcq", "true_false", "boolean"]
    options: Any = Field(default_factory=list)
    correct_answer: Any
    explanation: Optional[str] = Field(None, max_length=5000)
    points: float = Field(default=1, gt=0, le=1000)
    order_index: int = Field(default=0, ge=0)


class AssignmentCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    instructions: Optional[str] = Field(None, max_length=12000)
    lesson_id: Optional[str] = Field(None, max_length=80)
    due_date: Optional[str] = None
    max_score: Optional[float] = Field(default=100, gt=0, le=100000)
    is_published: bool = False


class AssignmentWrite(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    instructions: Optional[str] = Field(None, max_length=12000)
    due_date: Optional[str] = None
    lesson_id: Optional[str] = Field(None, max_length=80)
    max_score: Optional[float] = Field(None, gt=0, le=100000)
    is_published: Optional[bool] = None


class GradeSubmissionIn(BaseModel):
    score: float = Field(..., ge=0, le=100000)
    feedback: Optional[str] = Field(None, max_length=10000)


def _validate_assessment_location(course_id: str, module_id: Optional[str], lesson_id: Optional[str], require_published: bool = False):
    resolved_module = module_id
    if lesson_id:
        lesson_rows = (
            supabase.table("learnora_lessons")
            .select("id,module_id,status")
            .eq("id", lesson_id)
            .limit(1)
            .execute()
        ).data or []
        if not lesson_rows:
            raise HTTPException(404, "Lesson not found.")
        if require_published and lesson_rows[0].get("status") != "published":
            raise HTTPException(409, "Publish the lesson before publishing its assessment.")
        lesson_module = str(lesson_rows[0]["module_id"])
        if resolved_module and str(resolved_module) != lesson_module:
            raise HTTPException(422, "The selected lesson does not belong to the selected module.")
        resolved_module = lesson_module
    if resolved_module:
        module_rows = (
            supabase.table("course_modules")
            .select("id,course_id,status")
            .eq("id", resolved_module)
            .eq("course_id", course_id)
            .limit(1)
            .execute()
        ).data or []
        if not module_rows:
            raise HTTPException(422, "The selected module does not belong to this course.")
        if require_published and module_rows[0].get("status") != "published":
            raise HTTPException(409, "Publish the module before publishing its assessment.")
    return resolved_module


def _question_rows(quiz_id: str):
    return (
        supabase.table("quiz_questions")
        .select("id,quiz_id,question,question_type,options,correct_answer,explanation,points,order_index")
        .eq("quiz_id", quiz_id)
        .order("order_index")
        .execute()
    ).data or []


def _validate_question_payload(question: dict):
    question_type = str(question.get("question_type") or "").lower()
    if question_type not in {"multiple_choice", "single_choice", "mcq", "true_false", "boolean"}:
        raise HTTPException(422, "This question type is not supported by automatic grading.")
    answer = question.get("correct_answer")
    if answer is None or (isinstance(answer, str) and not answer.strip()):
        raise HTTPException(422, "Provide a correct answer for every auto-graded question.")
    if question_type in {"true_false", "boolean"}:
        value = answer.get("value", answer.get("answer")) if isinstance(answer, dict) else answer
        if str(value).strip().lower() not in {"true", "false"}:
            raise HTTPException(422, "True/false questions must use True or False as the correct answer.")
        return
    options = question.get("options")
    if isinstance(options, dict):
        values = [str(value).strip().casefold() for value in options.keys()]
        values.extend(str(value).strip().casefold() for value in options.values())
    elif isinstance(options, list):
        values = []
        for option in options:
            if isinstance(option, dict):
                values.append(str(option.get("value", option.get("label", option.get("text", "")))).strip().casefold())
            else:
                values.append(str(option).strip().casefold())
    else:
        values = []
    if not values:
        raise HTTPException(422, "Choice questions need at least one answer option.")
    if isinstance(answer, dict):
        answer = answer.get("value", answer.get("answer", answer.get("label", "")))
    answers = answer if isinstance(answer, list) else [answer]
    if question_type in {"single_choice", "mcq"} and len(answers) != 1:
        raise HTTPException(422, "Single-choice questions must have exactly one correct answer.")
    if any(str(value).strip().casefold() not in values for value in answers):
        raise HTTPException(422, "The correct answer must match one of the configured answer options.")


def _assert_quiz_publishable(quiz_id: str):
    quiz = _quiz(quiz_id)
    _validate_assessment_location(str(quiz["course_id"]), quiz.get("module_id"), quiz.get("lesson_id"), require_published=True)
    questions = _question_rows(quiz_id)
    if not questions:
        raise HTTPException(409, "Add at least one question before publishing this quiz.")
    for question in questions:
        try:
            _validate_question_payload(question)
        except HTTPException as exc:
            raise HTTPException(409, exc.detail) from None
        if float(question.get("points") or 0) <= 0:
            raise HTTPException(409, "Every question must have a positive point value.")


@router.get("/courses/{course_id}")
def list_course_assessments(course_id: str, staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    _course(course_id)
    modules = (
        supabase.table("course_modules")
        .select("id,title,order_index,status")
        .eq("course_id", course_id)
        .order("order_index")
        .execute()
    ).data or []
    quizzes = (
        supabase.table("quizzes")
        .select("id,course_id,module_id,lesson_id,title,description,passing_score,max_attempts,is_published,created_at")
        .eq("course_id", course_id)
        .order("created_at", desc=True)
        .execute()
    ).data or []
    assignments = (
        supabase.table("assignments")
        .select("id,course_id,lesson_id,title,description,instructions,due_date,max_score,is_published,created_at")
        .eq("course_id", course_id)
        .order("created_at", desc=True)
        .execute()
    ).data or []
    return {"success": True, "modules": modules, "quizzes": quizzes, "assignments": assignments}


@router.get("/courses/{course_id}/performance")
def course_performance(course_id: str, staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    _course(course_id)
    enrolments = (
        supabase.table("learnora_enrolments")
        .select("id,user_id,status,enrolled_at,completed_at,organisation_id,cohort_id")
        .eq("course_id", course_id)
        .in_("status", ["active", "completed"])
        .order("enrolled_at", desc=True)
        .execute()
    ).data or []
    latest_enrolment_by_user = {}
    for row in enrolments:
        if row.get("user_id"):
            latest_enrolment_by_user.setdefault(str(row["user_id"]), row)
    enrolments = list(latest_enrolment_by_user.values())
    user_ids = list(latest_enrolment_by_user)
    if not user_ids:
        return {"success": True, "course_id": course_id, "learners": [], "count": 0}
    users = supabase.table("users").select("id,name,email,role").in_("id", user_ids).execute().data or []
    user_map = {str(row["id"]): row for row in users}
    modules = (
        supabase.table("course_modules")
        .select("id")
        .eq("course_id", course_id)
        .eq("status", "published")
        .execute()
    ).data or []
    module_ids = [str(row["id"]) for row in modules]
    lessons = (
        supabase.table("learnora_lessons")
        .select("id")
        .in_("module_id", module_ids)
        .eq("status", "published")
        .execute()
    ).data or [] if module_ids else []
    lesson_ids = [str(row["id"]) for row in lessons]
    progress_rows = (
        supabase.table("learnora_lesson_progress")
        .select("user_id,lesson_id,progress_percent,completed,last_accessed_at")
        .in_("user_id", user_ids)
        .in_("lesson_id", lesson_ids)
        .execute()
    ).data or [] if lesson_ids else []
    quizzes = (
        supabase.table("quizzes")
        .select("id,title,passing_score")
        .eq("course_id", course_id)
        .eq("is_published", True)
        .execute()
    ).data or []
    quiz_ids = [str(row["id"]) for row in quizzes]
    quiz_title_map = {str(row["id"]): row.get("title") for row in quizzes}
    quiz_threshold_map = {str(row["id"]): effective_passing_score(row) for row in quizzes}
    attempts = (
        supabase.table("quiz_attempts")
        .select("id,user_id,quiz_id,score,passed,submitted_at")
        .in_("user_id", user_ids)
        .in_("quiz_id", quiz_ids)
        .order("submitted_at", desc=True)
        .execute()
    ).data or [] if quiz_ids else []
    assignments = (
        supabase.table("assignments")
        .select("id,title,max_score")
        .eq("course_id", course_id)
        .eq("is_published", True)
        .execute()
    ).data or []
    assignment_ids = [str(row["id"]) for row in assignments]
    assignment_title_map = {str(row["id"]): row.get("title") for row in assignments}
    submissions = (
        supabase.table("assignment_submissions")
        .select("id,user_id,assignment_id,status,score,feedback,submitted_at,graded_at")
        .in_("user_id", user_ids)
        .in_("assignment_id", assignment_ids)
        .order("submitted_at", desc=True)
        .execute()
    ).data or [] if assignment_ids else []
    by_user_progress, by_user_attempts, by_user_submissions = {}, {}, {}
    for row in progress_rows:
        by_user_progress.setdefault(str(row["user_id"]), []).append(row)
    for row in attempts:
        by_user_attempts.setdefault(str(row["user_id"]), []).append(row)
    latest_submission_by_user_assignment = {}
    for row in submissions:
        key = (str(row.get("user_id")), str(row.get("assignment_id")))
        latest_submission_by_user_assignment.setdefault(key, row)
    for (submission_user_id, _assignment_id), row in latest_submission_by_user_assignment.items():
        by_user_submissions.setdefault(submission_user_id, []).append(row)
    learners = []
    for enrolment in enrolments:
        user_id = str(enrolment.get("user_id"))
        learner_progress = by_user_progress.get(user_id, [])
        learner_attempts = by_user_attempts.get(user_id, [])
        learner_submissions = by_user_submissions.get(user_id, [])
        learners.append({
            "enrolment": enrolment,
            "learner": user_map.get(user_id),
            "lesson_summary": {
                "total": len(lesson_ids),
                "completed": sum(1 for row in learner_progress if row.get("completed")),
                "tracked": len(learner_progress),
            },
            "quiz_attempts": [{**row, "quiz_title": quiz_title_map.get(str(row.get("quiz_id")))} for row in learner_attempts],
            "assignment_submissions": [{**row, "assignment_title": assignment_title_map.get(str(row.get("assignment_id")))} for row in learner_submissions],
            "assessment_summary": {
                "quizzes_passed": len({str(row["quiz_id"]) for row in learner_attempts if row.get("passed") is True and float(row.get("score") or 0) >= quiz_threshold_map.get(str(row.get("quiz_id")), 70)}),
                "quizzes_total": len(quizzes),
                "assignments_graded": sum(1 for row in learner_submissions if row.get("status") == "graded"),
                "assignments_total": len(assignments),
            },
        })
    return {"success": True, "course_id": course_id, "learners": learners, "count": len(learners)}


@router.post("/courses/{course_id}/quizzes", status_code=201)
def create_quiz(course_id: str, body: QuizCreate, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    _course(course_id)
    module_id = _validate_assessment_location(course_id, body.module_id, body.lesson_id)
    payload = body.model_dump()
    payload.update({"course_id": course_id, "module_id": module_id, "is_published": False})
    saved = supabase.table("quizzes").insert(payload).execute()
    if not saved.data:
        raise HTTPException(500, "Quiz could not be created.")
    return {"success": True, "quiz": saved.data[0]}


@router.patch("/quizzes/{quiz_id}")
def update_quiz(quiz_id: str, body: QuizWrite, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    quiz = _quiz(quiz_id)
    updates = body.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(400, "No quiz changes supplied.")
    if any(key in updates and updates[key] is None for key in ("title", "passing_score", "is_published")):
        raise HTTPException(422, "Quiz title, passing score and publication status cannot be null.")
    if updates.get("is_published") is True:
        _assert_quiz_publishable(quiz_id)
    if quiz.get("is_published") and any(key != "is_published" for key in updates):
        raise HTTPException(409, "Unpublish the quiz before changing its settings.")
    saved = supabase.table("quizzes").update(updates).eq("id", quiz_id).execute()
    if not saved.data:
        raise HTTPException(500, "Quiz update could not be confirmed.")
    return {"success": True, "quiz": saved.data[0]}


@router.get("/quizzes/{quiz_id}")
def get_quiz_for_staff(quiz_id: str, staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    quiz = _quiz(quiz_id)
    return {"success": True, "quiz": quiz, "questions": _question_rows(quiz_id)}


@router.post("/quizzes/{quiz_id}/questions", status_code=201)
def add_quiz_question(quiz_id: str, body: QuestionIn, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    _draft_quiz(quiz_id)
    _validate_question_payload(body.model_dump())
    saved = supabase.table("quiz_questions").insert({"quiz_id": quiz_id, **body.model_dump()}).execute()
    if not saved.data:
        raise HTTPException(500, "Question could not be added.")
    return {"success": True, "question": saved.data[0]}


@router.patch("/questions/{question_id}")
def update_quiz_question(question_id: str, body: QuestionIn, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    rows = supabase.table("quiz_questions").select("id,quiz_id").eq("id", question_id).limit(1).execute().data or []
    if not rows:
        raise HTTPException(404, "Question not found.")
    _draft_quiz(str(rows[0]["quiz_id"]))
    _validate_question_payload(body.model_dump())
    saved = supabase.table("quiz_questions").update(body.model_dump()).eq("id", question_id).execute()
    if not saved.data:
        raise HTTPException(500, "Question update could not be confirmed.")
    return {"success": True, "question": saved.data[0]}


@router.delete("/questions/{question_id}")
def delete_quiz_question(question_id: str, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    rows = supabase.table("quiz_questions").select("id,quiz_id").eq("id", question_id).limit(1).execute().data or []
    if not rows:
        raise HTTPException(404, "Question not found.")
    _draft_quiz(str(rows[0]["quiz_id"]))
    supabase.table("quiz_questions").delete().eq("id", question_id).execute()
    return {"success": True}


@router.post("/courses/{course_id}/assignments", status_code=201)
def create_assignment(course_id: str, body: AssignmentCreate, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    _course(course_id)
    _validate_assessment_location(course_id, None, body.lesson_id, require_published=body.is_published)
    payload = body.model_dump()
    payload["course_id"] = course_id
    if payload.get("is_published") and not (payload.get("instructions") or payload.get("description")):
        raise HTTPException(409, "Add assignment instructions before publishing.")
    saved = supabase.table("assignments").insert(payload).execute()
    if not saved.data:
        raise HTTPException(500, "Assignment could not be created.")
    return {"success": True, "assignment": saved.data[0]}


@router.patch("/assignments/{assignment_id}")
def update_assignment(assignment_id: str, body: AssignmentWrite, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    rows = supabase.table("assignments").select("id,course_id,is_published").eq("id", assignment_id).limit(1).execute().data or []
    if not rows:
        raise HTTPException(404, "Assignment not found.")
    _course(str(rows[0]["course_id"]))
    updates = body.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(400, "No assignment changes supplied.")
    if any(key in updates and updates[key] is None for key in ("title", "is_published")):
        raise HTTPException(422, "Assignment title and publication status cannot be null.")
    if rows[0].get("is_published") and any(key != "is_published" for key in updates):
        raise HTTPException(409, "Unpublish the assignment before changing its settings.")
    if "lesson_id" in updates:
        updates["lesson_id"] = _validate_assessment_location(
            str(rows[0]["course_id"]), None, updates.get("lesson_id"),
            require_published=updates.get("is_published") is True,
        )
    if updates.get("is_published") is True:
        current_location = supabase.table("assignments").select("lesson_id").eq("id", assignment_id).limit(1).execute().data or []
        _validate_assessment_location(str(rows[0]["course_id"]), None, current_location[0].get("lesson_id") if current_location else None, require_published=True)
    if updates.get("is_published") is True and not (updates.get("instructions") or updates.get("description")):
        current = supabase.table("assignments").select("description,instructions").eq("id", assignment_id).limit(1).execute().data or []
        if not current or not (current[0].get("instructions") or current[0].get("description")):
            raise HTTPException(409, "Add assignment instructions before publishing.")
    saved = supabase.table("assignments").update(updates).eq("id", assignment_id).execute()
    if not saved.data:
        raise HTTPException(500, "Assignment update could not be confirmed.")
    return {"success": True, "assignment": saved.data[0]}


@router.get("/assignments/{assignment_id}/submissions")
def assignment_submissions(assignment_id: str, staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    rows = supabase.table("assignments").select("id,course_id,title,max_score").eq("id", assignment_id).limit(1).execute().data or []
    if not rows:
        raise HTTPException(404, "Assignment not found.")
    _course(str(rows[0]["course_id"]))
    submissions = (
        supabase.table("assignment_submissions")
        .select("id,user_id,submission_text,file_url,status,score,feedback,submitted_at,graded_at,graded_by")
        .eq("assignment_id", assignment_id)
        .order("submitted_at", desc=True)
        .execute()
    ).data or []
    user_ids = list({str(row["user_id"]) for row in submissions if row.get("user_id")})
    users = supabase.table("users").select("id,name,email").in_("id", user_ids).execute().data or [] if user_ids else []
    user_map = {str(row["id"]): row for row in users}
    return {"success": True, "assignment": rows[0], "submissions": [{**row, "learner": user_map.get(str(row.get("user_id")))} for row in submissions]}


@router.post("/assignments/{assignment_id}/submissions/{submission_id}/grade")
def grade_assignment_submission(assignment_id: str, submission_id: str, body: GradeSubmissionIn, staff: InternalStaffContext = Depends(require_internal_permission("content.manage"))):
    assignment_rows = supabase.table("assignments").select("id,course_id,max_score").eq("id", assignment_id).limit(1).execute().data or []
    if not assignment_rows:
        raise HTTPException(404, "Assignment not found.")
    assignment = assignment_rows[0]
    _course(str(assignment["course_id"]))
    maximum = assignment.get("max_score")
    if maximum is not None and body.score > float(maximum):
        raise HTTPException(422, "The grade cannot exceed the assignment's maximum score.")
    submission_rows = supabase.table("assignment_submissions").select("id,assignment_id,user_id").eq("id", submission_id).eq("assignment_id", assignment_id).limit(1).execute().data or []
    if not submission_rows:
        raise HTTPException(404, "Submission not found for this assignment.")
    from datetime import datetime, timezone
    saved = supabase.table("assignment_submissions").update({
        "status": "graded",
        "score": body.score,
        "feedback": body.feedback.strip() if body.feedback else None,
        "graded_at": datetime.now(timezone.utc).isoformat(),
        "graded_by": staff.user_id,
    }).eq("id", submission_id).eq("assignment_id", assignment_id).execute()
    if not saved.data:
        raise HTTPException(500, "Grade could not be saved.")
    course_progress = _sync_enrolment_completion(
        str(submission_rows[0]["user_id"]),
        str(assignment["course_id"]),
        include_lesson_content=False,
    )
    log_audit_event(
        action="assignment_submission_graded",
        email=staff.email,
        account_type="staff",
        role="staff",
        metadata={
            "staff_id": staff.staff_id,
            "learner_user_id": submission_rows[0].get("user_id"),
            "course_id": str(assignment["course_id"]),
            "assignment_id": assignment_id,
            "submission_id": submission_id,
            "score": body.score,
            "max_score": maximum,
        },
    )
    return {"success": True, "submission": saved.data[0], "course_progress": course_progress}
