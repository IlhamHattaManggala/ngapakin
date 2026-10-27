# CLI entrypoint for NgapakIn / Larapak MVC Framework

import sys
import os
import pickle
from ngapak import Lexer, Parser, Compiler, VM, NgapakError, disassemble_chunk

def print_usage():
    print("Penggunaan NgapakIn / Larapak CLI:")
    print("  python ngapakin.py compile <file.ngpk>")
    print("  python ngapakin.py run <file.ngpk | file.ngpkc>")
    print("  python ngapakin.py debug <file.ngpk>")
    print("  python ngapakin.py serve [port]")
    print("  python ngapakin.py route:list")
    print("  python ngapakin.py make:controller <NamaController>")
    print("  python ngapakin.py make:middleware <NamaMiddleware>")
    print("  python ngapakin.py make:model <NamaModel>")
    print("  python ngapakin.py make:migration <NamaMigrasi>")
    print("  python ngapakin.py make:job <NamaJob>")
    print("  python ngapakin.py migrate")
    print("  python ngapakin.py rollback")
    print("  python ngapakin.py db:seed")
    print("  python ngapakin.py queue:work")
    print("  python ngapakin.py cache:clear")
    print("  python ngapakin.py new <NamaProject>")
    print("  python ngapakin.py package:install <nama-package>")
    print("  python ngapakin.py repl")
    print("  python ngapakin.py test")


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
    
    # Autoload all models in app/Models/
    models_path = "app/Models"
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
    
    # Load routing files
    for routes_file in ("routes/web.ngpk", "routes/api.ngpk"):
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

def run_server(port=None):
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse
    import mimetypes
    from framework.controller import ControllerLoader
    from framework.middleware import MiddlewarePipeline
    from framework.request import Request
    from framework.response import Response
    from framework.env import env
    
    port = int(port or env("APP_PORT", 8000))
    router = get_router()
    loader = ControllerLoader(os.path.abspath("app/Controllers"), router.vm)
    pipeline = MiddlewarePipeline(os.path.abspath("app/Middleware"), router.vm)
    
    class LarapakHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            print(f"Larapak server: {format % args}")

        def handle_http_request(self, method):
            parsed_url = urllib.parse.urlparse(self.path)
            path = parsed_url.path
            
            # Static file serving from public/ directory
            if method == "GET":
                public_dir = os.path.abspath("public")
                clean_path = path.lstrip("/").replace("\\", "/")
                if clean_path:
                    candidate_path = os.path.abspath(os.path.join(public_dir, clean_path))
                    if candidate_path.startswith(public_dir) and os.path.isfile(candidate_path):
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
            
            query = urllib.parse.parse_qs(parsed_url.query)
            query = {k: v[0] if len(v) == 1 else v for k, v in query.items()}
            
            body = {}
            if method in ("POST", "PUT"):
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    raw_body = self.rfile.read(content_length).decode('utf-8')
                    try:
                        import json
                        body = json.loads(raw_body)
                    except json.JSONDecodeError:
                        body = urllib.parse.parse_qs(raw_body)
                        body = {k: v[0] if len(v) == 1 else v for k, v in body.items()}

            route, params = router.match(method, path)
            if not route:
                self.send_response(404)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>404 Halaman Tidak Ditemukan</h1><p>Larapak web framework.</p>")
                return

            req = Request(
                method=method,
                path=path,
                headers=dict(self.headers),
                query=query,
                params=params,
                body=body
            )
            
            # Load or initialize session
            from framework.session import Session
            session_id = req.cookie("larapak_session")
            session = Session(session_id)
            session.start()
            
            req.session = session
            router.vm.globals["sesi"] = session
            
            res = Response()

            try:
                def destination(r_req, r_res):
                    action = route["action"]
                    if hasattr(action, 'chunk') or callable(action):
                        return router.vm.execute_callable(action, [r_req, r_res])
                    else:
                        return loader.call_action(action, r_req, r_res)

                final_res = pipeline.execute_chain(route["middleware"], req, res, destination)
                
                if not isinstance(final_res, Response):
                    final_res = Response(content=str(final_res))

                # Inject session cookie and save session
                final_res.cookie("larapak_session", session.session_id, path="/")
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
                    self.send_header("Set-Cookie", cookie_str)
                self.end_headers()
                
                if isinstance(final_res.content, str):
                    self.wfile.write(final_res.content.encode('utf-8'))
                else:
                    self.wfile.write(final_res.content)
            except Exception as e:
                session.save()
                self.send_response(500)
                self.send_header("Content-Type", "text/html")
                cookie_str = f"larapak_session={session.session_id}; Path=/"
                self.send_header("Set-Cookie", cookie_str)
                self.end_headers()
                err_msg = f"<h1>500 Internal Server Error</h1><p>{str(e)}</p>"
                self.wfile.write(err_msg.encode('utf-8'))
                import traceback
                traceback.print_exc()


        def do_GET(self):
            self.handle_http_request("GET")
            
        def do_POST(self):
            self.handle_http_request("POST")

        def do_PUT(self):
            self.handle_http_request("PUT")

        def do_DELETE(self):
            self.handle_http_request("DELETE")

    print(f"Larapak server aktif di http://localhost:{port} [SERVER] (Tekan Ctrl+C untuk berhenti)")
    httpd = HTTPServer(('', port), LarapakHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nLarapak server dihentikan.")
        httpd.server_close()

def create_new_project(project_name):
    target_dir = os.path.abspath(project_name)
    if os.path.exists(target_dir) and os.listdir(target_dir):
        print(f"Error: Direktori '{project_name}' sudah ada dan tidak kosong.")
        sys.exit(1)

    print(f"🚀 Nggawe proyek Larapak anyar ing folder: '{project_name}'...")

    # Struktur folder aplikasi bersih
    folders = [
        "app/Controllers",
        "app/Models",
        "app/Middleware",
        "app/Jobs",
        "database/migrations",
        "database/seeders",
        "public/css",
        "public/js",
        "public/images",
        "resources/views",
        "routes",
    ]
    for folder in folders:
        os.makedirs(os.path.join(target_dir, folder), exist_ok=True)

    # 1. routes/web.ngpk
    web_routes = """# Web routes for Larapak

rute.get("/", "HomeController@index")
"""
    with open(os.path.join(target_dir, "routes/web.ngpk"), "w", encoding="utf-8") as f:
        f.write(web_routes)

    # 2. routes/api.ngpk
    api_routes = """# API routes for Larapak

rute.get("/status", gawe(req, res)
    balekna res.json(["status": "bener", "app": "Larapak"])
rampung)
"""
    with open(os.path.join(target_dir, "routes/api.ngpk"), "w", encoding="utf-8") as f:
        f.write(api_routes)

    # 3. app/Controllers/HomeController.ngpk
    home_controller = f"""# HomeController for {project_name}

gawe index(req, res)
    fitur = ["Routing Cepet", "ActiveRecord ORM", "Blade-like Template", "Sesi & Cache SQLite"]
    balekna res.view("index", ["title": "{project_name}", "fitur": fitur])
rampung
"""
    with open(os.path.join(target_dir, "app/Controllers/HomeController.ngpk"), "w", encoding="utf-8") as f:
        f.write(home_controller)

    # 4. resources/views/layout.nview
    layout_view = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ title }} - Larapak Web</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <a href="/" class="logo">🚀 {{ title }}</a>
            <nav>
                <a href="/">Utama</a>
                <a href="/api/status">API Status</a>
            </nav>
        </header>

        <main class="card">
            @yield "content"
        </main>

        <footer>
            <p>Digawe nganggo dialek NgapakIn &copy; 2026</p>
        </footer>
    </div>
</body>
</html>
"""
    with open(os.path.join(target_dir, "resources/views/layout.nview"), "w", encoding="utf-8") as f:
        f.write(layout_view)

    # 5. resources/views/index.nview
    index_view = """@layout "layout.nview"

@section "content"
    <h1>Sugeng Rawuh ing {{ title }}! 🏠</h1>
    <p>Proyek anyar iki siap dikembangna nganggo sintaks NgapakIn lan arsitektur Larapak MVC.</p>

    <h3>Fitur Utama:</h3>
    <ul>
    @baleni f neng fitur
        <li>✨ {{ f }}</li>
    @rampung
    </ul>
@rampung
"""
    with open(os.path.join(target_dir, "resources/views/index.nview"), "w", encoding="utf-8") as f:
        f.write(index_view)

    # 6. public/css/style.css
    script_dir = os.path.dirname(os.path.abspath(__file__))
    current_css = os.path.join(script_dir, "public/css/style.css")
    if os.path.exists(current_css):
        with open(current_css, "r", encoding="utf-8") as f:
            css_content = f.read()
    else:
        css_content = """/* Larapak Default Modern Stylesheet */
:root {
  --primary: #4f46e5;
  --primary-hover: #4338ca;
  --bg-page: #f8fafc;
  --bg-surface: #ffffff;
  --text-main: #0f172a;
  --text-muted: #64748b;
  --border: #e2e8f0;
  --radius: 8px;
  --font-sans: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg-page: #0b0f19;
    --bg-surface: #111827;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --border: #1f2937;
  }
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: var(--font-sans); background-color: var(--bg-page); color: var(--text-main); line-height: 1.6; padding: 2rem 1rem; }
.container { max-width: 900px; margin: 0 auto; }
header { border-bottom: 1px solid var(--border); padding-bottom: 1.5rem; margin-bottom: 2rem; display: flex; align-items: center; justify-content: space-between; }
.logo { font-size: 1.5rem; font-weight: 700; color: var(--primary); text-decoration: none; }
.card { background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05); }
h1, h2, h3 { color: var(--text-main); margin-bottom: 0.75rem; font-weight: 600; }
p { color: var(--text-muted); margin-bottom: 1rem; }
code { background: rgba(79, 70, 229, 0.1); color: var(--primary); padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.9em; }
.btn { display: inline-block; background: var(--primary); color: #ffffff; padding: 0.6rem 1.2rem; border-radius: var(--radius); text-decoration: none; font-weight: 500; border: none; cursor: pointer; transition: background-color 0.15s ease; }
.btn:hover { background: var(--primary-hover); }
ul { list-style-type: none; padding-left: 0; }
li { padding: 0.5rem 0; border-bottom: 1px solid var(--border); }
li:last-child { border-bottom: none; }
.error { color: #ef4444; font-size: 0.875rem; margin-top: 0.25rem; display: block; }
"""
    with open(os.path.join(target_dir, "public/css/style.css"), "w", encoding="utf-8") as f:
        f.write(css_content)

    # 7. .env and .env.example
    env_content = f"""APP_NAME={project_name}
APP_ENV=local
APP_DEBUG=bener
APP_PORT=8000
APP_KEY=secret_{project_name}_key_2026

DB_CONNECTION=sqlite
DB_DATABASE=database.sqlite
DB_DEBUG=salah
"""
    with open(os.path.join(target_dir, ".env"), "w", encoding="utf-8") as f:
        f.write(env_content)
    with open(os.path.join(target_dir, ".env.example"), "w", encoding="utf-8") as f:
        f.write(env_content)

    # 8. README.md
    readme_content = f"""# {project_name}

Proyek aplikasi web Larapak sing digawe nganggo bahasa NgapakIn.

## Cara Mlaku
1. Pindah ing folder proyek:
   ```bash
   cd {project_name}
   ```
2. Jalankan server lokal:
   ```bash
   ngapakin serve 8000
   ```
3. Bukak browser ing `http://localhost:8000`.
"""
    with open(os.path.join(target_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"\nProyek '{project_name}' kasil digawe kanthi resik tanpa sampah engine!")
    print("\nLangkah sabanjure:")
    print(f"  cd {project_name}")
    print("  ngapakin serve\n")

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    if command == "new":
        if len(sys.argv) < 3:
            print("Error: Diharapkan nama proyek. Contoh: python ngapakin.py new toko-online")
            sys.exit(1)
        project_name = sys.argv[2]
        create_new_project(project_name)

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
        port = 8000
        if len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                pass
        run_server(port)

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
            
        os.makedirs("app/Controllers", exist_ok=True)
        filepath = os.path.join("app/Controllers", f"{name}.ngpk")
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
            
        os.makedirs("app/Middleware", exist_ok=True)
        filepath = os.path.join("app/Middleware", f"{name}.ngpk")
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
        os.makedirs("app/Models", exist_ok=True)
        filepath = os.path.join("app/Models", f"{name}.ngpk")
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
        os.makedirs("database/migrations", exist_ok=True)
        filepath = os.path.join("database/migrations", f"{filename}.ngpk")
        
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
        
        migrations_dir = "database/migrations"
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

    elif command == "rollback":
        from framework.database import db_manager
        batch_row = db_manager.execute("SELECT MAX(batch) as max_batch FROM migrations").fetchone()
        max_batch = batch_row["max_batch"]
        if max_batch is None or max_batch == 0:
            print("Tidak ada migrasi untuk di-rollback.")
            sys.exit(0)
            
        rows = db_manager.execute("SELECT migration FROM migrations WHERE batch = ? ORDER BY id DESC", [max_batch]).fetchall()
        
        migrations_dir = "database/migrations"
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
        seeder_file = "database/seeders/DatabaseSeeder.ngpk"
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
            
        os.makedirs("app/Jobs", exist_ok=True)
        filepath = os.path.join("app/Jobs", f"{name}.ngpk")
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
