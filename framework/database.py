# Database Connection & Transaction Manager for Larapak

import os
import sqlite3
from .env import env

class DatabaseConnection:
    def __init__(self, db_path="database.sqlite"):
        self.db_path = db_path
        self._conn = None
        self.query_log = []
        log_setting = env("DB_LOG_QUERIES", False)
        if isinstance(log_setting, bool):
            self.log_queries = log_setting
        else:
            self.log_queries = str(log_setting).lower() in ("bener", "true", "1")

    def get_connection(self):
        if self._conn is None:
            # Ensure folder exists
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def execute(self, sql, params=None):
        params = params or []
        self.query_log.append((sql, params))
        if self.log_queries:
            print(f"[SQL] {sql} | Params: {params}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor

    def execute_write(self, sql, params=None):
        params = params or []
        cursor = self.execute(sql, params)
        conn = self.get_connection()
        conn.commit()
        return cursor.lastrowid

    def begin_transaction(self):
        self.execute("BEGIN")

    def commit(self):
        self.execute("COMMIT")

    def rollback(self):
        self.execute("ROLLBACK")

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

# Global db connection
db_manager = DatabaseConnection(env("DB_DATABASE", "database.sqlite"))
