"""Authoritative Learnora access resolver.

Commercial events create entitlements; this service decides whether an
identity may actually use a resource. Keep this logic central so frontend
routers never invent their own access rules.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException

from routers.auth import supabase
from services.free_access import free_access_mode_enabled


def _now():
    return datetime.now(timezone.utc)


def _active(row):
    if not row or row.get("status") not in {"active", "trialing", "paid", "approved"}:
        return False

    start = row.get("starts_at")
    end = row.get("ends_at") or row.get("current_period_end")
    now = _now()

    if start:
        try:
            if datetime.fromisoformat(str(start).replace("Z", "+00:00")) > now:
                return False
        except ValueError:
            return False

    if end:
        try:
            if datetime.fromisoformat(str(end).replace("Z", "+00:00")) <= now:
                return False
        except ValueError:
            return False

    return True


def _course(course_id: str):
    result = (
        supabase
        .table("learnora_courses")
        .select("id,organisation_id,ownership,status,creator_id")
        .eq("id", course_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def resolve_course_access(
    user_id: str,
    course_id: str,
    organisation_id: Optional[str] = None,
    allow_free_access: bool = False,
):
    """Return access only from the caller's single account context.

    Individual purchases/subscriptions/free-launch access are never inherited
    by an organisation or cohort identity. Retained memberships reserve that
    context even when suspended or when the cohort has ended.
    """
    course = _course(course_id)
    if not course or course.get("status") != "published":
        return None

    try:
        cohort_accounts = (
            supabase.table("cohort_accounts")
            .select("id")
            .eq("id", user_id)
            .limit(1)
            .execute()
        ).data or []
        all_memberships = (
            supabase.table("organisation_members")
            .select("organisation_id,role,status")
            .eq("user_id", user_id)
            .execute()
        ).data or []
        all_cohort_memberships = (
            supabase.table("cohort_members")
            .select("id,cohort_id,status")
            .eq("user_id", user_id)
            .limit(1000)
            .execute()
        ).data or []
    except Exception as exc:
        print(f"Course identity scope lookup failed: {type(exc).__name__}")
        raise HTTPException(503, "Course access could not be verified. Please retry.") from None

    # Dedicated cohort accounts must use the cohort-learning API. A retained
    # legacy cohort membership also prevents individual purchase/free access.
    if cohort_accounts or all_cohort_memberships:
        return None

    if all_memberships:
        active_memberships = [
            row for row in all_memberships
            if str(row.get("status") or "").lower() == "active"
        ]
        all_organisation_ids = {
            str(row.get("organisation_id"))
            for row in all_memberships
            if row.get("organisation_id")
        }
        active_organisation_ids = {
            str(row.get("organisation_id"))
            for row in active_memberships
            if row.get("organisation_id")
        }
        if (
            not active_memberships
            or len(all_organisation_ids) != 1
            or len(active_organisation_ids) != 1
        ):
            return None
        resolved_organisation_id = next(iter(active_organisation_ids))
        if organisation_id and str(organisation_id) != resolved_organisation_id:
            return None
        organisation_id = resolved_organisation_id

    if organisation_id:
        # An organisation account can only use the active organisation
        # assignment/entitlement path. Its personal purchases and subscriptions
        # are deliberately not considered.
        if not all_memberships:
            return None
        membership = (
            supabase.table("organisation_members")
            .select("id,status,role")
            .eq("organisation_id", organisation_id)
            .eq("user_id", user_id)
            .eq("status", "active")
            .limit(1)
            .execute()
        )
        if not membership.data:
            return None
        if course.get("organisation_id") and str(course.get("organisation_id")) != str(organisation_id):
            return None

        entitlements = (
            supabase.table("learnora_access_entitlements")
            .select("*")
            .eq("course_id", course_id)
            .eq("organisation_id", organisation_id)
            .eq("status", "active")
            .execute()
        ).data or []
        for entitlement in entitlements:
            if _active(entitlement):
                return {
                    "allowed": True,
                    "source": entitlement.get("source_type"),
                    "entitlement": entitlement,
                }

        course_access = (
            supabase.table("course_access")
            .select("*")
            .eq("organisation_id", organisation_id)
            .eq("course_id", course_id)
            .eq("status", "active")
            .limit(1)
            .execute()
        )
        if course_access.data:
            lifecycle = (
                supabase.table("learnora_organisation_lifecycle")
                .select("status")
                .eq("organisation_id", organisation_id)
                .limit(1)
                .execute()
            )
            active_organisation = (
                supabase.table("organisations")
                .select("id,is_active")
                .eq("id", organisation_id)
                .eq("is_active", True)
                .limit(1)
                .execute()
            )
            if (
                active_organisation.data
                and lifecycle.data
                and lifecycle.data[0].get("status") in {"active", "expiring"}
            ):
                return {
                    "allowed": True,
                    "source": "organisation_assignment",
                    "membership": membership.data[0],
                    "course_access": course_access.data[0],
                }
        return None

    # Only identities with no retained organisation/cohort relationship reach
    # the individual learner access path.
    if (
        allow_free_access
        and free_access_mode_enabled()
        and not course.get("organisation_id")
        and course.get("ownership") == "learnora"
    ):
        return {"allowed": True, "source": "free_launch"}

    entitlements = (
        supabase.table("learnora_access_entitlements")
        .select("*")
        .eq("course_id", course_id)
        .eq("user_id", user_id)
        .eq("status", "active")
        .execute()
    ).data or []
    for entitlement in entitlements:
        if _active(entitlement):
            return {
                "allowed": True,
                "source": entitlement.get("source_type"),
                "entitlement": entitlement,
            }

    purchase = (
        supabase.table("learnora_course_purchases")
        .select("*")
        .eq("user_id", user_id)
        .eq("course_id", course_id)
        .eq("status", "paid")
        .order("purchased_at", desc=True)
        .limit(1)
        .execute()
    )
    if purchase.data:
        return {
            "allowed": True,
            "source": "purchase",
            "purchase": purchase.data[0],
        }

    if course.get("ownership") == "learnora":
        subscription = (
            supabase.table("learnora_subscriptions")
            .select("*")
            .eq("user_id", user_id)
            .in_("status", ["trialing", "active"])
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if subscription.data and _active(subscription.data[0]):
            return {
                "allowed": True,
                "source": "subscription",
                "subscription": subscription.data[0],
            }

    return None


def require_course_access(
    user_id: str,
    course_id: str,
    organisation_id: Optional[str] = None,
):
    result = resolve_course_access(
        user_id,
        course_id,
        organisation_id,
    )

    if not result:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this course.",
        )

    return result
