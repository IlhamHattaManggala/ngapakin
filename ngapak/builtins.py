# Built-in function definitions for NgapakIn

from .environment import NgapakCallable

class BuiltinDowo(NgapakCallable):
    """Returns the length of a string or list/structure."""
    def arity(self):
        return 1
        
    def call(self, interpreter, arguments):
        arg = arguments[0]
        if arg is None:
            return 0
        if isinstance(arg, (str, list, dict, tuple)):
            return len(arg)
        return 1

    def __repr__(self):
        return "<fungsi bawaan dowo>"

class BuiltinTanya(NgapakCallable):
    """Reads input from terminal with a prompt."""
    def arity(self):
        return 1
        
    def call(self, interpreter, arguments):
        prompt = str(arguments[0])
        return input(prompt)

    def __repr__(self):
        return "<fungsi bawaan tanya>"

class BuiltinAngka(NgapakCallable):
    """Converts a value to integer or float."""
    def arity(self):
        return 1
        
    def call(self, interpreter, arguments):
        val = arguments[0]
        try:
            if isinstance(val, (int, float)):
                return val
            val_str = str(val)
            if '.' in val_str:
                return float(val_str)
            return int(val_str)
        except ValueError:
            return 0

    def __repr__(self):
        return "<fungsi bawaan angka>"

class BuiltinTeks(NgapakCallable):
    """Converts a value to string representation."""
    def arity(self):
        return 1
        
    def call(self, interpreter, arguments):
        val = arguments[0]
        if val is None:
            return "kosong"
        if val is True:
            return "bener"
        if val is False:
            return "salah"
        return str(val)

    def __repr__(self):
        return "<fungsi bawaan teks>"

BUILTINS = {
    "dowo": BuiltinDowo(),
    "tanya": BuiltinTanya(),
    "angka": BuiltinAngka(),
    "teks": BuiltinTeks(),
}
