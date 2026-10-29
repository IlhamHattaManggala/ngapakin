# Project paths resolution and language scaffolding configuration for Larapak / NgapakIn

import os

PATHS_CONFIG = {
    "ngapak": {
        "app": "jeroan",
        "controllers": "jeroan/Pangatur",
        "models": "jeroan/Wujud",
        "middleware": "jeroan/Pencegat",
        "jobs": "jeroan/Gawean",
        "database": "lumbung",
        "migrations": "lumbung/owahan",
        "seeders": "lumbung/bibit",
        "routes": "dalan",
        "views": "sawangan",
        "public": "njobo",
        "public_css": "njobo/css",
        "public_js": "njobo/js",
        "public_images": "njobo/images",
    },
    "indonesia": {
        "app": "aplikasi",
        "controllers": "aplikasi/Pengendali",
        "models": "aplikasi/Model",
        "middleware": "aplikasi/Penyaring",
        "jobs": "aplikasi/Tugas",
        "database": "basisdata",
        "migrations": "basisdata/migrasi",
        "seeders": "basisdata/seeder",
        "routes": "rute",
        "views": "tampilan",
        "public": "publik",
        "public_css": "publik/css",
        "public_js": "publik/js",
        "public_images": "publik/gambar",
    },
    "english": {
        "app": "app",
        "controllers": "app/Controllers",
        "models": "app/Models",
        "middleware": "app/Middleware",
        "jobs": "app/Jobs",
        "database": "database",
        "migrations": "database/migrations",
        "seeders": "database/seeders",
        "routes": "routes",
        "views": "resources/views",
        "public": "public",
        "public_css": "public/css",
        "public_js": "public/js",
        "public_images": "public/images",
    }
}

def normalize_language(lang_input):
    """Normalize language input string to 'ngapak', 'indonesia', or 'english'."""
    if not lang_input:
        return "english"
    lang = lang_input.strip().lower()
    if lang in ("ngapak", "ngpk"):
        return "ngapak"
    elif lang in ("indonesia", "idn", "id"):
        return "indonesia"
    elif lang in ("english", "en", "inggris"):
        return "english"
    return "english"

def detect_project_language(base_dir="."):
    """
    Detect the project structure language.
    Checks .env APP_LANG first if present, then checks for directory existence.
    """
    # 1. Check .env if available
    env_file = os.path.join(base_dir, ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("APP_LANG="):
                        val = line.split("=", 1)[1].strip()
                        return normalize_language(val)
        except Exception:
            pass

    # 2. Check directory existence indicators
    if (os.path.exists(os.path.join(base_dir, "jeroan")) or 
        os.path.exists(os.path.join(base_dir, "dalan")) or 
        os.path.exists(os.path.join(base_dir, "sawangan"))):
        return "ngapak"
    if (os.path.exists(os.path.join(base_dir, "aplikasi")) or 
        os.path.exists(os.path.join(base_dir, "rute")) or 
        os.path.exists(os.path.join(base_dir, "tampilan"))):
        return "indonesia"
    if (os.path.exists(os.path.join(base_dir, "app")) or 
        os.path.exists(os.path.join(base_dir, "routes")) or 
        os.path.exists(os.path.join(base_dir, "resources"))):
        return "english"

    return "english"

def get_path(key, base_dir=".", preferred_lang=None):
    """
    Resolve path for a key ('controllers', 'models', 'views', etc.).
    First checks if the preferred or detected language candidate exists on disk.
    If not, checks other languages. If none exists, falls back to the preferred/detected candidate.
    """
    detected_lang = preferred_lang or detect_project_language(base_dir)
    primary = os.path.join(base_dir, PATHS_CONFIG[detected_lang][key])
    if os.path.exists(primary):
        return primary

    # Check candidates across other languages
    check_order = [detected_lang] + [l for l in ("english", "ngapak", "indonesia") if l != detected_lang]
    for lang in check_order:
        cand = os.path.join(base_dir, PATHS_CONFIG[lang][key])
        if os.path.exists(cand):
            return cand

    return primary

def get_controllers_path(base_dir="."):
    return get_path("controllers", base_dir)

def get_models_path(base_dir="."):
    return get_path("models", base_dir)

def get_middleware_path(base_dir="."):
    return get_path("middleware", base_dir)

def get_jobs_path(base_dir="."):
    return get_path("jobs", base_dir)

def get_migrations_path(base_dir="."):
    return get_path("migrations", base_dir)

def get_seeders_path(base_dir="."):
    return get_path("seeders", base_dir)

def get_routes_path(base_dir="."):
    return get_path("routes", base_dir)

def get_views_path(base_dir="."):
    return get_path("views", base_dir)

def get_public_path(base_dir="."):
    return get_path("public", base_dir)

def get_route_files(base_dir="."):
    """Find active route files (web and api)."""
    routes_dir = get_routes_path(base_dir)
    web_file = os.path.join(routes_dir, "web.ngpk")
    api_file = os.path.join(routes_dir, "api.ngpk")
    
    files = []
    if os.path.exists(web_file):
        files.append(web_file)
    if os.path.exists(api_file):
        files.append(api_file)

    if not files:
        for lang in ("english", "ngapak", "indonesia"):
            r_dir = os.path.join(base_dir, PATHS_CONFIG[lang]["routes"])
            w = os.path.join(r_dir, "web.ngpk")
            a = os.path.join(r_dir, "api.ngpk")
            if os.path.exists(w) and w not in files:
                files.append(w)
            if os.path.exists(a) and a not in files:
                files.append(a)

    return files

def get_seeder_file(base_dir="."):
    """Find active DatabaseSeeder.ngpk file."""
    seeders_dir = get_seeders_path(base_dir)
    candidate = os.path.join(seeders_dir, "DatabaseSeeder.ngpk")
    if os.path.exists(candidate):
        return candidate

    for lang in ("english", "ngapak", "indonesia"):
        cand = os.path.join(base_dir, PATHS_CONFIG[lang]["seeders"], "DatabaseSeeder.ngpk")
        if os.path.exists(cand):
            return cand

    return candidate
