"""Course-completion credentials and public verification."""

import hashlib
import hmac

from fastapi import APIRouter, Depends, HTTPException

from .auth import JWT_SECRET, CurrentUser, get_current_user, supabase
from .progress import _course_summary

router = APIRouter(prefix="/api/credentials", tags=["Credentials"])


def _certificate_number(user_id: str, course_id: str) -> str:
    message = f"learnora:course-completion:{user_id}:{course_id}".encode()
    digest = hmac.new(JWT_SECRET.encode(), message, hashlib.sha256).hexdigest().upper()
    return f"LRN-COURSE-{digest[:24]}"


def _course(course_id: str) -> dict:
    rows = (
        supabase.table("learnora_courses")
        .select("id,title,slug,status,ownership,organisation_id")
        .eq("id", course_id)
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        raise HTTPException(404, "Course not found.")
    course = rows[0]
    if course.get("status") not in {"published", "archived"}:
        raise HTTPException(409, "A certificate can only be issued for a published course.")
    return course


def _certificate_view(row: dict, course_title: str | None = None) -> dict:
    metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    return {
        "id": row.get("id"),
        "certificate_number": row.get("certificate_number"),
        "issued_at": row.get("issued_at"),
        "course_id": row.get("course_id"),
        "course_title": course_title or metadata.get("course_title") or "Learnora course",
        "recipient_name": metadata.get("recipient_name") or "Learnora learner",
        "verification_url": f"/verify-certificate/{row.get('certificate_number')}",
    }


@router.get("/me")
def my_credentials(user: CurrentUser = Depends(get_current_user)):
    rows = (
        supabase.table("certificates")
        .select("id,user_id,course_id,certificate_number,issued_at,metadata")
        .eq("user_id", user.id)
        .order("issued_at", desc=True)
        .execute()
    ).data or []
    course_ids = list({str(row["course_id"]) for row in rows if row.get("course_id")})
    course_map = {}
    if course_ids:
        course_rows = (
            supabase.table("learnora_courses")
            .select("id,title")
            .in_("id", course_ids)
            .execute()
        ).data or []
        course_map = {str(row["id"]): row.get("title") for row in course_rows}

    enrolments = (
        supabase.table("learnora_enrolments")
        .select("course_id,status")
        .eq("user_id", user.id)
        .in_("status", ["active", "completed"])
        .execute()
    ).data or []
    enrolled_ids = list({str(row["course_id"]) for row in enrolments if row.get("course_id")})
    eligible = []
    if enrolled_ids:
        courses = (
            supabase.table("learnora_courses")
            .select("id,title,status")
            .in_("id", enrolled_ids)
            .execute()
        ).data or []
        issued_course_ids = {str(row["course_id"]) for row in rows}
        for course in courses:
            if str(course["id"]) in issued_course_ids or course.get("status") not in {"published", "archived"}:
                continue
            summary = _course_summary(
                str(user.id),
                str(course["id"]),
                include_archived=course.get("status") == "archived",
            )
            if summary.get("completed"):
                eligible.append({
                    "course_id": str(course["id"]),
                    "course_title": course.get("title") or "Learnora course",
                    "completed_at": (summary.get("enrolment") or {}).get("completed_at"),
                })

    return {
        "success": True,
        "certificates": [_certificate_view(row, course_map.get(str(row.get("course_id")))) for row in rows],
        "eligible_courses": eligible,
    }


@router.post("/courses/{course_id}/issue", status_code=201)
def issue_course_certificate(
    course_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    course = _course(course_id)
    summary = _course_summary(
        str(user.id),
        course_id,
        include_archived=course.get("status") == "archived",
    )
    if not summary.get("completed"):
        raise HTTPException(
            409,
            "Complete every published lesson and required assessment before claiming this certificate.",
        )

    number = _certificate_number(str(user.id), course_id)
    existing = (
        supabase.table("certificates")
        .select("id,user_id,course_id,certificate_number,issued_at,metadata")
        .eq("certificate_number", number)
        .eq("user_id", user.id)
        .limit(1)
        .execute()
    ).data or []
    if existing:
        return {
            "success": True,
            "already_issued": True,
            "certificate": _certificate_view(existing[0], course.get("title")),
        }

    payload = {
        "user_id": user.id,
        "course_id": course_id,
        "organisation_id": course.get("organisation_id"),
        "certificate_number": number,
        "metadata": {
            "credential_type": "course_completion",
            "course_title": course.get("title") or "Learnora course",
            "course_slug": course.get("slug"),
            "recipient_name": user.name or "Learnora learner",
            "completion_percent": 100,
            "verification_version": 1,
        },
    }
    try:
        saved = supabase.table("certificates").insert(payload).execute()
        row = (saved.data or [None])[0]
    except Exception:
        # A concurrent request may have inserted the same deterministic credential.
        row = (
            supabase.table("certificates")
            .select("id,user_id,course_id,certificate_number,issued_at,metadata")
            .eq("certificate_number", number)
            .eq("user_id", user.id)
            .limit(1)
            .execute()
        ).data
        row = row[0] if row else None
        if not row:
            raise HTTPException(500, "The certificate could not be issued. Please retry.") from None

    if not row:
        raise HTTPException(500, "The certificate could not be issued. Please retry.")
    return {
        "success": True,
        "already_issued": False,
        "certificate": _certificate_view(row, course.get("title")),
    }


@router.get("/verify/{certificate_number}")
def verify_certificate(certificate_number: str):
    number = certificate_number.strip().upper()
    if not number or len(number) > 80:
        raise HTTPException(404, "Certificate not found.")
    rows = (
        supabase.table("certificates")
        .select("id,course_id,certificate_number,issued_at,metadata")
        .eq("certificate_number", number)
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        raise HTTPException(404, "No Learnora certificate matches that number.")

    row = rows[0]
    course_rows = (
        supabase.table("learnora_courses")
        .select("title")
        .eq("id", str(row["course_id"]))
        .limit(1)
        .execute()
    ).data or []
    metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    return {
        "success": True,
        "valid": True,
        "certificate": {
            "certificate_number": row.get("certificate_number"),
            "issued_at": row.get("issued_at"),
            "course_title": (course_rows[0].get("title") if course_rows else None) or metadata.get("course_title") or "Learnora course",
            "recipient_name": metadata.get("recipient_name") or "Learnora learner",
            "credential_type": metadata.get("credential_type") or "course_completion",
            "issuer": "Learnora ME",
        },
    }
