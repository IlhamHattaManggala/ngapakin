# Database Package for Larapak

from .driver import DatabaseDriver
from .sqlite_driver import SQLiteDriver
from .mysql_driver import MySQLDriver
from .postgres_driver import PostgresDriver
from .sqlserver_driver import SQLServerDriver
from .manager import DatabaseConnection

# Global default db connection instance
db_manager = DatabaseConnection()

__all__ = [
    "DatabaseDriver",
    "SQLiteDriver",
    "MySQLDriver",
    "PostgresDriver",
    "SQLServerDriver",
    "DatabaseConnection",
    "db_manager",
]
