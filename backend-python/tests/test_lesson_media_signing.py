import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

from routers import progress


class LessonMediaSigningTests(unittest.TestCase):
    def test_approved_external_video_providers_remain_available_to_the_player(self):
        videos = progress._sign_lesson_assets([
            {"id": "youtube-1", "provider": "youtube", "external_video_id": "video123"},
            {"id": "vimeo-1", "provider": "vimeo", "external_video_id": "456789"},
        ])

        self.assertEqual([video["provider"] for video in videos], ["youtube", "vimeo"])
        self.assertEqual(videos[0]["external_video_id"], "video123")
        self.assertEqual(videos[1]["external_video_id"], "456789")

    def test_legacy_video_and_resource_media_use_their_private_buckets(self):
        storage = MagicMock()
        storage.from_.return_value.create_signed_url.return_value = SimpleNamespace(
            data={"signedUrl": "https://media.example.invalid/signed"}
        )
        database = SimpleNamespace(storage=storage)

        with patch.object(progress, "supabase", database):
            videos = progress._sign_lesson_assets([{
                "id": "video-1",
                "provider": "supabase",
                "storage_path": "course/video.mp4",
            }])
            resources = progress._sign_lesson_assets(
                [{
                    "id": "resource-1",
                    "provider": "supabase",
                    "storage_path": "course/worksheet.pdf",
                }],
                default_supabase_bucket="learnora-resources",
            )

        self.assertEqual(videos[0]["signed_url"], "https://media.example.invalid/signed")
        self.assertEqual(resources[0]["signed_url"], "https://media.example.invalid/signed")
        self.assertEqual(
            storage.from_.call_args_list,
            [call("learnora-course-media"), call("learnora-resources")],
        )

    def test_learner_workspace_returns_signed_private_videos_and_resources(self):
        class Query:
            def __init__(self, data):
                self.data = data
            def select(self, *_args, **_kwargs): return self
            def eq(self, *_args, **_kwargs): return self
            def limit(self, *_args, **_kwargs): return self
            def order(self, *_args, **_kwargs): return self
            def execute(self): return SimpleNamespace(data=self.data)

        database = SimpleNamespace(table=lambda name: {
            "learner_lesson_notes": Query([]),
            "lesson_videos": Query([{
                "id": "video-1", "provider": "cloudflare",
                "storage_path": "courses/course-1/lesson-1/video.mp4",
                "status": "ready",
            }]),
            "lesson_resources": Query([{
                "id": "resource-1", "provider": "supabase",
                "storage_path": "courses/course-1/lesson-1/resources/guide.pdf",
            }]),
        }[name])

        def signer(rows, **kwargs):
            return [{**row, "signed_url": "https://media.example.invalid/" + row["id"]} for row in rows]

        with patch("routers.progress._lesson_context", return_value=(
            {"id": "lesson-1", "content": "Lesson notes"}, "course-1"
        )), patch.object(progress, "supabase", database), patch.object(
            progress, "_sign_lesson_assets", side_effect=signer
        ) as sign:
            result = progress.get_lesson_workspace("lesson-1", SimpleNamespace(id="learner-1"))

        self.assertEqual(result["videos"][0]["signed_url"], "https://media.example.invalid/video-1")
        self.assertEqual(result["resources"][0]["signed_url"], "https://media.example.invalid/resource-1")
        self.assertEqual(sign.call_count, 2)
        self.assertEqual(sign.call_args_list[1].kwargs["default_supabase_bucket"], "learnora-resources")


if __name__ == "__main__":
    unittest.main()
