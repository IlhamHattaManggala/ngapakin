# MySQL Database Driver for Larapak (Optional Dependency)

from .driver import DatabaseDriver

class MySQLDriver(DatabaseDriver):
    def __init__(self, host="127.0.0.1", port=3306, database="", user="root", password="", charset="utf8mb4"):
        self.host = host
        self.port = int(port or 3306)
        self.database = database
        self.user = user
        self.password = password
        self.charset = charset
        self._conn = None

    def _get_driver_module(self):
        try:
            import pymysql
            import pymysql.cursors
            return pymysql
        except ImportError:
            raise ImportError(
                "Driver MySQL membutuhkan paket 'pymysql'. "
                "Silakan pasang dengan menjalankan: pip install pymysql "
                "atau: pip install 'ngapakin[mysql]'"
            )

    def connect(self):
        if self._conn is None:
            pymysql = self._get_driver_module()
            try:
                self._conn = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    charset=self.charset,
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=False
                )
            except Exception as e:
                # Sanitized error message without leaking credentials
                raise ConnectionError(f"Gagal terhubung ke MySQL ({self.host}:{self.port}/{self.database}): {str(e)}")
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
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid

    def begin(self):
        conn = self.connect()
        conn.begin()

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
        clean = identifier.replace('`', '``')
        return f"`{clean}`"
