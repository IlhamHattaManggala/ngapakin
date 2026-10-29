# Database Package for Larapak

from .driver import DatabaseDriver
from .sqlite_driver import SQLiteDriver
from .mysql_driver import MySQLDriver
from .postgres_driver import PostgresDriver
from .manager import DatabaseConnection

# Global default db connection instance
db_manager = DatabaseConnection()

__all__ = [
    "DatabaseDriver",
    "SQLiteDriver",
    "MySQLDriver",
    "PostgresDriver",
    "DatabaseConnection",
    "db_manager",
]
