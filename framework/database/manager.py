# Database Connection & Transaction Manager for Larapak

import os
from .driver import DatabaseDriver
from .sqlite_driver import SQLiteDriver
from .mysql_driver import MySQLDriver
from .postgres_driver import PostgresDriver
from .sqlserver_driver import SQLServerDriver
from framework.env import env

class DatabaseConnection:
    def __init__(self, connection_name=None, **options):
        self.connection_name = connection_name or env("DB_CONNECTION", "sqlite").lower()
        self.options = options
        self.query_log = []
        self._driver = None
        
        log_setting = env("DB_DEBUG", env("DB_LOG_QUERIES", False))
        if isinstance(log_setting, bool):
            self.log_queries = log_setting
        else:
            self.log_queries = str(log_setting).lower() in ("bener", "true", "1")

        self._init_driver()

    def _init_driver(self):
        conn = self.connection_name
        if conn in ("sqlite", "sqlite3"):
            db_path = self.options.get("database") or env("DB_DATABASE", "database.sqlite")
            timeout = float(self.options.get("timeout") or env("DB_TIMEOUT", 30.0))
            enable_wal = env("DB_WAL", True)
            self._driver = SQLiteDriver(db_path=db_path, timeout=timeout, enable_wal=enable_wal)
        elif conn == "mysql":
            self._driver = MySQLDriver(
                host=self.options.get("host") or env("DB_HOST", "127.0.0.1"),
                port=self.options.get("port") or env("DB_PORT", 3306),
                database=self.options.get("database") or env("DB_DATABASE", ""),
                user=self.options.get("username") or env("DB_USERNAME", "root"),
                password=self.options.get("password") or env("DB_PASSWORD", ""),
                charset=self.options.get("charset") or env("DB_CHARSET", "utf8mb4")
            )
        elif conn in ("pgsql", "postgres", "postgresql"):
            self._driver = PostgresDriver(
                host=self.options.get("host") or env("DB_HOST", "127.0.0.1"),
                port=self.options.get("port") or env("DB_PORT", 5432),
                database=self.options.get("database") or env("DB_DATABASE", ""),
                user=self.options.get("username") or env("DB_USERNAME", "postgres"),
                password=self.options.get("password") or env("DB_PASSWORD", ""),
                sslmode=self.options.get("sslmode") or env("DB_SSLMODE", "prefer")
            )
        elif conn in ("mssql", "sqlserver", "sqlsrv"):
            self._driver = SQLServerDriver(
                host=self.options.get("host") or env("DB_HOST", "127.0.0.1"),
                port=self.options.get("port") or env("DB_PORT", 1433),
                database=self.options.get("database") or env("DB_DATABASE", ""),
                user=self.options.get("username") or env("DB_USERNAME", "sa"),
                password=self.options.get("password") or env("DB_PASSWORD", ""),
                driver=self.options.get("driver") or env("DB_ODBC_DRIVER", None)
            )
        else:
            raise ValueError(f"Database connection '{conn}' tidak didukung. Pilihan: sqlite, mysql, pgsql, mssql.")

    @property
    def driver(self) -> DatabaseDriver:
        if self._driver is None:
            self._init_driver()
        return self._driver

    @property
    def db_path(self):
        """Getter for SQLite database path for backward compatibility."""
        if isinstance(self._driver, SQLiteDriver):
            return self._driver.db_path
        return None

    @db_path.setter
    def db_path(self, new_path):
        """Setter for SQLite database path for backward compatibility with tests."""
        if isinstance(self._driver, SQLiteDriver):
            self._driver.disconnect()
            self._driver.db_path = new_path
        else:
            self.connection_name = "sqlite"
            self._driver = SQLiteDriver(db_path=new_path)

    @property
    def placeholder(self) -> str:
        return self.driver.placeholder

    def quote_identifier(self, identifier: str) -> str:
        return self.driver.quote_identifier(identifier)

    def get_connection(self):
        """Retrieve active connection handle for backward compatibility."""
        return self.driver.connect()

    def execute(self, sql: str, params: list = None):
        params = params or []
        self.query_log.append((sql, params))
        if self.log_queries:
            print(f"[SQL] {sql} | Params: {params}")
        return self.driver.execute(sql, params)

    def execute_write(self, sql: str, params: list = None):
        params = params or []
        self.query_log.append((sql, params))
        if self.log_queries:
            print(f"[SQL] {sql} | Params: {params}")
        return self.driver.execute_write(sql, params)

    def begin_transaction(self):
        self.driver.begin()

    def commit(self):
        self.driver.commit()

    def rollback(self):
        self.driver.rollback()

    def drop_all_tables(self):
        """Drop all user tables in the connected database cleanly."""
        driver_type = self.connection_name
        if driver_type in ("sqlite", "sqlite3"):
            cursor = self.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row["name"] for row in cursor.fetchall()]
            self.execute_write("PRAGMA foreign_keys = OFF")
            for t in tables:
                quoted = self.quote_identifier(t)
                self.execute_write(f"DROP TABLE IF EXISTS {quoted}")
            self.execute_write("PRAGMA foreign_keys = ON")
            return tables
        elif driver_type == "mysql":
            cursor = self.execute("SHOW TABLES")
            tables = [list(row.values())[0] for row in cursor.fetchall()]
            self.execute_write("SET FOREIGN_KEY_CHECKS = 0")
            for t in tables:
                quoted = self.quote_identifier(t)
                self.execute_write(f"DROP TABLE IF EXISTS {quoted}")
            self.execute_write("SET FOREIGN_KEY_CHECKS = 1")
            return tables
        elif driver_type in ("pgsql", "postgres", "postgresql"):
            cursor = self.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            tables = [row["tablename"] for row in cursor.fetchall()]
            for t in tables:
                quoted = self.quote_identifier(t)
                self.execute_write(f"DROP TABLE IF EXISTS {quoted} CASCADE")
            return tables
        elif driver_type in ("mssql", "sqlserver", "sqlsrv"):
            cursor = self.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            tables = [row["TABLE_NAME"] if "TABLE_NAME" in row else list(row.values())[0] for row in cursor.fetchall()]
            for t in tables:
                quoted = self.quote_identifier(t)
                self.execute_write(f"ALTER TABLE {quoted} NOCHECK CONSTRAINT ALL")
            for t in tables:
                quoted = self.quote_identifier(t)
                self.execute_write(f"DROP TABLE IF EXISTS {quoted}")
            return tables
        return []

    def close(self):
        if self._driver:
            self._driver.disconnect()

    @property
    def query_count(self) -> int:
        return len(self.query_log)

    def reset_query_log(self):
        self.query_log = []
