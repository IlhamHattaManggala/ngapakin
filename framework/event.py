# Event Dispatcher for Larapak

class Event:
    def __init__(self, vm=None):
        self.vm = vm
        self.listeners = {}

    def rungokna(self, event_name, listener):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(listener)

    def listen(self, event_name, listener):
        self.rungokna(event_name, listener)

    def kirim(self, event_name, data=None):
        if event_name not in self.listeners:
            return
            
        for listener in self.listeners[event_name]:
            # Call the listener
            if hasattr(listener, 'chunk'):
                # Ngapak VM Function
                if self.vm:
                    self.vm.execute_callable(listener, [data] if data is not None else [])
            elif callable(listener):
                listener(data) if data is not None else listener()

    def dispatch(self, event_name, data=None):
        self.kirim(event_name, data)
