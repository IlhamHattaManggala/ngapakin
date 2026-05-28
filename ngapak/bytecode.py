# Bytecode representation for NgapakIn VM

class Chunk:
    def __init__(self):
        self.code = []         # List of instruction bytes (integers)
        self.constants = []    # Constant pool (values)
        self.lines = []        # Line numbers for each instruction byte

    def write(self, byte, line):
        """Write an instruction byte to the chunk."""
        if not isinstance(byte, int) or byte < 0 or byte > 255:
            # Opcode and operands are bytes, but can be larger indices if needed.
            # In Python, using a list of integers allows arbitrary range for simplicity (e.g. indices > 255).
            pass
        self.code.append(byte)
        self.lines.append(line)

    def add_constant(self, value):
        """Add a value to the constant pool. Returns index of the constant."""
        # Avoid duplicate constants if possible to save space
        for idx, const in enumerate(self.constants):
            if const == value:
                return idx
        self.constants.append(value)
        return len(self.constants) - 1

class NgapakVMFunction:
    def __init__(self, name, arity):
        self.name = name
        self.arity = arity
        self.chunk = Chunk()

    def __repr__(self):
        return f"<fungsi-vm {self.name}>"
