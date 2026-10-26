"""Static regression checks for cross-layer frontend security contracts."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class FrontendSecurityContractTests(unittest.TestCase):
    def test_bearer_token_is_session_scoped_and_legacy_persistent_token_is_cleared(self):
        client = (ROOT / "frontend-v02" / "lib" / "api" / "client.ts").read_text(encoding="utf-8")
        auth = (ROOT / "frontend-v02" / "lib" / "api" / "auth.ts").read_text(encoding="utf-8")
        self.assertIn('sessionStorage.getItem("phx_token")', client)
        self.assertIn('sessionStorage.setItem("phx_token",v)', client)
        self.assertIn('localStorage.removeItem("phx_token")', client)
        self.assertNotIn('localStorage.getItem("phx_token")', client)
        self.assertNotIn('localStorage.getItem("phx_token")', auth)
        self.assertIn("return token();", auth)

    def test_frontend_security_headers_include_csp_and_clickjacking_protection(self):
        for app in ("frontend-v02", "frontend-team"):
            config = ROOT / app / "vercel.json"
            self.assertTrue(config.is_file(), f"Missing {config}")
            content = config.read_text(encoding="utf-8")
            with self.subTest(app=app):
                self.assertIn("Content-Security-Policy", content)
                self.assertIn("X-Frame-Options", content)
                self.assertIn("X-Content-Type-Options", content)


if __name__ == "__main__":
    unittest.main()
