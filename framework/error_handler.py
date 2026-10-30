# High-End Interactive Developer Error Page & Production 500 Handler for Larapak
# Designed according to /frontend-design and /high-end-visual-design specifications (Anti AI-Slop)

import os
import sys
import html
import linecache
import traceback
import platform
from framework.env import env

def get_code_snippet(filepath: str, error_line: int, window: int = 5):
    """Extract code context around the error line with line numbers."""
    if not filepath or not os.path.exists(filepath):
        return []

    lines = []
    start = max(1, error_line - window)
    end = error_line + window

    for line_num in range(start, end + 1):
        line_content = linecache.getline(filepath, line_num)
        if not line_content and line_num > error_line:
            break
        lines.append({
            "number": line_num,
            "content": line_content.rstrip("\r\n"),
            "is_error": (line_num == error_line)
        })
    return lines

def render_exception(exc: Exception, req=None) -> str:
    """
    Render a high-end interactive debug error page when APP_DEBUG=bener,
    or a pristine, secure, production 500 error page when APP_DEBUG=salah.
    """
    is_debug = env("APP_DEBUG", False)
    if not is_debug:
        return render_production_500()

    # 1. Inspect exception details
    exc_type = type(exc).__name__
    exc_message = str(exc) or "Ora ana katrangan kesalahan (No error message provided)."
    tb = exc.__traceback__
    extracted_tb = traceback.extract_tb(tb) if tb else []

    # Find the most relevant error frame (prefer project files over standard library)
    error_frame = None
    if extracted_tb:
        for f in reversed(extracted_tb):
            if not f.filename.startswith("<") and os.path.exists(f.filename):
                error_frame = f
                break
        if not error_frame:
            error_frame = extracted_tb[-1]

    error_file = error_frame.filename if error_frame else "unknown"
    error_line = error_frame.lineno if error_frame else 0
    error_func = error_frame.name if error_frame else ""

    code_lines = get_code_snippet(error_file, error_line) if error_file else []

    # 2. Extract request details
    req_method = getattr(req, "method", "GET") if req else "GET"
    req_path = getattr(req, "path", "/") if req else "/"
    req_ip = getattr(req, "ip", "127.0.0.1") if req else "127.0.0.1"
    req_headers = getattr(req, "headers", {}) if req else {}
    req_query = getattr(req, "query", {}) if req else {}
    req_body = getattr(req, "body", {}) if req else {}
    req_cookies = getattr(req, "cookies", {}) if req else {}

    # 3. Environment info
    from framework import __version__ as larapak_version
    db_conn = env("DB_CONNECTION", "sqlite")
    cache_driver = env("CACHE_DRIVER", "sqlite")
    queue_driver = env("QUEUE_DRIVER", "sqlite")
    py_version = platform.python_version()
    os_name = f"{platform.system()} {platform.release()}"

    # Render snippet HTML
    snippet_html = ""
    if code_lines:
        for item in code_lines:
            hl_class = "error-line" if item["is_error"] else ""
            marker = "&gt;" if item["is_error"] else " "
            escaped_code = html.escape(item["content"]) or "&nbsp;"
            snippet_html += f"""<div class="code-row {hl_class}">
    <span class="line-marker">{marker}</span>
    <span class="line-num">{item["number"]}</span>
    <span class="line-code">{escaped_code}</span>
</div>"""
    else:
        snippet_html = """<div class="code-empty">Cuplikan kode ora kasedhiya kanggo berkas iki.</div>"""

    # Render Stack Trace Frames
    frames_html = ""
    for idx, f in enumerate(reversed(extracted_tb)):
        fname = os.path.basename(f.filename)
        dir_name = os.path.dirname(f.filename)
        frames_html += f"""<div class="frame-item">
    <div class="frame-header">
        <span class="frame-index">#{len(extracted_tb) - idx}</span>
        <span class="frame-func"><strong>{html.escape(f.name)}()</strong></span>
        <span class="frame-loc">{html.escape(fname)}:<span class="text-ember">{f.lineno}</span></span>
    </div>
    <div class="frame-path">{html.escape(dir_name)}</div>
    <div class="frame-code"><code>{html.escape(f.line or '')}</code></div>
</div>"""

    # Render Tables
    def render_dict_table(data_dict, empty_msg):
        if not data_dict:
            return f"""<p class="empty-state">{empty_msg}</p>"""
        rows = ""
        for k, v in data_dict.items():
            rows += f"""<tr>
                <td class="col-key">{html.escape(str(k))}</td>
                <td class="col-val"><code>{html.escape(str(v))}</code></td>
            </tr>"""
        return f"""<table class="data-table"><tbody>{rows}</tbody></table>"""

    headers_table = render_dict_table(req_headers, "Ora ana header panyuwunan.")
    query_table = render_dict_table(req_query, "Ora ana query parameter.")
    body_table = render_dict_table(req_body, "Ora ana body payload.")
    cookies_table = render_dict_table(req_cookies, "Ora ana cookie.")

    return f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(exc_type)} - Larapak Debugger</title>
    <style>
        :root {{
            --bg-base: #09090b;
            --bg-surface: #141416;
            --bg-surface-elevated: #1c1c1f;
            --bg-surface-code: #0d0d0f;
            --border-hairline: rgba(255, 255, 255, 0.08);
            --border-accent: rgba(245, 130, 32, 0.3);
            --text-primary: #ededec;
            --text-secondary: #a1a1aa;
            --text-muted: #71717a;
            --accent-ember: #f58220;
            --accent-red: #ef4444;
            --accent-red-bg: rgba(239, 68, 68, 0.12);
            --font-sans: -apple-system, BlinkMacSystemFont, "Plus Jakarta Sans", "Segoe UI", Roboto, sans-serif;
            --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-base);
            color: var(--text-primary);
            font-family: var(--font-sans);
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* Top Navigation Shell (Double-Bezel architecture) */
        .topbar-wrapper {{
            padding: 1rem 1.75rem;
            border-bottom: 1px solid var(--border-hairline);
            background-color: rgba(9, 9, 11, 0.85);
            backdrop-filter: blur(16px);
            position: sticky;
            top: 0;
            z-index: 40;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .brand-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.65rem;
            background: var(--bg-surface);
            border: 1px solid var(--border-hairline);
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            font-size: 0.825rem;
            font-weight: 600;
            color: var(--text-primary);
        }}
        .pulse-orb {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--accent-red);
            box-shadow: 0 0 10px var(--accent-red);
        }}
        .status-badge {{
            background: var(--accent-red-bg);
            color: var(--accent-red);
            border: 1px solid rgba(239, 68, 68, 0.25);
            font-size: 0.75rem;
            font-weight: 700;
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            letter-spacing: 0.04em;
        }}

        /* Header Hero Container */
        .hero-section {{
            padding: 2.5rem 1.75rem 2rem 1.75rem;
            max-width: 1240px;
            width: 100%;
            margin: 0 auto;
        }}
        .meta-line {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.85rem;
        }}
        .exc-type {{
            font-family: var(--font-mono);
            font-size: 0.95rem;
            color: var(--accent-red);
            font-weight: 700;
        }}
        .exc-title {{
            font-size: 1.85rem;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.02em;
            line-height: 1.3;
            margin-bottom: 1.25rem;
            word-break: break-word;
        }}
        .file-location-box {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--bg-surface);
            border: 1px solid var(--border-hairline);
            padding: 0.5rem 0.9rem;
            border-radius: 8px;
            font-family: var(--font-mono);
            font-size: 0.825rem;
            color: var(--text-secondary);
        }}
        .file-location-box strong {{
            color: var(--text-primary);
        }}

        /* Main Workspace & Tabs */
        .workspace {{
            max-width: 1240px;
            width: 100%;
            margin: 0 auto;
            padding: 0 1.75rem 3.5rem 1.75rem;
            flex-grow: 1;
        }}

        .tab-nav {{
            display: flex;
            gap: 0.5rem;
            border-bottom: 1px solid var(--border-hairline);
            margin-bottom: 1.75rem;
        }}
        .tab-btn {{
            background: none;
            border: none;
            color: var(--text-muted);
            font-family: var(--font-sans);
            font-size: 0.9rem;
            font-weight: 600;
            padding: 0.75rem 1.25rem;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: color 0.15s ease, border-color 0.15s ease;
        }}
        .tab-btn:hover {{
            color: var(--text-primary);
        }}
        .tab-btn.active {{
            color: var(--accent-ember);
            border-bottom-color: var(--accent-ember);
        }}

        .tab-pane {{
            display: none;
        }}
        .tab-pane.active {{
            display: block;
        }}

        /* Double-Bezel Outer Card */
        .outer-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-hairline);
            border-radius: 14px;
            padding: 1.25rem;
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6);
        }}

        /* Code Viewer */
        .code-container {{
            background: var(--bg-surface-code);
            border: 1px solid var(--border-hairline);
            border-radius: 10px;
            overflow-x: auto;
            font-family: var(--font-mono);
            font-size: 0.85rem;
            padding: 1rem 0;
            margin-bottom: 1.5rem;
        }}
        .code-row {{
            display: flex;
            align-items: center;
            padding: 0.2rem 1.25rem;
            line-height: 1.6;
        }}
        .code-row.error-line {{
            background-color: var(--accent-red-bg);
            border-left: 3px solid var(--accent-red);
        }}
        .line-marker {{
            width: 1.5rem;
            color: var(--accent-red);
            font-weight: bold;
            user-select: none;
        }}
        .line-num {{
            width: 3.5rem;
            color: var(--text-muted);
            user-select: none;
        }}
        .line-code {{
            white-space: pre;
            color: var(--text-primary);
        }}
        .error-line .line-code {{
            color: #ffffff;
            font-weight: 600;
        }}

        /* StackTrace List */
        .trace-title {{
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 1rem;
        }}
        .frame-item {{
            background: var(--bg-surface-elevated);
            border: 1px solid var(--border-hairline);
            border-radius: 8px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.75rem;
        }}
        .frame-header {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            font-size: 0.875rem;
            margin-bottom: 0.25rem;
        }}
        .frame-index {{
            color: var(--text-muted);
            font-family: var(--font-mono);
            font-size: 0.8rem;
        }}
        .frame-func {{
            color: var(--text-primary);
        }}
        .frame-loc {{
            color: var(--text-secondary);
            font-size: 0.8rem;
        }}
        .frame-path {{
            font-family: var(--font-mono);
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-bottom: 0.4rem;
            word-break: break-all;
        }}
        .frame-code {{
            background: var(--bg-surface-code);
            padding: 0.4rem 0.75rem;
            border-radius: 6px;
            font-family: var(--font-mono);
            font-size: 0.8rem;
            color: #e4e4e7;
            overflow-x: auto;
        }}

        /* Data Tables */
        .section-header {{
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 1.5rem 0 0.75rem 0;
        }}
        .section-header:first-of-type {{
            margin-top: 0;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            margin-bottom: 1.5rem;
        }}
        .data-table tr {{
            border-bottom: 1px solid var(--border-hairline);
        }}
        .data-table td {{
            padding: 0.65rem 0.85rem;
            vertical-align: top;
        }}
        .col-key {{
            width: 25%;
            color: var(--text-secondary);
            font-weight: 500;
        }}
        .col-val {{
            width: 75%;
            color: var(--text-primary);
            word-break: break-all;
        }}
        .col-val code {{
            font-family: var(--font-mono);
            font-size: 0.825rem;
            background: var(--bg-surface-elevated);
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
        }}
        .empty-state {{
            font-size: 0.85rem;
            color: var(--text-muted);
            padding: 0.5rem 0;
            font-style: italic;
        }}

        .text-ember {{ color: var(--accent-ember); }}
    </style>
</head>
<body>
    <header class="topbar-wrapper">
        <div style="display:flex; align-items:center; gap: 0.85rem;">
            <div class="brand-pill">
                <span class="pulse-orb"></span>
                <span>Larapak Engine</span>
            </div>
            <span class="status-badge">500 &bull; ERROR</span>
        </div>
        <div style="font-size:0.8rem; color:var(--text-muted);">
            NgapakIn VM Debugger &bull; Larapak v{larapak_version}
        </div>
    </header>

    <div class="hero-section">
        <div class="meta-line">
            <span class="exc-type">{html.escape(exc_type)}</span>
            <span style="color:var(--border-hairline)">|</span>
            <span style="font-size:0.85rem; color:var(--text-secondary);">{req_method} {html.escape(req_path)}</span>
        </div>
        <h1 class="exc-title">{html.escape(exc_message)}</h1>
        <div class="file-location-box">
            <span>Berkas: <strong>{html.escape(os.path.basename(error_file))}</strong>:<span class="text-ember">{error_line}</span></span>
            <span style="color:var(--text-muted); font-size:0.75rem;">({html.escape(error_file)})</span>
        </div>
    </div>

    <main class="workspace">
        <nav class="tab-nav">
            <button class="tab-btn active" onclick="switchTab('tab-trace', this)">StackTrace & Berkas</button>
            <button class="tab-btn" onclick="switchTab('tab-request', this)">Panyuwunan (Request)</button>
            <button class="tab-btn" onclick="switchTab('tab-env', this)">Lingkungan (Environment)</button>
        </nav>

        <!-- Tab 1: Code & Trace -->
        <div id="tab-trace" class="tab-pane active">
            <div class="outer-card">
                <div class="code-container">
                    {snippet_html}
                </div>

                <div class="trace-title">Riwayat Pemanggilan (Traceback):</div>
                <div class="frames-list">
                    {frames_html}
                </div>
            </div>
        </div>

        <!-- Tab 2: Request -->
        <div id="tab-request" class="tab-pane">
            <div class="outer-card">
                <h3 class="section-header">Informasi Rute & Klien</h3>
                <table class="data-table">
                    <tbody>
                        <tr><td class="col-key">Metode HTTP</td><td class="col-val"><code>{req_method}</code></td></tr>
                        <tr><td class="col-key">Path URL</td><td class="col-val"><code>{html.escape(req_path)}</code></td></tr>
                        <tr><td class="col-key">Alamat IP Klien</td><td class="col-val"><code>{html.escape(req_ip)}</code></td></tr>
                    </tbody>
                </table>

                <h3 class="section-header">Header HTTP</h3>
                {headers_table}

                <h3 class="section-header">Parameter Query String</h3>
                {query_table}

                <h3 class="section-header">Input Body Payload</h3>
                {body_table}

                <h3 class="section-header">Cookies</h3>
                {cookies_table}
            </div>
        </div>

        <!-- Tab 3: Environment -->
        <div id="tab-env" class="tab-pane">
            <div class="outer-card">
                <h3 class="section-header">Konfigurasi Sistem Larapak</h3>
                <table class="data-table">
                    <tbody>
                        <tr><td class="col-key">Versi Larapak</td><td class="col-val"><code>{larapak_version}</code></td></tr>
                        <tr><td class="col-key">Versi Python Runtime</td><td class="col-val"><code>{py_version}</code></td></tr>
                        <tr><td class="col-key">Sistem Operasi</td><td class="col-val"><code>{os_name}</code></td></tr>
                        <tr><td class="col-key">Database Driver</td><td class="col-val"><code>{db_conn}</code></td></tr>
                        <tr><td class="col-key">Cache Driver</td><td class="col-val"><code>{cache_driver}</code></td></tr>
                        <tr><td class="col-key">Queue Driver</td><td class="col-val"><code>{queue_driver}</code></td></tr>
                        <tr><td class="col-key">Mode Debug (APP_DEBUG)</td><td class="col-val"><code class="text-ember">bener (Aktif)</code></td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </main>

    <script>
        function switchTab(tabId, btn) {{
            var panes = document.querySelectorAll('.tab-pane');
            for (var i = 0; i < panes.length; i++) {{
                panes[i].classList.remove('active');
            }}
            var btns = document.querySelectorAll('.tab-btn');
            for (var j = 0; j < btns.length; j++) {{
                btns[j].classList.remove('active');
            }}
            var target = document.getElementById(tabId);
            if (target) {{
                target.classList.add('active');
                btn.classList.add('active');
            }}
        }}
    </script>
</body>
</html>"""

def render_production_500() -> str:
    """Ultra-clean, production-ready 500 error page that prevents leaking stack traces."""
    return """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>500 Kesalahan Server - Larapak</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: #09090b;
            color: #ededec;
            font-family: -apple-system, BlinkMacSystemFont, "Plus Jakarta Sans", "Segoe UI", Roboto, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 1.5rem;
            line-height: 1.5;
        }
        .error-shell {
            background: #141416;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            max-width: 520px;
            width: 100%;
            padding: 3rem 2.5rem;
            text-align: center;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
        }
        .badge-500 {
            display: inline-block;
            background: rgba(239, 68, 68, 0.12);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.25);
            font-size: 0.8rem;
            font-weight: 700;
            padding: 0.3rem 0.8rem;
            border-radius: 9999px;
            margin-bottom: 1.25rem;
            letter-spacing: 0.05em;
        }
        h1 {
            font-size: 1.65rem;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.02em;
            margin-bottom: 0.75rem;
        }
        p {
            font-size: 0.95rem;
            color: #a1a1aa;
            line-height: 1.6;
            margin-bottom: 2rem;
        }
        .btn-home {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            background-color: #ffffff;
            color: #09090b;
            font-size: 0.875rem;
            font-weight: 600;
            padding: 0.7rem 1.4rem;
            border-radius: 8px;
            text-decoration: none;
            transition: background-color 0.15s ease, transform 0.1s ease;
        }
        .btn-home:hover {
            background-color: #e4e4e7;
            transform: translateY(-1px);
        }
        .footer-note {
            margin-top: 2rem;
            font-size: 0.775rem;
            color: #71717a;
        }
    </style>
</head>
<body>
    <div class="error-shell">
        <span class="badge-500">500 &bull; SERVER ERROR</span>
        <h1>Alangan Ing Server</h1>
        <p>Nyuwun pangapunten, sistem nuju ngalami alangan teknis. Aja kuwatir, tim teknis wis diwenehi kabar lan lagi ndandani alangan iki.</p>
        <a href="/" class="btn-home">
            <span>Bali Menyang Kaca Utama</span>
            <span>&rarr;</span>
        </a>
        <div class="footer-note">Larapak MVC Web Framework</div>
    </div>
</body>
</html>"""
