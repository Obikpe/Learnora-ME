"""Regression tests for criteria-driven course-completion badge awards."""
import unittest
from types import SimpleNamespace

from services.course_completion_badges import award_course_completion_badges


class FakeQuery:
    def __init__(self, table, database):
        self.table = table
        self.database = database
        self.payload = None

    def select(self, *_args, **_kwargs):
        return self

    def upsert(self, payload, **_kwargs):
        self.payload = payload
        return self

    def execute(self):
        if self.table == "badges":
            return SimpleNamespace(data=self.database.badges)
        key = (self.payload["badge_id"], self.payload["user_id"])
        self.database.awards.add(key)
        return SimpleNamespace(data=[self.payload])


class FakeDatabase:
    def __init__(self):
        self.badges = [
            {
                "id": "badge-data-analytics",
                "criteria": {
                    "type": "course_completion",
                    "course_id": "course-intro-analytics",
                    "skill_id": "skill-data-analytics",
                },
            },
            {
                "id": "badge-sql",
                "criteria": {
                    "type": "course_completion",
                    "course_id": "course-sql",
                    "skill_id": "skill-sql",
                },
            },
        ]
        self.awards = set()

    def table(self, name):
        return FakeQuery(name, self)


class CourseCompletionBadgeTests(unittest.TestCase):
    def test_only_badges_mapped_to_the_completed_course_are_awarded(self):
        database = FakeDatabase()
        awarded = award_course_completion_badges(
            "learner-1",
            "course-intro-analytics",
            database=database,
        )
        self.assertEqual(awarded, ["badge-data-analytics"])
        self.assertEqual(database.awards, {("badge-data-analytics", "learner-1")})

    def test_awarding_is_idempotent(self):
        database = FakeDatabase()
        first = award_course_completion_badges("learner-1", "course-intro-analytics", database=database)
        second = award_course_completion_badges("learner-1", "course-intro-analytics", database=database)
        self.assertEqual(first, second)
        self.assertEqual(len(database.awards), 1)

    def test_unknown_course_does_not_award_unrelated_badges(self):
        database = FakeDatabase()
        self.assertEqual(award_course_completion_badges("learner-1", "unknown-course", database=database), [])
        self.assertEqual(database.awards, set())


if __name__ == "__main__":
    unittest.main()
