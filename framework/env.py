# Environment Configuration Loader for Larapak (.env)

import os

_ENV_LOADED = False

def load_env(env_file=".env"):
    """Loads key-value pairs from .env file into os.environ."""
    global _ENV_LOADED
    if not os.path.exists(env_file):
        return
        
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                # Strip wrapping single or double quotes
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                # Only set if not already overridden by system environment
                if key not in os.environ:
                    os.environ[key] = val
                    
    _ENV_LOADED = True

def env(key, default=None):
    """Retrieves an environment variable with optional fallback default."""
    if not _ENV_LOADED:
        load_env()
    val = os.environ.get(key, default)
    # Type conversions for standard boolean and null strings
    if val == "bener" or val == "true" or val == "True":
        return True
    if val == "salah" or val == "false" or val == "False":
        return False
    if val == "kosong" or val == "null" or val == "None":
        return None
    return val
