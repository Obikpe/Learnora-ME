"""Idempotent awards for criteria-driven course-completion badges.

These badges recognise completed learning. They do not count as verified skill
mastery, which remains based on reviewed, skill-mapped project evidence.
"""
from __future__ import annotations

from typing import Any


def award_course_completion_badges(user_id: str, course_id: str, *, database: Any = None) -> list[str]:
    if not user_id or not course_id:
        return []
    if database is None:
        from routers.auth import supabase as database

    badge_rows = database.table("badges").select("id,criteria").execute().data or []
    awarded: list[str] = []
    for badge in badge_rows:
        criteria = badge.get("criteria") if isinstance(badge.get("criteria"), dict) else {}
        if criteria.get("type") != "course_completion" or str(criteria.get("course_id") or "") != str(course_id):
            continue
        badge_id = str(badge.get("id") or "")
        if not badge_id:
            continue
        database.table("learner_badges").upsert(
            {"badge_id": badge_id, "user_id": str(user_id)},
            on_conflict="badge_id,user_id",
        ).execute()
        awarded.append(badge_id)
    return awarded
