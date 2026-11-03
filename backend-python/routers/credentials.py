"""Course-completion credentials and public verification."""

import hashlib
import hmac
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .auth import JWT_SECRET, CurrentUser, get_current_user, log_audit_event, supabase
from .internal_auth import InternalStaffContext, require_internal_permission
from .progress import _course_summary

router = APIRouter(prefix="/api/credentials", tags=["Credentials"])


class CertificateRevocationIn(BaseModel):
    reason: str = Field(..., min_length=5, max_length=1000)


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
        "status": "revoked" if row.get("revoked_at") else "valid",
        "revoked_at": row.get("revoked_at"),
        "revocation_reason": row.get("revocation_reason"),
        "valid": not bool(row.get("revoked_at")),
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
        try:
            course_rows = (
                supabase.table("learnora_courses")
                .select("id,title")
                .in_("id", course_ids)
                .execute()
            ).data or []
            course_map = {str(row["id"]): row.get("title") for row in course_rows}
        except Exception as exc:
            print(f"Certificate course-title lookup failed: {type(exc).__name__}")

    try:
        enrolments = (
            supabase.table("learnora_enrolments")
            .select("course_id,status")
            .eq("user_id", user.id)
            .in_("status", ["active", "completed"])
            .execute()
        ).data or []
    except Exception as exc:
        print(f"Certificate eligibility lookup failed: {type(exc).__name__}")
        enrolments = []
    enrolled_ids = list({str(row["course_id"]) for row in enrolments if row.get("course_id")})
    eligible = []
    if enrolled_ids:
        try:
            courses = (
                supabase.table("learnora_courses")
                .select("id,title,status")
                .in_("id", enrolled_ids)
                .execute()
            ).data or []
        except Exception as exc:
            print(f"Certificate course eligibility lookup failed: {type(exc).__name__}")
            courses = []
        issued_course_ids = {str(row["course_id"]) for row in rows}
        for course in courses:
            if str(course["id"]) in issued_course_ids or course.get("status") not in {"published", "archived"}:
                continue
            try:
                summary = _course_summary(
                    str(user.id),
                    str(course["id"]),
                    include_archived=course.get("status") == "archived",
                    include_lesson_content=False,
                )
            except HTTPException:
                continue
            except Exception as exc:
                print(f"Certificate eligibility calculation failed: {type(exc).__name__}")
                continue
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

    # Check by learner/course first so a JWT secret rotation cannot issue a
    # second certificate for a course that was already certified.
    try:
        existing = (
            supabase.table("certificates")
            .select("id,user_id,course_id,certificate_number,issued_at,metadata,revoked_at,revocation_reason")
            .eq("user_id", user.id)
            .eq("course_id", course_id)
            .limit(1)
            .execute()
        ).data or []
    except Exception:
        existing = (
            supabase.table("certificates")
            .select("id,user_id,course_id,certificate_number,issued_at,metadata")
            .eq("user_id", user.id)
            .eq("course_id", course_id)
            .limit(1)
            .execute()
        ).data or []
    if existing:
        if existing[0].get("revoked_at"):
            raise HTTPException(409, "This certificate has been revoked and cannot be reissued. Contact Learnora support.")
        return {
            "success": True,
            "already_issued": True,
            "certificate": _certificate_view(existing[0], course.get("title")),
        }

    number = _certificate_number(str(user.id), course_id)
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
        try:
            row = (
                supabase.table("certificates")
                .select("id,user_id,course_id,certificate_number,issued_at,metadata,revoked_at,revocation_reason")
                .eq("certificate_number", number)
                .eq("user_id", user.id)
                .limit(1)
                .execute()
            ).data
        except Exception:
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
    try:
        rows = (
            supabase.table("certificates")
            .select("id,course_id,certificate_number,issued_at,metadata,revoked_at")
            .eq("certificate_number", number)
            .limit(1)
            .execute()
        ).data or []
    except Exception:
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
        "valid": not bool(row.get("revoked_at")),
        "certificate": {
            "certificate_number": row.get("certificate_number"),
            "status": "revoked" if row.get("revoked_at") else "valid",
            "revoked_at": row.get("revoked_at"),
            "issued_at": row.get("issued_at"),
            "course_title": (course_rows[0].get("title") if course_rows else None) or metadata.get("course_title") or "Learnora course",
            "recipient_name": metadata.get("recipient_name") or "Learnora learner",
            "credential_type": metadata.get("credential_type") or "course_completion",
            "issuer": "Learnora ME",
        },
    }


@router.get("/internal")
def internal_certificates(staff: InternalStaffContext = Depends(require_internal_permission("courses.view"))):
    rows = (
        supabase.table("certificates")
        .select("id,user_id,course_id,certificate_number,issued_at,metadata,revoked_at,revoked_by,revocation_reason")
        .order("issued_at", desc=True)
        .limit(200)
        .execute()
    ).data or []
    user_ids = list({str(row["user_id"]) for row in rows if row.get("user_id")})
    course_ids = list({str(row["course_id"]) for row in rows if row.get("course_id")})
    users = supabase.table("users").select("id,name,email").in_("id", user_ids).execute().data or [] if user_ids else []
    courses = supabase.table("learnora_courses").select("id,title").in_("id", course_ids).execute().data or [] if course_ids else []
    user_map = {str(row["id"]): row for row in users}
    course_map = {str(row["id"]): row for row in courses}
    return {
        "success": True,
        "certificates": [
            {
                **_certificate_view(row, course_map.get(str(row.get("course_id")), {}).get("title")),
                "learner": user_map.get(str(row.get("user_id"))),
                "revoked_by": row.get("revoked_by"),
            }
            for row in rows
        ],
        "limit": 200,
    }


@router.post("/internal/{certificate_id}/revoke")
def revoke_certificate(
    certificate_id: str,
    body: CertificateRevocationIn,
    staff: InternalStaffContext = Depends(require_internal_permission("content.manage")),
):
    try:
        certificate_id = str(UUID(certificate_id))
    except ValueError:
        raise HTTPException(404, "Certificate not found.") from None
    reason = body.reason.strip()
    if len(reason) < 5:
        raise HTTPException(422, "Provide a meaningful revocation reason.")
    rows = (
        supabase.table("certificates")
        .select("id,certificate_number,revoked_at")
        .eq("id", certificate_id)
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        raise HTTPException(404, "Certificate not found.")
    if rows[0].get("revoked_at"):
        return {"success": True, "already_revoked": True, "certificate_number": rows[0]["certificate_number"]}
    now = datetime.now(timezone.utc).isoformat()
    saved = (
        supabase.table("certificates")
        .update({"revoked_at": now, "revoked_by": staff.user_id, "revocation_reason": reason})
        .eq("id", certificate_id)
        .is_("revoked_at", "null")
        .execute()
    ).data or []
    if not saved:
        latest = supabase.table("certificates").select("revoked_at,certificate_number").eq("id", certificate_id).limit(1).execute().data or []
        if latest and latest[0].get("revoked_at"):
            return {"success": True, "already_revoked": True, "certificate_number": latest[0].get("certificate_number")}
        raise HTTPException(409, "Certificate revocation could not be confirmed.")
    log_audit_event(
        action="course_certificate_revoked",
        email=staff.email,
        account_type="staff",
        role="staff",
        metadata={"staff_id": staff.staff_id, "certificate_id": certificate_id, "certificate_number": rows[0]["certificate_number"], "reason": reason},
    )
    return {"success": True, "certificate": {"id": certificate_id, "certificate_number": rows[0]["certificate_number"], "revoked_at": now}}
