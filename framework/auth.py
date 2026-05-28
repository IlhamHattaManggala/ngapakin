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
        """Login user with email and password."""
        if self.vm and "User" in self.vm.globals:
            User = self.vm.globals["User"]
            from framework.model import Model
            # Query user using ModelQueryBuilder
            # We will make sure Model.nek works and returns a user.
            # Or we can query directly via SQL for safety inside auth:
            table = Model.get_table_name(User)
            row = db_manager.execute(f"SELECT * FROM {table} WHERE email = ?", [email]).fetchone()
            if row:
                user_dict = dict(row)
                if user_dict.get("password") == password:
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
