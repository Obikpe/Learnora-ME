"""Regression tests for inactive-organisation membership writes."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from fastapi import HTTPException
from routers import organisation_members


class Query:
    def __init__(self, db, table):
        self.db = db
        self.table_name = table
        self.filters = {}
        self.operation = "select"
        self.payload = None

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, key, value):
        self.filters[key] = str(value)
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def update(self, payload):
        self.operation = "update"
        self.payload = payload
        self.db.update_called = True
        return self

    def execute(self):
        rows = self.db.rows.get(self.table_name, [])
        matches = [row for row in rows if all(str(row.get(k)) == v for k, v in self.filters.items())]
        if self.operation == "update":
            for row in matches:
                row.update(self.payload or {})
        return SimpleNamespace(data=matches)


class FakeSupabase:
    def __init__(self, rows):
        self.rows = rows
        self.update_called = False

    def table(self, name):
        return Query(self, name)


def platform_admin():
    return SimpleNamespace(is_platform_admin=True, organisation_id=None, user_id="platform-admin")


class InactiveOrganisationMembershipTests(unittest.TestCase):
    def setUp(self):
        self.org_id = "11111111-1111-4111-8111-111111111111"
        self.user_id = "22222222-2222-4222-8222-222222222222"
        self.member_id = "33333333-3333-4333-8333-333333333333"
        self.db = FakeSupabase({
            "organisations": [{"id": self.org_id, "is_active": False, "settings": {}}],
            "users": [{"id": self.user_id, "email": "learner@example.com", "name": "Learner", "role": "normal"}],
            "organisation_members": [{
                "id": self.member_id, "organisation_id": self.org_id,
                "user_id": self.user_id, "role": "learner", "status": "suspended",
                "joined_at": "2026-01-01T00:00:00Z",
            }],
        })

    def test_existing_member_can_be_found_by_normalized_email(self):
        with patch.object(organisation_members, "supabase", self.db):
            user = organisation_members._user_by_email(" Learner@Example.com ")
        self.assertEqual(user["id"], self.user_id)

    def test_invalid_member_email_is_rejected(self):
        with patch.object(organisation_members, "supabase", self.db):
            with self.assertRaises(HTTPException) as raised:
                organisation_members._user_by_email("not-an-email")
        self.assertEqual(raised.exception.status_code, 400)

    def test_member_creation_requires_exactly_one_account_identifier(self):
        self.db.rows["organisations"][0]["is_active"] = True
        payload = organisation_members.AddOrganisationMember(
            user_id=UUID(self.user_id), email="learner@example.com", role="learner"
        )
        with patch.object(organisation_members, "supabase", self.db):
            with self.assertRaises(HTTPException) as raised:
                organisation_members.add_member(UUID(self.org_id), payload, platform_admin())
        self.assertEqual(raised.exception.status_code, 400)
        self.assertFalse(self.db.update_called)

    def test_cannot_add_member_to_inactive_organisation(self):
        payload = organisation_members.AddOrganisationMember(user_id=UUID(self.user_id), role="learner")
        with patch.object(organisation_members, "supabase", self.db):
            with self.assertRaises(HTTPException) as raised:
                organisation_members.add_member(UUID(self.org_id), payload, platform_admin())
        self.assertEqual(raised.exception.status_code, 409)
        self.assertFalse(self.db.update_called)

    def test_cannot_reactivate_member_in_inactive_organisation(self):
        payload = organisation_members.UpdateOrganisationMember(status="active")
        with patch.object(organisation_members, "supabase", self.db):
            with self.assertRaises(HTTPException) as raised:
                organisation_members.update_member(UUID(self.org_id), UUID(self.member_id), payload, platform_admin())
        self.assertEqual(raised.exception.status_code, 409)
        self.assertEqual(self.db.rows["organisation_members"][0]["status"], "suspended")
        self.assertFalse(self.db.update_called)


if __name__ == "__main__":
    unittest.main()
