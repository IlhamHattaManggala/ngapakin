# Middleware pipeline execution for Larapak

import os
from ngapak import Lexer, Parser, Compiler, NgapakError

class MiddlewarePipeline:
    def __init__(self, middleware_path, vm):
        self.middleware_path = middleware_path
        self.vm = vm
        self.middleware_map = {
            "auth": "AuthMiddleware"  # Map shorthand aliases
        }
        self.loaded_middleware = {}

    def execute_chain(self, middleware_names, req, res, destination):
        """Execute middleware list sequentially, ending at destination controller call."""
        idx = 0
        
        def next_step(current_req, current_res):
            nonlocal idx
            if idx < len(middleware_names):
                name = middleware_names[idx]
                idx += 1
                return self.run_middleware(name, current_req, current_res, next_step)
            else:
                return destination(current_req, current_res)
                
        return next_step(req, res)

    def run_middleware(self, name, req, res, next_cb):
        if name.startswith("throttle"):
            # Format: throttle:max_attempts,decay_minutes (e.g. throttle:60,1)
            max_attempts = 60
            decay_minutes = 1
            if ":" in name:
                parts = name.split(":", 1)[1].split(",")
                try:
                    max_attempts = int(parts[0])
                    if len(parts) > 1:
                        decay_minutes = int(parts[1])
                except (ValueError, IndexError):
                    pass

            from framework.cache import Cache
            from framework.response import Response
            import time

            cache = Cache()
            client_ip = getattr(req, "ip", "127.0.0.1")
            route_path = getattr(req, "path", "/")
            cache_key = f"throttle:{client_ip}:{route_path}"
            
            decay_seconds = max(1, decay_minutes * 60)
            now = int(time.time())

            entry = cache.get(cache_key)
            if not entry or not isinstance(entry, dict) or entry.get("reset_at", 0) <= now:
                entry = {"count": 1, "reset_at": now + decay_seconds}
                cache.set(cache_key, entry, decay_seconds)
            else:
                entry["count"] += 1
                remaining_time = max(1, entry["reset_at"] - now)
                cache.set(cache_key, entry, remaining_time)

            remaining = max(0, max_attempts - entry["count"])
            reset_in = max(1, entry["reset_at"] - now)

            if entry["count"] > max_attempts:
                headers = {
                    "Retry-After": str(reset_in),
                    "X-RateLimit-Limit": str(max_attempts),
                    "X-RateLimit-Remaining": "0"
                }
                accept_header = getattr(req, "headers", {}).get("Accept", "").lower()
                is_json = "application/json" in accept_header or getattr(req, "path", "").startswith("/api")
                if is_json:
                    import json
                    err_json = {
                        "status": "salah",
                        "code": 429,
                        "pesan": "Kakehan panyuwunan (Too Many Requests). Mangga baleni maneh sedhela maning.",
                        "retry_after_detik": reset_in
                    }
                    headers["Content-Type"] = "application/json; charset=utf-8"
                    return Response(status=429, headers=headers, content=json.dumps(err_json))
                else:
                    html_msg = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>429 Too Many Requests - Larapak</title>
    <style>
        body {{ background-color: #09090b; color: #ededec; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }}
        .card {{ background-color: #161615; border: 1px solid rgba(255, 255, 255, 0.08); padding: 2.5rem 3rem; border-radius: 14px; max-width: 480px; text-align: center; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7); }}
        h1 {{ font-size: 1.4rem; color: #f58220; margin-bottom: 0.75rem; }}
        p {{ font-size: 0.9rem; color: #a1a1aa; line-height: 1.6; margin-bottom: 1.5rem; }}
        .badge {{ display: inline-block; background: rgba(245, 130, 32, 0.12); color: #f58220; padding: 0.35rem 0.85rem; border-radius: 9999px; font-size: 0.825rem; font-weight: 600; border: 1px solid rgba(245, 130, 32, 0.25); }}
    </style>
</head>
<body>
    <div class="card">
        <h1>429 &bull; Kakehan Panyuwunan</h1>
        <p>Panyuwunan panjenengan ngluwihi wates (Too Many Requests). Mangga entosi sawetawis wekdal sadurunge nyobi malih.</p>
        <span class="badge">Baleni maneh ing {reset_in} detik</span>
    </div>
</body>
</html>"""
                    headers["Content-Type"] = "text/html; charset=utf-8"
                    return Response(status=429, headers=headers, content=html_msg)

            res_obj = next_cb(req, res)
            if isinstance(res_obj, Response):
                res_obj.headers["X-RateLimit-Limit"] = str(max_attempts)
                res_obj.headers["X-RateLimit-Remaining"] = str(remaining)
            return res_obj

        class_name = self.middleware_map.get(name, name)
        
        # Load and run middleware file once to register its functions
        if class_name not in self.loaded_middleware:
            filepath = os.path.join(self.middleware_path, f"{class_name}.ngpk")
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Middleware '{class_name}' tidak ditemukan di '{filepath}'")
                
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
                
            lexer = Lexer(source, filepath)
            tokens = lexer.tokenize()
            parser = Parser(tokens, filepath)
            ast = parser.parse()
            
            compiler = Compiler(filepath)
            main_fn = compiler.compile(ast)
            
            self.vm.execute_callable(main_fn, [])
            self.loaded_middleware[class_name] = True

        # Middlewares define a global function called 'tangani(req, res, lanjut)'
        if "tangani" not in self.vm.globals:
            return next_cb(req, res)
            
        tangani_fn = self.vm.globals["tangani"]
        
        # Run middleware tangani(req, res, next_cb) on VM.
        # next_cb is passed directly as Python callback.
        res_obj = self.vm.execute_callable(tangani_fn, [req, res, next_cb])
        return res_obj
