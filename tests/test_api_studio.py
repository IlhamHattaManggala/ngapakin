# Unit Tests for Larapak Route & API Studio and OpenAPI 3.0 Generator

import json
import unittest
from framework.router import Router
from framework.studio import is_studio_enabled, generate_openapi_spec, render_studio_html
from framework.wsgi import LarapakWSGI


class TestApiStudio(unittest.TestCase):
    def setUp(self):
        self.router = Router()
        self.router.get("/", "HomeController@index")
        self.router.get("/produk/{id}", "ProductController@detail")
        self.router.post("/api/produk", "ProductApiController@store")
        self.router.put("/api/produk/{id}", "ProductApiController@update")
        self.router.delete("/api/produk/{id}", "ProductApiController@destroy")

    def test_studio_is_enabled_by_default(self):
        self.assertTrue(is_studio_enabled())

    def test_generate_openapi_spec(self):
        spec = generate_openapi_spec(self.router, app_name="TokoOnline", version="1.0.7")
        self.assertEqual(spec["openapi"], "3.0.3")
        self.assertEqual(spec["info"]["title"], "TokoOnline API & Route Spec")
        self.assertIn("/produk/{id}", spec["paths"])
        self.assertIn("get", spec["paths"]["/produk/{id}"])
        self.assertEqual(spec["paths"]["/produk/{id}"]["get"]["parameters"][0]["name"], "id")
        self.assertEqual(spec["paths"]["/produk/{id}"]["get"]["parameters"][0]["in"], "path")
        self.assertIn("/api/produk", spec["paths"])
        self.assertIn("post", spec["paths"]["/api/produk"])
        self.assertIn("requestBody", spec["paths"]["/api/produk"]["post"])

    def test_render_studio_html(self):
        html = render_studio_html(self.router)
        self.assertIn("Larapak Route & API Studio", html)
        self.assertIn("HomeController@index", html)
        self.assertIn("ProductController@detail", html)
        self.assertIn("/api-studio/openapi.json", html)
        self.assertIn("Pratinjau Tampilan (Live)", html)
        self.assertIn("preview-iframe", html)
        self.assertIn("raw-code-box", html)
        self.assertIn("copyResponseCode", html)

    def test_wsgi_serves_api_studio(self):
        app = LarapakWSGI(router=self.router)
        app.loader = type("DummyLoader", (), {"call_action": lambda *args: "dummy"})()
        app.pipeline = type("DummyPipeline", (), {"execute_chain": lambda self, mw, req, res, dest: dest(req, res)})()
        app._initialized = True

        # Test GET /api-studio
        environ_studio = {
            "REQUEST_METHOD": "GET",
            "PATH_INFO": "/api-studio",
            "wsgi.url_scheme": "http",
            "SERVER_NAME": "localhost",
            "SERVER_PORT": "8000"
        }
        headers_captured = []
        status_captured = []

        def start_response(status, headers):
            status_captured.append(status)
            headers_captured.extend(headers)

        body = app(environ_studio, start_response)
        response_text = b"".join(body).decode("utf-8")
        self.assertEqual(status_captured[0], "200 OK")
        self.assertTrue(any("text/html" in v for k, v in headers_captured if k.lower() == "content-type"))
        self.assertIn("Larapak Route & API Studio", response_text)

        # Test GET /api/studio alias
        headers_captured.clear()
        status_captured.clear()
        environ_alias = dict(environ_studio, PATH_INFO="/api/studio")
        body = app(environ_alias, start_response)
        self.assertEqual(status_captured[0], "200 OK")

        # Test GET /api-studio/openapi.json
        headers_captured.clear()
        status_captured.clear()
        environ_spec = dict(environ_studio, PATH_INFO="/api-studio/openapi.json")
        body = app(environ_spec, start_response)
        response_json = json.loads(b"".join(body).decode("utf-8"))
        self.assertEqual(status_captured[0], "200 OK")
        self.assertTrue(any("application/json" in v for k, v in headers_captured if k.lower() == "content-type"))
        self.assertEqual(response_json["openapi"], "3.0.3")
        self.assertIn("/produk/{id}", response_json["paths"])


if __name__ == "__main__":
    unittest.main()
