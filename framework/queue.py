# Queue / Job System for Larapak
# Supports SQLite (default) with atomic reservation and optional Redis

import os
import time
import json
from framework.env import env
from framework.database import db_manager, DatabaseConnection

class RedisQueueDriver:
    """Redis-backed Queue Driver for high-concurrency atomic processing."""
    def __init__(self, host="127.0.0.1", port=6379, password=None, db=0):
        try:
            import redis
            self.client = redis.Redis(
                host=host,
                port=int(port or 6379),
                password=password or None,
                db=int(db or 0),
                decode_responses=True
            )
            self.client.ping()
        except ImportError:
            raise ImportError(
                "Driver Queue Redis membutuhkan paket 'redis'. "
                "Silakan pasang dengan menjalankan: pip install redis "
                "atau: pip install 'ngapakin[redis]'"
            )
        except Exception as e:
            raise ConnectionError(f"Gagal terhubung ke Redis Queue: {str(e)}")

    def push(self, queue_name: str, payload_dict: dict, delay: int = 0):
        serialized = json.dumps(payload_dict)
        key = f"queue:{queue_name}"
        return bool(self.client.lpush(key, serialized))

    def pop(self, queue_name: str):
        key = f"queue:{queue_name}"
        data = self.client.rpop(key)
        if not data:
            return None
        return json.loads(data)


class SQLiteQueueDriver:
    """SQLite-backed Queue Driver with atomic reservation and brief lock durations."""
    def __init__(self, db=None):
        if db is not None:
            self.db = db
        else:
            custom_db = env("QUEUE_DATABASE")
            if custom_db:
                self.db = DatabaseConnection(connection_name="sqlite", database=custom_db)
            else:
                self.db = db_manager
        self._ensure_table()

    def _ensure_table(self):
        self.db.execute_write(
            "CREATE TABLE IF NOT EXISTS jobs ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "queue VARCHAR(255), "
            "payload TEXT, "
            "attempts INTEGER, "
            "reserved_at INTEGER, "
            "available_at INTEGER, "
            "created_at INTEGER)"
        )

    def push(self, queue_name: str, payload_dict: dict, delay: int = 0):
        payload = json.dumps(payload_dict)
        now = int(time.time())
        self.db.execute_write(
            "INSERT INTO jobs (queue, payload, attempts, reserved_at, available_at, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [queue_name, payload, 0, None, now + delay, now]
        )
        return True

    def reserve_next(self, queue_name: str, lock_timeout: int = 60):
        """Atomically find and reserve the next available job, minimizing lock duration."""
        now = int(time.time())
        # Brief query to find candidate job
        row = self.db.execute(
            "SELECT * FROM jobs WHERE queue = ? AND (reserved_at IS NULL OR reserved_at < ?) "
            "AND available_at <= ? ORDER BY id ASC LIMIT 1",
            [queue_name, now - lock_timeout, now]
        ).fetchone()

        if not row:
            return None

        job_id = row["id"]
        # Atomically reserve and commit immediately so lock is released!
        affected = self.db.execute_write(
            "UPDATE jobs SET reserved_at = ?, attempts = attempts + 1 "
            "WHERE id = ? AND (reserved_at IS NULL OR reserved_at < ?)",
            [now, job_id, now - lock_timeout]
        )
        
        # If another worker reserved it in the split millisecond, skip
        if affected == 0:
            return None

        return dict(row)

    def delete_job(self, job_id: int):
        self.db.execute_write("DELETE FROM jobs WHERE id = ?", [job_id])

    def release_job(self, job_id: int, delay: int = 10):
        """Release job back to queue with delay for retry."""
        now = int(time.time())
        self.db.execute_write(
            "UPDATE jobs SET reserved_at = NULL, available_at = ? WHERE id = ?",
            [now + delay, job_id]
        )


class Queue:
    def __init__(self, vm=None, driver=None, db=None):
        self.vm = vm
        self.driver_name = (driver or env("QUEUE_DRIVER", "sqlite")).lower()
        if self.driver_name == "redis":
            self.driver = RedisQueueDriver(
                host=env("REDIS_HOST", "127.0.0.1"),
                port=env("REDIS_PORT", 6379),
                password=env("REDIS_PASSWORD"),
                db=env("REDIS_QUEUE_DB", 0)
            )
        else:
            self.driver = SQLiteQueueDriver(db=db)

    def lebokna(self, job_name, data=None, queue_name="default", delay=0):
        payload_data = {
            "job_class": job_name,
            "data": data or {}
        }
        return self.driver.push(queue_name, payload_data, delay)

    def push(self, job_name, data=None, queue_name="default", delay=0):
        return self.lebokna(job_name, data, queue_name, delay)

    def siji(self, queue_name="default"):
        """Process a single job from the queue with lock released during execution."""
        if isinstance(self.driver, RedisQueueDriver):
            payload_data = self.driver.pop(queue_name)
            if not payload_data:
                return False
            job_class_name = payload_data.get("job_class")
            job_data = payload_data.get("data", {})
            return self._execute_job_class(job_class_name, job_data)
        else:
            job_record = self.driver.reserve_next(queue_name)
            if not job_record:
                return False

            job_id = job_record["id"]
            payload_data = json.loads(job_record["payload"])
            job_class_name = payload_data.get("job_class")
            job_data = payload_data.get("data", {})

            print(f"[Queue Worker] Memproses pekerjaan #{job_id}: {job_class_name}")

            # Execute job logic outside any database locks
            success = self._execute_job_class(job_class_name, job_data)
            if success:
                self.driver.delete_job(job_id)
                print(f"[Queue Worker] Pekerjaan #{job_id} sukses diselesaikan.")
            else:
                # Retry up to 3 attempts, then release
                if job_record["attempts"] >= 3:
                    print(f"[Queue Worker] Pekerjaan #{job_id} gagal setelah 3 percobaan. Dihapus.")
                    self.driver.delete_job(job_id)
                else:
                    self.driver.release_job(job_id, delay=15)
            return True

    def _execute_job_class(self, job_class_name: str, job_data: dict) -> bool:
        try:
            self._autoload_jobs()
            if not self.vm or job_class_name not in self.vm.globals:
                print(f"[Queue Worker] Error: Kelas pekerjaan {job_class_name} tidak ditemukan di VM globals.")
                return False

            job_class = self.vm.globals[job_class_name]
            from ngapak.vm import NgapakClass, NgapakInstance

            if isinstance(job_class, NgapakClass):
                instance = NgapakInstance(job_class)
            else:
                instance = job_class()

            method = None
            for method_name in ("tangani", "handle"):
                if isinstance(instance, NgapakInstance):
                    if method_name in instance.class_attributes:
                        method = instance.class_attributes[method_name]
                        break
                    elif instance.ngapak_class.parent_class and hasattr(instance.ngapak_class.parent_class, method_name):
                        method = getattr(instance.ngapak_class.parent_class, method_name)
                        break
                elif hasattr(instance, method_name):
                    method = getattr(instance, method_name)
                    break

            if method:
                if hasattr(method, "chunk"):
                    self.vm.execute_callable(method, [instance, job_data])
                elif callable(method):
                    method(job_data)
                return True
            else:
                print(f"[Queue Worker] Error: Metode 'tangani' atau 'handle' tidak ditemukan pada kelas {job_class_name}")
                return False
        except Exception as e:
            print(f"[Queue Worker] Gagal memproses {job_class_name}: {str(e)}")
            return False

    def _autoload_jobs(self):
        from framework.paths import get_jobs_path
        jobs_path = get_jobs_path()
        if not os.path.exists(jobs_path) or not self.vm:
            return

        from ngapak import Lexer, Parser, Compiler
        for filename in os.listdir(jobs_path):
            if filename.endswith(".ngpk"):
                filepath = os.path.join(jobs_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()
                    lexer = Lexer(source, filepath)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens, filepath)
                    ast = parser.parse()
                    compiler = Compiler(filepath)
                    main_fn = compiler.compile(ast)
                    self.vm.execute_callable(main_fn, [])
                except Exception as e:
                    print(f"[Queue] Gagal autoload berkas job '{filename}': {str(e)}")
