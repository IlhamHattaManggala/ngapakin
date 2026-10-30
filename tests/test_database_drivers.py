import os
import unittest
from framework.database.driver import DatabaseDriver
from framework.database.sqlite_driver import SQLiteDriver
from framework.database.mysql_driver import MySQLDriver
from framework.database.postgres_driver import PostgresDriver
from framework.database.sqlserver_driver import SQLServerDriver
from framework.database.manager import DatabaseConnection

class TestDatabaseDrivers(unittest.TestCase):
    def setUp(self):
        self.sqlite_test_db = "test_driver_sqlite.sqlite"
        if os.path.exists(self.sqlite_test_db):
            os.remove(self.sqlite_test_db)

    def tearDown(self):
        if hasattr(self, "driver") and self.driver:
            self.driver.disconnect()
        if os.path.exists(self.sqlite_test_db):
            try:
                os.remove(self.sqlite_test_db)
            except OSError:
                pass

    def test_sqlite_driver_crud_and_transaction(self):
        self.driver = SQLiteDriver(db_path=self.sqlite_test_db)
        driver = self.driver
        self.assertEqual(driver.placeholder, "?")
        self.assertEqual(driver.quote_identifier("users"), '"users"')

        # Create table
        driver.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(100))")
        
        # Insert with transaction
        driver.begin()
        row_id = driver.execute_write("INSERT INTO users (name) VALUES (?)", ["Ilham"])
        driver.commit()
        self.assertEqual(row_id, 1)

        # Select
        cursor = driver.execute("SELECT * FROM users WHERE id = ?", [1])
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["name"], "Ilham")

        # Rollback test
        driver.begin()
        driver.execute_write("INSERT INTO users (name) VALUES (?)", ["RollbackName"])
        driver.rollback()
        
        cursor_check = driver.execute("SELECT * FROM users WHERE name = ?", ["RollbackName"])
        self.assertIsNone(cursor_check.fetchone())

        driver.disconnect()

    def test_mysql_driver_interface_and_placeholders(self):
        mysql = MySQLDriver(host="127.0.0.1", port=3306, database="testdb", user="app", password="super_secret_password")
        self.assertEqual(mysql.placeholder, "%s")
        self.assertEqual(mysql.quote_identifier("users"), "`users`")

        # If pymysql is not installed, it should raise informative ImportError instructing pip install
        try:
            import pymysql
            pymysql_installed = True
        except ImportError:
            pymysql_installed = False

        if not pymysql_installed:
            with self.assertRaises(ImportError) as ctx:
                mysql.connect()
            self.assertIn("pymysql", str(ctx.exception))
        else:
            # If pymysql is installed, attempting to connect to offline local host raises ConnectionError without leaking password
            with self.assertRaises(ConnectionError) as ctx:
                mysql.connect()
            self.assertNotIn("super_secret_password", str(ctx.exception))

    def test_postgres_driver_interface_and_placeholders(self):
        pgsql = PostgresDriver(host="127.0.0.1", port=5432, database="testdb", user="postgres", password="super_secret_postgres_password")
        self.assertEqual(pgsql.placeholder, "%s")
        self.assertEqual(pgsql.quote_identifier("articles"), '"articles"')

        # If psycopg2 is not installed, it should raise informative ImportError instructing pip install
        try:
            import psycopg2
            psycopg2_installed = True
        except ImportError:
            psycopg2_installed = False

        if not psycopg2_installed:
            with self.assertRaises(ImportError) as ctx:
                pgsql.connect()
            self.assertIn("psycopg2", str(ctx.exception))
        else:
            # If psycopg2 is installed, attempting to connect to offline local host raises ConnectionError without leaking password
            with self.assertRaises(ConnectionError) as ctx:
                pgsql.connect()
            self.assertNotIn("super_secret_postgres_password", str(ctx.exception))

    def test_sqlserver_driver_interface_and_placeholders(self):
        mssql = SQLServerDriver(host="127.0.0.1", port=1433, database="testdb", user="sa", password="super_secret_mssql_password")
        self.assertEqual(mssql.placeholder, "%s")
        self.assertEqual(mssql.quote_identifier("products"), "[products]")
        self.assertEqual(mssql.quote_identifier("user]name"), "[user]]name]")

        # Check pymssql / pyodbc presence
        try:
            import pymssql
            mssql_installed = True
        except ImportError:
            try:
                import pyodbc
                mssql_installed = True
            except ImportError:
                mssql_installed = False

        if not mssql_installed:
            with self.assertRaises(ImportError) as ctx:
                mssql.connect()
            self.assertIn("SQL Server", str(ctx.exception))
        else:
            with self.assertRaises(ConnectionError) as ctx:
                mssql.connect()
            self.assertNotIn("super_secret_mssql_password", str(ctx.exception))

    def test_database_manager_driver_switching(self):
        # Default SQLite
        mgr = DatabaseConnection(connection_name="sqlite", database=self.sqlite_test_db)
        self.assertIsInstance(mgr.driver, SQLiteDriver)
        self.assertEqual(mgr.placeholder, "?")

        # MySQL connection initialization
        mgr_mysql = DatabaseConnection(connection_name="mysql", host="localhost", database="mydb")
        self.assertIsInstance(mgr_mysql.driver, MySQLDriver)
        self.assertEqual(mgr_mysql.placeholder, "%s")

        # PostgreSQL connection initialization
        mgr_pgsql = DatabaseConnection(connection_name="pgsql", host="localhost", database="mydb")
        self.assertIsInstance(mgr_pgsql.driver, PostgresDriver)
        self.assertEqual(mgr_pgsql.placeholder, "%s")

        # SQL Server connection initialization (sqlsrv / mssql)
        mgr_sqlsrv = DatabaseConnection(connection_name="sqlsrv", host="localhost", database="mydb")
        self.assertIsInstance(mgr_sqlsrv.driver, SQLServerDriver)
        self.assertEqual(mgr_sqlsrv.placeholder, "%s")

        # Unsupported driver
        with self.assertRaises(ValueError):
            DatabaseConnection(connection_name="oracle")


if __name__ == "__main__":
    unittest.main()
