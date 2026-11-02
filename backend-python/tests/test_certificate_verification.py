"""Certificate verification must respect revocation without leaking staff-only reasons."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from routers import credentials


class Query:
    def __init__(self, table, fixtures):
        self.table_name = table
        self.fixtures = fixtures
        self.filters = []
    def select(self, *_args, **_kwargs): return self
    def eq(self, key, value):
        self.filters.append((key, value))
        return self
    def limit(self, _value): return self
    def execute(self):
        rows = list(self.fixtures.get(self.table_name, []))
        for key, value in self.filters:
            rows = [row for row in rows if str(row.get(key)) == str(value)]
        return SimpleNamespace(data=rows)


class FakeSupabase:
    def __init__(self, fixtures): self.fixtures = fixtures
    def table(self, name): return Query(name, self.fixtures)


class CertificateVerificationTests(unittest.TestCase):
    def _fixtures(self, revoked_at=None):
        return {
            "certificates": [{
                "id": "certificate-1",
                "course_id": "course-1",
                "certificate_number": "LRN-COURSE-ABC123",
                "issued_at": "2026-10-01T12:00:00+00:00",
                "metadata": {"recipient_name": "Learner", "course_title": "SQL Foundations"},
                "revoked_at": revoked_at,
                "revocation_reason": "Staff-only internal reason",
            }],
            "learnora_courses": [{"id": "course-1", "title": "SQL Foundations"}],
        }

    def test_valid_certificate_is_publicly_verified(self):
        with patch.object(credentials, "supabase", FakeSupabase(self._fixtures())):
            result = credentials.verify_certificate(" lrn-course-abc123 ")
        self.assertTrue(result["valid"])
        self.assertEqual(result["certificate"]["status"], "valid")
        self.assertNotIn("revocation_reason", result["certificate"])

    def test_revoked_certificate_is_not_reported_as_valid(self):
        fixtures = self._fixtures("2026-11-02T10:00:00+00:00")
        with patch.object(credentials, "supabase", FakeSupabase(fixtures)):
            result = credentials.verify_certificate("LRN-COURSE-ABC123")
        self.assertFalse(result["valid"])
        self.assertEqual(result["certificate"]["status"], "revoked")
        self.assertEqual(result["certificate"]["revoked_at"], "2026-11-02T10:00:00+00:00")
        self.assertNotIn("revocation_reason", result["certificate"])


if __name__ == "__main__":
    unittest.main()
