# SQLite Database Driver for Larapak with WAL Mode & Concurrency Retries

import os
import time
import random
import sqlite3
from .driver import DatabaseDriver

class SQLiteDriver(DatabaseDriver):
    def __init__(self, db_path="database.sqlite", timeout=30.0, enable_wal=True):
        self.db_path = db_path
        self.timeout = timeout
        self.enable_wal = enable_wal
        self._conn = None
        self._in_transaction = False

    def connect(self):
        if self._conn is None:
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)

            self._conn = sqlite3.connect(
                self.db_path,
                timeout=self.timeout,
                check_same_thread=False
            )
            self._conn.row_factory = sqlite3.Row

            # Configure WAL mode and busy timeout for high concurrency
            if self.enable_wal:
                try:
                    self._conn.execute("PRAGMA journal_mode = WAL;")
                    self._conn.execute("PRAGMA synchronous = NORMAL;")
                except sqlite3.Error:
                    pass

            try:
                self._conn.execute(f"PRAGMA busy_timeout = {int(self.timeout * 1000)};")
            except sqlite3.Error:
                pass

        return self._conn

    def disconnect(self):
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def _execute_with_retry(self, operation):
        """Execute SQLite operation with retry on database locking."""
        max_retries = 5
        base_delay = 0.05
        for attempt in range(max_retries):
            try:
                return operation()
            except sqlite3.OperationalError as e:
                err_msg = str(e).lower()
                if "locked" in err_msg or "busy" in err_msg:
                    if attempt < max_retries - 1:
                        sleep_time = base_delay * (2 ** attempt) + random.uniform(0, 0.05)
                        time.sleep(sleep_time)
                        continue
                raise

    def execute(self, sql: str, params: list = None):
        params = params or []
        conn = self.connect()

        def op():
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor

        return self._execute_with_retry(op)

    def execute_write(self, sql: str, params: list = None):
        params = params or []
        conn = self.connect()

        def op():
            cursor = conn.cursor()
            cursor.execute(sql, params)
            if not self._in_transaction:
                conn.commit()
            return cursor.lastrowid

        return self._execute_with_retry(op)

    def begin(self):
        self._in_transaction = True
        try:
            self.execute("BEGIN")
        except sqlite3.OperationalError:
            pass

    def commit(self):
        if self._conn:
            try:
                self._conn.commit()
            except Exception:
                pass
        self._in_transaction = False

    def rollback(self):
        if self._conn:
            try:
                self._conn.rollback()
            except Exception:
                pass
        self._in_transaction = False

    @property
    def placeholder(self) -> str:
        return "?"

    def quote_identifier(self, identifier: str) -> str:
        clean = identifier.replace('"', '""')
        return f'"{clean}"'
