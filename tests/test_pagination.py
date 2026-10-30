# Unit tests for Pagination and Offset (kaca / paginate / lewati)

import unittest
import os
from framework.database import DatabaseConnection
from framework.query_builder import QueryBuilder
from framework.model import Model
from ngapak.vm import VM

class Product(Model):
    tabel = "products"
    fillable = ["name", "price"]

class TestPagination(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_file = "test_pagination.sqlite"
        if os.path.exists(cls.db_file):
            os.remove(cls.db_file)
        cls.db = DatabaseConnection(connection_name="sqlite", database=cls.db_file)

        from framework.database import db_manager
        db_manager.db_path = cls.db_file

        # Create products table and seed 25 items
        cls.db.execute_write("CREATE TABLE products (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(100), price INT)")
        for i in range(1, 26):
            cls.db.execute_write("INSERT INTO products (name, price) VALUES (?, ?)", [f"Barang {i}", i * 1000])

    @classmethod
    def tearDownClass(cls):
        from framework.database import db_manager
        db_manager.close()
        if os.path.exists(cls.db_file):
            try:
                os.remove(cls.db_file)
            except Exception:
                pass

    def test_query_builder_offset_and_limit(self):
        qb = QueryBuilder("products")
        items = qb.ambil(5).lewati(10).kabeh()
        self.assertEqual(len(items), 5)
        self.assertEqual(items[0]["name"], "Barang 11")
        self.assertEqual(items[-1]["name"], "Barang 15")

    def test_query_builder_kaca_pagination_first_page(self):
        qb = QueryBuilder("products")
        res = qb.kaca(saben_kaca=10, kaca_saiki=1)

        self.assertEqual(res["total"], 25)
        self.assertEqual(res["saben_kaca"], 10)
        self.assertEqual(res["kaca_saiki"], 1)
        self.assertEqual(res["kaca_pungkasan"], 3)
        self.assertFalse(res["ana_sadurunge"])
        self.assertTrue(res["ana_sabanjure"])
        self.assertEqual(len(res["data"]), 10)
        self.assertEqual(res["data"][0]["name"], "Barang 1")

    def test_query_builder_kaca_pagination_last_page(self):
        qb = QueryBuilder("products")
        res = qb.kaca(saben_kaca=10, kaca_saiki=3)

        self.assertEqual(res["total"], 25)
        self.assertEqual(res["kaca_saiki"], 3)
        self.assertEqual(res["kaca_pungkasan"], 3)
        self.assertTrue(res["ana_sadurunge"])
        self.assertFalse(res["ana_sabanjure"])
        self.assertEqual(len(res["data"]), 5) # remaining 5 items
        self.assertEqual(res["data"][-1]["name"], "Barang 25")

    def test_model_paginate(self):
        Model.active_vm = VM()
        res = Product.paginate(per_page=8, page=2)

        self.assertEqual(res["total"], 25)
        self.assertEqual(res["saben_kaca"], 8)
        self.assertEqual(res["kaca_saiki"], 2)
        self.assertEqual(res["kaca_pungkasan"], 4)
        self.assertTrue(res["ana_sadurunge"])
        self.assertTrue(res["ana_sabanjure"])
        self.assertEqual(len(res["data"]), 8)
        self.assertIsInstance(res["data"][0], Product)
        self.assertEqual(res["data"][0].name, "Barang 9")

if __name__ == "__main__":
    unittest.main()
