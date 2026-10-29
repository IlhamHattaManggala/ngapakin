# Cookie Helper and Session Manager for Larapak
# Supports dedicated SQLite storage with WAL mode & busy timeout

import uuid
import time
import json
from framework.env import env
from framework.database import db_manager, DatabaseConnection

class Session:
    def __init__(self, session_id=None, db=None):
        self.session_id = session_id or str(uuid.uuid4())
        self.data = {}
        self.is_started = False
        
        if db is not None:
            self.db = db
        else:
            custom_db = env("SESSION_DATABASE")
            if custom_db:
                self.db = DatabaseConnection(connection_name="sqlite", database=custom_db)
            else:
                self.db = db_manager

    def start(self):
        if self.is_started:
            return
        
        # Ensure session table exists
        self.db.execute_write(
            "CREATE TABLE IF NOT EXISTS sessions (id VARCHAR(255) PRIMARY KEY, payload TEXT, last_activity INTEGER)"
        )
        
        # Load session data
        row = self.db.execute("SELECT payload FROM sessions WHERE id = ?", [self.session_id]).fetchone()
        if row:
            try:
                self.data = json.loads(row["payload"])
            except Exception:
                self.data = {}
        else:
            self.data = {}
            self.db.execute_write(
                "INSERT OR REPLACE INTO sessions (id, payload, last_activity) VALUES (?, ?, ?)",
                [self.session_id, json.dumps(self.data), int(time.time())]
            )
        self.is_started = True

    def entuk(self, key, default=None):
        self.start()
        return self.data.get(key, default)

    def get(self, key, default=None):
        return self.entuk(key, default)

    def pasang(self, key, value):
        self.start()
        self.data[key] = value

    def set(self, key, value):
        self.pasang(key, value)

    def put(self, key, value):
        self.pasang(key, value)

    def lalekna(self, key):
        self.start()
        if key in self.data:
            del self.data[key]

    def forget(self, key):
        self.lalekna(key)

    def remove(self, key):
        self.lalekna(key)

    def resiki(self):
        self.start()
        self.data = {}

    def clear(self):
        self.resiki()

    def flush(self):
        self.resiki()

    def simpen(self):
        if not self.is_started:
            return
        self.db.execute_write(
            "INSERT OR REPLACE INTO sessions (id, payload, last_activity) VALUES (?, ?, ?)",
            [self.session_id, json.dumps(self.data), int(time.time())]
        )

    def save(self):
        self.simpen()

    def cleanup_expired(self, max_age_seconds=86400):
        """Remove sessions inactive longer than max_age_seconds (default 24h)."""
        cutoff = int(time.time() - max_age_seconds)
        self.db.execute_write("DELETE FROM sessions WHERE last_activity < ?", [cutoff])
