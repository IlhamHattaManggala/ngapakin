# Cookie Helper and SQLite-backed Session Manager for Larapak

import uuid
import time
import json
from framework.database import db_manager

class Session:
    def __init__(self, session_id=None):
        self.session_id = session_id or str(uuid.uuid4())
        self.data = {}
        self.is_started = False

    def start(self):
        if self.is_started:
            return
        
        # Ensure session table exists
        db_manager.execute_write(
            "CREATE TABLE IF NOT EXISTS sessions (id VARCHAR(255) PRIMARY KEY, payload TEXT, last_activity INTEGER)"
        )
        
        # Load session data
        row = db_manager.execute("SELECT payload FROM sessions WHERE id = ?", [self.session_id]).fetchone()
        if row:
            try:
                self.data = json.loads(row["payload"])
            except Exception:
                self.data = {}
        else:
            self.data = {}
            db_manager.execute_write(
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
        db_manager.execute_write(
            "INSERT OR REPLACE INTO sessions (id, payload, last_activity) VALUES (?, ?, ?)",
            [self.session_id, json.dumps(self.data), int(time.time())]
        )

    def save(self):
        self.simpen()
