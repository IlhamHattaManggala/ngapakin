# Schema Migration Builder for Larapak

from .database import db_manager

class TableBuilder:
    def __init__(self, table_name):
        self.table_name = table_name
        self.columns = []

    def id(self):
        self.columns.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
        return self

    def string(self, name):
        self.columns.append(f"{name} VARCHAR(255)")
        return self

    def integer(self, name):
        self.columns.append(f"{name} INTEGER")
        return self

    def text(self, name):
        self.columns.append(f"{name} TEXT")
        return self

    def timestamps(self):
        # Using SQLite compatible format
        self.columns.append("created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        self.columns.append("updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        return self

class SchemaBuilder:
    def gawe(self, table_name, callback):
        builder = TableBuilder(table_name)
        
        # Execute the VM function callback
        from framework.model import Model
        if Model.active_vm and (hasattr(callback, 'chunk') or callable(callback)):
            Model.active_vm.execute_callable(callback, [builder])
        else:
            # Fallback
            callback(builder)
            
        columns_sql = ", ".join(builder.columns)
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
        db_manager.execute_write(sql)

    def buang(self, table_name):
        sql = f"DROP TABLE IF EXISTS {table_name}"
        db_manager.execute_write(sql)

schema = SchemaBuilder()
