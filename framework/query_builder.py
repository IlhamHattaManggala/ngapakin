# Fluent SQL Query Builder for Larapak

from .database import db_manager

class QueryBuilder:
    def __init__(self, table=None):
        self._table = table
        self._wheres = []
        self._limit = None
        self._order_by = None

    def tabel(self, table_name):
        self._table = table_name
        return self

    def nek(self, kolom, op, nilai=None):
        if nilai is None:
            # If only two arguments are passed: nek("id", 1) -> id = 1
            nilai = op
            op = "="
        self._wheres.append((kolom, op, nilai))
        return self

    def neng(self, kolom, op, nilai=None):
        return self.nek(kolom, op, nilai)


    def ambil(self, jumlah):
        self._limit = jumlah
        return self

    def urut_karo(self, kolom, arah="ASC"):
        self._order_by = (kolom, arah)
        return self

    def _build_select(self):
        sql = f"SELECT * FROM {self._table}"
        params = []
        
        if self._wheres:
            where_clauses = []
            for col, op, val in self._wheres:
                where_clauses.append(f"{col} {op} ?")
                params.append(val)
            sql += " WHERE " + " AND ".join(where_clauses)
            
        if self._order_by:
            col, direction = self._order_by
            sql += f" ORDER BY {col} {direction}"
            
        if self._limit is not None:
            sql += f" LIMIT {self._limit}"
            
        return sql, params

    def golek(self):
        self._limit = 1
        sql, params = self._build_select()
        cursor = db_manager.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def kabeh(self):
        sql, params = self._build_select()
        cursor = db_manager.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def tambah(self, data):
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        sql = f"INSERT INTO {self._table} ({columns}) VALUES ({placeholders})"
        params = list(data.values())
        return db_manager.execute_write(sql, params)

    def anyari(self, data):
        set_clauses = []
        params = []
        for col, val in data.items():
            set_clauses.append(f"{col} = ?")
            params.append(val)
            
        sql = f"UPDATE {self._table} SET " + ", ".join(set_clauses)
        
        if self._wheres:
            where_clauses = []
            for col, op, val in self._wheres:
                where_clauses.append(f"{col} {op} ?")
                params.append(val)
            sql += " WHERE " + " AND ".join(where_clauses)
            
        return db_manager.execute_write(sql, params)

    def busak(self):
        sql = f"DELETE FROM {self._table}"
        params = []
        
        if self._wheres:
            where_clauses = []
            for col, op, val in self._wheres:
                where_clauses.append(f"{col} {op} ?")
                params.append(val)
            sql += " WHERE " + " AND ".join(where_clauses)
            
        return db_manager.execute_write(sql, params)
