# SQL Server (MSSQL) Database Driver for Larapak
# Supports pymssql (default) and pyodbc (ODBC fallback)

import importlib
from .driver import DatabaseDriver

class DictCursorWrapper:
    """Wrapper around raw database cursor to consistently return rows as dictionaries."""
    def __init__(self, cursor):
        self._cursor = cursor

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        if isinstance(row, dict):
            return row
        columns = [col[0] for col in self._cursor.description]
        return dict(zip(columns, row))

    def fetchall(self):
        rows = self._cursor.fetchall()
        if not rows:
            return []
        if isinstance(rows[0], dict):
            return rows
        columns = [col[0] for col in self._cursor.description]
        return [dict(zip(columns, r)) for r in rows]

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class SQLServerDriver(DatabaseDriver):
    def __init__(self, host="127.0.0.1", port=1433, database="", user="sa", password="", driver=None):
        self.host = host
        self.port = int(port or 1433)
        self.database = database
        self.user = user
        self.password = password
        self.driver_name = driver or "ODBC Driver 18 for SQL Server"
        self._conn = None
        self._backend = None  # 'pymssql' or 'pyodbc'

    def _get_driver_module(self):
        try:
            module = importlib.import_module("pymssql")
            self._backend = "pymssql"
            return module
        except ImportError:
            try:
                module = importlib.import_module("pyodbc")
                self._backend = "pyodbc"
                return module
            except ImportError:
                raise ImportError(
                    "Driver SQL Server membutuhkan paket 'pymssql' atau 'pyodbc'. "
                    "Silakan pasang dengan menjalankan: pip install pymssql "
                    "atau: pip install 'ngapakin[mssql]'"
                )

    def connect(self):
        if self._conn is None:
            module = self._get_driver_module()
            try:
                if self._backend == "pymssql":
                    self._conn = module.connect(
                        server=self.host,
                        port=self.port,
                        user=self.user,
                        password=self.password,
                        database=self.database,
                        as_dict=True,
                        autocommit=False
                    )
                else:  # pyodbc
                    conn_str = (
                        f"DRIVER={{{self.driver_name}}};"
                        f"SERVER={self.host},{self.port};"
                        f"DATABASE={self.database};"
                        f"UID={self.user};"
                        f"PWD={self.password};"
                        "TrustServerCertificate=yes;"
                    )
                    self._conn = module.connect(conn_str, autocommit=False)
            except Exception as e:
                # Sanitized error message without leaking credentials
                raise ConnectionError(
                    f"Gagal terhubung ke SQL Server ({self.host}:{self.port}/{self.database}): {str(e)}"
                )
        return self._conn

    def disconnect(self):
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def execute(self, sql: str, params: list = None):
        params = params or []
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return DictCursorWrapper(cursor)

    def execute_write(self, sql: str, params: list = None):
        params = params or []
        conn = self.connect()
        cursor = conn.cursor()

        clean_sql = sql.strip()
        is_insert = clean_sql.upper().startswith("INSERT")

        if is_insert and "OUTPUT" not in clean_sql.upper():
            # Append SCOPE_IDENTITY to retrieve the newly generated identity ID
            batch_sql = f"{clean_sql}; SELECT SCOPE_IDENTITY() AS id;"
            cursor.execute(batch_sql, params)
            last_id = None
            try:
                # Some drivers return multiple result sets, advance if needed
                row = cursor.fetchone()
                if row:
                    last_id = row[0] if not isinstance(row, dict) else row.get("id")
            except Exception:
                pass
            conn.commit()
            return last_id
        else:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount

    def begin(self):
        # pyodbc and pymssql manage transactions automatically on execute
        pass

    def commit(self):
        if self._conn:
            self._conn.commit()

    def rollback(self):
        if self._conn:
            self._conn.rollback()

    @property
    def placeholder(self) -> str:
        # pymssql uses %s, pyodbc uses ?
        if self._backend is None:
            try:
                self._get_driver_module()
            except ImportError:
                self._backend = "pymssql"
        return "%s" if self._backend == "pymssql" else "?"

    def quote_identifier(self, identifier: str) -> str:
        clean = identifier.replace("]", "]]")
        return f"[{clean}]"
