# WSGI Application Adapter for Production Deployment (Gunicorn, uWSGI, etc.)

import os
import mimetypes
import urllib.parse
from framework.request import Request
from framework.response import Response
from framework.session import Session
from framework.csrf import CSRF, CSRFException
from framework.upload import PayloadTooLargeError
from framework.database import db_manager

# Mapping of HTTP status codes to reason phrases
STATUS_PHRASES = {
    200: "200 OK",
    201: "201 Created",
    204: "204 No Content",
    301: "301 Moved Permanently",
    302: "302 Found",
    400: "400 Bad Request",
    401: "401 Unauthorized",
    403: "403 Forbidden",
    404: "404 Not Found",
    405: "405 Method Not Allowed",
    413: "413 Payload Too Large",
    422: "422 Unprocessable Entity",
    500: "500 Internal Server Error",
}

class LarapakWSGI:
    """Standard WSGI Application Callable for Larapak Framework."""

    def __init__(self, router=None):
        self.router = router
        self._initialized = False

    def _ensure_initialized(self):
        if not self._initialized:
            # Lazy load router and controllers
            import ngapakin
            if self.router is None:
                self.router = ngapakin.get_router()
            from framework.paths import get_controllers_path, get_middleware_path
            self.loader = ngapakin.ControllerLoader(
                os.path.abspath(get_controllers_path()),
                self.router.vm
            )
            self.pipeline = ngapakin.MiddlewarePipeline(
                os.path.abspath(get_middleware_path()),
                self.router.vm
            )
            self._initialized = True

    def __call__(self, environ, start_response):
        self._ensure_initialized()
        
        # 1. Parse HTTP environment
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "/")
        query_string = environ.get("QUERY_STRING", "")
        
        query = urllib.parse.parse_qs(query_string, keep_blank_values=True)
        query = {k: v[0] if len(v) == 1 else v for k, v in query.items()}

        # 2. Extract headers
        headers = {}
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                header_name = key[5:].replace("_", "-").title()
                headers[header_name] = value
            elif key in ("CONTENT_TYPE", "CONTENT_LENGTH") and value:
                header_name = key.replace("_", "-").title()
                headers[header_name] = value

        # 3. Static file serving (e.g. for development or fallback)
        if method == "GET":
            from framework.paths import get_public_path
            public_dir = os.path.abspath(get_public_path())
            clean_path = path.lstrip("/").replace("\\", "/")
            if clean_path:
                candidate_path = os.path.abspath(os.path.join(public_dir, clean_path))
                if candidate_path.startswith(public_dir + os.sep) and os.path.isfile(candidate_path):
                    mime_type, _ = mimetypes.guess_type(candidate_path)
                    mime_type = mime_type or "application/octet-stream"
                    file_size = os.path.getsize(candidate_path)
                    
                    status = "200 OK"
                    response_headers = [
                        ("Content-Type", mime_type),
                        ("Content-Length", str(file_size)),
                        ("Cache-Control", "public, max-age=3600")
                    ]
                    start_response(status, response_headers)
                    with open(candidate_path, "rb") as f:
                        return [f.read()]

        # 4. Read body
        raw_body = b""
        content_length_str = headers.get("Content-Length") or environ.get("CONTENT_LENGTH")
        if content_length_str:
            try:
                content_length = int(content_length_str)
                wsgi_input = environ.get("wsgi.input")
                if wsgi_input and content_length > 0:
                    raw_body = wsgi_input.read(content_length)
            except (ValueError, TypeError):
                pass

        # 5. Parse payload (JSON, urlencoded, multipart)
        try:
            body, files = Request.parse_payload(headers, raw_body)
        except PayloadTooLargeError:
            status = "413 Payload Too Large"
            response_headers = [("Content-Type", "text/html; charset=utf-8")]
            start_response(status, response_headers)
            return [b"<h1>413 Payload Too Large</h1><p>Ukuran berkas melebihi batas.</p>"]

        # 6. Instantiate Request (automatically applies HTTP Method Spoofing if _method is present in POST)
        req = Request(
            method=method,
            path=path,
            headers=headers,
            query=query,
            body=body,
            files=files,
            raw_body=raw_body
        )

        # 7. Session handling
        session_id = req.cookie("larapak_session")
        session = Session(session_id)
        session.start()
        req.session = session
        if self.router and hasattr(self.router, "vm") and self.router.vm and hasattr(self.router.vm, "globals"):
            self.router.vm.globals["sesi"] = session

        # Ensure CSRF token is available
        CSRF.token(session)

        # 8. CSRF Verification
        try:
            CSRF.verify(req, session)
        except CSRFException as e:
            session.save()
            status = "403 Forbidden"
            response_headers = [("Content-Type", "text/html; charset=utf-8")]
            start_response(status, response_headers)
            return [f"<h1>403 Forbidden</h1><p>{str(e)}</p>".encode("utf-8")]

        # 8.5 Check Larapak Route & API Studio
        from framework.studio import is_studio_enabled, render_studio_html, generate_openapi_spec
        norm_path = path.rstrip("/")
        if is_studio_enabled() and (norm_path in ("/api-studio", "/api/studio") or path in ("/api-studio/openapi.json", "/api/studio/openapi.json")):
            session.save()
            if path.endswith("openapi.json"):
                import json
                spec = generate_openapi_spec(self.router)
                status = "200 OK"
                response_headers = [("Content-Type", "application/json; charset=utf-8")]
                start_response(status, response_headers)
                return [json.dumps(spec, indent=2).encode("utf-8")]
            else:
                html = render_studio_html(self.router, session)
                status = "200 OK"
                response_headers = [("Content-Type", "text/html; charset=utf-8")]
                start_response(status, response_headers)
                return [html.encode("utf-8")]

        # 9. Match Route
        route, params = self.router.match(req.method, path)
        if not route:
            session.save()
            status = "404 Not Found"
            response_headers = [("Content-Type", "text/html; charset=utf-8")]
            start_response(status, response_headers)
            return [b"<h1>404 Halaman Tidak Ditemukan</h1><p>Larapak web framework.</p>"]

        req.params = params
        res = Response()
        Response.active_vm = self.router.vm

        try:
            def destination(r_req, r_res):
                action = route["action"]
                if hasattr(action, "chunk"):
                    return self.router.vm.execute_callable(action, [r_req, r_res])
                elif callable(action):
                    return action(r_req, r_res)
                else:
                    return self.loader.call_action(action, r_req, r_res)

            final_res = self.pipeline.execute_chain(route["middleware"], req, res, destination)
            if not isinstance(final_res, Response):
                final_res = Response(content=str(final_res))

            # Set session cookie
            is_secure = environ.get("wsgi.url_scheme") == "https" or headers.get("X-Forwarded-Proto") == "https"
            final_res.cookie("larapak_session", session.session_id, path="/", secure=is_secure, httponly=True)
            session.save()

            status_line = STATUS_PHRASES.get(final_res.status, f"{final_res.status} HTTP Response")
            out_headers = list(final_res.headers.items())

            for cookie_name, cookie_data in final_res.cookies.items():
                cookie_str = f"{cookie_name}={cookie_data['value']}"
                if cookie_data.get("expires"):
                    cookie_str += f"; Expires={cookie_data['expires']}"
                if cookie_data.get("path"):
                    cookie_str += f"; Path={cookie_data['path']}"
                if cookie_data.get("domain"):
                    cookie_str += f"; Domain={cookie_data['domain']}"
                if cookie_data.get("secure"):
                    cookie_str += "; Secure"
                if cookie_data.get("httponly"):
                    cookie_str += "; HttpOnly"
                cookie_str += "; SameSite=Lax"
                out_headers.append(("Set-Cookie", cookie_str))

            start_response(status_line, out_headers)

            content = final_res.content
            if isinstance(content, str):
                return [content.encode("utf-8")]
            elif isinstance(content, bytes):
                return [content]
            return [str(content).encode("utf-8")]

        except Exception as e:
            session.save()
            status = "500 Internal Server Error"
            response_headers = [("Content-Type", "text/html; charset=utf-8")]
            start_response(status, response_headers)
            import traceback
            traceback.print_exc()
            from framework.error_handler import render_exception
            err_html = render_exception(e, req)
            return [err_html.encode("utf-8")]

        finally:
            # Request cleanup: cleanup files, reset/close thread connections
            for f in files.values():
                if hasattr(f, "cleanup"):
                    f.cleanup()


def get_wsgi_application():
    """Factory to get the production WSGI application callable."""
    return LarapakWSGI()

# Default WSGI entrypoint for Gunicorn/uWSGI: 'framework.wsgi:app'
app = get_wsgi_application()
application = app
