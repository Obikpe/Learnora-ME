"""Contract tests for Gmail API email delivery without SMTP or Resend."""
import base64
import unittest
from email import message_from_bytes
from unittest.mock import MagicMock, patch

import routers.auth as auth


class GmailApiDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.patches = [
            patch.object(auth, "APP_ENV", "production"),
            patch.object(auth, "GMAIL_OAUTH_CLIENT_ID", "client-id"),
            patch.object(auth, "GMAIL_OAUTH_CLIENT_SECRET", "client-secret"),
            patch.object(auth, "GMAIL_OAUTH_REFRESH_TOKEN", "refresh-token"),
            patch.object(auth, "GMAIL_USER_EMAIL", "sender@gmail.com"),
            patch.object(auth, "GMAIL_FROM_EMAIL", "sender@gmail.com"),
            patch.object(auth, "GMAIL_FROM_NAME", "Learnora Me"),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)

    def test_refreshes_oauth_token_and_sends_base64url_mime_message(self):
        token_response = MagicMock()
        token_response.is_success = True
        token_response.json.return_value = {"access_token": "short-lived-access-token"}
        send_response = MagicMock()
        send_response.is_success = True

        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.side_effect = [token_response, send_response]

        with patch.object(auth.httpx, "Client", return_value=client):
            auth._send_email(
                recipient="learner@example.com",
                subject="Verify your Learnora account",
                text_body="Open the verification link.",
                html_body="<p>Open the verification link.</p>",
            )

        self.assertEqual(client.post.call_count, 2)
        token_call = client.post.call_args_list[0]
        self.assertEqual(token_call.args[0], auth.GMAIL_OAUTH_TOKEN_URL)
        self.assertEqual(token_call.kwargs["data"]["grant_type"], "refresh_token")
        self.assertEqual(token_call.kwargs["data"]["refresh_token"], "refresh-token")

        send_call = client.post.call_args_list[1]
        self.assertEqual(send_call.args[0], auth.GMAIL_API_SEND_URL)
        self.assertEqual(
            send_call.kwargs["headers"]["Authorization"],
            "Bearer short-lived-access-token",
        )
        raw = send_call.kwargs["json"]["raw"]
        decoded = base64.urlsafe_b64decode(raw.encode("ascii"))
        mime = message_from_bytes(decoded)
        self.assertEqual(mime["To"], "learner@example.com")
        self.assertEqual(mime["Subject"], "Verify your Learnora account")

    def test_legacy_smtp_and_resend_environment_is_ignored(self):
        legacy_environment = {
            "SMTP_HOST": "smtp.gmail.com",
            "SMTP_PORT": "465",
            "SMTP_USERNAME": "old-sender@gmail.com",
            "SMTP_PASSWORD": "old-app-password",
            "RESEND_API_KEY": "legacy-resend-key",
            "RESEND_FROM_EMAIL": "onboarding@resend.dev",
        }
        with (
            patch.dict("os.environ", legacy_environment),
            patch.object(auth, "GMAIL_OAUTH_CLIENT_ID", ""),
            patch.object(auth, "GMAIL_OAUTH_CLIENT_SECRET", ""),
            patch.object(auth, "GMAIL_OAUTH_REFRESH_TOKEN", ""),
            patch.object(auth, "GMAIL_USER_EMAIL", ""),
            patch.object(auth, "GMAIL_FROM_EMAIL", ""),
        ):
            self.assertFalse(auth._email_configured())


if __name__ == "__main__":
    unittest.main()
