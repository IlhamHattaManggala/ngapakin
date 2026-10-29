# PostgreSQL Database Driver for Larapak (Optional Dependency)

from .driver import DatabaseDriver

class PostgresDriver(DatabaseDriver):
    def __init__(self, host="127.0.0.1", port=5432, database="", user="postgres", password="", sslmode="prefer"):
        self.host = host
        self.port = int(port or 5432)
        self.database = database
        self.user = user
        self.password = password
        self.sslmode = sslmode
        self._conn = None

    def _get_driver_module(self):
        try:
            import psycopg2
            import psycopg2.extras
            return psycopg2
        except ImportError:
            raise ImportError(
                "Driver PostgreSQL membutuhkan paket 'psycopg2'. "
                "Silakan pasang dengan menjalankan: pip install psycopg2-binary "
                "atau: pip install 'ngapakin[postgres]'"
            )

    def connect(self):
        if self._conn is None:
            psycopg2 = self._get_driver_module()
            import psycopg2.extras
            try:
                self._conn = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    dbname=self.database,
                    sslmode=self.sslmode,
                    cursor_factory=psycopg2.extras.RealDictCursor
                )
            except Exception as e:
                # Sanitized error message without leaking credentials
                raise ConnectionError(f"Gagal terhubung ke PostgreSQL ({self.host}:{self.port}/{self.database}): {str(e)}")
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
        return cursor

    def execute_write(self, sql: str, params: list = None):
        params = params or []
        conn = self.connect()
        cursor = conn.cursor()
        
        # If INSERT statement doesn't have RETURNING, append RETURNING id for last insert id retrieval if supported
        clean_sql = sql.strip()
        if clean_sql.upper().startswith("INSERT") and "RETURNING" not in clean_sql.upper():
            cursor.execute(f"{clean_sql} RETURNING id", params)
            last_id = cursor.fetchone()
            conn.commit()
            return last_id["id"] if last_id else None
        else:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount

    def begin(self):
        # psycopg2 starts transaction automatically on first query
        pass

    def commit(self):
        if self._conn:
            self._conn.commit()

    def rollback(self):
        if self._conn:
            self._conn.rollback()

    @property
    def placeholder(self) -> str:
        return "%s"

    def quote_identifier(self, identifier: str) -> str:
        clean = identifier.replace('"', '""')
        return f'"{clean}"'
