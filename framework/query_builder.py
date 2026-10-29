# Fluent SQL Query Builder for Larapak
# Multi-database support (SQLite, MySQL, PostgreSQL)

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
        # Normalize comparison operator for cross-database standard SQL
        if op == "==":
            op = "="
        self._wheres.append((kolom, op, nilai, "single"))
        return self

    def neng(self, kolom, op, nilai=None):
        return self.nek(kolom, op, nilai)

    def where_in(self, kolom, nilai_list):
        """Add WHERE kolom IN (...) clause."""
        values = list(nilai_list) if nilai_list is not None else []
        self._wheres.append((kolom, "IN", values, "in"))
        return self

    def neng_kumpulan(self, kolom, nilai_list):
        return self.where_in(kolom, nilai_list)

    def ambil(self, jumlah):
        self._limit = jumlah
        return self

    def limit(self, jumlah):
        return self.ambil(jumlah)

    def urut_karo(self, kolom, arah="ASC"):
        self._order_by = (kolom, arah)
        return self

    def order_by(self, kolom, arah="ASC"):
        return self.urut_karo(kolom, arah)

    def _build_select(self):
        ph = db_manager.placeholder
        quoted_table = db_manager.quote_identifier(self._table)
        sql = f"SELECT * FROM {quoted_table}"
        params = []

        if self._wheres:
            where_clauses = []
            for item in self._wheres:
                col, op, val, wtype = item
                quoted_col = db_manager.quote_identifier(col)
                if wtype == "in":
                    if not val:
                        # Empty IN list should evaluate to false
                        where_clauses.append("1 = 0")
                    else:
                        in_placeholders = ", ".join([ph] * len(val))
                        where_clauses.append(f"{quoted_col} IN ({in_placeholders})")
                        params.extend(val)
                else:
                    where_clauses.append(f"{quoted_col} {op} {ph}")
                    params.append(val)
            sql += " WHERE " + " AND ".join(where_clauses)

        if self._order_by:
            col, direction = self._order_by
            quoted_col = db_manager.quote_identifier(col)
            dir_clean = "DESC" if str(direction).upper() == "DESC" else "ASC"
            sql += f" ORDER BY {quoted_col} {dir_clean}"

        if self._limit is not None:
            sql += f" LIMIT {int(self._limit)}"

        return sql, params

    def golek(self):
        self._limit = 1
        sql, params = self._build_select()
        cursor = db_manager.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def first(self):
        return self.golek()

    def kabeh(self):
        sql, params = self._build_select()
        cursor = db_manager.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def all(self):
        return self.kabeh()

    def count(self):
        ph = db_manager.placeholder
        quoted_table = db_manager.quote_identifier(self._table)
        sql = f"SELECT COUNT(*) as count FROM {quoted_table}"
        params = []
        if self._wheres:
            where_clauses = []
            for item in self._wheres:
                col, op, val, wtype = item
                quoted_col = db_manager.quote_identifier(col)
                if wtype == "in":
                    if not val:
                        where_clauses.append("1 = 0")
                    else:
                        in_placeholders = ", ".join([ph] * len(val))
                        where_clauses.append(f"{quoted_col} IN ({in_placeholders})")
                        params.extend(val)
                else:
                    where_clauses.append(f"{quoted_col} {op} {ph}")
                    params.append(val)
            sql += " WHERE " + " AND ".join(where_clauses)
        cursor = db_manager.execute(sql, params)
        row = cursor.fetchone()
        return row["count"] if row else 0

    def tambah(self, data):
        ph = db_manager.placeholder
        quoted_table = db_manager.quote_identifier(self._table)
        columns = ", ".join([db_manager.quote_identifier(k) for k in data.keys()])
        placeholders = ", ".join([ph] * len(data))
        sql = f"INSERT INTO {quoted_table} ({columns}) VALUES ({placeholders})"
        params = list(data.values())
        return db_manager.execute_write(sql, params)

    def insert(self, data):
        return self.tambah(data)

    def anyari(self, data):
        ph = db_manager.placeholder
        quoted_table = db_manager.quote_identifier(self._table)
        set_clauses = []
        params = []
        for col, val in data.items():
            quoted_col = db_manager.quote_identifier(col)
            set_clauses.append(f"{quoted_col} = {ph}")
            params.append(val)

        sql = f"UPDATE {quoted_table} SET " + ", ".join(set_clauses)

        if self._wheres:
            where_clauses = []
            for item in self._wheres:
                col, op, val, wtype = item
                quoted_col = db_manager.quote_identifier(col)
                if wtype == "in":
                    if not val:
                        where_clauses.append("1 = 0")
                    else:
                        in_placeholders = ", ".join([ph] * len(val))
                        where_clauses.append(f"{quoted_col} IN ({in_placeholders})")
                        params.extend(val)
                else:
                    where_clauses.append(f"{quoted_col} {op} {ph}")
                    params.append(val)
            sql += " WHERE " + " AND ".join(where_clauses)

        return db_manager.execute_write(sql, params)

    def update(self, data):
        return self.anyari(data)

    def busak(self):
        ph = db_manager.placeholder
        quoted_table = db_manager.quote_identifier(self._table)
        sql = f"DELETE FROM {quoted_table}"
        params = []

        if self._wheres:
            where_clauses = []
            for item in self._wheres:
                col, op, val, wtype = item
                quoted_col = db_manager.quote_identifier(col)
                if wtype == "in":
                    if not val:
                        where_clauses.append("1 = 0")
                    else:
                        in_placeholders = ", ".join([ph] * len(val))
                        where_clauses.append(f"{quoted_col} IN ({in_placeholders})")
                        params.extend(val)
                else:
                    where_clauses.append(f"{quoted_col} {op} {ph}")
                    params.append(val)
            sql += " WHERE " + " AND ".join(where_clauses)

        return db_manager.execute_write(sql, params)

    def delete(self):
        return self.busak()
