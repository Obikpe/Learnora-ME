"""Creator finance routes must not reuse the broad course-assignment permission."""
import os
import unittest

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "unit-test-service-key")

from routers import creator_finance


class CreatorFinancePermissionTests(unittest.TestCase):
    def test_finance_mutations_use_distinct_permissions(self):
        expected = {
            "/api/creator-finance/sales": "creator_sales.record",
            "/api/creator-finance/sales/{sale_id}/release": "creator_sales.release",
            "/api/creator-finance/sales/{sale_id}/refund": "creator_sales.refund",
        }
        routes = {route.path: route for route in creator_finance.router.routes}
        for path, permission in expected.items():
            with self.subTest(path=path):
                route = routes[path]
                permission_dependencies = [
                    dependency.call
                    for dependency in route.dependant.dependencies
                    if getattr(dependency.call, "__name__", "") == "dependency"
                ]
                captured = []
                for dependency in permission_dependencies:
                    for cell in getattr(dependency, "__closure__", ()) or ():
                        try:
                            value = cell.cell_contents
                        except ValueError:
                            continue
                        if isinstance(value, str) and value in {
                            "courses.assign",
                            "creator_sales.record",
                            "creator_sales.release",
                            "creator_sales.refund",
                        }:
                            captured.append(value)
                self.assertIn(permission, captured)
                self.assertNotIn("courses.assign", captured)


if __name__ == "__main__":
    unittest.main()
