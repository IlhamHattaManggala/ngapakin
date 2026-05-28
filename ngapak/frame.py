# CallFrame tracking for VM execution context

class CallFrame:
    def __init__(self, function, ip=0, slots=0):
        self.function = function  # NgapakVMFunction object
        self.ip = ip              # Instruction pointer index in chunk.code
        self.slots = slots        # Stack index offset for local variables

    def __repr__(self):
        return f"<CallFrame {self.function.name} at IP {self.ip}>"
