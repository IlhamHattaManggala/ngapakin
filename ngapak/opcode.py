# Opcode definitions for NgapakIn Virtual Machine

class OpCode:
    OP_CONSTANT = 0        # Pushes a constant from constants pool
    OP_TRUE = 1            # Pushes True
    OP_FALSE = 2           # Pushes False
    OP_NULL = 3            # Pushes None (kosong)
    OP_POP = 4             # Pops top of stack
    OP_DEFINE_GLOBAL = 5   # Defines global variable name (index in constants)
    OP_GET_GLOBAL = 6      # Reads global variable name
    OP_SET_GLOBAL = 7      # Sets global variable name
    OP_GET_LOCAL = 8       # Reads local variable from stack slot
    OP_SET_LOCAL = 9       # Sets local variable to stack slot
    OP_ADD = 10            # Left + Right
    OP_SUB = 11            # Left - Right
    OP_MUL = 12            # Left * Right
    OP_DIV = 13            # Left / Right
    OP_EQ = 14             # Left == Right
    OP_NEQ = 15            # Left != Right
    OP_LT = 16             # Left < Right
    OP_GT = 17             # Left > Right
    OP_LTE = 18            # Left <= Right
    OP_GTE = 19            # Left >= Right
    OP_JUMP = 20           # Unconditional jump (jump offset is next 2 bytes)
    OP_JUMP_IF_FALSE = 21  # Jump if top of stack is falsy (offset is next 2 bytes)
    OP_LOOP = 22           # Loop back jump (offset is next 2 bytes)
    OP_CALL = 23           # Call function (arity is next 1 byte)
    OP_RETURN = 24         # Return from function
    OP_PRINT = 25          # Print top of stack (tulis)
    OP_GET_MEMBER = 26     # Accesses member/attribute by name (index in constants)
    OP_CALL_METHOD = 27    # Calls method on object (method name index in constants, followed by arity byte)
    OP_BUILD_DICT = 28     # Builds dictionary from stack (arity/number of key-value pairs is next byte)
    OP_BUILD_LIST = 29     # Builds list from stack (arity/number of elements is next byte)
    OP_DEFINE_CLASS = 30   # Defines class: name (const idx), parent (const idx), pops body dict
    OP_SET_MEMBER = 31     # Sets member/attribute by name: name (const idx), pops val, pops obj, pushes val

