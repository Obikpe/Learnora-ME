"""Learner track completion reviews with explicit consent and staff moderation."""
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from .auth import CurrentUser, get_current_user, log_audit_event, supabase
from .internal_auth import InternalStaffContext, require_internal_permission
from .progress import track_progress

router = APIRouter(prefix="/api/track-reviews", tags=["Track Reviews"])
internal_router = APIRouter(prefix="/api/internal/track-reviews", tags=["Internal Track Reviews"])


class TrackReviewIn(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)
    public_consent: bool = False


class TrackReviewModerationIn(BaseModel):
    status: Literal["approved", "rejected"]


def _track_id(value: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(404, "Track not found.") from None


def _public_track(track_id: str) -> dict:
    rows = (
        supabase.table("learnora_learning_paths")
        .select("id,name,slug,status")
        .eq("id", track_id)
        .is_("owner_user_id", "null")
        .is_("organisation_id", "null")
        .in_("status", ["published", "archived"])
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        raise HTTPException(404, "Track not found.")
    return rows[0]


def _assert_completed(track_id: str, user: CurrentUser) -> dict:
    progress = track_progress(track_id, user)
    if not progress.get("completed"):
        raise HTTPException(409, "Complete every required course in this track before leaving a review.")
    return progress


def _clean_comment(value: str | None) -> str | None:
    cleaned = value.strip() if value else ""
    return cleaned or None


@router.get("/tracks/{track_id}")
def public_track_reviews(track_id: str):
    track_id = _track_id(track_id)
    track = _public_track(track_id)
    ratings = (
        supabase.table("learnora_track_reviews")
        .select("rating")
        .eq("track_id", track_id)
        .eq("public_consent", True)
        .eq("moderation_status", "approved")
        .execute()
    ).data or []
    rows = (
        supabase.table("learnora_track_reviews")
        .select("id,rating,comment,created_at")
        .eq("track_id", track_id)
        .eq("public_consent", True)
        .eq("moderation_status", "approved")
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    ).data or []
    rating_values = [int(row["rating"]) for row in ratings]
    return {
        "success": True,
        "track": {"id": track["id"], "name": track["name"], "slug": track.get("slug")},
        "average_rating": round(sum(rating_values) / len(rating_values), 1) if rating_values else None,
        "rating_count": len(rating_values),
        "reviews": rows,
    }


@router.get("/tracks/{track_id}/me")
def my_track_review(track_id: str, user: CurrentUser = Depends(get_current_user)):
    track_id = _track_id(track_id)
    _assert_completed(track_id, user)
    rows = (
        supabase.table("learnora_track_reviews")
        .select("id,track_id,rating,comment,public_consent,moderation_status,moderated_at,created_at,updated_at")
        .eq("track_id", track_id)
        .eq("user_id", str(user.id))
        .limit(1)
        .execute()
    ).data or []
    return {"success": True, "review": rows[0] if rows else None}


@router.post("/tracks/{track_id}/me", status_code=201)
def create_track_review(track_id: str, body: TrackReviewIn, user: CurrentUser = Depends(get_current_user)):
    track_id = _track_id(track_id)
    _assert_completed(track_id, user)
    existing = (
        supabase.table("learnora_track_reviews")
        .select("id")
        .eq("track_id", track_id)
        .eq("user_id", str(user.id))
        .limit(1)
        .execute()
    ).data or []
    if existing:
        raise HTTPException(409, "You have already reviewed this track. Edit your existing review instead.")
    now = datetime.now(timezone.utc).isoformat()
    saved = (
        supabase.table("learnora_track_reviews")
        .insert({
            "track_id": track_id,
            "user_id": str(user.id),
            "rating": body.rating,
            "comment": _clean_comment(body.comment),
            "public_consent": body.public_consent,
            "moderation_status": "pending",
            "created_at": now,
            "updated_at": now,
        })
        .execute()
    ).data or []
    if not saved:
        raise HTTPException(500, "Your track review could not be saved.")
    return {"success": True, "review": saved[0]}


@router.patch("/tracks/{track_id}/me")
def update_track_review(track_id: str, body: TrackReviewIn, user: CurrentUser = Depends(get_current_user)):
    track_id = _track_id(track_id)
    _assert_completed(track_id, user)
    existing = (
        supabase.table("learnora_track_reviews")
        .select("id")
        .eq("track_id", track_id)
        .eq("user_id", str(user.id))
        .limit(1)
        .execute()
    ).data or []
    if not existing:
        raise HTTPException(404, "Your review for this track was not found.")
    saved = (
        supabase.table("learnora_track_reviews")
        .update({
            "rating": body.rating,
            "comment": _clean_comment(body.comment),
            "public_consent": body.public_consent,
            "moderation_status": "pending",
            "moderated_by": None,
            "moderated_at": None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("id", existing[0]["id"])
        .eq("user_id", str(user.id))
        .eq("track_id", track_id)
        .execute()
    ).data or []
    if not saved:
        raise HTTPException(500, "Your track review could not be updated.")
    return {"success": True, "review": saved[0]}


@internal_router.get("")
def list_track_reviews(
    status: str | None = Query(default=None, pattern="^(pending|approved|rejected)$"),
    staff: InternalStaffContext = Depends(require_internal_permission("track_reviews.moderate")),
):
    query = (
        supabase.table("learnora_track_reviews")
        .select("id,track_id,user_id,rating,comment,public_consent,moderation_status,moderated_by,moderated_at,created_at,updated_at")
        .order("created_at", desc=True)
        .limit(250)
    )
    if status:
        query = query.eq("moderation_status", status)
    rows = query.execute().data or []
    user_ids = list({str(row["user_id"]) for row in rows if row.get("user_id")})
    track_ids = list({str(row["track_id"]) for row in rows if row.get("track_id")})
    users = supabase.table("users").select("id,name,email").in_("id", user_ids).execute().data or [] if user_ids else []
    tracks = supabase.table("learnora_learning_paths").select("id,name,slug").in_("id", track_ids).execute().data or [] if track_ids else []
    user_map = {str(row["id"]): row for row in users}
    track_map = {str(row["id"]): row for row in tracks}
    return {
        "success": True,
        "reviews": [
            {**row, "learner": user_map.get(str(row.get("user_id"))), "track": track_map.get(str(row.get("track_id")))}
            for row in rows
        ],
        "limit": 250,
    }


@internal_router.post("/{review_id}/moderate")
def moderate_track_review(
    review_id: str,
    body: TrackReviewModerationIn,
    staff: InternalStaffContext = Depends(require_internal_permission("track_reviews.moderate")),
):
    try:
        review_id = str(UUID(review_id))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(404, "Track review not found.") from None
    rows = (
        supabase.table("learnora_track_reviews")
        .select("id,track_id,user_id,moderation_status,public_consent")
        .eq("id", review_id)
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        raise HTTPException(404, "Track review not found.")
    now = datetime.now(timezone.utc).isoformat()
    saved = (
        supabase.table("learnora_track_reviews")
        .update({
            "moderation_status": body.status,
            "moderated_by": str(staff.user_id),
            "moderated_at": now,
            "updated_at": now,
        })
        .eq("id", review_id)
        .execute()
    ).data or []
    if not saved:
        raise HTTPException(500, "Track review moderation could not be saved.")
    log_audit_event(
        action="track_review_moderated",
        email=staff.email,
        account_type="staff",
        role="staff",
        metadata={
            "staff_id": staff.staff_id,
            "review_id": review_id,
            "track_id": rows[0]["track_id"],
            "learner_user_id": rows[0]["user_id"],
            "moderation_status": body.status,
            "public_consent": rows[0]["public_consent"],
        },
    )
    return {"success": True, "review": saved[0]}
