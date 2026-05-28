# Request representation class for Larapak Web Framework

class Request:
    def __init__(self, method="GET", path="/", headers=None, query=None, params=None, body=None):
        self.method = method.upper()
        self.path = path
        self.headers = headers or {}
        self.query = query or {}
        self.params = params or {}
        self.body = body or {}
        
        # Parse cookies from headers
        self.cookies = {}
        cookie_header = self.headers.get("Cookie") or self.headers.get("cookie")
        if cookie_header:
            parts = cookie_header.split(";")
            for part in parts:
                if "=" in part:
                    k, v = part.strip().split("=", 1)
                    self.cookies[k] = v

    def cookie(self, name, default=None):
        return self.cookies.get(name, default)


    def get(self, key, default=None):
        """Retrieve inputs from parameters, query params, or body (POST)."""
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
        return f"<Request {self.method} {self.path}>"
