"""Database-backed in-app notifications for Learnora learners.

Notifications are deliberately best-effort: a notification write must never
turn a successful course publish/update into a failed course operation.
"""
import logging
import re
from html import escape
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Any

from routers.auth import supabase

logger = logging.getLogger(__name__)


def _chunks(values: list[str], size: int = 100):
    for start in range(0, len(values), size):
        yield values[start:start + size]


def _normalise(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def _course_text(course: dict) -> str:
    settings = course.get("settings") or {}
    values = [
        course.get("title"), course.get("short_description"),
        course.get("description"), course.get("level"),
        settings.get("track"), settings.get("category"),
        settings.get("subject"), settings.get("learning_track"),
    ]
    values.extend(settings.get("topics") or [])
    return _normalise(" ".join(str(v) for v in values if v))


def _profile_matches(profile: dict, course: dict, course_text: str) -> bool:
    track = _normalise(profile.get("preferred_track"))
    interests = [_normalise(v) for v in (profile.get("interests") or []) if _normalise(v)]
    if track:
        track_words = [w for w in track.split() if len(w) > 2]
        if track in course_text or (track_words and all(w in course_text for w in track_words)):
            return True
        # Short single-word tracks are matched only as whole normalized words.
        if len(track_words) == 1 and re.search(r"\b" + re.escape(track_words[0]) + r"\b", course_text):
            return True
    return any(i in course_text for i in interests)


def _candidate_user_ids(course: dict) -> set[str]:
    course_id = str(course.get("id") or "")
    ids: set[str] = set()
    # Existing learners should hear about material updates to courses they use.
    if course_id:
        try:
            enrolments = (
                supabase.table("learnora_enrolments")
                .select("user_id")
                .eq("course_id", course_id)
                .in_("status", ["active", "completed"])
                .execute()
            ).data or []
            ids.update(str(row["user_id"]) for row in enrolments if row.get("user_id"))
        except Exception:
            logger.exception("Could not resolve enrolled learners for notification")

    # Personalised recommendations are based on saved learner preferences.
    # No profile, no guessed track, and no synthetic recipients.
    try:
        profiles = (
            supabase.table("learner_onboarding_profiles")
            .select("user_id,preferred_track,interests,onboarding_completed")
            .eq("onboarding_completed", True)
            .limit(2000)
            .execute()
        ).data or []
        text = _course_text(course)
        for profile in profiles:
            user_id = profile.get("user_id")
            if user_id and _profile_matches(profile, course, text):
                ids.add(str(user_id))
    except Exception:
        logger.exception("Could not resolve learner track matches for notification")
    return ids


def _send_to_users(course: dict, event: str, title: str, body: str, action_url: str) -> int:
    try:
        course_id = str(course.get("id") or "")
        user_ids = _candidate_user_ids(course)
        if not user_ids:
            return 0

        # Publish events are idempotent. Use one query for the prior fan-out
        # instead of an N+1 query per learner. Meaningful course updates may
        # recur and are therefore not deduplicated.
        already_notified: set[str] = set()
        if event == "course_published":
            try:
                prior = (
                    supabase.table("learnora_notifications")
                    .select("user_id")
                    .eq("notification_type", event)
                    .contains("data", {"course_id": course_id})
                    .limit(5000)
                    .execute()
                ).data or []
                already_notified = {str(row["user_id"]) for row in prior if row.get("user_id")}
            except Exception:
                logger.exception("Could not check duplicate publish notifications")
        now = datetime.now(timezone.utc).isoformat()
        rows_to_insert = [{
            "user_id": user_id,
            "organisation_id": course.get("organisation_id"),
            "notification_type": event,
            "title": title,
            "body": body,
            "action_url": action_url,
            "data": {"course_id": course_id, "event": event, "updated_at": now},
            "created_at": now,
        } for user_id in user_ids if user_id not in already_notified]
        if not rows_to_insert:
            return 0
        inserted = 0
        for start in range(0, len(rows_to_insert), 100):
            result = supabase.table("learnora_notifications").insert(rows_to_insert[start:start + 100]).execute()
            inserted += len(result.data or [])
        return inserted
    except Exception:
        logger.exception("Notification delivery failed for course %s", course.get("id"))
        return 0


def notify_course_published(course: dict) -> int:
    """Notify learners whose saved track/interests match a newly published course."""
    title = str(course.get("title") or "A new Learnora course")
    return _send_to_users(
        course, "course_published", f"New course: {title}",
        f"A new course is available that may fit your learning track: {title}.",
        f"/courses/{course.get('id')}",
    )


def notify_course_updated(course: dict, changed_fields: list[str] | None = None) -> int:
    """Notify matched learners and enrolled learners about a published-course update."""
    title = str(course.get("title") or "Your course")
    changed = [x for x in (changed_fields or []) if x not in {"status", "updated_at"}]
    if not changed:
        return 0
    return _send_to_users(
        course, "course_updated", f"Course updated: {title}",
        f"There is a new update to {title}. Open the course to review the latest details.",
        f"/courses/{course.get('id')}",
    )



def _claim_delivery(user_id: str, event_key: str, channel: str, now: datetime) -> bool:
    result = supabase.rpc("claim_learner_notification_delivery", {
        "p_user_id": str(user_id),
        "p_event_key": event_key,
        "p_channel": channel,
        "p_now": now.isoformat(),
    }).execute()
    value = result.data
    if isinstance(value, list) and value:
        value = next(iter(value[0].values()), False) if isinstance(value[0], dict) else value[0]
    if isinstance(value, dict):
        value = next(iter(value.values()), False)
    return value is True


def _finish_delivery(
    user_id: str,
    event_key: str,
    channel: str,
    success: bool,
    now: datetime,
    error: str | None = None,
) -> None:
    try:
        supabase.rpc("finish_learner_notification_delivery", {
            "p_user_id": str(user_id),
            "p_event_key": event_key,
            "p_channel": channel,
            "p_success": success,
            "p_error": (error or "")[:500] if error else None,
            "p_now": now.isoformat(),
        }).execute()
    except Exception:
        logger.exception("Could not finalise notification delivery state")


def _create_in_app_once(
    *,
    user_id: str,
    event_key: str,
    notification_type: str,
    title: str,
    body: str,
    action_url: str,
    now: datetime,
    organisation_id: str | None = None,
) -> bool:
    if not _claim_delivery(user_id, event_key, "in_app", now):
        return False
    try:
        supabase.table("learnora_notifications").insert({
            "user_id": str(user_id),
            "organisation_id": organisation_id,
            "notification_type": notification_type,
            "title": title,
            "body": body,
            "action_url": action_url,
            "data": {"event_key": event_key, "automated": True},
            "created_at": now.isoformat(),
        }).execute()
        _finish_delivery(user_id, event_key, "in_app", True, now)
        return True
    except Exception as exc:
        logger.exception("In-app notification insert failed for %s", event_key)
        _finish_delivery(user_id, event_key, "in_app", False, now, type(exc).__name__)
        return False


def _send_automated_email_once(
    *,
    user_id: str,
    email: str,
    event_key: str,
    subject: str,
    text_body: str,
    html_body: str,
    now: datetime,
) -> bool:
    if not _claim_delivery(user_id, event_key, "email", now):
        return False
    try:
        from routers import auth
        auth._send_email(
            recipient=email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
        )
        _finish_delivery(user_id, event_key, "email", True, now)
        return True
    except Exception as exc:
        logger.exception("Automated email delivery failed for %s", event_key)
        _finish_delivery(user_id, event_key, "email", False, now, type(exc).__name__)
        return False


def send_post_setup_welcome(user_id: str) -> dict[str, bool]:
    """Create the one-time in-app welcome and send its matching email."""
    from html import escape
    from routers import auth

    now = datetime.now(timezone.utc)
    rows = (
        supabase.table("users")
        .select("id,name,email,account_status,email_verified")
        .eq("id", str(user_id))
        .eq("account_status", "active")
        .eq("email_verified", True)
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        return {"in_app": False, "email": False}
    user = rows[0]
    name = str(user.get("name") or "there").strip()
    safe_name = escape(name)
    event_key = "welcome:initial-setup:v1"
    title = "Welcome to Learnora ME"
    body = "Your learning journey starts here. Explore your dashboard, access your courses and begin learning at your own pace."
    in_app = _create_in_app_once(
        user_id=str(user_id),
        event_key=event_key,
        notification_type="welcome",
        title=title,
        body=body,
        action_url="/dashboard",
        now=now,
    )
    text_body = (
        f"Hi {name},\n\n"
        "Welcome to Learnora ME. Your learning journey starts here. "
        "Explore your dashboard, access your courses and begin learning at your own pace.\n\n"
        f"Open your dashboard: {auth.FRONTEND_URL}/dashboard\n\n"
        "Learnora ME"
    )
    html_body = f"""<!doctype html><html><body style="margin:0;background:#f5f7fb;font-family:Arial,sans-serif;color:#172033">
<div style="max-width:600px;margin:40px auto;padding:32px;background:#fff;border:1px solid #e5e7eb;border-radius:18px">
<h1 style="margin:0 0 16px">Welcome to Learnora ME</h1><p>Hi {safe_name},</p>
<p>Your learning journey starts here. Explore your dashboard, access your courses and begin learning at your own pace.</p>
<p style="margin:28px 0"><a href="{auth.FRONTEND_URL}/dashboard" style="display:inline-block;padding:14px 22px;border-radius:10px;background:#5b4bdb;color:#fff;text-decoration:none;font-weight:bold">Go to my dashboard</a></p>
<p style="font-size:13px;color:#64748b">Learnora ME · Learn. Practise. Build. Prove.</p>
</div></body></html>"""
    email_sent = _send_automated_email_once(
        user_id=str(user_id),
        email=str(user["email"]),
        event_key=event_key,
        subject="Welcome to Learnora ME",
        text_body=text_body,
        html_body=html_body,
        now=now,
    )
    return {"in_app": in_app, "email": email_sent}


def _process_deadline_reminders(now: datetime) -> int:
    from html import escape
    from routers import auth

    window_end = now + timedelta(hours=48)
    assignments = (
        supabase.table("assignments")
        .select("id,course_id,title,due_date")
        .eq("is_published", True)
        .gt("due_date", now.isoformat())
        .lte("due_date", window_end.isoformat())
        .limit(500)
        .execute()
    ).data or []
    delivered = 0
    for assignment in assignments:
        assignment_id = str(assignment.get("id") or "")
        course_id = str(assignment.get("course_id") or "")
        due_value = assignment.get("due_date")
        if not assignment_id or not course_id or not due_value:
            continue
        enrolments = (
            supabase.table("learnora_enrolments")
            .select("user_id")
            .eq("course_id", course_id)
            .eq("status", "active")
            .limit(5000)
            .execute()
        ).data or []
        user_ids = list({str(row["user_id"]) for row in enrolments if row.get("user_id")})
        if not user_ids:
            continue
        completed_ids: set[str] = set()
        for batch in _chunks(user_ids):
            submitted = (
                supabase.table("assignment_submissions")
                .select("user_id")
                .eq("assignment_id", assignment_id)
                .in_("user_id", batch)
                .limit(5000)
                .execute()
            ).data or []
            completed_ids.update(str(row["user_id"]) for row in submitted if row.get("user_id"))
        pending_ids = [user_id for user_id in user_ids if user_id not in completed_ids]
        if not pending_ids:
            continue
        users = []
        for batch in _chunks(pending_ids):
            users.extend((
                supabase.table("users")
                .select("id,name,email,email_verified,account_status")
                .in_("id", batch)
                .eq("account_status", "active")
                .limit(100)
                .execute()
            ).data or [])
        title = str(assignment.get("title") or "Your assignment")
        safe_title = escape(title)
        due_text = str(due_value)
        event_key = f"deadline:assignment:{assignment_id}:{due_text}"
        for user in users:
            user_id = str(user.get("id") or "")
            if not user_id:
                continue
            body = f"{title} is due within the next 48 hours. Submit your work before the deadline."
            if _create_in_app_once(
                user_id=user_id,
                event_key=event_key,
                notification_type="deadline_reminder",
                title=f"Upcoming deadline: {title}",
                body=body,
                action_url="/dashboard",
                now=now,
            ):
                delivered += 1
            if not user.get("email_verified") or not user.get("email"):
                continue
            text_body = (
                f"Hi {user.get('name') or 'there'},\n\n"
                f"{title} is due within the next 48 hours. Please submit your work before the deadline.\n\n"
                f"Open Learnora: {auth.FRONTEND_URL}/dashboard\n\nLearnora ME"
            )
            html_body = f"""<!doctype html><html><body style="margin:0;background:#f5f7fb;font-family:Arial,sans-serif;color:#172033">
<div style="max-width:600px;margin:40px auto;padding:32px;background:#fff;border:1px solid #e5e7eb;border-radius:18px">
<h1>Upcoming assignment deadline</h1><p>Hi {escape(str(user.get('name') or 'there'))},</p>
<p><strong>{safe_title}</strong> is due within the next 48 hours. Submit your work before the deadline.</p>
<p style="margin:28px 0"><a href="{auth.FRONTEND_URL}/dashboard" style="display:inline-block;padding:14px 22px;border-radius:10px;background:#5b4bdb;color:#fff;text-decoration:none;font-weight:bold">Continue learning</a></p>
</div></body></html>"""
            if _send_automated_email_once(
                user_id=user_id,
                email=str(user["email"]),
                event_key=event_key,
                subject=f"Upcoming deadline: {title}",
                text_body=text_body,
                html_body=html_body,
                now=now,
            ):
                delivered += 1
    return delivered


def _process_inactivity_reminders(now: datetime) -> int:
    from html import escape
    from routers import auth

    cutoff = now - timedelta(days=7)
    profiles = (
        supabase.table("learner_onboarding_profiles")
        .select("user_id,onboarding_completed_at")
        .eq("onboarding_completed", True)
        .limit(5000)
        .execute()
    ).data or []
    cohort_members = (
        supabase.table("cohort_members")
        .select("user_id,joined_at")
        .eq("status", "active")
        .not_.is_("user_id", "null")
        .limit(5000)
        .execute()
    ).data or []
    user_ids = list({
        str(row["user_id"])
        for row in [*profiles, *cohort_members]
        if row.get("user_id")
    })
    if not user_ids:
        return 0
    profile_map = {str(row["user_id"]): row for row in profiles if row.get("user_id")}
    joined_map: dict[str, str] = {}
    for member in cohort_members:
        member_user_id = str(member.get("user_id") or "")
        joined_at = str(member.get("joined_at") or "")
        if member_user_id and joined_at:
            if joined_at > joined_map.get(member_user_id, ""):
                joined_map[member_user_id] = joined_at
    users = []
    activity_rows = []
    for batch in _chunks(user_ids):
        users.extend((
            supabase.table("users")
            .select("id,name,email,email_verified,account_status,created_at,last_inactivity_email_at")
            .in_("id", batch)
            .eq("account_status", "active")
            .limit(100)
            .execute()
        ).data or [])
        activity_rows.extend((
            supabase.table("learner_learning_days")
            .select("learner_id,last_activity_at")
            .in_("learner_id", batch)
            .in_("account_type", ["individual", "cohort"])
            .order("last_activity_at", desc=True)
            .limit(20000)
            .execute()
        ).data or [])
    latest_activity: dict[str, str] = {}
    for row in activity_rows:
        learner_id = str(row.get("learner_id") or "")
        value = str(row.get("last_activity_at") or "")
        if learner_id and value and learner_id not in latest_activity:
            latest_activity[learner_id] = value
    delivered = 0
    for user in users:
        user_id = str(user.get("id") or "")
        if not user_id:
            continue
        profile = profile_map.get(user_id) or {}
        last_activity_value = latest_activity.get(user_id) or profile.get("onboarding_completed_at") or joined_map.get(user_id) or user.get("created_at")
        if not last_activity_value:
            continue
        try:
            last_activity = datetime.fromisoformat(str(last_activity_value).replace("Z", "+00:00"))
            if last_activity.tzinfo is None:
                last_activity = last_activity.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if last_activity > cutoff:
            continue
        event_key = f"inactivity:{last_activity.isoformat()}"
        name = str(user.get("name") or "there")
        body = "It has been a little while since your last completed learning activity. Your courses are ready whenever you are."
        if _create_in_app_once(
            user_id=user_id,
            event_key=event_key,
            notification_type="learning_inactivity",
            title="Ready to continue learning?",
            body=body,
            action_url="/dashboard",
            now=now,
        ):
            delivered += 1
        last_email_value = user.get("last_inactivity_email_at")
        if last_email_value:
            try:
                last_email = datetime.fromisoformat(str(last_email_value).replace("Z", "+00:00"))
                if last_email.tzinfo is None:
                    last_email = last_email.replace(tzinfo=timezone.utc)
                if last_email > now - timedelta(days=30):
                    continue
            except ValueError:
                pass
        if not user.get("email_verified") or not user.get("email"):
            continue
        safe_name = escape(name)
        text_body = (
            f"Hi {name},\n\n"
            "It has been 7 days since your last completed lesson, quiz or assessment. "
            "Your learning is ready when you are.\n\n"
            f"Continue learning: {auth.FRONTEND_URL}/dashboard\n\nLearnora ME"
        )
        html_body = f"""<!doctype html><html><body style="margin:0;background:#f5f7fb;font-family:Arial,sans-serif;color:#172033">
<div style="max-width:600px;margin:40px auto;padding:32px;background:#fff;border:1px solid #e5e7eb;border-radius:18px">
<h1>Ready to continue learning?</h1><p>Hi {safe_name},</p>
<p>It has been 7 days since your last completed lesson, quiz or assessment. Your learning is ready whenever you are.</p>
<p style="margin:28px 0"><a href="{auth.FRONTEND_URL}/dashboard" style="display:inline-block;padding:14px 22px;border-radius:10px;background:#5b4bdb;color:#fff;text-decoration:none;font-weight:bold">Continue learning</a></p>
</div></body></html>"""
        if _send_automated_email_once(
            user_id=user_id,
            email=str(user["email"]),
            event_key=event_key,
            subject="Your Learnora learning is ready when you are",
            text_body=text_body,
            html_body=html_body,
            now=now,
        ):
            try:
                supabase.table("users").update({
                    "last_inactivity_email_at": now.isoformat(),
                }).eq("id", user_id).eq("account_status", "active").execute()
            except Exception:
                logger.exception("Could not update inactivity email throttle for %s", user_id)
            delivered += 1
    return delivered


def _process_security_alert_retries(now: datetime) -> int:
    from html import escape

    retry_rows = (
        supabase.table("learner_notification_deliveries")
        .select("user_id,event_key,status,updated_at")
        .eq("channel", "email")
        .in_("status", ["pending", "failed", "sending"])
        .lte("next_attempt_at", now.isoformat())
        .order("updated_at")
        .limit(500)
        .execute()
    ).data or []
    delivered = 0
    user_cache: dict[str, dict | None] = {}
    for delivery in retry_rows:
        user_id = str(delivery.get("user_id") or "")
        event_key = str(delivery.get("event_key") or "")
        if not user_id or not event_key or not event_key.startswith("security:"):
            continue
        if delivery.get("status") == "sending":
            try:
                claimed_at = datetime.fromisoformat(str(delivery.get("updated_at")).replace("Z", "+00:00"))
                if claimed_at.tzinfo is None:
                    claimed_at = claimed_at.replace(tzinfo=timezone.utc)
                if claimed_at > now - timedelta(minutes=15):
                    continue
            except (TypeError, ValueError):
                continue
        if user_id not in user_cache:
            rows = (
                supabase.table("users")
                .select("id,email,email_verified,account_status")
                .eq("id", user_id)
                .eq("account_status", "active")
                .eq("email_verified", True)
                .limit(1)
                .execute()
            ).data or []
            user_cache[user_id] = rows[0] if rows else None
        user = user_cache[user_id]
        if not user or not user.get("email"):
            continue
        notices = (
            supabase.table("learnora_notifications")
            .select("title,body,data")
            .eq("user_id", user_id)
            .eq("notification_type", "security_alert")
            .contains("data", {"event_key": event_key})
            .limit(1)
            .execute()
        ).data or []
        if not notices:
            continue
        notice = notices[0]
        title = str(notice.get("title") or "Learnora security alert")
        body = str(notice.get("body") or "A security-related change occurred on your Learnora account.")
        if _send_automated_email_once(
            user_id=user_id,
            email=str(user["email"]),
            event_key=event_key,
            subject=title,
            text_body=f"{body}\n\nIf you did not make this change, contact Learnora support immediately.\n\nLearnora ME",
            html_body=(
                "<!doctype html><html><body style='font-family:Arial,sans-serif;color:#172033'>"
                f"<h1>{escape(title)}</h1><p>{escape(body)}</p>"
                "<p>If you did not make this change, contact "
                "<a href='mailto:learnorame@gmail.com'>Learnora support</a> immediately.</p>"
                "</body></html>"
            ),
            now=now,
        ):
            delivered += 1
    return delivered

def _process_weekly_in_app_summaries(now: datetime) -> int:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

    activity_rows = (
        supabase.table("learner_learning_days")
        .select("learner_id,activity_date,activity_count,timezone")
        .in_("account_type", ["individual", "cohort"])
        .gte("activity_date", (now.date() - timedelta(days=8)).isoformat())
        .lte("activity_date", now.date().isoformat())
        .order("activity_date", desc=True)
        .limit(20000)
        .execute()
    ).data or []
    by_user: dict[str, list[dict]] = {}
    for row in activity_rows:
        user_id = str(row.get("learner_id") or "")
        if user_id:
            by_user.setdefault(user_id, []).append(row)

    active_user_ids: set[str] = set()
    candidate_ids = list(by_user)
    for batch in _chunks(candidate_ids):
        active_rows = (
            supabase.table("users")
            .select("id")
            .in_("id", batch)
            .eq("account_status", "active")
            .limit(100)
            .execute()
        ).data or []
        active_user_ids.update(str(row["id"]) for row in active_rows if row.get("id"))

    delivered = 0
    for user_id, rows in by_user.items():
        if user_id not in active_user_ids:
            continue
        timezone_name = next(
            (str(row.get("timezone")) for row in rows if row.get("timezone")),
            "Africa/Lagos",
        )
        try:
            local_now = now.astimezone(ZoneInfo(timezone_name))
        except (ZoneInfoNotFoundError, ValueError):
            local_now = now.astimezone(ZoneInfo("Africa/Lagos"))
            timezone_name = "Africa/Lagos"
        # The worker runs once daily. Deliver on the learner's local Monday,
        # regardless of hour, so every timezone is reached without an hourly cron.
        # The event key below prevents duplicate summaries if the worker is retried.
        if local_now.weekday() != 0:
            continue
        week_end = local_now.date()
        week_start = week_end - timedelta(days=7)
        week_rows = []
        for row in rows:
            try:
                activity_date = date.fromisoformat(str(row.get("activity_date")))
            except (TypeError, ValueError):
                continue
            if week_start <= activity_date < week_end:
                week_rows.append(row)
        if not week_rows:
            continue
        activity_count = sum(int(row.get("activity_count") or 0) for row in week_rows)
        if activity_count <= 0:
            continue
        active_days = len({str(row.get("activity_date")) for row in week_rows})
        event_key = f"weekly-summary:{week_start.isoformat()}"
        if _create_in_app_once(
            user_id=user_id,
            event_key=event_key,
            notification_type="weekly_learning_summary",
            title="Your weekly learning summary",
            body=(
                f"Last week, you completed {activity_count} learning activities "
                f"across {active_days} active days. Keep building your momentum this week."
            ),
            action_url="/dashboard",
            now=now,
        ):
            delivered += 1
    return delivered



def _process_birthday_messages(now: datetime) -> int:
    """Send one birthday notification and email per active learner per local year."""
    rows = (
        supabase.table("users")
        .select("id,name,email,email_verified,email_verified_at,account_status,date_of_birth,timezone")
        .eq("account_status", "active")
        .limit(10000)
        .execute()
    ).data or []

    delivered = 0
    for user in rows:
        user_id = str(user.get("id") or "")
        if not user_id or not (user.get("email_verified") is True or user.get("email_verified_at")):
            continue
        try:
            birth_date = date.fromisoformat(str(user.get("date_of_birth"))[:10])
        except (TypeError, ValueError):
            continue

        timezone_name = str(user.get("timezone") or "Africa/Lagos")
        try:
            local_now = now.astimezone(ZoneInfo(timezone_name))
        except (ZoneInfoNotFoundError, ValueError):
            local_now = now.astimezone(ZoneInfo("Africa/Lagos"))

        birthday_day = birth_date.day
        is_leap_year = local_now.year % 4 == 0 and (local_now.year % 100 != 0 or local_now.year % 400 == 0)
        # Observe 29 February birthdays on 28 February in non-leap years.
        if birth_date.month == 2 and birth_date.day == 29 and not is_leap_year:
            birthday_day = 28
        if (birth_date.month, birthday_day) != (local_now.month, local_now.day):
            continue

        name = str(user.get("name") or "there").strip()
        safe_name = escape(name)
        title = "Happy Birthday from Learnora!"
        body = f"Happy Birthday, {name}! We hope you have a wonderful day. Keep learning, practising and building things you are proud of."
        event_key = f"birthday:{local_now.year}"

        in_app_sent = _create_in_app_once(
            user_id=user_id,
            event_key=event_key,
            notification_type="birthday",
            title=title,
            body=body,
            action_url="/dashboard",
            now=now,
        )

        email_sent = False
        if user.get("email"):
            text_body = (
                f"Hi {name},\n\nHappy Birthday from everyone at Learnora! "
                "We hope you have a wonderful day and a year full of meaningful learning, "
                "new ideas and things you are proud to build.\n\n"
                "Open your Learnora dashboard: https://learnorame.vercel.app/dashboard\n\n"
                "Learnora ME"
            )
            html_body = f"""<!doctype html><html><body style="margin:0;background:#f5f7fb;font-family:Arial,sans-serif;color:#172033">
<div style="max-width:600px;margin:40px auto;padding:32px;background:#fff;border:1px solid #e5e7eb;border-radius:18px">
<h1 style="margin:0 0 16px;color:#5b4bdb">Happy Birthday, {safe_name}!</h1>
<p>Everyone at Learnora wishes you a wonderful birthday.</p>
<p>May the year ahead bring meaningful learning, new ideas and things you are proud to build.</p>
<p style="margin:28px 0"><a href="https://learnorame.vercel.app/dashboard" style="display:inline-block;padding:14px 22px;border-radius:10px;background:#5b4bdb;color:#fff;text-decoration:none;font-weight:bold">Open my dashboard</a></p>
<p style="font-size:13px;color:#64748b">Learnora ME · Learn. Practise. Build. Prove.</p>
</div></body></html>"""
            email_sent = _send_automated_email_once(
                user_id=user_id,
                email=str(user["email"]),
                event_key=event_key,
                subject=f"Happy Birthday, {name}!",
                text_body=text_body,
                html_body=html_body,
                now=now,
            )

        if in_app_sent or email_sent:
            delivered += 1
    return delivered


def process_automated_learner_notifications() -> dict[str, int]:
    """Daily worker for welcome retries, security alerts and learning reminders."""
    now = datetime.now(timezone.utc)
    results = {"welcome": 0, "security": 0, "deadlines": 0, "inactivity": 0, "weekly_summaries": 0, "birthdays": 0}
    try:
        welcome_retries = (
            supabase.table("learner_notification_deliveries")
            .select("user_id")
            .eq("event_key", "welcome:initial-setup:v1")
            .in_("status", ["pending", "failed", "sending"])
            .lte("next_attempt_at", now.isoformat())
            .limit(1000)
            .execute()
        ).data or []
        retry_user_ids = list({str(row["user_id"]) for row in welcome_retries if row.get("user_id")})
        for user_id in retry_user_ids:
            outcome = send_post_setup_welcome(user_id)
            if outcome.get("email") or outcome.get("in_app"):
                results["welcome"] += 1
    except Exception:
        logger.exception("Post-setup welcome retry batch failed")
    try:
        results["security"] = _process_security_alert_retries(now)
    except Exception:
        logger.exception("Security notification retry batch failed")
    try:
        results["deadlines"] = _process_deadline_reminders(now)
    except Exception:
        logger.exception("Deadline notification batch failed")
    try:
        results["inactivity"] = _process_inactivity_reminders(now)
    except Exception:
        logger.exception("Inactivity notification batch failed")
    try:
        results["weekly_summaries"] = _process_weekly_in_app_summaries(now)
    except Exception:
        logger.exception("Weekly in-app learning summary batch failed")
    try:
        results["birthdays"] = _process_birthday_messages(now)
    except Exception:
        logger.exception("Birthday notification batch failed")
    return results



def notify_security_event(
    *,
    user_id: str,
    event_key: str,
    title: str,
    body: str,
) -> dict[str, bool]:
    """Deliver a high-impact learner security event in-app and by email."""
    from html import escape

    now = datetime.now(timezone.utc)
    rows = (
        supabase.table("users")
        .select("id,name,email,email_verified,account_status")
        .eq("id", str(user_id))
        .eq("account_status", "active")
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        return {"in_app": False, "email": False}
    user = rows[0]
    in_app = _create_in_app_once(
        user_id=str(user_id),
        event_key=event_key,
        notification_type="security_alert",
        title=title,
        body=body,
        action_url="/dashboard/settings",
        now=now,
    )
    if not user.get("email_verified") or not user.get("email"):
        return {"in_app": in_app, "email": False}
    name = str(user.get("name") or "there")
    safe_name = escape(name)
    text_body = f"Hi {name},\n\n{body}\n\nIf you did not make this change, contact Learnora support immediately.\n\nLearnora ME"
    html_body = f"""<!doctype html><html><body style="margin:0;background:#f5f7fb;font-family:Arial,sans-serif;color:#172033">
<div style="max-width:600px;margin:40px auto;padding:32px;background:#fff;border:1px solid #e5e7eb;border-radius:18px">
<h1>{escape(title)}</h1><p>Hi {safe_name},</p><p>{escape(body)}</p>
<p>If you did not make this change, contact <a href="mailto:learnorame@gmail.com">Learnora support</a> immediately.</p>
</div></body></html>"""
    email_sent = _send_automated_email_once(
        user_id=str(user_id),
        email=str(user["email"]),
        event_key=event_key,
        subject=title,
        text_body=text_body,
        html_body=html_body,
        now=now,
    )
    return {"in_app": in_app, "email": email_sent}



def send_marketing_campaign_email_once(
    *,
    user_id: str,
    campaign_id: str,
    subject: str,
    text_body: str,
    html_body: str,
) -> bool:
    """Send one consent-checked campaign email with a per-message unsubscribe link.

    Campaign authoring/audience selection belongs to the future messaging
    platform; this delivery primitive is deliberately not an audience builder.
    """
    from html import escape
    from routers import auth
    from routers.account_lifecycle import create_marketing_unsubscribe_url

    campaign = str(campaign_id or "").strip()
    if not campaign or len(campaign) > 120:
        raise ValueError("A valid campaign identifier is required.")
    now = datetime.now(timezone.utc)
    eligible = (
        supabase.table("users")
        .select("id,email,email_verified,account_status,marketing_email_opt_in")
        .eq("id", str(user_id))
        .eq("account_status", "active")
        .eq("email_verified", True)
        .eq("marketing_email_opt_in", True)
        .limit(1)
        .execute()
    ).data or []
    if not eligible:
        return False

    event_key = f"marketing:{campaign}"
    if not _claim_delivery(str(user_id), event_key, "email", now):
        return False

    unsubscribe_url = ""
    try:
        unsubscribe_url = create_marketing_unsubscribe_url(str(user_id))
        # Re-check consent as close as possible to the provider send. This
        # closes the normal queue-delay window after an audience was selected.
        current = (
            supabase.table("users")
            .select("id,email,email_verified,account_status,marketing_email_opt_in")
            .eq("id", str(user_id))
            .eq("account_status", "active")
            .eq("email_verified", True)
            .eq("marketing_email_opt_in", True)
            .limit(1)
            .execute()
        ).data or []
        if not current:
            raw_token = unsubscribe_url.partition("#token=")[2]
            if raw_token:
                supabase.table("learner_marketing_unsubscribe_tokens").update({
                    "consumed_at": now.isoformat(),
                }).eq("token_hash", auth._hash_token(raw_token)).is_("consumed_at", "null").execute()
            supabase.table("learner_notification_deliveries").update({
                "status": "suppressed",
                "last_error": "Marketing email consent was withdrawn before delivery.",
                "updated_at": now.isoformat(),
            }).eq("user_id", str(user_id)).eq("event_key", event_key).eq("channel", "email").eq("status", "sending").execute()
            return False

        user = current[0]
        text_with_unsubscribe = (
            f"{text_body.rstrip()}\n\n"
            f"Unsubscribe from Learnora marketing emails: {unsubscribe_url}\n"
        )
        html_with_unsubscribe = (
            f"{html_body}"
            f'<p style="margin-top:28px;font-size:12px;line-height:1.6;color:#64748b">'
            f'You are receiving this because you opted in to Learnora marketing emails. '
            f'<a href="{escape(unsubscribe_url, quote=True)}">Unsubscribe</a>.</p>'
        )
        auth._send_email(
            recipient=str(user["email"]),
            subject=subject,
            text_body=text_with_unsubscribe,
            html_body=html_with_unsubscribe,
        )
        _finish_delivery(str(user_id), event_key, "email", True, now)
        return True
    except Exception as exc:
        logger.exception("Marketing campaign email delivery failed for campaign %s", campaign)
        _finish_delivery(str(user_id), event_key, "email", False, now, type(exc).__name__)
        return False



def create_learner_notification(
    *,
    user_id: str,
    event_key: str,
    notification_type: str,
    title: str,
    body: str,
    action_url: str = "/dashboard/notifications",
    organisation_id: str | None = None,
) -> bool:
    """Create one durable in-app notification for a learner event."""
    return _create_in_app_once(
        user_id=str(user_id),
        event_key=event_key,
        notification_type=notification_type,
        title=title,
        body=body,
        action_url=action_url,
        organisation_id=organisation_id,
        now=datetime.now(timezone.utc),
    )


def create_account_event_notification(
    *,
    user_id: str,
    event_key: str,
    title: str,
    body: str,
    action_url: str = "/dashboard/settings",
) -> bool:
    """Create an idempotent in-app account lifecycle notification."""
    return create_learner_notification(
        user_id=user_id,
        event_key=event_key,
        notification_type="account_update",
        title=title,
        body=body,
        action_url=action_url,
    )
