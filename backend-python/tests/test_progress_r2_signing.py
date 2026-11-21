from unittest.mock import MagicMock, patch

from routers.progress import _sign_lesson_assets


def test_cloudflare_lesson_video_gets_a_short_lived_r2_url_from_its_recorded_bucket():
    row = {
        "id": "video-1",
        "provider": "cloudflare",
        "storage_bucket": "learnora-private-media",
        "storage_path": "courses/course-1/lessons/lesson-1/package-1.mp4",
        "status": "ready",
    }
    client = MagicMock()
    client.generate_presigned_url.return_value = "https://r2.example/signed-video"

    with patch("routers.progress._r2_s3_client", return_value=client):
        result = _sign_lesson_assets([row], require_private_provider=True)

    assert result[0]["signed_url"] == "https://r2.example/signed-video"
    client.generate_presigned_url.assert_called_once_with(
        "get_object",
        Params={
            "Bucket": "learnora-private-media",
            "Key": "courses/course-1/lessons/lesson-1/package-1.mp4",
        },
        ExpiresIn=3600,
    )


def test_private_lesson_asset_signing_does_not_return_external_video_providers():
    rows = [
        {"id": "external-1", "provider": "youtube", "external_video_id": "abc123"},
        {"id": "external-2", "provider": "vimeo", "external_video_id": "xyz456"},
    ]

    assert _sign_lesson_assets(rows, require_private_provider=True) == []


def test_cloudflare_lesson_video_remains_unavailable_when_r2_credentials_are_missing():
    row = {
        "id": "video-2",
        "provider": "cloudflare",
        "storage_bucket": "learnora-private-media",
        "storage_path": "courses/course-1/lessons/lesson-2/package-2.mp4",
    }

    with patch("routers.progress._r2_s3_client", return_value=None):
        result = _sign_lesson_assets([row], require_private_provider=True)

    assert result[0]["signed_url"] is None
