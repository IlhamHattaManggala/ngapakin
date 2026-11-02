# Response representation class for Larapak Web Framework

import os
import json

class Response:
    active_vm = None

    def __init__(self, content="", status=200, headers=None):
        self.content = content
        self.status = status
        self.headers = headers or {}
        self.cookies = {}
        if "Content-Type" not in self.headers:
            self.headers["Content-Type"] = "text/html; charset=utf-8"

    def cookie(self, name, value, expires=None, path='/', domain=None, secure=False, httponly=False):
        self.cookies[name] = {
            "value": value,
            "expires": expires,
            "path": path,
            "domain": domain,
            "secure": secure,
            "httponly": httponly
        }
        return self


    def html(self, html_content, status=200):
        self.content = html_content
        self.status = status
        self.headers["Content-Type"] = "text/html; charset=utf-8"
        return self

    def view(self, name, context=None):
        """Render a view template using Larapak TemplateEngine."""
        context = context or {}
        from framework.template_engine import TemplateEngine
        
        # Retrieve view template from active views directory
        from framework.paths import get_views_path
        views_path = os.path.abspath(get_views_path())
        engine = TemplateEngine(views_path, Response.active_vm)
        
        html_content = engine.render(name, context)
        self.headers["X-Larapak-View"] = str(name)
        if isinstance(context, dict):
            self.headers["X-Larapak-Context-Keys"] = ",".join(str(k) for k in context.keys())
        return self.html(html_content)

    def json(self, data, status=200):
        self.content = json.dumps(data)
        self.status = status
        self.headers["Content-Type"] = "application/json"
        self.headers["X-Larapak-Type"] = "json"
        return self

    def xml(self, xml_content, status=200):
        """Return an XML response with standard application/xml Content-Type."""
        self.content = xml_content
        self.status = status
        self.headers["Content-Type"] = "application/xml; charset=utf-8"
        self.headers["X-Larapak-Type"] = "xml"
        return self

    def text(self, text_content, status=200):
        """Return a plain text response with standard text/plain Content-Type."""
        self.content = text_content
        self.status = status
        self.headers["Content-Type"] = "text/plain; charset=utf-8"
        self.headers["X-Larapak-Type"] = "text"
        return self

    def redirect(self, url, status=302):
        self.content = f"Redirecting to {url}..."
        self.status = status
        self.headers["Location"] = url
        return self

    def __repr__(self):
        return f"<Response {self.status}>"
