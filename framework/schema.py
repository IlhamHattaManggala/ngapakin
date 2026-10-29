# Schema Migration Builder for Larapak
# Multi-database support (SQLite, MySQL, PostgreSQL)

from .database import db_manager

class TableBuilder:
    def __init__(self, table_name, driver_type="sqlite"):
        self.table_name = table_name
        self.driver_type = driver_type or "sqlite"
        self.columns = []

    def id(self):
        if self.driver_type in ("mysql",):
            self.columns.append("id INT AUTO_INCREMENT PRIMARY KEY")
        elif self.driver_type in ("pgsql", "postgres", "postgresql"):
            self.columns.append("id SERIAL PRIMARY KEY")
        else:
            self.columns.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
        return self

    def string(self, name, length=255):
        quoted = db_manager.quote_identifier(name)
        self.columns.append(f"{quoted} VARCHAR({int(length)})")
        return self

    def integer(self, name):
        quoted = db_manager.quote_identifier(name)
        self.columns.append(f"{quoted} INTEGER")
        return self

    def text(self, name):
        quoted = db_manager.quote_identifier(name)
        self.columns.append(f"{quoted} TEXT")
        return self

    def timestamps(self):
        created_col = db_manager.quote_identifier("created_at")
        updated_col = db_manager.quote_identifier("updated_at")
        if self.driver_type in ("pgsql", "postgres", "postgresql"):
            self.columns.append(f"{created_col} TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            self.columns.append(f"{updated_col} TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        else:
            self.columns.append(f"{created_col} DATETIME DEFAULT CURRENT_TIMESTAMP")
            self.columns.append(f"{updated_col} DATETIME DEFAULT CURRENT_TIMESTAMP")
        return self

class SchemaBuilder:
    def gawe(self, table_name, callback):
        driver_type = getattr(db_manager, "connection_name", "sqlite")
        builder = TableBuilder(table_name, driver_type=driver_type)
        
        # Execute the VM function callback if it's a Ngapak function, otherwise call directly
        from framework.model import Model
        if Model.active_vm and hasattr(callback, 'chunk'):
            Model.active_vm.execute_callable(callback, [builder])
        else:
            callback(builder)
            
        columns_sql = ", ".join(builder.columns)
        quoted_table = db_manager.quote_identifier(table_name)
        sql = f"CREATE TABLE IF NOT EXISTS {quoted_table} ({columns_sql})"
        db_manager.execute_write(sql)

    def buang(self, table_name):
        quoted_table = db_manager.quote_identifier(table_name)
        sql = f"DROP TABLE IF EXISTS {quoted_table}"
        db_manager.execute_write(sql)

schema = SchemaBuilder()
