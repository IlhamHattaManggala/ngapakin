import io
import unittest
from framework.wsgi import LarapakWSGI
from framework.router import Router
from framework.response import Response
from framework.csrf import CSRF
from framework.session import Session

class TestWSGIAdapter(unittest.TestCase):
    def setUp(self):
        CSRF.clear_exemptions()
        self.router = Router()
        
        # Simple test routes
        self.router.get("/hello", lambda req, res: res.html("<h1>Sugeng Rawuh</h1>"))
        self.router.post("/submit", lambda req, res: res.json({"received": req.input("title")}))
        self.router.put("/resource/{id}", lambda req, res: res.json({"updated": req.params.get("id")}))
        
        # Route exempted from CSRF for easy testing
        CSRF.exempt("/api/exempt")
        self.router.post("/api/exempt", lambda req, res: res.json({"status": "exempted"}))

        # Instantiate WSGI app with our test router
        self.app = LarapakWSGI(router=self.router)
        self.app._initialized = True
        
        from framework.controller import ControllerLoader
        from framework.middleware import MiddlewarePipeline
        import os
        from ngapak import VM
        
        vm = VM()
        vm.globals["sesi"] = Session()
        self.router.vm = vm
        self.app.loader = ControllerLoader(os.path.abspath("app/Controllers"), vm)
        self.app.pipeline = MiddlewarePipeline(os.path.abspath("app/Middleware"), vm)

    def test_get_request(self):
        response_status = None
        response_headers = []

        def start_response(status, headers):
            nonlocal response_status, response_headers
            response_status = status
            response_headers = headers

        environ = {
            "REQUEST_METHOD": "GET",
            "PATH_INFO": "/hello",
            "QUERY_STRING": "",
            "wsgi.input": io.BytesIO(b""),
            "wsgi.url_scheme": "http"
        }

        body = self.app(environ, start_response)
        self.assertEqual(response_status, "200 OK")
        self.assertTrue(any(k == "Content-Type" and "text/html" in v for k, v in response_headers))
        self.assertIn(b"Sugeng Rawuh", b"".join(body))

    def test_404_not_found(self):
        response_status = None
        def start_response(status, headers):
            nonlocal response_status
            response_status = status

        environ = {
            "REQUEST_METHOD": "GET",
            "PATH_INFO": "/halaman_gaib",
            "QUERY_STRING": "",
            "wsgi.input": io.BytesIO(b""),
            "wsgi.url_scheme": "http"
        }

        body = self.app(environ, start_response)
        self.assertEqual(response_status, "404 Not Found")
        self.assertIn(b"404 Halaman Tidak Ditemukan", b"".join(body))

    def test_csrf_protection_under_wsgi(self):
        response_status = None
        def start_response(status, headers):
            nonlocal response_status
            response_status = status

        payload = b"title=BelajarNgapak"
        environ = {
            "REQUEST_METHOD": "POST",
            "PATH_INFO": "/submit",
            "CONTENT_TYPE": "application/x-www-form-urlencoded",
            "CONTENT_LENGTH": str(len(payload)),
            "wsgi.input": io.BytesIO(payload),
            "wsgi.url_scheme": "http"
        }

        # POST without CSRF token must result in 403 Forbidden
        body = self.app(environ, start_response)
        self.assertEqual(response_status, "403 Forbidden")

    def test_csrf_exempt_route_under_wsgi(self):
        response_status = None
        def start_response(status, headers):
            nonlocal response_status
            response_status = status

        payload = b'{"msg": "halo"}'
        environ = {
            "REQUEST_METHOD": "POST",
            "PATH_INFO": "/api/exempt",
            "CONTENT_TYPE": "application/json",
            "CONTENT_LENGTH": str(len(payload)),
            "wsgi.input": io.BytesIO(payload),
            "wsgi.url_scheme": "http"
        }

        body = self.app(environ, start_response)
        self.assertEqual(response_status, "200 OK")
        self.assertIn(b"exempted", b"".join(body))

    def test_method_spoofing_under_wsgi(self):
        response_status = None
        def start_response(status, headers):
            nonlocal response_status
            response_status = status

        CSRF.exempt("/resource/*")
        payload = b"_method=PUT&name=updated"
        environ = {
            "REQUEST_METHOD": "POST",
            "PATH_INFO": "/resource/99",
            "CONTENT_TYPE": "application/x-www-form-urlencoded",
            "CONTENT_LENGTH": str(len(payload)),
            "wsgi.input": io.BytesIO(payload),
            "wsgi.url_scheme": "http"
        }

        body = self.app(environ, start_response)
        self.assertEqual(response_status, "200 OK")
        self.assertIn(b'"updated": "99"', b"".join(body))


if __name__ == "__main__":
    unittest.main()
