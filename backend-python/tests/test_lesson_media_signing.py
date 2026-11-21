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


if __name__ == "__main__":
    unittest.main()
