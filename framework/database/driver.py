# Database Driver Base Interface for Larapak

from abc import ABC, abstractmethod

class DatabaseDriver(ABC):
    """Abstract Base Class for Larapak Database Drivers."""

    @abstractmethod
    def connect(self):
        """Establish connection to database."""
        pass

    @abstractmethod
    def disconnect(self):
        """Close connection to database."""
        pass

    @abstractmethod
    def execute(self, sql: str, params: list = None):
        """Execute a query and return a cursor or result set."""
        pass

    @abstractmethod
    def execute_write(self, sql: str, params: list = None):
        """Execute an INSERT/UPDATE/DELETE query and return last insert ID or affected rows."""
        pass

    @abstractmethod
    def begin(self):
        """Begin transaction."""
        pass

    @abstractmethod
    def commit(self):
        """Commit transaction."""
        pass

    @abstractmethod
    def rollback(self):
        """Rollback transaction."""
        pass

    @property
    @abstractmethod
    def placeholder(self) -> str:
        """Return parameter placeholder token (?, %s, etc.)."""
        pass

    @abstractmethod
    def quote_identifier(self, identifier: str) -> str:
        """Quote a table or column name securely."""
        pass
