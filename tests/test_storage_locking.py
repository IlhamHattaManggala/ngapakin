import os
import time
import unittest
from framework.session import Session
from framework.cache import Cache
from framework.queue import Queue
from framework.database import DatabaseConnection

class TestStorageLockingAndSeparation(unittest.TestCase):
    def setUp(self):
        self.session_db_file = "test_sessions_storage.sqlite"
        self.cache_db_file = "test_cache_storage.sqlite"
        self.queue_db_file = "test_queue_storage.sqlite"

        for f in (self.session_db_file, self.cache_db_file, self.queue_db_file):
            if os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass

        self.session_db = DatabaseConnection(connection_name="sqlite", database=self.session_db_file)
        self.cache_db = DatabaseConnection(connection_name="sqlite", database=self.cache_db_file)
        self.queue_db = DatabaseConnection(connection_name="sqlite", database=self.queue_db_file)

        self.session = Session("sess_concurrent_1", db=self.session_db)
        self.cache = Cache(db=self.cache_db)
        self.queue = Queue(db=self.queue_db)

    def tearDown(self):
        self.session_db.close()
        self.cache_db.close()
        self.queue_db.close()

        for f in (self.session_db_file, self.cache_db_file, self.queue_db_file):
            if os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass

    def test_storage_databases_are_independent(self):
        # 1. Write to session
        self.session.pasang("user_id", 101)
        self.session.simpen()

        # 2. Write to cache
        self.cache.pasang("weather", "cerah", seconds=60)

        # 3. Write to queue
        self.queue.push("SendEmailJob", {"to": "user@example.com"})

        # Verify that session DB contains only session table, not cache or jobs!
        tables_session = [r["name"] for r in self.session_db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        self.assertIn("sessions", tables_session)
        self.assertNotIn("cache", tables_session)
        self.assertNotIn("jobs", tables_session)

        # Verify cache DB contains only cache
        tables_cache = [r["name"] for r in self.cache_db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        self.assertIn("cache", tables_cache)
        self.assertNotIn("sessions", tables_cache)

        # Verify queue DB contains only jobs
        tables_queue = [r["name"] for r in self.queue_db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        self.assertIn("jobs", tables_queue)
        self.assertNotIn("sessions", tables_queue)

    def test_wal_mode_enabled_on_storage(self):
        # Check journal_mode PRAGMA on session_db
        cursor = self.session_db.execute("PRAGMA journal_mode;")
        mode = cursor.fetchone()[0]
        # In SQLite, WAL mode returns 'wal'
        self.assertEqual(mode.lower(), "wal")

    def test_queue_atomic_reservation_prevents_duplicate_processing(self):
        self.queue.push("UniqueJob", {"id": 1})
        
        # Worker 1 reserves the job
        job1 = self.queue.driver.reserve_next("default", lock_timeout=60)
        self.assertIsNotNone(job1)
        self.assertEqual(job1["id"], 1)

        # Worker 2 attempts to reserve while Worker 1 is processing: should get None!
        job2 = self.queue.driver.reserve_next("default", lock_timeout=60)
        self.assertIsNone(job2)


if __name__ == "__main__":
    unittest.main()
