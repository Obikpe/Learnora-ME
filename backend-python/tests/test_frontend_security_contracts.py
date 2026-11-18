"""Static regression checks for cross-layer frontend security contracts."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class FrontendSecurityContractTests(unittest.TestCase):
    def test_browser_auth_uses_cookie_session_and_clears_legacy_bearer_storage(self):
        client = (ROOT / "frontend-v02" / "lib" / "api" / "client.ts").read_text(encoding="utf-8")
        auth = (ROOT / "frontend-v02" / "lib" / "api" / "auth.ts").read_text(encoding="utf-8")
        self.assertIn('sessionStorage.setItem("phx_token", "cookie-session")', client)
        self.assertIn('localStorage.removeItem("phx_token")', client)
        self.assertIn('sessionStorage.removeItem("phx_token")', client)
        self.assertIn('sessionStorage.setItem("phx_session_epoch"', client)
        self.assertIn('sessionStorage.setItem("phx_logged_out", "1")', client)
        self.assertIn("credentials", client)
        self.assertIn("same-origin", client)
        self.assertIn('return "cookie-session:" +', auth)
        self.assertNotIn('localStorage.getItem("phx_token")', client)
        self.assertNotIn('localStorage.getItem("phx_token")', auth)

    def test_login_requires_server_verified_cookie_session_before_redirect(self):
        login = (ROOT / "frontend-v02" / "app" / "login" / "page.tsx").read_text(encoding="utf-8")
        self.assertIn("me=await currentUser()", login)
        self.assertIn("clearToken()", login)
        self.assertNotIn("verifiedMe||result", login)
        self.assertIn('me.role === "normal" && me.account_type === "learner"', login)

    def test_dashboard_preserves_last_successful_data_on_transient_failure(self):
        dashboard = (ROOT / "frontend-v02" / "app" / "dashboard" / "page.tsx").read_text(encoding="utf-8")
        client = (ROOT / "frontend-v02" / "lib" / "api" / "client.ts").read_text(encoding="utf-8")
        self.assertIn("if (progressData)", dashboard)
        self.assertIn("setLearning(progressData)", dashboard)
        self.assertIn("Keep the last successful dashboard data", dashboard)
        self.assertIn("setError(\"Your learning records could not be loaded.", dashboard)
        self.assertIn("error.status = response.status", client)
        self.assertIn('if (progressResult[1].status === "fulfilled") setActivitySummary', dashboard)
        self.assertIn("if (evidenceResult.status === \"fulfilled\") setEvidence", dashboard)

    def test_dashboard_session_gate_recovers_from_temporary_verification_failures(self):
        guard = (ROOT / "frontend-v02" / "components" / "dashboard" / "DashboardSessionGuard.tsx").read_text(encoding="utf-8")
        self.assertIn("status === 401 || status === 403", guard)
        self.assertIn("status === 409", guard)
        self.assertIn("We could not verify your Learnora session", guard)
        self.assertIn("onClick={() => void validate()}", guard)
        self.assertIn('"/login?next="', guard)
        self.assertNotIn('window.location.replace("/")', guard)

    def test_individual_dashboard_sections_do_not_expose_assigned_account_discovery(self):
        page = (ROOT / "frontend-v02" / "app" / "dashboard" / "[section]" / "page.tsx").read_text(encoding="utf-8")
        self.assertIn("const assignedOnly=Boolean(", page)
        self.assertIn('location.href=me.account_type==="cohort"?"/dashboard/cohort":"/dashboard"', page)
        self.assertIn('me.account_type!=="learner"||me.role!=="normal"', page)
        self.assertIn('memberships.some((membership:any)=>membership.status==="active")', page)

    def test_active_learnora_me_ui_has_no_product_specific_legacy_workspace(self):
        root = ROOT / "frontend-v02"
        sidebar = (root / "components" / "dashboard" / "Sidebar.tsx").read_text(encoding="utf-8")
        section = (root / "app" / "dashboard" / "[section]" / "page.tsx").read_text(encoding="utf-8")
        courses = (root / "app" / "courses" / "page.tsx").read_text(encoding="utf-8")
        tracks = (root / "app" / "tracks" / "page.tsx").read_text(encoding="utf-8")
        legacy_route = (root / "app" / "dashboard" / "witstart" / "page.tsx").read_text(encoding="utf-8")
        self.assertNotIn("witstart", sidebar.lower())
        self.assertNotIn("witstart", section.lower())
        self.assertNotIn("witstart", courses.lower())
        self.assertNotIn("witstart", tracks.lower())
        self.assertIn('redirect("/dashboard")', legacy_route)

    def test_ai_tutor_is_hidden_and_unavailable_during_active_quizzes(self):
        legacy_route = (ROOT / "frontend-v02" / "app" / "dashboard" / "learning" / "[courseId]" / "page.tsx").read_text(encoding="utf-8")
        ai_api = (ROOT / "backend-python" / "routers" / "ai.py").read_text(encoding="utf-8")
        ai_page = (ROOT / "frontend-v02" / "app" / "dashboard" / "ai" / "page.tsx").read_text(encoding="utf-8")
        self.assertIn('redirect("/courses/"+encodeURIComponent(params.courseId))', legacy_route)
        self.assertIn("_assert_no_active_quiz_session(str(user.id))", ai_api)
        self.assertIn("isQuizActiveInThisTab()", ai_page)
        self.assertIn("Tutor unavailable during quizzes", ai_page)
        self.assertIn('request<any>("/progress/quiz-sessions/me")', ai_page)

    def test_certificate_verification_has_one_route_and_displays_revocation(self):
        route = ROOT / "frontend-v02" / "app" / "verify-certificate"
        self.assertTrue((route / "[certificateNumber]" / "page.tsx").is_file())
        self.assertFalse((route / "[number]").exists(), "Next.js cannot define duplicate dynamic route folders.")
        page = (route / "[certificateNumber]" / "page.tsx").read_text(encoding="utf-8")
        self.assertIn('data.status==="revoked"', page)
        self.assertIn("Revoked record", page)

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
