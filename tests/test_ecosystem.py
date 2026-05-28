import os
import time
import unittest
from framework.database import db_manager
from framework.session import Session
from framework.request import Request
from framework.response import Response
from framework.validation import Validator
from framework.cache import Cache
from framework.event import Event
from framework.queue import Queue
from framework.package_manager import PackageManager
from editors.vscode.language_server import check_syntax
from ngapak import Lexer, Parser, Compiler, VM

class TestEcosystem(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_ecosystem.sqlite"
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass
        db_manager.db_path = self.db_path
        db_manager.close()

        self.vm = VM()
        self.vm.globals["sesi"] = Session()
        self.vm.globals["validator"] = Validator
        self.vm.globals["cache"] = Cache()
        self.vm.globals["event"] = Event(self.vm)
        self.vm.globals["queue"] = Queue(self.vm)

    def tearDown(self):
        db_manager.close()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass
        # Clean up mock packages
        if os.path.exists("packages/test_pkg"):
            import shutil
            shutil.rmtree("packages/test_pkg", ignore_errors=True)

    def run_source(self, source):
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        main_fn = compiler.compile(ast)
        self.vm.run(main_fn)

    def test_session_management(self):
        # 1. Test basic session functionalities
        ses = Session("test_session_123")
        ses.pasang("name", "Ilham Hatta")
        ses.pasang("role", "Developer")
        ses.simpen()

        # Reload session
        ses2 = Session("test_session_123")
        self.assertEqual(ses2.entuk("name"), "Ilham Hatta")
        self.assertEqual(ses2.entuk("role"), "Developer")

        # Test forget
        ses2.lalekna("role")
        ses2.simpen()

        ses3 = Session("test_session_123")
        self.assertEqual(ses3.entuk("name"), "Ilham Hatta")
        self.assertIsNone(ses3.entuk("role"))

    def test_cookie_helper(self):
        # 1. Test Request cookie parsing
        req = Request(
            method="GET",
            headers={"Cookie": "larapak_session=abc123xyz; theme=dark"}
        )
        self.assertEqual(req.cookie("larapak_session"), "abc123xyz")
        self.assertEqual(req.cookie("theme"), "dark")

        # 2. Test Response cookie setting
        res = Response()
        res.cookie("user_id", "45", secure=True, httponly=True)
        self.assertIn("user_id", res.cookies)
        self.assertEqual(res.cookies["user_id"]["value"], "45")
        self.assertTrue(res.cookies["user_id"]["secure"])
        self.assertTrue(res.cookies["user_id"]["httponly"])

    def test_validation_engine(self):
        # Test valid data
        data = {"email": "test@example.com", "age": "20", "name": "Budi"}
        rules = {
            "email": "required|email",
            "age": "required|numeric|min:18",
            "name": "required"
        }
        val = Validator.gawe(data, rules)
        self.assertFalse(val.gagal())
        self.assertEqual(val.valid()["email"], "test@example.com")
        self.assertEqual(val.valid()["age"], "20")

        # Test invalid data
        invalid_data = {"email": "invalidemail", "age": "15"}
        val_invalid = Validator.make(invalid_data, rules)
        self.assertTrue(val_invalid.fails())
        errors = val_invalid.errors()
        self.assertIn("email", errors)
        self.assertIn("age", errors)
        self.assertIn("name", errors)

    def test_cache_system(self):
        cache = Cache()
        cache.pasang("username", "ilham_atta", 2) # expires in 2s
        self.assertEqual(cache.entuk("username"), "ilham_atta")
        
        # Test expiration
        time.sleep(2.5)
        self.assertIsNone(cache.entuk("username"))

    def test_event_listener_system(self):
        source = """
        # Register a listener
        state = ["val": 10]
        
        gawe tangani_event(data)
            state.val = state.val + data
        rampung
        
        event.listen("user.login", tangani_event)
        
        # Dispatch event
        event.dispatch("user.login", 5)
        
        res_val = state.val
        """
        self.run_source(source)
        self.assertEqual(self.vm.globals.get("res_val"), 15)

    def test_queue_job_system(self):
        # 1. Create a mock job folder structure
        os.makedirs("app/Jobs", exist_ok=True)
        job_filepath = "app/Jobs/SendLogJob.ngpk"
        job_code = """
        kelas SendLogJob
            gawe tangani(isi, data)
                tulis("LOG DIJALANKAN: " + data.get("message"))
                sesi.pasang("last_job_msg", data.get("message"))
            rampung
        rampung
        """
        with open(job_filepath, "w", encoding="utf-8") as f:
            f.write(job_code)

        try:
            # 2. Push job to queue
            q = Queue(self.vm)
            q.push("SendLogJob", {"message": "Hello Queue Worker!"})

            # 3. Process the queue job
            processed = q.siji()
            self.assertTrue(processed)
            
            # 4. Verify side effects
            self.assertEqual(self.vm.globals["sesi"].get("last_job_msg"), "Hello Queue Worker!")
        finally:
            if os.path.exists(job_filepath):
                os.remove(job_filepath)

    def test_package_manager(self):
        pm = PackageManager(self.vm)
        pm.install_package("test-pkg")

        # Discover & boot
        pm.boot_packages()
        
        # Verify provider has registered package_version helper in VM globals
        self.assertIn("test_pkg_versi", self.vm.globals)
        self.assertEqual(self.vm.globals["test_pkg_versi"], "1.0.0")

    def test_language_server_diagnostics(self):
        # Valid code
        valid_code = "a = 5\ntulis(a)"
        diag = check_syntax(valid_code)
        self.assertEqual(len(diag), 0)

        # Invalid code (syntax error: missing rampung)
        invalid_code = "gawe test()\n    tulis(1)"
        diag_invalid = check_syntax(invalid_code)
        self.assertEqual(len(diag_invalid), 1)
        self.assertIn("rampung", diag_invalid[0]["message"])

if __name__ == '__main__':
    unittest.main()
