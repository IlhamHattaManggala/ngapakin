# Authentication System for Larapak

from framework.database import db_manager

class Auth:
    def __init__(self, vm=None):
        self.vm = vm

    @property
    def sesi(self):
        if self.vm and "sesi" in self.vm.globals:
            return self.vm.globals["sesi"]
        return None

    def user(self):
        ses = self.sesi
        if not ses:
            return None
        user_id = ses.get("auth_user_id")
        if not user_id:
            return None
        
        if self.vm and "User" in self.vm.globals:
            User = self.vm.globals["User"]
            # Call User.golek(user_id)
            # golek is a classmethod on Model, which wraps it.
            # In Python, we can call it using __func__ since Model.golek is a classmethod
            from framework.model import Model
            return Model.golek.__func__(User, user_id)
        return None

    def cek(self):
        return self.user() is not None

    def check(self):
        return self.cek()

    def mlebu(self, email, password):
        """Login user with email and password securely."""
        if self.vm and "User" in self.vm.globals:
            User = self.vm.globals["User"]
            from framework.model import Model
            from framework.hashing import Hash
            
            table = Model.get_table_name(User)
            row = db_manager.execute(f"SELECT * FROM {table} WHERE email = ?", [email]).fetchone()
            if row:
                user_dict = dict(row)
                stored_pass = str(user_dict.get("password") or "")
                
                # Constant-time verification supporting encoded hash and legacy plain-text
                if Hash.verify_password(password, stored_pass):
                    # Safely migrate legacy/outdated password to new secure hash
                    if Hash.needs_rehash(stored_pass):
                        try:
                            new_hash = Hash.hash_password(password)
                            db_manager.execute_write(
                                f"UPDATE {table} SET password = ? WHERE id = ?",
                                [new_hash, user_dict.get("id")]
                            )
                            user_dict["password"] = new_hash
                        except Exception:
                            # Do not break authentication if rehash write fails
                            pass

                    ses = self.sesi
                    if ses:
                        ses.set("auth_user_id", user_dict.get("id"))
                    
                    # Instantiate user object
                    from ngapak.vm import NgapakInstance
                    instance = User() if hasattr(User, 'attributes') else User.__new__(User)
                    if isinstance(instance, NgapakInstance):
                        instance.fields.update(user_dict)
                    else:
                        instance.__dict__.update(user_dict)
                    return True
        return False

    def login(self, email, password):
        return self.mlebu(email, password)

    def metu(self):
        """Logout current user."""
        ses = self.sesi
        if ses:
            ses.forget("auth_user_id")

    def logout(self):
        self.metu()
