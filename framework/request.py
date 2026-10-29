# Request representation class for Larapak Web Framework
# Supports Method Spoofing, Cookies, JSON, Form-data, and Multipart File Uploads

import json
import urllib.parse
import email
import email.policy
from framework.upload import UploadedFile, PayloadTooLargeError

ALLOWED_SPOOFED_METHODS = {"PUT", "PATCH", "DELETE"}

class Request:
    def __init__(self, method="GET", path="/", headers=None, query=None, params=None, body=None, files=None, raw_body=b""):
        self.original_method = (method or "GET").upper()
        self.method = self.original_method
        self.path = path or "/"
        self.headers = headers or {}
        self.query = query or {}
        self.params = params or {}
        self.body = body or {}
        self.files = files or {}
        self.raw_body = raw_body
        self.session = None

        # 1. Parse cookies from headers
        self.cookies = {}
        cookie_header = self.headers.get("Cookie") or self.headers.get("cookie")
        if cookie_header:
            parts = cookie_header.split(";")
            for part in parts:
                if "=" in part:
                    k, v = part.strip().split("=", 1)
                    self.cookies[k] = v

        # 2. HTTP Method Spoofing (Only allowed from POST)
        if self.original_method == "POST":
            spoofed = None
            if isinstance(self.body, dict) and "_method" in self.body:
                spoofed = self.body["_method"]
            elif "X-HTTP-Method-Override" in self.headers:
                spoofed = self.headers["X-HTTP-Method-Override"]
            elif "x-http-method-override" in self.headers:
                spoofed = self.headers["x-http-method-override"]

            if spoofed:
                normalized_spoofed = str(spoofed).strip().upper()
                if normalized_spoofed in ALLOWED_SPOOFED_METHODS:
                    self.method = normalized_spoofed

    @classmethod
    def parse_payload(cls, headers: dict, raw_body: bytes, max_size: int = 10 * 1024 * 1024):
        """
        Parse raw request body into (body_dict, files_dict) based on Content-Type.
        Supports application/json, application/x-www-form-urlencoded, and multipart/form-data.
        Enforces max_size limit.
        """
        if not raw_body:
            return {}, {}

        if max_size is not None and len(raw_body) > max_size:
            raise PayloadTooLargeError(
                f"Ukuran payload ({len(raw_body)} bytes) melebihi batas maksimum ({max_size} bytes)."
            )

        content_type_header = headers.get("Content-Type") or headers.get("content-type") or ""
        ct_lower = content_type_header.lower()

        body = {}
        files = {}

        if "application/json" in ct_lower:
            try:
                decoded_str = raw_body.decode("utf-8")
                body = json.loads(decoded_str)
                if not isinstance(body, dict):
                    body = {"_data": body}
            except Exception:
                body = {}
            return body, files

        if "multipart/form-data" in ct_lower:
            try:
                # Use standard email parser with default policy for MIME multipart
                header_line = f"Content-Type: {content_type_header}\r\n\r\n".encode("ascii", errors="replace")
                msg = email.message_from_bytes(header_line + raw_body, policy=email.policy.default)
                
                for part in msg.iter_parts():
                    name = part.get_param("name", header="content-disposition")
                    if not name:
                        continue
                    
                    filename = part.get_filename()
                    payload_bytes = part.get_payload(decode=True) or b""

                    if filename is not None:
                        # Uploaded file part
                        if filename.strip(): # ignore empty file selection
                            content_type = part.get_content_type()
                            files[name] = UploadedFile(
                                client_filename=filename,
                                content=payload_bytes,
                                content_type=content_type
                            )
                    else:
                        # Regular form field
                        try:
                            body[name] = payload_bytes.decode("utf-8")
                        except UnicodeDecodeError:
                            body[name] = payload_bytes.decode("latin1", errors="replace")
            except Exception as e:
                # Fallback on malformed multipart
                pass
            return body, files

        # Default: application/x-www-form-urlencoded
        try:
            raw_text = raw_body.decode("utf-8")
            parsed = urllib.parse.parse_qs(raw_text, keep_blank_values=True)
            body = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
        except Exception:
            body = {}

        return body, files

    def cookie(self, name, default=None):
        return self.cookies.get(name, default)

    def file(self, name):
        """Retrieve uploaded file by field name."""
        return self.files.get(name)

    def has_file(self, name):
        return name in self.files

    def get(self, key, default=None):
        """Retrieve input from route params, query string, or parsed body."""
        if key in self.params:
            return self.params[key]
        if key in self.query:
            return self.query[key]
        if key in self.body:
            return self.body[key]
        return default

    def input(self, key, default=None):
        return self.get(key, default)

    def all(self):
        """Merge all query parameters and body inputs."""
        merged = {}
        merged.update(self.query)
        merged.update(self.body)
        return merged

    def __repr__(self):
        return f"<Request {self.method} {self.path} (Original: {self.original_method})>"
