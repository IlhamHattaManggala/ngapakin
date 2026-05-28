# Router implementation for Larapak Web Framework

import re

class Router:
    def __init__(self):
        self.routes = []  # List of route dictionaries: {"method", "path", "action", "middleware"}
        self.current_group_prefix = ""
        self.current_group_middleware = []
        self.vm = None    # Will be injected by the VM before running

    def get(self, path, action):
        self.add_route("GET", path, action)

    def post(self, path, action):
        self.add_route("POST", path, action)

    def put(self, path, action):
        self.add_route("PUT", path, action)

    def delete(self, path, action):
        self.add_route("DELETE", path, action)

    def add_route(self, method, path, action):
        full_path = self.current_group_prefix + path
        # Normalize duplicate slashes
        full_path = "/" + "/".join([p for p in full_path.split("/") if p])
        
        self.routes.append({
            "method": method.upper(),
            "path": full_path,
            "action": action,
            "middleware": list(self.current_group_middleware)
        })

    def group(self, options, group_func):
        """Register routes inside a group with common prefix and middleware."""
        # Save previous state
        prev_prefix = self.current_group_prefix
        prev_middleware = list(self.current_group_middleware)

        # Apply options
        prefix = options.get("prefix", "")
        self.current_group_prefix = prev_prefix + prefix
        
        middleware = options.get("middleware", [])
        if isinstance(middleware, str):
            middleware = [middleware]
        self.current_group_middleware.extend(middleware)

        # Invoke VM function using execute_callable, or Python function directly
        if self.vm and hasattr(group_func, 'chunk'):
            self.vm.execute_callable(group_func, [])
        elif callable(group_func):
            group_func()

        # Restore previous state
        self.current_group_prefix = prev_prefix
        self.current_group_middleware = prev_middleware

    def match(self, method, path):
        """Match request path against registered routes. Returns (route, params)."""
        for route in self.routes:
            if route["method"] != method.upper():
                continue
                
            # Translate {id} to (?P<id>[^/]+) regex capture group
            pattern = re.sub(r'\{([a-zA-Z0-9_]+)\}', r'(?P<\1>[^/]+)', route["path"])
            regex = f"^{pattern}$"
            
            match = re.match(regex, path)
            if match:
                return route, match.groupdict()
        return None, {}
