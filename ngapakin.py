# CLI entrypoint for NgapakIn / Larapak MVC Framework

import sys
import os
import pickle
from ngapak import Lexer, Parser, Compiler, VM, NgapakError, disassemble_chunk

# Kamus Alias Perintah Dialek Ngapak Asli
NGAPAK_COMMAND_ALIASES = {
    # 1. Proyek & Server
    "anyar": "new",
    "ladeni": "serve",
    "urubna": "serve",
    "mlaku": "serve",
    "dalan:daptar": "route:list",
    "daptar:dalan": "route:list",
    "rute:daptar": "route:list",

    # 2. Generator / Scaffolding (make:*)
    "gawe:pangatur": "make:controller",
    "gawe:controller": "make:controller",
    "gawe:wujud": "make:model",
    "gawe:model": "make:model",
    "gawe:migrasi": "make:migration",
    "gawe:pencegat": "make:middleware",
    "gawe:middleware": "make:middleware",
    "gawe:gawean": "make:job",
    "gawe:job": "make:job",
    "gawe:bibit": "make:seeder",
    "gawe:seeder": "make:seeder",

    # 3. Database & Migrasi
    "migrasi": "migrate",
    "munggah": "migrate",
    "migrasi:anyar": "migrate:fresh",
    "migrasi:resik": "migrate:fresh",
    "migrasi:status": "migrate:status",
    "mudhun": "rollback",
    "migrasi:mundur": "rollback",
    "bibiti": "db:seed",
    "lumbung:bibit": "db:seed",

    # 4. Antrean, Cache & Paket
    "gawean:tandang": "queue:work",
    "antrean:tandang": "queue:work",
    "resik:cache": "cache:clear",
    "resiki:cache": "cache:clear",
    "paket:pasang": "package:install",
    "pasang:paket": "package:install",

    # 5. Frontend & Utilitas
    "rikat:rakit": "css:build",
    "rikat:bangun": "css:build",
    "rikat:pantau": "css:watch",
    "coba": "test",
    "nyoba": "test",
}

def print_usage():
    print("""Penggunaan NgapakIn & Larapak CLI:

Perintah Dialek Ngapak (Asli):
  ngapakin anyar <NamaProyek> [--bahasa=ngapak|indonesia|english]
  ngapakin ladeni [port]                         (Urubna server lokal)
  ngapakin dalan:daptar                          (Daftar kabeh rute HTTP)
  ngapakin gawe:pangatur <NamaController>        (Gawe controller anyar)
  ngapakin gawe:wujud <NamaModel>                (Gawe model ORM anyar)
  ngapakin gawe:migrasi <NamaMigrasi>            (Gawe skema migrasi anyar)
  ngapakin gawe:pencegat <NamaMiddleware>        (Gawe middleware anyar)
  ngapakin gawe:gawean <NamaJob>                 (Gawe background queue job)
  ngapakin gawe:bibit <NamaSeeder>               (Gawe database seeder)
  ngapakin migrasi                               (Jalankna migrasi database)
  ngapakin migrasi:anyar [--seed]                (Reset & migrasi anyar)
  ngapakin migrasi:status                        (Status tabel migrasi)
  ngapakin mudhun                                (Rollback migrasi)
  ngapakin bibiti                                (Jalankna database seeder)
  ngapakin gawean:tandang                        (Jalankna queue worker)
  ngapakin resik:cache                           (Resiki cache sistem)
  ngapakin paket:pasang <nama-paket>             (Pasang paket eksternal)
  ngapakin rikat:rakit                           (Kompilasi Rikat CSS JIT)
  ngapakin rikat:pantau                          (Pantau perubahan template)
  ngapakin coba                                  (Jalankna seluruh test suite)

Perintah Standar (Laravel Artisan Style):
  ngapakin new, serve, route:list, make:controller, make:model, make:migration,
  make:middleware, make:job, make:seeder, migrate, migrate:fresh, migrate:status,
  rollback, db:seed, queue:work, cache:clear, package:install, css:build, css:watch, test
""")


def create_vm(router=None):
    """Factory to create a VM preloaded with Framework bindings and Models."""
    from framework.model import Model
    from framework.schema import schema
    from framework.response import Response
    from framework.session import Session
    from framework.validation import Validator
    from framework.cache import Cache
    from framework.event import Event
    from framework.auth import Auth
    from framework.queue import Queue
    from framework.env import env
    from framework.hashing import Hash
    
    vm = VM()
    Response.active_vm = vm
    Model.active_vm = vm
    
    vm.globals["Model"] = Model
    vm.globals["schema"] = schema
    vm.globals["sesi"] = Session()
    vm.globals["validator"] = Validator
    vm.globals["cache"] = Cache()
    vm.globals["event"] = Event(vm)
    vm.globals["auth"] = Auth(vm)
    vm.globals["queue"] = Queue(vm)
    vm.globals["env"] = env
    vm.globals["hash"] = Hash
    
    # Autoload all models in active models directory
    from framework.paths import get_models_path
    models_path = get_models_path()
    if os.path.exists(models_path):
        for filename in os.listdir(models_path):
            if filename.endswith(".ngpk"):
                filepath = os.path.join(models_path, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    source = f.read()
                lexer = Lexer(source, filepath)
                tokens = lexer.tokenize()
                parser = Parser(tokens, filepath)
                ast = parser.parse()
                compiler = Compiler(filepath)
                main_fn = compiler.compile(ast)
                vm.execute_callable(main_fn, [])
                
    if router:
        vm.globals["rute"] = router
        router.vm = vm
        
    # Auto-discover and boot service providers of installed packages
    from framework.package_manager import PackageManager
    pm = PackageManager(vm)
    pm.boot_packages()
        
    return vm


def get_router():
    """Load routes/web.ngpk and routes/api.ngpk onto VM and return populated Router."""
    from framework.router import Router
    
    router = Router()
    vm = create_vm(router)
    
    from framework.paths import get_route_files
    # Load active routing files
    for routes_file in get_route_files():
        if os.path.exists(routes_file):
            with open(routes_file, "r", encoding="utf-8") as f:
                source = f.read()
            lexer = Lexer(source, routes_file)
            tokens = lexer.tokenize()
            parser = Parser(tokens, routes_file)
            ast = parser.parse()
            
            compiler = Compiler(routes_file)
            main_fn = compiler.compile(ast)
            vm.execute_callable(main_fn, [])
            
    return router

def run_migration_file(filepath, action="munggah"):
    vm = create_vm()
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    lexer = Lexer(source, filepath)
    tokens = lexer.tokenize()
    parser = Parser(tokens, filepath)
    ast = parser.parse()
    compiler = Compiler(filepath)
    main_fn = compiler.compile(ast)
    
    # Execute migration script main scope to define functions
    vm.execute_callable(main_fn, [])
    
    # Execute munggah() or mudhun()
    if action in vm.globals:
        vm.execute_callable(vm.globals[action], [])
    else:
        raise ValueError(f"Fungsi '{action}' tidak ditemukan di berkas migrasi '{filepath}'.")

def run_server(host=None, port=None):
    from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
    import urllib.parse
    import mimetypes
    from framework.controller import ControllerLoader
    from framework.middleware import MiddlewarePipeline
    from framework.request import Request
    from framework.response import Response
    from framework.session import Session
    from framework.csrf import CSRF, CSRFException
    from framework.upload import PayloadTooLargeError
    from framework.env import env
    
    from framework.paths import get_controllers_path, get_middleware_path, get_public_path
    host = host or env("APP_HOST", "127.0.0.1")
    port = int(port or env("APP_PORT", 8000))
    router = get_router()
    loader = ControllerLoader(os.path.abspath(get_controllers_path()), router.vm)
    pipeline = MiddlewarePipeline(os.path.abspath(get_middleware_path()), router.vm)
    
    class LarapakHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            print(f"Larapak server: {format % args}")

        def handle_http_request(self, method):
            parsed_url = urllib.parse.urlparse(self.path)
            path = parsed_url.path
            
            # Static file serving from active public directory
            if method == "GET":
                public_dir = os.path.abspath(get_public_path())
                clean_path = path.lstrip("/").replace("\\", "/")
                if clean_path:
                    candidate_path = os.path.abspath(os.path.join(public_dir, clean_path))
                    if candidate_path.startswith(public_dir + os.sep) and os.path.isfile(candidate_path):
                        mime_type, _ = mimetypes.guess_type(candidate_path)
                        mime_type = mime_type or "application/octet-stream"
                        file_size = os.path.getsize(candidate_path)
                        self.send_response(200)
                        self.send_header("Content-Type", mime_type)
                        self.send_header("Content-Length", str(file_size))
                        self.send_header("Cache-Control", "public, max-age=3600")
                        self.end_headers()
                        with open(candidate_path, "rb") as f:
                            while chunk := f.read(65536):
                                self.wfile.write(chunk)
                        return
                    elif clean_path == "js/rikat.js":
                        from framework.assets import RIKAT_JS
                        js_bytes = RIKAT_JS.encode("utf-8")
                        self.send_response(200)
                        self.send_header("Content-Type", "application/javascript")
                        self.send_header("Content-Length", str(len(js_bytes)))
                        self.send_header("Cache-Control", "public, max-age=3600")
                        self.end_headers()
                        self.wfile.write(js_bytes)
                        return
            
            query = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
            query = {k: v[0] if len(v) == 1 else v for k, v in query.items()}
            
            raw_body = b""
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                raw_body = self.rfile.read(content_length)

            try:
                body, files = Request.parse_payload(dict(self.headers), raw_body)
            except PayloadTooLargeError:
                self.send_response(413)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<h1>413 Payload Too Large</h1><p>Ukuran berkas/payload melebihi batas.</p>")
                return

            req = Request(
                method=method,
                path=path,
                headers=dict(self.headers),
                query=query,
                body=body,
                files=files,
                raw_body=raw_body
            )

            # Load or initialize session
            session_id = req.cookie("larapak_session")
            session = Session(session_id)
            session.start()
            
            req.session = session
            router.vm.globals["sesi"] = session
            
            # Ensure CSRF token is available
            CSRF.token(session)

            # CSRF Verification on state-changing requests
            try:
                CSRF.verify(req, session)
            except CSRFException as e:
                session.save()
                self.send_response(403)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"<h1>403 Forbidden</h1><p>{str(e)}</p>".encode("utf-8"))
                return

            # Check Larapak Route & API Studio
            from framework.studio import is_studio_enabled, render_studio_html, generate_openapi_spec
            norm_path = path.rstrip("/")
            if is_studio_enabled() and (norm_path in ("/api-studio", "/api/studio") or path in ("/api-studio/openapi.json", "/api/studio/openapi.json")):
                session.save()
                if path.endswith("openapi.json"):
                    import json
                    spec = generate_openapi_spec(router)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps(spec, indent=2).encode("utf-8"))
                    return
                else:
                    html = render_studio_html(router, session)
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(html.encode("utf-8"))
                    return

            # Match Route with effective HTTP method
            route, params = router.match(req.method, path)
            if not route:
                session.save()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<h1>404 Halaman Tidak Ditemukan</h1><p>Larapak web framework.</p>")
                return

            req.params = params
            res = Response()
            Response.active_vm = router.vm

            try:
                def destination(r_req, r_res):
                    action = route["action"]
                    if hasattr(action, 'chunk'):
                        return router.vm.execute_callable(action, [r_req, r_res])
                    elif callable(action):
                        return action(r_req, r_res)
                    else:
                        return loader.call_action(action, r_req, r_res)

                final_res = pipeline.execute_chain(route["middleware"], req, res, destination)
                
                if not isinstance(final_res, Response):
                    final_res = Response(content=str(final_res))

                # Inject secure session cookie and save session
                final_res.cookie("larapak_session", session.session_id, path="/", httponly=True)
                session.save()

                self.send_response(final_res.status)
                for k, v in final_res.headers.items():
                    self.send_header(k, v)
                for cookie_name, cookie_data in final_res.cookies.items():
                    cookie_str = f"{cookie_name}={cookie_data['value']}"
                    if cookie_data.get('expires'):
                        cookie_str += f"; Expires={cookie_data['expires']}"
                    if cookie_data.get('path'):
                        cookie_str += f"; Path={cookie_data['path']}"
                    if cookie_data.get('domain'):
                        cookie_str += f"; Domain={cookie_data['domain']}"
                    if cookie_data.get('secure'):
                        cookie_str += "; Secure"
                    if cookie_data.get('httponly'):
                        cookie_str += "; HttpOnly"
                    cookie_str += "; SameSite=Lax"
                    self.send_header("Set-Cookie", cookie_str)
                self.end_headers()
                
                if isinstance(final_res.content, str):
                    self.wfile.write(final_res.content.encode('utf-8'))
                else:
                    self.wfile.write(final_res.content)
            except Exception as e:
                session.save()
                self.send_response(500)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                from framework.error_handler import render_exception
                err_html = render_exception(e, req)
                self.wfile.write(err_html.encode('utf-8'))
                import traceback
                traceback.print_exc()
            finally:
                for f in files.values():
                    if hasattr(f, "cleanup"):
                        f.cleanup()

        def do_GET(self):
            self.handle_http_request("GET")
            
        def do_POST(self):
            self.handle_http_request("POST")

        def do_PUT(self):
            self.handle_http_request("PUT")

        def do_PATCH(self):
            self.handle_http_request("PATCH")

        def do_DELETE(self):
            self.handle_http_request("DELETE")

    display_host = "localhost" if host in ("127.0.0.1", "0.0.0.0") else host
    print(f"Larapak development server aktif di http://{display_host}:{port} [Multi-threaded] (Tekan Ctrl+C untuk berhenti)")
    httpd = ThreadingHTTPServer((host, port), LarapakHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nLarapak server dihentikan.")
        httpd.server_close()

def create_new_project(project_name, language="english"):
    from framework.paths import normalize_language, PATHS_CONFIG
    lang = normalize_language(language)
    paths = PATHS_CONFIG[lang]

    target_dir = os.path.abspath(project_name)
    if os.path.exists(target_dir) and os.listdir(target_dir):
        print(f"Error: Direktori '{project_name}' sudah ada dan tidak kosong.")
        sys.exit(1)

    lang_titles = {
        "ngapak": "dialek Ngapak",
        "indonesia": "Bahasa Indonesia",
        "english": "English standard"
    }
    print(f"🚀 Nggawe proyek Larapak anyar ing folder: '{project_name}' [Basa: {lang_titles.get(lang, lang)}]...")

    # Struktur folder aplikasi bersih berdasarkan bahasa
    folders = [
        paths["controllers"],
        paths["models"],
        paths["middleware"],
        paths["jobs"],
        paths["migrations"],
        paths["seeders"],
        paths["public_css"],
        paths["public_js"],
        paths["public_images"],
        paths["views"],
        paths["routes"],
    ]
    for folder in folders:
        os.makedirs(os.path.join(target_dir, folder), exist_ok=True)

    # 1. Routes (web.ngpk & api.ngpk)
    web_routes = f"""# Web routes for Larapak ({lang})

rute.get("/", "HomeController@index")
"""
    with open(os.path.join(target_dir, paths["routes"], "web.ngpk"), "w", encoding="utf-8") as f:
        f.write(web_routes)

    api_routes = f"""# API routes for Larapak ({lang})

rute.get("/status", gawe(req, res)
    balekna res.json(["status": "bener", "app": "Larapak", "bahasa": "{lang}", "author": "Ilham Hatta Manggala"])
rampung)
"""
    with open(os.path.join(target_dir, paths["routes"], "api.ngpk"), "w", encoding="utf-8") as f:
        f.write(api_routes)

    # 2. HomeController.ngpk
    home_controller = f"""# HomeController for {project_name}

gawe index(req, res)
    balekna res.view("index", ["title": "{project_name}"])
rampung
"""
    with open(os.path.join(target_dir, paths["controllers"], "HomeController.ngpk"), "w", encoding="utf-8") as f:
        f.write(home_controller)

    # 3. Views
    import base64
    from framework.assets import LOGO_BASE64, LAYOUT_TEMPLATE, INDEX_TEMPLATE, STYLE_CSS, RIKAT_JS

    with open(os.path.join(target_dir, paths["views"], "layout.nview"), "w", encoding="utf-8") as f:
        f.write(LAYOUT_TEMPLATE)

    with open(os.path.join(target_dir, paths["views"], "index.nview"), "w", encoding="utf-8") as f:
        f.write(INDEX_TEMPLATE)

    # 4. Public assets (logo, favicon, CSS)
    logo_bytes = base64.b64decode(LOGO_BASE64)
    with open(os.path.join(target_dir, paths["public_images"], "logo.png"), "wb") as f:
        f.write(logo_bytes)
    with open(os.path.join(target_dir, paths["public"], "favicon.png"), "wb") as f:
        f.write(logo_bytes)
    with open(os.path.join(target_dir, paths["public"], "favicon.ico"), "wb") as f:
        f.write(logo_bytes)

    with open(os.path.join(target_dir, paths["public_css"], "style.css"), "w", encoding="utf-8") as f:
        f.write(STYLE_CSS)

    # 4b. Rikat CSS & Rikat UI (Zero-dependency Tailwind & PrimeNG alternative)
    from framework.css_engine import compile_rikat_css
    target_views = os.path.join(target_dir, paths["views"])
    target_css = os.path.join(target_dir, paths["public_css"], "rikat.css")
    target_alias_css = os.path.join(target_dir, paths["public_css"], "larapak.css")
    target_js = os.path.join(target_dir, paths["public_js"], "rikat.js")

    compiled_css = compile_rikat_css(views_dir=target_views, output_file=target_css)
    with open(target_alias_css, "w", encoding="utf-8") as f:
        f.write(compiled_css)

    with open(target_js, "w", encoding="utf-8") as f_dst:
        f_dst.write(RIKAT_JS)

    # 5. .env and .env.example
    env_content = f"""APP_NAME={project_name}
APP_ENV=local
APP_DEBUG=bener
APP_PORT=8000
APP_KEY=secret_{project_name}_key_2026
APP_LANG={lang}

DB_CONNECTION=sqlite
DB_DATABASE=database.sqlite
DB_DEBUG=salah
"""
    with open(os.path.join(target_dir, ".env"), "w", encoding="utf-8") as f:
        f.write(env_content)
    with open(os.path.join(target_dir, ".env.example"), "w", encoding="utf-8") as f:
        f.write(env_content)

    # 6. docker-compose.yml
    docker_compose_content = f"""services:
  app:
    image: ilhamhatta/larapak:latest
    container_name: {project_name}-app
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - APP_ENV=local
      - APP_DEBUG=bener
      - APP_PORT=8000
      - DB_CONNECTION=sqlite
      - DB_DATABASE=database.sqlite
"""
    with open(os.path.join(target_dir, "docker-compose.yml"), "w", encoding="utf-8") as f:
        f.write(docker_compose_content)

    # 7. README.md
    if lang == "ngapak":
        readme_desc = "Proyek aplikasi web Larapak sing digawe nganggo struktur dialek Ngapak."
        step_text = "Langkah sabanjure:"
    elif lang == "indonesia":
        readme_desc = "Proyek aplikasi web Larapak dengan struktur direktori Bahasa Indonesia."
        step_text = "Langkah selanjutnya:"
    else:
        readme_desc = "Larapak web application project built with NgapakIn language."
        step_text = "Next steps:"

    readme_content = f"""# {project_name}

{readme_desc}

## Cara Menjalankan

### Opsi 1: Menggunakan CLI Lokal
1. Masuk ke direktori proyek:
   ```bash
   cd {project_name}
   ```
2. Jalankan server lokal:
   ```bash
   ngapakin serve 8000
   ```
3. Buka peramban di `http://localhost:8000`.

### Opsi 2: Menggunakan Docker (Tanpa Install Python)
1. Jalankan container:
   ```bash
   docker compose up -d
   ```
2. Buka peramban di `http://localhost:8000`.
"""
    with open(os.path.join(target_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"\nProyek '{project_name}' kasil digawe kanthi resik tanpa sampah engine! [Basa: {lang}]")
    print(f"\n{step_text}")
    print(f"  cd {project_name}")
    print("  ngapakin serve\n")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h", "help", "tulung", "pitulung"):
        print_usage()
        sys.exit(0 if len(sys.argv) >= 2 and sys.argv[1] in ("--help", "-h", "help", "tulung", "pitulung") else 1)

    raw_command = sys.argv[1]
    command = NGAPAK_COMMAND_ALIASES.get(raw_command, raw_command)

    if command == "new":
        if len(sys.argv) < 3:
            print("Error: Diharapkan nama proyek. Contoh: python ngapakin.py new toko-online [--bahasa=ngapak|indonesia|english]")
            sys.exit(1)

        args = sys.argv[2:]
        project_name = None
        language = "english"
        i = 0
        while i < len(args):
            arg = args[i]
            if arg.startswith("--bahasa="):
                language = arg.split("=", 1)[1]
            elif arg.startswith("--lang="):
                language = arg.split("=", 1)[1]
            elif arg.startswith("--language="):
                language = arg.split("=", 1)[1]
            elif arg.startswith("-b="):
                language = arg.split("=", 1)[1]
            elif arg in ("-b", "--bahasa", "--lang", "--language"):
                if i + 1 < len(args):
                    language = args[i + 1]
                    i += 1
            elif not arg.startswith("-") and project_name is None:
                project_name = arg
            i += 1

        if not project_name:
            print("Error: Diharapkan nama proyek. Contoh: python ngapakin.py new toko-online [--bahasa=ngapak|indonesia|english]")
            sys.exit(1)

        create_new_project(project_name, language)

    elif command == "compile":
        if len(sys.argv) < 3:
            print("Error: Diharapkan path berkas .ngpk")
            sys.exit(1)
        filepath = sys.argv[2]
        if not filepath.endswith(".ngpk"):
            print("Error: Berkas harus berakhiran '.ngpk'")
            sys.exit(1)
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        lexer = Lexer(source, filepath)
        tokens = lexer.tokenize()
        parser = Parser(tokens, filepath)
        ast = parser.parse()
        compiler = Compiler(filepath)
        main_fn = compiler.compile(ast)
        
        out_filepath = filepath + "c"
        with open(out_filepath, "wb") as f:
            pickle.dump(main_fn, f)
        print(f"Berhasil mengompilasi '{filepath}' ke '{out_filepath}'")

    elif command == "run":
        if len(sys.argv) < 3:
            print("Error: Diharapkan path berkas .ngpk atau .ngpkc")
            sys.exit(1)
        filepath = sys.argv[2]
        if filepath.endswith(".ngpkc"):
            with open(filepath, "rb") as f:
                main_fn = pickle.load(f)
            vm = create_vm()
            vm.run(main_fn, debug_mode=False, filename=filepath)
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            lexer = Lexer(source, filepath)
            tokens = lexer.tokenize()
            parser = Parser(tokens, filepath)
            ast = parser.parse()
            compiler = Compiler(filepath)
            main_fn = compiler.compile(ast)
            vm = create_vm()
            vm.run(main_fn, debug_mode=False, filename=filepath)

    elif command == "debug":
        if len(sys.argv) < 3:
            print("Error: Diharapkan path berkas .ngpk")
            sys.exit(1)
        filepath = sys.argv[2]
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        lexer = Lexer(source, filepath)
        tokens = lexer.tokenize()
        parser = Parser(tokens, filepath)
        ast = parser.parse()
        compiler = Compiler(filepath)
        main_fn = compiler.compile(ast)
        
        disassemble_chunk(main_fn.chunk, main_fn.name)
        for const in main_fn.chunk.constants:
            if hasattr(const, 'chunk'):
                disassemble_chunk(const.chunk, const.name)
                
        print("=== Memulai Penelusuran VM (Trace) ===")
        vm = create_vm()
        vm.run(main_fn, debug_mode=True, filename=filepath)
        print("=== Selesai Penelusuran VM ===")

    elif command == "serve":
        host = None
        port = None
        if len(sys.argv) == 3:
            arg = sys.argv[2]
            if arg.isdigit():
                port = int(arg)
            else:
                host = arg
        elif len(sys.argv) >= 4:
            host = sys.argv[2]
            try:
                port = int(sys.argv[3])
            except ValueError:
                pass
        run_server(host=host, port=port)

    elif command == "route:list":
        router = get_router()
        print(f"{'Method':<8} | {'Path':<30} | {'Action':<30} | {'Middleware':<20}")
        print("-" * 96)
        for r in router.routes:
            action_name = r["action"].name if hasattr(r["action"], 'name') else str(r["action"])
            mw_str = ", ".join(r["middleware"]) if r["middleware"] else "None"
            print(f"{r['method']:<8} | {r['path']:<30} | {action_name:<30} | {mw_str:<20}")

    elif command == "make:controller":
        if len(sys.argv) < 3:
            print("Error: Diharapkan nama controller")
            sys.exit(1)
        name = sys.argv[2]
        if not name.endswith("Controller"):
            name += "Controller"
            
        from framework.paths import get_controllers_path
        controllers_dir = get_controllers_path()
        os.makedirs(controllers_dir, exist_ok=True)
        filepath = os.path.join(controllers_dir, f"{name}.ngpk")
        if os.path.exists(filepath):
            print(f"Error: Controller '{name}' sudah ada di '{filepath}'")
            sys.exit(1)
            
        content = f"""# Controller {name} untuk Larapak

gawe index(req, res)
    balekna res.html("<h1>Aksi index untuk {name}</h1>")
rampung
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Berhasil membuat controller di '{filepath}'")

    elif command == "make:middleware":
        if len(sys.argv) < 3:
            print("Error: Diharapkan nama middleware")
            sys.exit(1)
        name = sys.argv[2]
        if not name.endswith("Middleware"):
            name += "Middleware"
            
        from framework.paths import get_middleware_path
        middleware_dir = get_middleware_path()
        os.makedirs(middleware_dir, exist_ok=True)
        filepath = os.path.join(middleware_dir, f"{name}.ngpk")
        if os.path.exists(filepath):
            print(f"Error: Middleware '{name}' sudah ada di '{filepath}'")
            sys.exit(1)
            
        content = f"""# Middleware {name} untuk Larapak

gawe tangani(req, res, lanjut)
    # Lakukan pengecekan di sini
    balekna lanjut(req, res)
rampung
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Berhasil membuat middleware di '{filepath}'")

    elif command == "make:model":
        if len(sys.argv) < 3:
            print("Error: Diharapkan nama model")
            sys.exit(1)
        name = sys.argv[2]
        from framework.paths import get_models_path
        models_dir = get_models_path()
        os.makedirs(models_dir, exist_ok=True)
        filepath = os.path.join(models_dir, f"{name}.ngpk")
        if os.path.exists(filepath):
            print(f"Error: Model '{name}' sudah ada di '{filepath}'")
            sys.exit(1)
        table_name = f"{name.lower()}s"
        content = f"""# Model {name} untuk Larapak

kelas {name} extends Model
    tabel = "{table_name}"
    fillable = ["name", "email"]
rampung
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Berhasil membuat model di '{filepath}'")

    elif command == "make:migration":
        if len(sys.argv) < 3:
            print("Error: Diharapkan nama migrasi")
            sys.exit(1)
        name = sys.argv[2]
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
        filename = f"{timestamp}_{name}"
        from framework.paths import get_migrations_path
        migrations_dir = get_migrations_path()
        os.makedirs(migrations_dir, exist_ok=True)
        filepath = os.path.join(migrations_dir, f"{filename}.ngpk")
        
        table_name = "tabel_baru"
        if "create_" in name and "_table" in name:
            table_name = name.replace("create_", "").replace("_table", "")
            
        content = f"""# Migrasi: {name}

gawe munggah()
    schema.gawe("{table_name}", gawe(tabel)
        tabel.id()
        tabel.string("name")
        tabel.timestamps()
    rampung)
rampung

gawe mudhun()
    schema.buang("{table_name}")
rampung
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Berhasil membuat berkas migrasi di '{filepath}'")

    elif command == "migrate":
        from framework.database import db_manager
        db_manager.execute_write("CREATE TABLE IF NOT EXISTS migrations (id INTEGER PRIMARY KEY AUTOINCREMENT, migration VARCHAR(255), batch INTEGER)")
        
        rows = db_manager.execute("SELECT migration FROM migrations").fetchall()
        executed = {row["migration"] for row in rows}
        
        batch_row = db_manager.execute("SELECT MAX(batch) as max_batch FROM migrations").fetchone()
        current_batch = (batch_row["max_batch"] or 0) + 1
        
        from framework.paths import get_migrations_path
        migrations_dir = get_migrations_path()
        if not os.path.exists(migrations_dir):
            print("Tidak ada berkas migrasi untuk dijalankan.")
            sys.exit(0)
            
        migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith(".ngpk")])
        
        run_count = 0
        for f in migration_files:
            migration_name = f[:-5]
            if migration_name not in executed:
                print(f"Menjalankan migrasi: {migration_name}...")
                filepath = os.path.join(migrations_dir, f)
                run_migration_file(filepath, "munggah")
                db_manager.execute_write("INSERT INTO migrations (migration, batch) VALUES (?, ?)", [migration_name, current_batch])
                print(f"Migrasi sukses: {migration_name}")
                run_count += 1
                
        if run_count == 0:
            print("Tidak ada migrasi baru untuk dijalankan.")

    elif command == "migrate:fresh":
        from framework.database import db_manager
        print("Menghapus seluruh tabel di database...")
        dropped = db_manager.drop_all_tables()
        if dropped:
            print(f"Berhasil membersihkan tabel: {', '.join(dropped)}")
        else:
            print("Database sudah bersih dari tabel.")

        db_manager.execute_write("CREATE TABLE IF NOT EXISTS migrations (id INTEGER PRIMARY KEY AUTOINCREMENT, migration VARCHAR(255), batch INTEGER)")

        from framework.paths import get_migrations_path
        migrations_dir = get_migrations_path()
        if os.path.exists(migrations_dir):
            migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith(".ngpk")])
            for f in migration_files:
                migration_name = f[:-5]
                print(f"Menjalankan migrasi: {migration_name}...")
                filepath = os.path.join(migrations_dir, f)
                run_migration_file(filepath, "munggah")
                db_manager.execute_write("INSERT INTO migrations (migration, batch) VALUES (?, ?)", [migration_name, 1])
                print(f"Migrasi sukses: {migration_name}")

        print("Migrasi fresh selesai dengan sukses!")

        if "--seed" in sys.argv:
            from framework.paths import get_seeder_file
            seeder_file = get_seeder_file()
            if os.path.exists(seeder_file):
                print("\nMenjalankan seeder database...")
                vm = create_vm()
                with open(seeder_file, "r", encoding="utf-8") as f:
                    source = f.read()
                lexer = Lexer(source, seeder_file)
                tokens = lexer.tokenize()
                parser = Parser(tokens, seeder_file)
                ast = parser.parse()
                compiler = Compiler(seeder_file)
                main_fn = compiler.compile(ast)
                vm.execute_callable(main_fn, [])
                print("Database berhasil di-seed!")

    elif command == "migrate:status":
        from framework.database import db_manager
        db_manager.execute_write("CREATE TABLE IF NOT EXISTS migrations (id INTEGER PRIMARY KEY AUTOINCREMENT, migration VARCHAR(255), batch INTEGER)")
        rows = db_manager.execute("SELECT migration, batch FROM migrations").fetchall()
        executed_map = {row["migration"]: row["batch"] for row in rows}

        from framework.paths import get_migrations_path
        migrations_dir = get_migrations_path()
        migration_files = []
        if os.path.exists(migrations_dir):
            migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith(".ngpk")])

        print(f"\n+--------+------------------------------------------------------+---------+")
        print(f"| Ran?   | Migration File                                       | Batch   |")
        print(f"+--------+------------------------------------------------------+---------+")
        if not migration_files:
            print(f"| (kosong) Tidak ada berkas migrasi ditemukan.                            |")
        else:
            for f in migration_files:
                name = f[:-5]
                if name in executed_map:
                    ran_badge = "Yes"
                    batch_str = f"Batch {executed_map[name]}"
                else:
                    ran_badge = "No"
                    batch_str = "Pending"
                print(f"| {ran_badge:<6} | {name:<52} | {batch_str:<7} |")
        print(f"+--------+------------------------------------------------------+---------+\n")

    elif command == "rollback":
        from framework.database import db_manager
        batch_row = db_manager.execute("SELECT MAX(batch) as max_batch FROM migrations").fetchone()
        max_batch = batch_row["max_batch"]
        if max_batch is None or max_batch == 0:
            print("Tidak ada migrasi untuk di-rollback.")
            sys.exit(0)
            
        rows = db_manager.execute("SELECT migration FROM migrations WHERE batch = ? ORDER BY id DESC", [max_batch]).fetchall()
        
        from framework.paths import get_migrations_path
        migrations_dir = get_migrations_path()
        for row in rows:
            migration_name = row["migration"]
            print(f"Mematikan (rollback) migrasi: {migration_name}...")
            filepath = os.path.join(migrations_dir, f"{migration_name}.ngpk")
            if os.path.exists(filepath):
                run_migration_file(filepath, "mudhun")
            else:
                print(f"Peringatan: Berkas migrasi '{migration_name}.ngpk' tidak ditemukan. Menghapus dari DB...")
                
            db_manager.execute_write("DELETE FROM migrations WHERE migration = ?", [migration_name])
            print(f"Rollback sukses: {migration_name}")

    elif command == "db:seed":
        from framework.paths import get_seeder_file
        seeder_file = get_seeder_file()
        if not os.path.exists(seeder_file):
            print(f"Error: Berkas seeder '{seeder_file}' tidak ditemukan.")
            sys.exit(1)
            
        print("Menjalankan seeder database...")
        vm = create_vm()
        with open(seeder_file, "r", encoding="utf-8") as f:
            source = f.read()
        lexer = Lexer(source, seeder_file)
        tokens = lexer.tokenize()
        parser = Parser(tokens, seeder_file)
        ast = parser.parse()
        compiler = Compiler(seeder_file)
        main_fn = compiler.compile(ast)
        vm.execute_callable(main_fn, [])
        print("Database berhasil di-seed!")

    elif command == "make:job":
        if len(sys.argv) < 3:
            print("Error: Diharapkan nama job")
            sys.exit(1)
        name = sys.argv[2]
        if not name.endswith("Job"):
            name += "Job"
            
        from framework.paths import get_jobs_path
        jobs_dir = get_jobs_path()
        os.makedirs(jobs_dir, exist_ok=True)
        filepath = os.path.join(jobs_dir, f"{name}.ngpk")
        if os.path.exists(filepath):
            print(f"Error: Job '{name}' sudah ada di '{filepath}'")
            sys.exit(1)
            
        content = f"""# Pekerjaan (Job) {name} untuk Larapak
# Jalankan pekerjaan ini di queue

kelas {name}
    gawe tangani(isi, data)
        # Logika pekerjaan di sini
        tulis("Memproses data job: " + data.get("pesan"))
    rampung
rampung
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Berhasil membuat berkas job di '{filepath}'")

    elif command == "make:seeder":
        if len(sys.argv) < 3:
            print("Error: Diharapkan nama seeder. Contoh: ngapakin gawe:bibit ProdukSeeder")
            sys.exit(1)
        name = sys.argv[2]
        if not name.endswith("Seeder"):
            name += "Seeder"

        from framework.paths import get_seeders_path
        seeders_dir = get_seeders_path()
        os.makedirs(seeders_dir, exist_ok=True)
        filepath = os.path.join(seeders_dir, f"{name}.ngpk")
        if os.path.exists(filepath):
            print(f"Error: Seeder '{name}' sudah ada di '{filepath}'")
            sys.exit(1)

        content = f"""# Database Seeder {name} untuk Larapak
# Berkas pengisian data awal database

gawe tandang()
    # Logika seeder: db.tabel("pengguna").lebokna(...)
    tulis("Menjalankan seeder {name}...")
rampung
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Berhasil membuat berkas seeder di '{filepath}'")

    elif command == "queue:work":
        print("Larapak queue worker aktif (Tekan Ctrl+C untuk berhenti)...")
        vm = create_vm()
        from framework.queue import Queue
        q = Queue(vm)
        import time
        try:
            while True:
                processed = q.siji()
                if not processed:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\nQueue worker dihentikan.")

    elif command == "cache:clear":
        print("Membersihkan cache...")
        from framework.cache import Cache
        c = Cache()
        c.clear()
        print("Cache berhasil dibersihkan!")

    elif command == "package:install":
        if len(sys.argv) < 3:
            print("Error: Diharapkan nama package")
            sys.exit(1)
        name = sys.argv[2]
        from framework.package_manager import PackageManager
        pm = PackageManager()
        pm.install_package(name)

    elif command in ("css:build", "rikat:build"):
        from framework.css_engine import compile_rikat_css
        from framework.paths import get_views_path, get_public_path
        print("Membangun aset Rikat CSS (Tailwind & PrimeNG alternative)...")
        views_dir = os.path.abspath(get_views_path())
        public_dir = os.path.abspath(get_public_path())
        out_css = os.path.join(public_dir, "css", "rikat.css")
        out_alias = os.path.join(public_dir, "css", "larapak.css")
        os.makedirs(os.path.join(public_dir, "css"), exist_ok=True)
        content = compile_rikat_css(views_dir=views_dir, output_file=out_css)
        with open(out_alias, "w", encoding="utf-8") as f:
            f.write(content)
        size_kb = len(content.encode("utf-8")) / 1024
        print(f"Sukses! Rikat CSS terkompilasi ke '{out_css}' ({size_kb:.1f} KB)")
        print(f"Alias kompatibilitas dibuat di '{out_alias}'")

    elif command in ("css:watch", "rikat:watch"):
        from framework.css_engine import compile_rikat_css
        from framework.paths import get_views_path, get_public_path
        import time
        views_dir = os.path.abspath(get_views_path())
        public_dir = os.path.abspath(get_public_path())
        out_css = os.path.join(public_dir, "css", "rikat.css")
        out_alias = os.path.join(public_dir, "css", "larapak.css")
        os.makedirs(os.path.join(public_dir, "css"), exist_ok=True)
        print("Rikat CSS Watcher aktif (Tekan Ctrl+C untuk berhenti)...")
        print(f"Memantau perubahan di: {views_dir}")
        last_mtime = 0
        def get_max_mtime(d):
            m = 0
            if os.path.exists(d):
                for root, _, files in os.walk(d):
                    for f in files:
                        p = os.path.join(root, f)
                        try:
                            m = max(m, os.path.getmtime(p))
                        except Exception:
                            pass
            return m
        try:
            while True:
                current_mtime = get_max_mtime(views_dir)
                if current_mtime > last_mtime:
                    last_mtime = current_mtime
                    content = compile_rikat_css(views_dir=views_dir, output_file=out_css)
                    with open(out_alias, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"[{time.strftime('%H:%M:%S')}] Rikat CSS terkompilasi ({len(content.encode('utf-8')) / 1024:.1f} KB)")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nRikat CSS Watcher dihentikan.")

    elif command == "repl":
        print("=== NgapakIn REPL Terminal (Larapak MVC Framework) ===")
        print("Ketik 'metu' atau 'exit' untuk keluar.")
        print("Gunakan 'rampung' untuk menutup blok logika/fungsi.")
        
        from ngapak.token import T_GAWE, T_KELAS, T_NEK, T_BALENI, T_RAMPUNG
        vm = create_vm()
        
        buffer = []
        
        while True:
            try:
                prompt = "... " if buffer else "ngapak> "
                line = input(prompt)
                
                # Check for exit command
                if not buffer and line.strip() in ("metu", "exit", "exit()", "quit()"):
                    break
                    
                if line.strip() == "":
                    if buffer:
                        buffer.append(line)
                    continue
                
                buffer.append(line)
                source_code = "\n".join(buffer)
                
                try:
                    lexer = Lexer(source_code, "<repl>")
                    tokens = lexer.tokenize()
                    
                    block_starters = (T_GAWE, T_KELAS, T_NEK, T_BALENI)
                    block_count = 0
                    for tok in tokens:
                        if tok.type in block_starters:
                            block_count += 1
                        elif tok.type == T_RAMPUNG:
                            block_count -= 1
                    
                    if block_count > 0:
                        continue
                    
                    parser = Parser(tokens, "<repl>")
                    ast = parser.parse()
                    
                    compiler = Compiler("<repl>")
                    main_fn = compiler.compile(ast)
                    
                    # Execute
                    vm.execute_callable(main_fn, [])
                    buffer = [] # clear buffer
                except Exception as e:
                    # check if we should continue reading
                    block_starters = (T_GAWE, T_KELAS, T_NEK, T_BALENI)
                    block_count = 0
                    try:
                        lexer = Lexer(source_code, "<repl>")
                        tokens = lexer.tokenize()
                        for tok in tokens:
                            if tok.type in block_starters:
                                block_count += 1
                            elif tok.type == T_RAMPUNG:
                                block_count -= 1
                    except Exception:
                        pass
                        
                    if block_count > 0:
                        continue
                        
                    print(f"Error: {str(e)}")
                    buffer = []
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt (Ketik 'metu' untuk keluar)")
                buffer = []
            except EOFError:
                break

    elif command == "test":
        import unittest
        print("\n🚀 Menjalankan seluruh test suite NgapakIn & Larapak...\n")
        suite = unittest.defaultTestLoader.discover("tests")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        if not result.wasSuccessful():
            sys.exit(1)

    else:
        print(f"Perintah tidak dikenal: '{command}'")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
