# Unit test for Error Handler (Debug vs Production Mode)

import unittest
import os
from framework.error_handler import render_exception, get_code_snippet
from framework.request import Request

class TestErrorHandler(unittest.TestCase):
    def test_debug_mode_renders_full_interactive_debugger(self):
        os.environ["APP_DEBUG"] = "bener"
        try:
            1 / 0
        except ZeroDivisionError as e:
            req = Request(
                method="GET",
                path="/test-error",
                headers={"User-Agent": "TestBrowser/1.0", "X-Forwarded-For": "203.0.113.195"},
                query={"filter": "active"}
            )
            html_output = render_exception(e, req)

            self.assertIn("ZeroDivisionError", html_output)
            self.assertIn("Larapak Engine", html_output)
            self.assertIn("StackTrace & Berkas", html_output)
            self.assertIn("Panyuwunan (Request)", html_output)
            self.assertIn("Lingkungan (Environment)", html_output)
            self.assertIn("203.0.113.195", html_output)
            self.assertIn("/test-error", html_output)

    def test_production_mode_renders_clean_safe_500(self):
        os.environ["APP_DEBUG"] = "salah"
        try:
            raise RuntimeError("Database connection string leaked! password=secret123")
        except RuntimeError as e:
            html_output = render_exception(e)

            self.assertIn("500 &bull; SERVER ERROR", html_output)
            self.assertIn("Alangan Ing Server", html_output)
            # Must NOT leak secret details or file traces in production
            self.assertNotIn("password=secret123", html_output)
            self.assertNotIn("StackTrace", html_output)

    def test_get_code_snippet(self):
        # Read this test file itself
        lines = get_code_snippet(__file__, 10, window=3)
        self.assertTrue(len(lines) > 0)
        has_error_line = any(line["is_error"] and line["number"] == 10 for line in lines)
        self.assertTrue(has_error_line)

if __name__ == "__main__":
    unittest.main()
