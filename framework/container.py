# Service Container for Larapak Web Framework

class Container:
    def __init__(self):
        self.bindings = {}
        self.instances = {}
        self.vm = None  # Injected by VM

    def bind(self, name, factory):
        """Bind a dependency resolver function to a name."""
        self.bindings[name] = factory

    def singleton(self, name, factory):
        """Bind a singleton dependency resolver."""
        def singleton_factory():
            if name not in self.instances:
                if self.vm and callable(factory):
                    # If it's a VM function, invoke it
                    self.instances[name] = self.vm.execute_callable(factory, [])
                else:
                    self.instances[name] = factory()
            return self.instances[name]
        self.bindings[name] = singleton_factory

    def make(self, name):
        """Resolve dependency by name."""
        if name in self.instances:
            return self.instances[name]
            
        if name in self.bindings:
            factory = self.bindings[name]
            # Check if it is a VM function
            if self.vm and hasattr(factory, 'chunk'):
                res = self.vm.execute_callable(factory, [])
                return res
            elif callable(factory):
                res = factory()
                return res
            else:
                return factory
                
        raise KeyError(f"Dependency '{name}' tidak ditemukan di Service Container.")
