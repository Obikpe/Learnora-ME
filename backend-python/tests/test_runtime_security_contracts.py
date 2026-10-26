"""Regression checks for runtime configuration and readiness disclosure."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RuntimeSecurityContractTests(unittest.TestCase):
    def test_platform_environment_is_not_overridden_by_local_dotenv(self):
        source = (ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn("load_dotenv(dotenv_path=ENV_PATH, override=False)", source)

    def test_local_frontends_default_to_local_api_not_production(self):
        for relative in ("frontend-v02/lib/api/client.ts", "frontend-team/lib/api.ts"):
            source = (ROOT.parent / relative).read_text(encoding="utf-8")
            with self.subTest(frontend=relative):
                self.assertIn("http://localhost:8000", source)
                self.assertIn("process.env.NODE_ENV", source)

    def test_local_cors_allows_both_frontend_ports_only_outside_production(self):
        source = (ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn('if os.getenv("APP_ENV", "production").strip().lower() != "production":', source)
        self.assertIn('origins.extend(["http://localhost:3000", "http://localhost:3001"])', source)

    def test_local_run_scripts_target_active_apps(self):
        package = json.loads((ROOT.parent / "package.json").read_text(encoding="utf-8"))
        self.assertIn("frontend-v02", package["scripts"]["dev:me"])
        self.assertIn("frontend-team", package["scripts"]["dev:teams"])
        self.assertIn("backend-python", package["scripts"]["dev:backend"])
        env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
        self.assertIn("APP_ENV=development", env_example)
        self.assertIn("FRONTEND_URL=http://localhost:3000", env_example)
        self.assertIn("INTERNAL_FRONTEND_URL=http://localhost:3001", env_example)

    def test_course_content_errors_do_not_return_database_exception_details(self):
        for relative in ("routers/course_content.py", "routers/internal_content.py"):
            source = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(router=relative):
                self.assertNotIn("str(exc)", source)

    def test_readiness_response_does_not_disclose_internal_check_details(self):
        source = (ROOT / "main.py").read_text(encoding="utf-8")
        readiness = source.split("@app.get(\"/api/ready\")", 1)[1]
        self.assertNotIn('"checks":', readiness)
        self.assertNotIn('"database": "unavailable"', readiness)
        self.assertNotIn('"database": "reachable"', readiness)


if __name__ == "__main__":
    unittest.main()
