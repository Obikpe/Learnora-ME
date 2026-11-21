import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

from routers import progress


class LessonMediaSigningTests(unittest.TestCase):
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
