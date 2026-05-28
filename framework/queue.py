# Queue / Job System for Larapak

import os
import time
import json
from framework.database import db_manager

class Queue:
    def __init__(self, vm=None):
        self.vm = vm
        self._ensure_table()

    def _ensure_table(self):
        db_manager.execute_write(
            "CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, queue VARCHAR(255), payload TEXT, attempts INTEGER, reserved_at INTEGER, available_at INTEGER, created_at INTEGER)"
        )

    def lebokna(self, job_name, data=None, queue_name="default", delay=0):
        payload = json.dumps({
            "job_class": job_name,
            "data": data or {}
        })
        now = int(time.time())
        db_manager.execute_write(
            "INSERT INTO jobs (queue, payload, attempts, reserved_at, available_at, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            [queue_name, payload, 0, None, now + delay, now]
        )
        return True

    def push(self, job_name, data=None, queue_name="default", delay=0):
        return self.lebokna(job_name, data, queue_name, delay)

    def siji(self, queue_name="default"):
        """Process a single job from the queue."""
        now = int(time.time())
        # Select next job that is not reserved and available
        row = db_manager.execute(
            "SELECT * FROM jobs WHERE queue = ? AND (reserved_at IS NULL OR reserved_at < ?) AND available_at <= ? ORDER BY id ASC LIMIT 1",
            [queue_name, now - 60, now] # 60 seconds lock timeout
        ).fetchone()
        
        if not row:
            return False
            
        job_id = row["id"]
        # Reserve job
        db_manager.execute_write(
            "UPDATE jobs SET reserved_at = ?, attempts = attempts + 1 WHERE id = ?",
            [now, job_id]
        )
        
        payload_data = json.loads(row["payload"])
        job_class_name = payload_data["job_class"]
        job_data = payload_data["data"]
        
        print(f"[Queue Worker] Memproses pekerjaan #{job_id}: {job_class_name}")
        
        success = False
        try:
            # Autoload all jobs from app/Jobs/ if not already loaded
            self._autoload_jobs()
            
            if self.vm and job_class_name in self.vm.globals:
                job_class = self.vm.globals[job_class_name]
                
                from ngapak.vm import NgapakClass, NgapakInstance
                
                # Instantiate
                if isinstance(job_class, NgapakClass):
                    instance = NgapakInstance(job_class)
                else:
                    instance = job_class()
                
                # Look for method `tangani` or `handle`
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
                    if hasattr(method, 'chunk'):
                        # Ngapak VM Function: we pass (instance, job_data)
                        self.vm.execute_callable(method, [instance, job_data])
                    elif callable(method):
                        # Python method
                        method(job_data)
                    success = True
                else:
                    print(f"[Queue Worker] Error: Metode 'tangani' atau 'handle' tidak ditemukan pada kelas {job_class_name}")
            else:
                print(f"[Queue Worker] Error: Kelas pekerjaan {job_class_name} tidak ditemukan di VM globals.")
        except Exception as e:
            print(f"[Queue Worker] Gagal memproses pekerjaan #{job_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            
        if success:
            db_manager.execute_write("DELETE FROM jobs WHERE id = ?", [job_id])
            print(f"[Queue Worker] Pekerjaan #{job_id} sukses diselesaikan.")
            return True
        else:
            if row["attempts"] >= 3:
                db_manager.execute_write("DELETE FROM jobs WHERE id = ?", [job_id])
                print(f"[Queue Worker] Pekerjaan #{job_id} gagal setelah 3 percobaan. Dihapus.")
            else:
                db_manager.execute_write(
                    "UPDATE jobs SET reserved_at = NULL, available_at = ? WHERE id = ?",
                    [int(time.time()) + 10, job_id]
                )
                print(f"[Queue Worker] Pekerjaan #{job_id} dilepas kembali untuk dicoba lagi nanti.")
            return False

    def _autoload_jobs(self):
        """Autoload files in app/Jobs directory if they are not already loaded in VM globals."""
        jobs_path = "app/Jobs"
        if not os.path.exists(jobs_path):
            return
            
        from ngapak.lexer import Lexer
        from ngapak.parser import Parser
        from ngapak.compiler import Compiler
        
        for filename in os.listdir(jobs_path):
            if filename.endswith(".ngpk"):
                filepath = os.path.join(jobs_path, filename)
                # Parse class name (remove .ngpk)
                class_name = filename[:-5]
                if self.vm and class_name not in self.vm.globals:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()
                    lexer = Lexer(source, filepath)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens, filepath)
                    ast = parser.parse()
                    compiler = Compiler(filepath)
                    main_fn = compiler.compile(ast)
                    self.vm.execute_callable(main_fn, [])
