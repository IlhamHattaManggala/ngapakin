# Cache Manager for Larapak
# Supports SQLite (default) and Redis (optional)

import time
import json
from framework.env import env
from framework.database import db_manager, DatabaseConnection

class RedisCacheDriver:
    """Redis-backed Cache Driver."""
    def __init__(self, host="127.0.0.1", port=6379, password=None, db=0):
        try:
            import redis
            self.client = redis.Redis(
                host=host,
                port=int(port or 6379),
                password=password or None,
                db=int(db or 0),
                decode_responses=True
            )
            # Ping to verify connection
            self.client.ping()
        except ImportError:
            raise ImportError(
                "Driver Cache Redis membutuhkan paket 'redis'. "
                "Silakan pasang dengan menjalankan: pip install redis "
                "atau: pip install 'ngapakin[redis]'"
            )
        except Exception as e:
            raise ConnectionError(f"Gagal terhubung ke Redis Cache: {str(e)}")

    def set(self, key, value, seconds=None):
        serialized = json.dumps(value)
        if seconds is not None:
            return bool(self.client.setex(key, int(seconds), serialized))
        return bool(self.client.set(key, serialized))

    def get(self, key, default=None):
        val = self.client.get(key)
        if val is None:
            return default
        try:
            return json.loads(val)
        except Exception:
            return default

    def forget(self, key):
        return bool(self.client.delete(key))

    def clear(self):
        return bool(self.client.flushdb())

    def has(self, key):
        return bool(self.client.exists(key))


class SQLiteCacheDriver:
    """SQLite-backed Cache Driver with dedicated connection and WAL mode."""
    def __init__(self, db=None):
        if db is not None:
            self.db = db
        else:
            custom_db = env("CACHE_DATABASE")
            if custom_db:
                self.db = DatabaseConnection(connection_name="sqlite", database=custom_db)
            else:
                self.db = db_manager
        self._ensure_table()

    def _ensure_table(self):
        self.db.execute_write(
            "CREATE TABLE IF NOT EXISTS cache (key VARCHAR(255) PRIMARY KEY, value TEXT, expiration INTEGER)"
        )

    def set(self, key, value, seconds=None):
        expiration = None
        if seconds is not None:
            expiration = int(time.time() + seconds)
        serialized = json.dumps(value)
        self.db.execute_write(
            "INSERT OR REPLACE INTO cache (key, value, expiration) VALUES (?, ?, ?)",
            [key, serialized, expiration]
        )
        return True

    def get(self, key, default=None):
        row = self.db.execute("SELECT value, expiration FROM cache WHERE key = ?", [key]).fetchone()
        if not row:
            return default
        expiration = row["expiration"]
        if expiration is not None and expiration <= time.time():
            self.forget(key)
            return default
        try:
            return json.loads(row["value"])
        except Exception:
            return default

    def forget(self, key):
        self.db.execute_write("DELETE FROM cache WHERE key = ?", [key])
        return True

    def clear(self):
        self.db.execute_write("DELETE FROM cache")
        return True

    def has(self, key):
        return self.get(key, None) is not None


class Cache:
    """Unified Cache Manager for Larapak."""
    def __init__(self, driver=None, db=None):
        driver_name = (driver or env("CACHE_DRIVER", "sqlite")).lower()
        if driver_name == "redis":
            self.driver = RedisCacheDriver(
                host=env("REDIS_HOST", "127.0.0.1"),
                port=env("REDIS_PORT", 6379),
                password=env("REDIS_PASSWORD"),
                db=env("REDIS_CACHE_DB", 0)
            )
        else:
            self.driver = SQLiteCacheDriver(db=db)

    def pasang(self, key, value, seconds=None):
        return self.driver.set(key, value, seconds)

    def set(self, key, value, seconds=None):
        return self.pasang(key, value, seconds)

    def put(self, key, value, seconds=None):
        return self.pasang(key, value, seconds)

    def entuk(self, key, default=None):
        return self.driver.get(key, default)

    def get(self, key, default=None):
        return self.entuk(key, default)

    def lalekna(self, key):
        return self.driver.forget(key)

    def forget(self, key):
        return self.lalekna(key)

    def remove(self, key):
        return self.lalekna(key)

    def resiki(self):
        return self.driver.clear()

    def clear(self):
        return self.resiki()

    def flush(self):
        return self.resiki()

    def nduwe(self, key):
        return self.driver.has(key)

    def has(self, key):
        return self.nduwe(key)
