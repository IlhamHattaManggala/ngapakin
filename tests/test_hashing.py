import os
import unittest
from framework.hashing import Hash, hash_password, verify_password, needs_rehash
from framework.auth import Auth
from framework.database import db_manager
from framework.session import Session
from framework.model import Model
from ngapak import VM

class TestPasswordHashing(unittest.TestCase):
    def test_hash_format_and_verification(self):
        password = "RahasiaNgapak123!"
        hashed = hash_password(password)
        
        # Verify it is not plain text and formatted properly
        self.assertNotEqual(password, hashed)
        self.assertTrue(Hash.is_hashed(hashed))
        self.assertTrue(hashed.startswith("$pbkdf2-sha256$") or hashed.startswith("$argon2"))
        
        # Correct password verification
        self.assertTrue(verify_password(password, hashed))
        
        # Wrong password verification
        self.assertFalse(verify_password("PasswordSalah123", hashed))
        self.assertFalse(verify_password("", hashed))
        self.assertFalse(verify_password(password, "random_garbage_hash"))

    def test_corrupted_hash_handling(self):
        password = "SecretPassword"
        # Truncated or malformed hashes
        self.assertFalse(verify_password(password, "$pbkdf2-sha256$corrupted"))
        self.assertFalse(verify_password(password, "$pbkdf2-sha256$i=100$bad$bad"))
        self.assertFalse(verify_password(password, None))
        self.assertFalse(verify_password(None, "hash"))

    def test_needs_rehash(self):
        plain = "plain_password"
        self.assertTrue(needs_rehash(plain))
        
        fresh_hash = hash_password("test")
        # Fresh hash should not need rehash under same parameters
        self.assertFalse(needs_rehash(fresh_hash))
        
        # Outdated iteration hash should trigger needs_rehash
        old_hash = "$pbkdf2-sha256$i=1000,l=32$c2FsdHNhbHQ=$aGFzaGhhc2g="
        self.assertTrue(needs_rehash(old_hash))

    def test_legacy_plaintext_migration_in_auth(self):
        test_db = "test_auth_migration.sqlite"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        db_manager.db_path = test_db
        db_manager.close()
        
        # Create users table with legacy plain-text password
        db_manager.execute_write(
            "CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, email VARCHAR(255), password VARCHAR(255), name VARCHAR(255))"
        )
        db_manager.execute_write(
            "INSERT INTO users (email, password, name) VALUES (?, ?, ?)",
            ["user@example.com", "old_plain_pass", "Budi"]
        )

        vm = VM()
        session = Session()
        vm.globals["sesi"] = session
        
        class User(Model):
            tabel = "users"
            fillable = ["email", "password", "name"]
        
        vm.globals["User"] = User
        Model.active_vm = vm
        
        auth = Auth(vm)
        
        # 1. Failed login with wrong password
        self.assertFalse(auth.mlebu("user@example.com", "wrong_password"))
        
        # 2. Successful login with legacy plain password
        self.assertTrue(auth.mlebu("user@example.com", "old_plain_pass"))
        self.assertTrue(auth.cek())
        
        # 3. Verify that password in DB has been migrated to encoded hash!
        row = db_manager.execute("SELECT password FROM users WHERE email = ?", ["user@example.com"]).fetchone()
        migrated_pass = row["password"]
        self.assertNotEqual(migrated_pass, "old_plain_pass")
        self.assertTrue(Hash.is_hashed(migrated_pass))
        
        # 4. Subsequent login works using newly hashed password
        self.assertTrue(auth.mlebu("user@example.com", "old_plain_pass"))
        
        db_manager.close()
        if os.path.exists(test_db):
            os.remove(test_db)


if __name__ == "__main__":
    unittest.main()
