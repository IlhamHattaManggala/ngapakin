# Environment and scope tracking for NgapakIn

class ReturnException(Exception):
    """Exception used to unwind interpreter call stack for function return values."""
    def __init__(self, value):
        self.value = value

class NgapakCallable:
    def call(self, interpreter, arguments):
        raise NotImplementedError()
        
    def arity(self):
        raise NotImplementedError()

class NgapakFunction(NgapakCallable):
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, arguments):
        # Local scope points to the parent/closure where function was defined
        env = Environment(self.closure)
        for name, val in zip(self.declaration.params, arguments):
            env.define(name, val)
            
        try:
            interpreter.execute_block(self.declaration.body, env)
        except ReturnException as r:
            return r.value
        return None

    def __repr__(self):
        return f"<fungsi {self.declaration.name}>"

class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.records = {}

    def get(self, name):
        if name in self.records:
            return self.records[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise KeyError(f"Variabel atau fungsi '{name}' tidak didefinisikan.")

    def define(self, name, value):
        self.records[name] = value

    def assign(self, name, value):
        if name in self.records:
            self.records[name] = value
            return
        if self.parent is not None:
            try:
                self.parent.assign(name, value)
                return
            except KeyError:
                pass
        self.records[name] = value
