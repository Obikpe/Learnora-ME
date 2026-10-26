"""Static regression checks for cross-layer frontend security contracts."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class FrontendSecurityContractTests(unittest.TestCase):
    def test_browser_auth_uses_cookie_session_and_clears_legacy_bearer_storage(self):
        client = (ROOT / "frontend-v02" / "lib" / "api" / "client.ts").read_text(encoding="utf-8")
        auth = (ROOT / "frontend-v02" / "lib" / "api" / "auth.ts").read_text(encoding="utf-8")
        self.assertIn('sessionStorage.getItem("phx_token")', client)
        self.assertIn('sessionStorage.setItem("phx_token","cookie-session")', client)
        self.assertIn('localStorage.removeItem("phx_token")', client)
        self.assertNotIn('localStorage.getItem("phx_token")', client)
        self.assertNotIn('localStorage.getItem("phx_token")', auth)
        self.assertIn('sessionStorage.getItem("phx_token") || "cookie-session"', auth)
        self.assertIn('credentials:"same-origin"', client)
        self.assertIn('t!=="cookie-session"', client)
        self.assertIn('const BASE=""', client)

    def test_frontend_api_proxies_are_configured_for_same_origin_cookies(self):
        for relative in ("frontend-v02/next.config.mjs", "frontend-team/next.config.mjs"):
            source = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(config=relative):
                self.assertIn("API_PROXY_TARGET", source)
                self.assertIn("http://localhost:8000", source)
                self.assertIn("/api/:path*", source)

    def test_email_token_pages_support_new_fragments_and_existing_query_links(self):
        for relative in ("frontend-v02/app/verify-email/page.tsx", "frontend-v02/app/reset-password/page.tsx"):
            source = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(page=relative):
                self.assertIn("window.location.hash", source)
                self.assertIn("window.location.search", source)
                self.assertIn("window.history.replaceState", source)

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
