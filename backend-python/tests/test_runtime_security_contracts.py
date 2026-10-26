"""Regression checks for runtime configuration and readiness disclosure."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RuntimeSecurityContractTests(unittest.TestCase):
    def test_platform_environment_is_not_overridden_by_local_dotenv(self):
        source = (ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn("load_dotenv(dotenv_path=ENV_PATH, override=False)", source)

    def test_readiness_response_does_not_disclose_internal_check_details(self):
        source = (ROOT / "main.py").read_text(encoding="utf-8")
        readiness = source.split("@app.get(\"/api/ready\")", 1)[1]
        self.assertNotIn('"checks":', readiness)
        self.assertNotIn('"database": "unavailable"', readiness)
        self.assertNotIn('"database": "reachable"', readiness)


if __name__ == "__main__":
    unittest.main()
