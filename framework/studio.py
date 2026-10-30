# Larapak Route & API Studio
# Interactive Route Explorer, Live View Previewer, REST API Sandbox, and OpenAPI 3.0 Generator

import os
import re
import json
from framework.env import env
from framework.csrf import CSRF


def is_studio_enabled() -> bool:
    """Check if API Studio is allowed to run based on environment settings."""
    studio_conf = env("APP_STUDIO", None)
    if studio_conf is not None:
        if isinstance(studio_conf, bool):
            return studio_conf
        return str(studio_conf).lower() in ("bener", "true", "1", "on")
    
    # By default, enabled in debug mode or local development
    debug_conf = env("APP_DEBUG", True)
    if isinstance(debug_conf, bool):
        return debug_conf
    return str(debug_conf).lower() in ("bener", "true", "1", "on")


def generate_openapi_spec(router, app_name="Larapak Application", version="1.0.7") -> dict:
    """Generate a standard OpenAPI 3.0.3 specification from registered router routes."""
    paths = {}

    for route in router.routes:
        method = route["method"].lower()
        if method not in ("get", "post", "put", "patch", "delete", "head", "options"):
            continue

        raw_path = route["path"]
        clean_path = "/" + "/".join([p for p in raw_path.split("/") if p])
        if clean_path not in paths:
            paths[clean_path] = {}

        action_name = route["action"].name if hasattr(route["action"], "name") else str(route["action"])
        param_names = re.findall(r"\{([a-zA-Z0-9_]+)\}", clean_path)

        parameters = []
        for p_name in param_names:
            parameters.append({
                "name": p_name,
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "description": f"Parameter URL dinamis '{p_name}'"
            })

        middlewares = route.get("middleware", [])
        is_api = clean_path.startswith("/api") or "api" in clean_path.lower()
        tag = "API Endpoints" if is_api else "Web Views & Rute"

        operation = {
            "tags": [tag],
            "summary": f"{action_name}",
            "description": f"Rute ditangani oleh `{action_name}`. Middleware: `{', '.join(middlewares) if middlewares else 'Tidak ada'}`.",
            "parameters": parameters,
            "responses": {
                "200": {
                    "description": "Respons Berhasil",
                    "content": {
                        "application/json" if is_api else "text/html": {
                            "schema": {"type": "object" if is_api else "string"}
                        }
                    }
                },
                "400": {"description": "Permintaan Tidak Valid (Bad Request)"},
                "404": {"description": "Rute atau Sumber Daya Tidak Ditemukan"},
                "500": {"description": "Kesalahan Server Internal"}
            }
        }

        if method in ("post", "put", "patch"):
            operation["requestBody"] = {
                "description": "Payload permintaan (JSON atau Form Data)",
                "required": False,
                "content": {
                    "application/json": {
                        "schema": {"type": "object"}
                    },
                    "application/x-www-form-urlencoded": {
                        "schema": {"type": "object"}
                    }
                }
            }

        paths[clean_path][method] = operation

    return {
        "openapi": "3.0.3",
        "info": {
            "title": f"{app_name} API & Route Spec",
            "version": version,
            "description": "Dokumentasi rute dan REST API otomatis yang digenerate oleh **Larapak Route & API Studio**."
        },
        "servers": [
            {"url": "/", "description": "Server Aplikasi Larapak Aktif"}
        ],
        "paths": paths
    }


def render_studio_html(router, session=None, base_url="") -> str:
    """Render the high-end, anti-AI-slop Larapak Route & API Studio interface."""
    app_name = env("APP_NAME", "LarapakApp")
    app_env = env("APP_ENV", "local")
    app_debug = env("APP_DEBUG", "bener")
    csrf_token = CSRF.token(session) if session else ""

    # Prepare routes data
    routes_data = []
    for idx, r in enumerate(router.routes):
        method = r["method"].upper()
        path = r["path"]
        action = r["action"].name if hasattr(r["action"], "name") else str(r["action"])
        middlewares = r.get("middleware", [])
        params = re.findall(r"\{([a-zA-Z0-9_]+)\}", path)
        is_api = path.startswith("/api") or "api" in path.lower() or "api" in action.lower()

        routes_data.append({
            "id": idx,
            "method": method,
            "path": path,
            "action": action,
            "middlewares": middlewares,
            "params": params,
            "is_api": is_api,
            "type_label": "API (JSON)" if is_api else "VIEW (HTML)"
        })

    routes_json = json.dumps(routes_data)

    return f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Larapak Route & API Studio | {app_name}</title>
    <meta name="csrf-token" content="{csrf_token}">
    <style>
        :root {{
            --bg-base: #07090e;
            --bg-surface: #0d111a;
            --bg-panel: #111723;
            --bg-card: #151d2c;
            --bg-hover: #1c2638;
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-focus: rgba(255, 255, 255, 0.2);
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --text-faint: #64748b;
            
            --color-get: #10b981;
            --color-get-bg: rgba(16, 185, 129, 0.12);
            --color-post: #3b82f6;
            --color-post-bg: rgba(59, 130, 246, 0.12);
            --color-put: #f59e0b;
            --color-put-bg: rgba(245, 158, 11, 0.12);
            --color-patch: #8b5cf6;
            --color-patch-bg: rgba(139, 92, 246, 0.12);
            --color-delete: #ef4444;
            --color-delete-bg: rgba(239, 68, 68, 0.12);

            --accent: #38bdf8;
            --accent-bg: rgba(56, 189, 248, 0.1);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            height: 100vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}

        code, pre, .font-mono {{
            font-family: "JetBrains Mono", Consolas, Menlo, Monaco, Courier, monospace;
        }}

        /* Header Bar */
        .studio-header {{
            height: 54px;
            background-color: var(--bg-surface);
            border-bottom: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 18px;
            flex-shrink: 0;
            z-index: 10;
        }}

        .brand-cluster {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .brand-logo {{
            width: 28px;
            height: 28px;
            border-radius: 6px;
            background: linear-gradient(135deg, #0284c7, #38bdf8);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 14px;
            color: #fff;
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
        }}

        .brand-title {{
            font-size: 14px;
            font-weight: 700;
            letter-spacing: -0.3px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .badge {{
            font-size: 11px;
            padding: 2px 7px;
            border-radius: 4px;
            font-weight: 600;
            letter-spacing: 0;
        }}

        .badge-version {{
            background: rgba(255, 255, 255, 0.06);
            color: var(--text-muted);
            border: 1px solid var(--border-subtle);
        }}

        .badge-env {{
            background: rgba(16, 185, 129, 0.12);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.25);
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .pulse-dot {{
            width: 6px;
            height: 6px;
            background-color: #34d399;
            border-radius: 50%;
            box-shadow: 0 0 6px #34d399;
        }}

        .header-actions {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .btn {{
            font-size: 12px;
            font-weight: 500;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
            border: 1px solid transparent;
        }}

        .btn-ghost {{
            background: transparent;
            color: var(--text-muted);
            border-color: var(--border-subtle);
        }}

        .btn-ghost:hover {{
            background: var(--bg-hover);
            color: var(--text-main);
            border-color: var(--border-focus);
        }}

        .btn-primary {{
            background: #0284c7;
            color: #fff;
            border-color: #38bdf8;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        }}

        .btn-primary:hover {{
            background: #0369a1;
        }}

        /* Main Workspace Split Layout */
        .studio-workspace {{
            display: flex;
            flex: 1;
            height: calc(100vh - 54px);
            overflow: hidden;
        }}

        /* Left Sidebar: Route List */
        .sidebar {{
            width: 360px;
            background-color: var(--bg-surface);
            border-right: 1px solid var(--border-subtle);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }}

        .sidebar-search {{
            padding: 12px;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .search-input-wrap {{
            position: relative;
        }}

        .search-input {{
            width: 100%;
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            color: var(--text-main);
            font-size: 12px;
            border-radius: 6px;
            padding: 8px 10px 8px 28px;
            outline: none;
            transition: border-color 0.15s ease;
        }}

        .search-input:focus {{
            border-color: var(--accent);
        }}

        .search-icon {{
            position: absolute;
            left: 9px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-faint);
            font-size: 12px;
            pointer-events: none;
        }}

        .filter-strip {{
            padding: 8px 12px;
            display: flex;
            gap: 6px;
            overflow-x: auto;
            border-bottom: 1px solid var(--border-subtle);
            background: var(--bg-surface);
            scrollbar-width: none;
        }}

        .filter-strip::-webkit-scrollbar {{
            display: none;
        }}

        .filter-pill {{
            font-size: 11px;
            font-weight: 500;
            padding: 3px 8px;
            border-radius: 4px;
            background: transparent;
            color: var(--text-muted);
            border: 1px solid var(--border-subtle);
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.15s ease;
        }}

        .filter-pill.active, .filter-pill:hover {{
            background: var(--bg-hover);
            color: var(--text-main);
            border-color: var(--border-focus);
        }}

        .route-list {{
            flex: 1;
            overflow-y: auto;
            padding: 6px;
        }}

        .route-item {{
            padding: 10px 12px;
            border-radius: 6px;
            cursor: pointer;
            margin-bottom: 3px;
            border: 1px solid transparent;
            transition: all 0.12s ease;
            position: relative;
        }}

        .route-item:hover {{
            background: var(--bg-card);
            border-color: var(--border-subtle);
        }}

        .route-item.selected {{
            background: var(--bg-card);
            border-color: rgba(56, 189, 248, 0.3);
            box-shadow: inset 3px 0 0 0 var(--accent);
        }}

        .route-item-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            margin-bottom: 4px;
        }}

        .method-badge {{
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "JetBrains Mono", monospace;
            letter-spacing: 0.5px;
            display: inline-block;
        }}

        .method-get {{ color: var(--color-get); background: var(--color-get-bg); border: 1px solid rgba(16, 185, 129, 0.3); }}
        .method-post {{ color: var(--color-post); background: var(--color-post-bg); border: 1px solid rgba(59, 130, 246, 0.3); }}
        .method-put {{ color: var(--color-put); background: var(--color-put-bg); border: 1px solid rgba(245, 158, 11, 0.3); }}
        .method-patch {{ color: var(--color-patch); background: var(--color-patch-bg); border: 1px solid rgba(139, 92, 246, 0.3); }}
        .method-delete {{ color: var(--color-delete); background: var(--color-delete-bg); border: 1px solid rgba(239, 68, 68, 0.3); }}

        .type-badge {{
            font-size: 9.5px;
            padding: 1px 5px;
            border-radius: 3px;
            font-weight: 600;
        }}

        .type-view {{
            background: rgba(6, 182, 212, 0.12);
            color: #22d3ee;
            border: 1px solid rgba(6, 182, 212, 0.3);
        }}

        .type-api {{
            background: rgba(168, 85, 247, 0.12);
            color: #c084fc;
            border: 1px solid rgba(168, 85, 247, 0.3);
        }}

        .route-path {{
            font-size: 12.5px;
            font-weight: 600;
            color: var(--text-main);
            word-break: break-all;
        }}

        .route-action {{
            font-size: 11px;
            color: var(--text-faint);
            margin-top: 3px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        /* Right Panel: Studio Playground */
        .main-panel {{
            flex: 1;
            display: flex;
            flex-direction: column;
            background-color: var(--bg-base);
            overflow: hidden;
        }}

        .request-header-strip {{
            padding: 14px 18px;
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border-subtle);
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .url-bar-row {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}

        .url-input-container {{
            flex: 1;
            display: flex;
            align-items: center;
            background: var(--bg-panel);
            border: 1px solid var(--border-subtle);
            border-radius: 6px;
            padding: 0 10px;
            height: 38px;
            transition: border-color 0.15s ease;
        }}

        .url-input-container:focus-within {{
            border-color: var(--accent);
        }}

        .url-prefix {{
            font-size: 12px;
            color: var(--text-faint);
            margin-right: 2px;
            user-select: none;
        }}

        .url-input {{
            flex: 1;
            background: transparent;
            border: none;
            color: var(--text-main);
            font-size: 13px;
            outline: none;
            font-family: "JetBrains Mono", monospace;
        }}

        .btn-send {{
            height: 38px;
            padding: 0 20px;
            font-size: 13px;
            font-weight: 600;
            background: #0284c7;
            color: #fff;
            border: 1px solid #38bdf8;
            border-radius: 6px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.15s ease;
        }}

        .btn-send:hover {{
            background: #0369a1;
        }}

        .route-meta-row {{
            display: flex;
            align-items: center;
            gap: 14px;
            font-size: 11.5px;
            color: var(--text-muted);
            flex-wrap: wrap;
        }}

        .meta-tag {{
            display: flex;
            align-items: center;
            gap: 5px;
            background: var(--bg-card);
            padding: 3px 8px;
            border-radius: 4px;
            border: 1px solid var(--border-subtle);
        }}

        /* Split Request / Response View */
        .workspace-split {{
            flex: 1;
            display: flex;
            overflow: hidden;
        }}

        .request-column {{
            width: 440px;
            border-right: 1px solid var(--border-subtle);
            display: flex;
            flex-direction: column;
            background: var(--bg-surface);
        }}

        .response-column {{
            flex: 1;
            display: flex;
            flex-direction: column;
            background: var(--bg-base);
            overflow: hidden;
        }}

        .tab-bar {{
            height: 38px;
            border-bottom: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            padding: 0 12px;
            gap: 4px;
            background: var(--bg-surface);
            flex-shrink: 0;
        }}

        .tab-btn {{
            font-size: 11.5px;
            font-weight: 500;
            padding: 6px 10px;
            border-radius: 5px;
            background: transparent;
            color: var(--text-muted);
            border: none;
            cursor: pointer;
            transition: all 0.15s ease;
        }}

        .tab-btn:hover {{
            color: var(--text-main);
            background: var(--bg-hover);
        }}

        .tab-btn.active {{
            color: var(--text-main);
            background: var(--bg-card);
            font-weight: 600;
        }}

        .tab-content {{
            flex: 1;
            overflow-y: auto;
            padding: 14px;
        }}

        .field-group {{
            margin-bottom: 12px;
        }}

        .field-label {{
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 5px;
            display: block;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .text-input, .text-area {{
            width: 100%;
            background: var(--bg-panel);
            border: 1px solid var(--border-subtle);
            border-radius: 5px;
            color: var(--text-main);
            font-size: 12.5px;
            padding: 8px 10px;
            outline: none;
            font-family: inherit;
        }}

        .text-area {{
            font-family: "JetBrains Mono", monospace;
            font-size: 12px;
            min-height: 140px;
            resize: vertical;
        }}

        .text-input:focus, .text-area:focus {{
            border-color: var(--accent);
        }}

        /* Response Panel */
        .response-status-bar {{
            height: 42px;
            border-bottom: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            background: var(--bg-surface);
            font-size: 12px;
            flex-shrink: 0;
        }}

        .status-pill {{
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: "JetBrains Mono", monospace;
        }}

        .status-2xx {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}
        .status-3xx {{ background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }}
        .status-4xx {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .status-5xx {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }}

        .response-metrics {{
            display: flex;
            align-items: center;
            gap: 12px;
            color: var(--text-muted);
            font-size: 11.5px;
        }}

        .response-view-container {{
            flex: 1;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            position: relative;
        }}

        .preview-iframe {{
            width: 100%;
            height: 100%;
            border: none;
            background: #fff;
            transition: max-width 0.2s ease;
        }}

        .iframe-viewport-wrap {{
            flex: 1;
            display: flex;
            justify-content: center;
            background: #000;
            overflow: auto;
        }}

        .code-box {{
            flex: 1;
            overflow: auto;
            padding: 16px;
            background: var(--bg-base);
            color: #e2e8f0;
            font-size: 12px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-break: break-all;
            user-select: text;
        }}

        .viewport-controls {{
            display: flex;
            align-items: center;
            gap: 6px;
            margin-right: 10px;
        }}

        .viewport-btn {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            color: var(--text-muted);
            font-size: 11px;
            padding: 2px 7px;
            border-radius: 4px;
            cursor: pointer;
        }}

        .viewport-btn.active {{
            color: var(--text-main);
            border-color: var(--accent);
            background: var(--bg-hover);
        }}

        .notice-box {{
            padding: 10px 12px;
            border-radius: 5px;
            font-size: 11.5px;
            line-height: 1.5;
            background: rgba(56, 189, 248, 0.08);
            border: 1px solid rgba(56, 189, 248, 0.2);
            color: #7dd3fc;
            margin-bottom: 12px;
        }}

        .empty-state {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: var(--text-faint);
            gap: 10px;
            text-align: center;
            padding: 20px;
        }}

        .empty-state-icon {{
            font-size: 32px;
            opacity: 0.6;
        }}
    </style>
</head>
<body>

    <!-- Header -->
    <header class="studio-header">
        <div class="brand-cluster">
            <div class="brand-logo">N</div>
            <div class="brand-title">
                Larapak Route & API Studio
                <span class="badge badge-version">v1.0.7</span>
                <span class="badge badge-env"><span class="pulse-dot"></span>{app_env}</span>
            </div>
        </div>
        <div class="header-actions">
            <a href="/api-studio/openapi.json" target="_blank" class="btn btn-ghost" title="Lihat Spesifikasi Standar OpenAPI 3.0">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
                <span>OpenAPI 3.0</span>
            </a>
            <a href="/" target="_blank" class="btn btn-ghost" title="Buka Halaman Utama Aplikasi Web">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
                <span>Buka Web</span>
            </a>
        </div>
    </header>

    <!-- Split Workspace -->
    <div class="studio-workspace">
        
        <!-- Sidebar: Route Explorer -->
        <aside class="sidebar">
            <div class="sidebar-search">
                <div class="search-input-wrap">
                    <span class="search-icon">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    </span>
                    <input type="text" id="route-search" class="search-input" placeholder="Cari path, controller, atau method...">
                </div>
            </div>

            <div class="filter-strip">
                <button class="filter-pill active" onclick="setFilter('ALL')">Semua</button>
                <button class="filter-pill" onclick="setFilter('GET')">GET</button>
                <button class="filter-pill" onclick="setFilter('POST')">POST</button>
                <button class="filter-pill" onclick="setFilter('PUT')">PUT</button>
                <button class="filter-pill" onclick="setFilter('DELETE')">DELETE</button>
                <button class="filter-pill" onclick="setFilter('VIEW')">View (HTML)</button>
                <button class="filter-pill" onclick="setFilter('API')">API (JSON)</button>
            </div>

            <div class="route-list" id="route-list-container">
                <!-- Dynamically populated -->
            </div>
        </aside>

        <!-- Main Panel: Request & Live Response Inspector -->
        <main class="main-panel">
            
            <!-- Target URL & Action Bar -->
            <div class="request-header-strip">
                <div class="url-bar-row">
                    <span id="active-method-badge" class="method-badge method-get">GET</span>
                    <div class="url-input-container">
                        <span class="url-prefix">http://localhost:8000</span>
                        <input type="text" id="active-path-input" class="url-input" value="/">
                    </div>
                    <button class="btn-send" id="btn-send" onclick="sendActiveRequest()">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                        <span>Kirim Permintaan</span>
                        <kbd style="font-size:10px; opacity:0.75; padding:2px 5px; background:rgba(255,255,255,0.18); border-radius:3px; font-family:monospace; margin-left:3px;">Ctrl ↵</kbd>
                    </button>
                </div>
                <div class="route-meta-row">
                    <div class="meta-tag">
                        <strong>Target:</strong> <span id="meta-action" class="font-mono">-</span>
                    </div>
                    <div class="meta-tag">
                        <strong>Tipe:</strong> <span id="meta-type">-</span>
                    </div>
                    <div class="meta-tag" id="meta-middleware-tag">
                        <strong>Middleware:</strong> <span id="meta-middleware">-</span>
                    </div>
                </div>
            </div>

            <!-- Workspace Sub Split -->
            <div class="workspace-split">
                
                <!-- Request Configuration Tabs -->
                <div class="request-column">
                    <div class="tab-bar">
                        <button class="tab-btn active" onclick="setRequestTab('params')">Parameter URL</button>
                        <button class="tab-btn" onclick="setRequestTab('query')">Query Params</button>
                        <button class="tab-btn" onclick="setRequestTab('headers')">Headers</button>
                        <button class="tab-btn" onclick="setRequestTab('body')">Body</button>
                    </div>

                    <!-- Tab: URL Params -->
                    <div class="tab-content" id="tab-params">
                        <div id="url-params-container">
                            <p style="font-size: 12px; color: var(--text-faint);">Tidak ada parameter URL dinamis pada rute ini.</p>
                        </div>
                    </div>

                    <!-- Tab: Query Params -->
                    <div class="tab-content" id="tab-query" style="display: none;">
                        <div class="field-group">
                            <label class="field-label">Query String (Kunci = Nilai)</label>
                            <input type="text" id="query-string-input" class="text-input font-mono" placeholder="misal: cari=sepatu&halaman=2">
                            <span style="font-size: 11px; color: var(--text-faint); margin-top: 4px; display: block;">
                                Otomatis ditambahkan ke akhir URL saat pengiriman.
                            </span>
                        </div>
                    </div>

                    <!-- Tab: Headers -->
                    <div class="tab-content" id="tab-headers" style="display: none;">
                        <div class="field-group">
                            <label class="field-label">Authorization (Bearer Token)</label>
                            <input type="text" id="header-auth" class="text-input font-mono" placeholder="Bearer eyJhbGciOi...">
                        </div>
                        <div class="field-group">
                            <label class="field-label">Accept Header</label>
                            <input type="text" id="header-accept" class="text-input font-mono" value="text/html,application/xhtml+xml,application/json">
                        </div>
                    </div>

                    <!-- Tab: Body -->
                    <div class="tab-content" id="tab-body" style="display: none;">
                        <div class="notice-box">
                            <div style="display: flex; align-items: center; gap: 7px; margin-bottom: 3px;">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                                <strong>Auto-CSRF Protected</strong>
                            </div>
                            Token CSRF aktif (<code class="font-mono">{csrf_token[:8]}...</code>) otomatis disertakan pada header <code>X-CSRF-TOKEN</code> dan payload form.
                        </div>
                        <div class="field-group">
                            <label class="field-label">Format Body</label>
                            <select id="body-format" class="text-input" onchange="toggleBodyFormat()">
                                <option value="json">JSON (application/json)</option>
                                <option value="form">Form URL-Encoded (application/x-www-form-urlencoded)</option>
                            </select>
                        </div>
                        <div class="field-group">
                            <label class="field-label">Payload Isi Body</label>
                            <textarea id="body-content" class="text-area" placeholder='{{"kunci": "nilai"}}'></textarea>
                        </div>
                    </div>
                </div>

                <!-- Live Response Inspector -->
                <div class="response-column">
                    <div class="response-status-bar">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span id="res-status-pill" class="status-pill status-2xx" style="display: none;">200 OK</span>
                            <span id="res-view-badge" class="badge type-view" style="display: none;">Template View</span>
                        </div>
                        <div class="response-metrics">
                            <span id="res-time-metric">0 ms</span>
                            <span id="res-size-metric">0 KB</span>
                            <div class="viewport-controls" id="viewport-controls" style="display: none;">
                                <button class="viewport-btn active" onclick="setViewport('100%')">Desktop</button>
                                <button class="viewport-btn" onclick="setViewport('768px')">Tablet</button>
                                <button class="viewport-btn" onclick="setViewport('375px')">Mobile</button>
                            </div>
                        </div>
                    </div>

                    <div class="tab-bar">
                        <button class="tab-btn active" id="tab-res-preview-btn" onclick="setResponseTab('preview')">Pratinjau Tampilan (Live)</button>
                        <button class="tab-btn" id="tab-res-code-btn" onclick="setResponseTab('code')">Kode Mentah (Raw)</button>
                        <button class="tab-btn" id="tab-res-headers-btn" onclick="setResponseTab('headers')">Header Respons</button>
                    </div>

                    <div class="response-view-container" id="response-container">
                        <!-- Empty initial state -->
                        <div class="empty-state" id="empty-state">
                            <div class="empty-state-icon">
                                <svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color: var(--accent); opacity: 0.85;"><circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>
                            </div>
                            <div style="font-size: 14px; font-weight: 600; color: var(--text-main);">Pilih Rute & Kirim Permintaan</div>
                            <div style="font-size: 12px; max-width: 320px; color: var(--text-muted); line-height: 1.5;">
                                Klik tombol <strong>Kirim Permintaan</strong> di atas untuk melihat pratinjau halaman web secara interaktif atau respons data JSON yang dihasilkan.
                            </div>
                        </div>

                        <!-- Live Preview Tab (iframe) -->
                        <div class="iframe-viewport-wrap" id="res-tab-preview" style="display: none;">
                            <iframe id="preview-iframe" class="preview-iframe" sandbox="allow-same-origin allow-scripts allow-forms"></iframe>
                        </div>

                        <!-- Raw Code Tab -->
                        <div id="res-tab-code" style="display: none; position: relative; height: 100%; width: 100%;">
                            <button class="btn btn-ghost" onclick="copyResponseCode()" style="position: absolute; right: 14px; top: 12px; font-size: 11px; z-index: 5; background: var(--bg-card);">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                                <span id="copy-btn-text">Salin Kode</span>
                            </button>
                            <pre class="code-box font-mono" id="raw-code-box" style="height: 100%; width: 100%;"></pre>
                        </div>

                        <!-- Response Headers Tab -->
                        <div class="tab-content" id="res-tab-headers" style="display: none;">
                            <table style="width: 100%; border-collapse: collapse; font-size: 12px; font-family: monospace;">
                                <thead>
                                    <tr style="border-bottom: 1px solid var(--border-subtle); text-align: left; color: var(--text-muted);">
                                        <th style="padding: 6px;">Header</th>
                                        <th style="padding: 6px;">Nilai</th>
                                    </tr>
                                </thead>
                                <tbody id="res-headers-tbody"></tbody>
                            </table>
                        </div>
                    </div>
                </div>

            </div>

        </main>

    </div>

    <!-- JavaScript Controller -->
    <script>
        const routes = {routes_json};
        const csrfToken = "{csrf_token}";
        let currentRoute = routes[0] || null;
        let currentFilter = 'ALL';
        let searchQuery = '';

        function init() {{
            renderRouteList();
            if (currentRoute) {{
                selectRoute(currentRoute.id);
            }}

            document.getElementById('route-search').addEventListener('input', (e) => {{
                searchQuery = e.target.value.toLowerCase();
                renderRouteList();
            }});
        }}

        function setFilter(filter) {{
            currentFilter = filter;
            document.querySelectorAll('.filter-pill').forEach(btn => {{
                btn.classList.toggle('active', btn.innerText.includes(filter) || (filter === 'ALL' && btn.innerText === 'Semua'));
            }});
            renderRouteList();
        }}

        function renderRouteList() {{
            const container = document.getElementById('route-list-container');
            container.innerHTML = '';

            const filtered = routes.filter(r => {{
                if (currentFilter === 'VIEW' && r.is_api) return false;
                if (currentFilter === 'API' && !r.is_api) return false;
                if (!['ALL', 'VIEW', 'API'].includes(currentFilter) && r.method !== currentFilter) return false;

                if (searchQuery) {{
                    const matchPath = r.path.toLowerCase().includes(searchQuery);
                    const matchAction = r.action.toLowerCase().includes(searchQuery);
                    const matchMethod = r.method.toLowerCase().includes(searchQuery);
                    return matchPath || matchAction || matchMethod;
                }}
                return true;
            }});

            filtered.forEach(r => {{
                const el = document.createElement('div');
                el.className = `route-item ${{currentRoute && currentRoute.id === r.id ? 'selected' : ''}}`;
                el.onclick = () => selectRoute(r.id);

                const typeClass = r.is_api ? 'type-api' : 'type-view';

                el.innerHTML = `
                    <div class="route-item-top">
                        <span class="method-badge method-${{r.method.toLowerCase()}}">${{r.method}}</span>
                        <span class="type-badge ${{typeClass}}">${{r.type_label}}</span>
                    </div>
                    <div class="route-path font-mono">${{r.path}}</div>
                    <div class="route-action font-mono">${{r.action}}</div>
                `;
                container.appendChild(el);
            }});
        }}

        function selectRoute(id) {{
            currentRoute = routes.find(r => r.id === id);
            if (!currentRoute) return;

            renderRouteList();

            // Update Header Strip
            const badge = document.getElementById('active-method-badge');
            badge.className = `method-badge method-${{currentRoute.method.toLowerCase()}}`;
            badge.innerText = currentRoute.method;

            document.getElementById('active-path-input').value = currentRoute.path;
            document.getElementById('meta-action').innerText = currentRoute.action;
            document.getElementById('meta-type').innerText = currentRoute.type_label;
            document.getElementById('meta-middleware').innerText = currentRoute.middlewares.length > 0 
                ? currentRoute.middlewares.join(', ') 
                : 'Tidak ada';

            // Populate URL params
            const paramsContainer = document.getElementById('url-params-container');
            if (currentRoute.params && currentRoute.params.length > 0) {{
                let html = '';
                currentRoute.params.forEach(p => {{
                    html += `
                        <div class="field-group">
                            <label class="field-label">Parameter {{${{p}}}}</label>
                            <input type="text" class="text-input font-mono param-field" data-param="${{p}}" placeholder="Nilai untuk ${{p}}..." oninput="updatePathWithParams()">
                        </div>
                    `;
                }});
                paramsContainer.innerHTML = html;
            }} else {{
                paramsContainer.innerHTML = '<p style="font-size: 12px; color: var(--text-faint);">Tidak ada parameter URL dinamis pada rute ini.</p>';
            }}
        }}

        function updatePathWithParams() {{
            if (!currentRoute) return;
            let path = currentRoute.path;
            document.querySelectorAll('.param-field').forEach(input => {{
                const paramName = input.getAttribute('data-param');
                const val = input.value.trim() || `{{${{paramName}}}}`;
                path = path.replace(`{{${{paramName}}}}`, val);
            }});
            document.getElementById('active-path-input').value = path;
        }}

        function setRequestTab(tab) {{
            document.querySelectorAll('.request-column .tab-btn').forEach(btn => btn.classList.remove('active'));
            ['params', 'query', 'headers', 'body'].forEach(t => {{
                const tabEl = document.getElementById(`tab-${{t}}`);
                if (tabEl) tabEl.style.display = (t === tab) ? 'block' : 'none';
            }});
            event.target.classList.add('active');
        }}

        function setResponseTab(tab) {{
            document.querySelectorAll('.response-column .tab-btn').forEach(btn => btn.classList.remove('active'));
            ['preview', 'code', 'headers'].forEach(t => {{
                const tabEl = document.getElementById(`res-tab-${{t}}`);
                if (tabEl) tabEl.style.display = (t === tab) ? 'flex' : 'none';
            }});
            document.getElementById(`tab-res-${{tab}}-btn`).classList.add('active');
        }}

        function setViewport(width) {{
            const iframe = document.getElementById('preview-iframe');
            iframe.style.maxWidth = width;
            document.querySelectorAll('.viewport-btn').forEach(btn => {{
                btn.classList.toggle('active', btn.innerText.toLowerCase().includes(width === '100%' ? 'desktop' : (width === '768px' ? 'tablet' : 'mobile')));
            }});
        }}

        function toggleBodyFormat() {{
            const format = document.getElementById('body-format').value;
            const textarea = document.getElementById('body-content');
            if (format === 'json' && !textarea.value.trim()) {{
                textarea.placeholder = '{{\\n  "key": "value"\\n}}';
            }} else if (format === 'form' && !textarea.value.trim()) {{
                textarea.placeholder = 'kunci=nilai&nama=Larapak';
            }}
        }}

        async function sendActiveRequest() {{
            if (!currentRoute) return;

            let path = document.getElementById('active-path-input').value;
            const queryString = document.getElementById('query-string-input').value.trim();
            if (queryString) {{
                path += (path.includes('?') ? '&' : '?') + queryString.replace(/^\\?/, '');
            }}

            const method = currentRoute.method;
            const headers = {{
                'Accept': document.getElementById('header-accept').value || 'text/html,application/json'
            }};

            const auth = document.getElementById('header-auth').value.trim();
            if (auth) headers['Authorization'] = auth;

            let body = undefined;
            if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {{
                // Auto attach CSRF
                if (csrfToken) {{
                    headers['X-CSRF-TOKEN'] = csrfToken;
                }}

                const format = document.getElementById('body-format').value;
                const rawContent = document.getElementById('body-content').value.trim();

                if (format === 'json') {{
                    headers['Content-Type'] = 'application/json';
                    let jsonObj = {{}};
                    try {{
                        jsonObj = rawContent ? JSON.parse(rawContent) : {{}};
                    }} catch (e) {{
                        alert('Format JSON pada Body tidak valid!');
                        return;
                    }}
                    if (csrfToken && !jsonObj._token) {{
                        jsonObj._token = csrfToken;
                    }}
                    body = JSON.stringify(jsonObj);
                }} else {{
                    headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    let params = new URLSearchParams(rawContent);
                    if (csrfToken && !params.has('_token')) {{
                        params.append('_token', csrfToken);
                    }}
                    body = params.toString();
                }}
            }}

            const btn = document.getElementById('btn-send');
            btn.innerHTML = '⏳ Memproses...';
            btn.disabled = true;

            const startTime = performance.now();

            try {{
                const res = await fetch(path, {{
                    method: method,
                    headers: headers,
                    body: body
                }});

                const duration = Math.round(performance.now() - startTime);
                const text = await res.text();
                const contentType = res.headers.get('Content-Type') || '';
                const isHtml = contentType.includes('text/html');
                const isJson = contentType.includes('application/json');

                // Update Status Bar
                const statusPill = document.getElementById('res-status-pill');
                statusPill.style.display = 'inline-block';
                statusPill.innerText = `${{res.status}} ${{res.statusText || 'Response'}}`;
                statusPill.className = 'status-pill ' + 
                    (res.status < 300 ? 'status-2xx' : (res.status < 400 ? 'status-3xx' : (res.status < 500 ? 'status-4xx' : 'status-5xx')));

                document.getElementById('res-time-metric').innerText = `${{duration}} ms`;
                const sizeKb = (new Blob([text]).size / 1024).toFixed(1);
                document.getElementById('res-size-metric').innerText = `${{sizeKb}} KB`;

                const viewBadge = document.getElementById('res-view-badge');
                const renderedViewName = res.headers.get('X-Larapak-View');
                if (renderedViewName) {{
                    viewBadge.style.display = 'inline-block';
                    viewBadge.innerText = `View: ${{renderedViewName}}.nview`;
                }} else {{
                    viewBadge.style.display = isHtml ? 'inline-block' : 'none';
                    viewBadge.innerText = isHtml ? 'HTML View' : 'JSON';
                }}

                // Hide empty state
                document.getElementById('empty-state').style.display = 'none';

                // Fill iframe for rendered view
                const iframe = document.getElementById('preview-iframe');
                iframe.srcdoc = text;

                // Fill raw code
                const codeBox = document.getElementById('raw-code-box');
                if (isJson) {{
                    try {{
                        codeBox.innerText = JSON.stringify(JSON.parse(text), null, 2);
                    }} catch (e) {{
                        codeBox.innerText = text;
                    }}
                }} else {{
                    codeBox.innerText = text;
                }}

                // Fill Response Headers
                const headersTbody = document.getElementById('res-headers-tbody');
                headersTbody.innerHTML = '';
                res.headers.forEach((val, key) => {{
                    const tr = document.createElement('tr');
                    tr.style.borderBottom = '1px solid var(--border-subtle)';
                    tr.innerHTML = `
                        <td style="padding: 6px; color: var(--accent); font-weight: 600;">${{key}}</td>
                        <td style="padding: 6px; color: var(--text-main); word-break: break-all;">${{val}}</td>
                    `;
                    headersTbody.appendChild(tr);
                }});

                // Auto switch tab based on response type
                document.getElementById('viewport-controls').style.display = isHtml ? 'flex' : 'none';
                if (isHtml) {{
                    setResponseTab('preview');
                }} else {{
                    setResponseTab('code');
                }}

            }} catch (err) {{
                alert('Gagal mengirim permintaan: ' + err.message);
            }} finally {{
                btn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> <span>Kirim Permintaan</span> <kbd style="font-size:10px; opacity:0.75; padding:2px 5px; background:rgba(255,255,255,0.18); border-radius:3px; font-family:monospace; margin-left:3px;">Ctrl ↵</kbd>`;
                btn.disabled = false;
            }}
        }}

        function copyResponseCode() {{
            const code = document.getElementById('raw-code-box').innerText;
            if (!code) return;
            navigator.clipboard.writeText(code).then(() => {{
                const btnText = document.getElementById('copy-btn-text');
                if (btnText) {{
                    btnText.innerText = 'Tersalin!';
                    setTimeout(() => {{
                        btnText.innerText = 'Salin Kode';
                    }}, 2000);
                }}
            }}).catch(() => {{}});
        }}

        // Shortcut: Ctrl + Enter to Send Request
        document.addEventListener('keydown', (e) => {{
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {{
                e.preventDefault();
                sendActiveRequest();
            }}
        }});

        window.onload = init;
    </script>
</body>
</html>
"""
