# Unit tests for Database Manager drop_all_tables and Migration Status

import unittest
import os
from framework.database import DatabaseConnection

class TestMigrationFreshAndStatus(unittest.TestCase):
    def setUp(self):
        self.db_file = "test_mig_fresh.sqlite"
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
        self.db = DatabaseConnection(connection_name="sqlite", database=self.db_file)

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.db_file):
            try:
                os.remove(self.db_file)
            except Exception:
                pass

    def test_drop_all_tables(self):
        # Create a few tables
        self.db.execute_write("CREATE TABLE users (id INT, name TEXT)")
        self.db.execute_write("CREATE TABLE posts (id INT, title TEXT)")
        self.db.execute_write("CREATE TABLE comments (id INT, content TEXT)")

        # Verify tables exist
        rows = self.db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
        self.assertEqual(len(rows), 3)

        # Drop all tables
        dropped = self.db.drop_all_tables()
        self.assertEqual(len(dropped), 3)
        self.assertIn("users", dropped)
        self.assertIn("posts", dropped)
        self.assertIn("comments", dropped)

        # Verify no tables remain
        rows_after = self.db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
        self.assertEqual(len(rows_after), 0)

if __name__ == "__main__":
    unittest.main()
