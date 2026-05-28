# Bytecode disassembler and debugger tools for NgapakIn VM

from .opcode import OpCode

def disassemble_chunk(chunk, name):
    """Print all instructions in a chunk in human-readable format."""
    print(f"=== {name} ===")
    offset = 0
    while offset < len(chunk.code):
        offset = disassemble_instruction(chunk, offset)
    print("=== END ===\n")

def disassemble_instruction(chunk, offset):
    """Disassemble a single instruction at a given offset. Returns the next offset."""
    byte = chunk.code[offset]
    line = chunk.lines[offset]
    
    # Print line number or vertical bar if on same line as previous instruction
    line_str = f"{line:4d}" if (offset == 0 or chunk.lines[offset] != chunk.lines[offset-1]) else "   |"
    
    # OP_CONSTANT
    if byte == OpCode.OP_CONSTANT:
        const_idx = chunk.code[offset + 1]
        val = chunk.constants[const_idx]
        print(f"{offset:04d} {line_str} OP_CONSTANT {const_idx} ({repr(val)})")
        return offset + 2
        
    # OP_DEFINE_GLOBAL, OP_GET_GLOBAL, OP_SET_GLOBAL
    elif byte in (OpCode.OP_DEFINE_GLOBAL, OpCode.OP_GET_GLOBAL, OpCode.OP_SET_GLOBAL):
        name_idx = chunk.code[offset + 1]
        name = chunk.constants[name_idx]
        op_name = {
            OpCode.OP_DEFINE_GLOBAL: "OP_DEFINE_GLOBAL",
            OpCode.OP_GET_GLOBAL: "OP_GET_GLOBAL",
            OpCode.OP_SET_GLOBAL: "OP_SET_GLOBAL"
        }[byte]
        print(f"{offset:04d} {line_str} {op_name} {name_idx} ('{name}')")
        return offset + 2
        
    # OP_GET_LOCAL, OP_SET_LOCAL
    elif byte in (OpCode.OP_GET_LOCAL, OpCode.OP_SET_LOCAL):
        slot = chunk.code[offset + 1]
        op_name = "OP_GET_LOCAL" if byte == OpCode.OP_GET_LOCAL else "OP_SET_LOCAL"
        print(f"{offset:04d} {line_str} {op_name} slot {slot}")
        return offset + 2
        
    # Jumps: OP_JUMP, OP_JUMP_IF_FALSE, OP_LOOP
    elif byte in (OpCode.OP_JUMP, OpCode.OP_JUMP_IF_FALSE, OpCode.OP_LOOP):
        high = chunk.code[offset + 1]
        low = chunk.code[offset + 2]
        jump_offset = (high << 8) | low
        op_name = {
            OpCode.OP_JUMP: "OP_JUMP",
            OpCode.OP_JUMP_IF_FALSE: "OP_JUMP_IF_FALSE",
            OpCode.OP_LOOP: "OP_LOOP"
        }[byte]
        
        target = offset + 3 + (jump_offset if byte != OpCode.OP_LOOP else -jump_offset)
        print(f"{offset:04d} {line_str} {op_name} offset {jump_offset} -> target {target:04d}")
        return offset + 3
        
    # OP_CALL
    elif byte == OpCode.OP_CALL:
        arity = chunk.code[offset + 1]
        print(f"{offset:04d} {line_str} OP_CALL arity {arity}")
        return offset + 2
        
    # OP_GET_MEMBER
    elif byte == OpCode.OP_GET_MEMBER:
        name_idx = chunk.code[offset + 1]
        name = chunk.constants[name_idx]
        print(f"{offset:04d} {line_str} OP_GET_MEMBER {name_idx} ('.{name}')")
        return offset + 2
        
    # OP_CALL_METHOD
    elif byte == OpCode.OP_CALL_METHOD:
        name_idx = chunk.code[offset + 1]
        arity = chunk.code[offset + 2]
        name = chunk.constants[name_idx]
        print(f"{offset:04d} {line_str} OP_CALL_METHOD {name_idx} ('.{name}()') arity {arity}")
        return offset + 3
        
    # OP_BUILD_DICT
    elif byte == OpCode.OP_BUILD_DICT:
        arity = chunk.code[offset + 1]
        print(f"{offset:04d} {line_str} OP_BUILD_DICT item_count {arity}")
        return offset + 2
        
    # OP_BUILD_LIST
    elif byte == OpCode.OP_BUILD_LIST:
        arity = chunk.code[offset + 1]
        print(f"{offset:04d} {line_str} OP_BUILD_LIST element_count {arity}")
        return offset + 2
        
    # OP_DEFINE_CLASS
    elif byte == OpCode.OP_DEFINE_CLASS:
        name_idx = chunk.code[offset + 1]
        parent_idx = chunk.code[offset + 2]
        name = chunk.constants[name_idx]
        parent = chunk.constants[parent_idx] if parent_idx != 0xff else "None"
        print(f"{offset:04d} {line_str} OP_DEFINE_CLASS '{name}' extends '{parent}'")
        return offset + 3

    # OP_SET_MEMBER
    elif byte == OpCode.OP_SET_MEMBER:
        name_idx = chunk.code[offset + 1]
        name = chunk.constants[name_idx]
        print(f"{offset:04d} {line_str} OP_SET_MEMBER {name_idx} ('.{name} = val')")
        return offset + 2
        
    # Single-byte instructions
    else:
        simple_ops = {
            OpCode.OP_TRUE: "OP_TRUE",
            OpCode.OP_FALSE: "OP_FALSE",
            OpCode.OP_NULL: "OP_NULL",
            OpCode.OP_POP: "OP_POP",
            OpCode.OP_ADD: "OP_ADD",
            OpCode.OP_SUB: "OP_SUB",
            OpCode.OP_MUL: "OP_MUL",
            OpCode.OP_DIV: "OP_DIV",
            OpCode.OP_EQ: "OP_EQ",
            OpCode.OP_NEQ: "OP_NEQ",
            OpCode.OP_LT: "OP_LT",
            OpCode.OP_GT: "OP_GT",
            OpCode.OP_LTE: "OP_LTE",
            OpCode.OP_GTE: "OP_GTE",
            OpCode.OP_RETURN: "OP_RETURN",
            OpCode.OP_PRINT: "OP_PRINT"
        }
        op_name = simple_ops.get(byte, f"OP_UNKNOWN ({byte})")
        print(f"{offset:04d} {line_str} {op_name}")
        return offset + 1
