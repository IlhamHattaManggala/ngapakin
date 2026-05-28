# Cache Manager for Larapak

import time
import json
from framework.database import db_manager

class Cache:
    def __init__(self):
        self._ensure_table()

    def _ensure_table(self):
        db_manager.execute_write(
            "CREATE TABLE IF NOT EXISTS cache (key VARCHAR(255) PRIMARY KEY, value TEXT, expiration INTEGER)"
        )

    def pasang(self, key, value, seconds=None):
        expiration = None
        if seconds is not None:
            expiration = int(time.time() + seconds)
        
        serialized = json.dumps(value)
        db_manager.execute_write(
            "INSERT OR REPLACE INTO cache (key, value, expiration) VALUES (?, ?, ?)",
            [key, serialized, expiration]
        )
        return True

    def set(self, key, value, seconds=None):
        return self.pasang(key, value, seconds)

    def entuk(self, key, default=None):
        row = db_manager.execute("SELECT value, expiration FROM cache WHERE key = ?", [key]).fetchone()
        if not row:
            return default
            
        expiration = row["expiration"]
        if expiration is not None and expiration < int(time.time()):
            # Expired, remove it
            self.lalekna(key)
            return default
            
        try:
            return json.loads(row["value"])
        except Exception:
            return default

    def get(self, key, default=None):
        return self.entuk(key, default)

    def lalekna(self, key):
        db_manager.execute_write("DELETE FROM cache WHERE key = ?", [key])
        return True

    def forget(self, key):
        return self.lalekna(key)

    def remove(self, key):
        return self.lalekna(key)

    def resiki(self):
        db_manager.execute_write("DELETE FROM cache")
        return True

    def clear(self):
        return self.resiki()

    def nduwe(self, key):
        val = self.entuk(key, None)
        return val is not None

    def has(self, key):
        return self.nduwe(key)
