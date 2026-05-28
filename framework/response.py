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
        
        # Retrieve view template from resources/views
        views_path = os.path.abspath("resources/views")
        engine = TemplateEngine(views_path, Response.active_vm)
        
        html_content = engine.render(name, context)
        return self.html(html_content)

    def json(self, data, status=200):
        self.content = json.dumps(data)
        self.status = status
        self.headers["Content-Type"] = "application/json"
        return self

    def redirect(self, url, status=302):
        self.content = f"Redirecting to {url}..."
        self.status = status
        self.headers["Location"] = url
        return self

    def __repr__(self):
        return f"<Response {self.status}>"
