# AST to Bytecode Compiler for NgapakIn

from .ast import *
from .opcode import OpCode
from .bytecode import Chunk, NgapakVMFunction
from .errors import NgapakSyntaxError

class Compiler:
    def __init__(self, filename="<stdin>"):
        self.filename = filename
        self.current_function = NgapakVMFunction("main", 0)  # Top level chunk
        self.scope_depth = 0
        self.locals = []            # Stack slots tracking: {"name": str, "depth": int}
        self.globals_tracked = set() # Track defined globals in this compilation unit

    def compile(self, node):
        """Entrypoint for compilation of an AST node."""
        return node.accept(self)

    def emit_byte(self, byte, line):
        self.current_function.chunk.write(byte, line)

    def add_constant(self, value):
        return self.current_function.chunk.add_constant(value)

    def emit_jump(self, instruction, line):
        self.emit_byte(instruction, line)
        self.emit_byte(0xff, line)  # High byte placeholder
        self.emit_byte(0xff, line)  # Low byte placeholder
        return len(self.current_function.chunk.code) - 2

    def patch_jump(self, offset):
        # We compute relative jump offset from the byte after the jump payload
        jump_distance = len(self.current_function.chunk.code) - (offset + 2)
        if jump_distance > 65535:
            raise NgapakSyntaxError("Terlalu banyak kode untuk melakukan lompatan (jump offset overflow)", line=1)
        self.current_function.chunk.code[offset] = (jump_distance >> 8) & 0xff
        self.current_function.chunk.code[offset + 1] = jump_distance & 0xff

    def emit_loop(self, loop_start, line):
        self.emit_byte(OpCode.OP_LOOP, line)
        # Relative jump backwards from loop opcode's next two payload bytes
        offset = len(self.current_function.chunk.code) - loop_start + 2
        if offset > 65535:
            raise NgapakSyntaxError("Perulangan (loop) terlalu panjang", line=line)
        self.emit_byte((offset >> 8) & 0xff, line)
        self.emit_byte(offset & 0xff, line)

    def resolve_local(self, name):
        """Find local variable slot index in stack by name. Returns -1 if global."""
        for idx in range(len(self.locals) - 1, -1, -1):
            if self.locals[idx]["name"] == name:
                return idx
        return -1

    def begin_scope(self):
        self.scope_depth += 1

    def end_scope(self, line):
        self.scope_depth -= 1
        # Pop variables that are out of scope
        while self.locals and self.locals[-1]["depth"] > self.scope_depth:
            self.emit_byte(OpCode.OP_POP, line)
            self.locals.pop()

    def compile_function(self, func_node):
        """Compile a function AST node into a separate NgapakVMFunction."""
        fn_compiler = Compiler(self.filename)
        fn_compiler.current_function = NgapakVMFunction(func_node.name, len(func_node.params))
        fn_compiler.scope_depth = 1
        
        # Local slot 0 is reserved for the function itself
        fn_compiler.locals.append({"name": func_node.name, "depth": 0})
        
        # Add parameter variables into stack slots
        for param in func_node.params:
            fn_compiler.locals.append({"name": param, "depth": 1})

        for stmt in func_node.body:
            fn_compiler.compile(stmt)

        # Default function completion returns Null
        line = func_node.line if hasattr(func_node, 'line') else 1
        fn_compiler.emit_byte(OpCode.OP_NULL, line)
        fn_compiler.emit_byte(OpCode.OP_RETURN, line)
        
        return fn_compiler.current_function

    # Visitor Methods

    def visit_ProgramNode(self, node):
        self.locals.append({"name": "main", "depth": 0})
        for stmt in node.statements:
            self.compile(stmt)
        return self.current_function

    def visit_TulisNode(self, node):
        self.compile(node.expr)
        line = node.line if hasattr(node, 'line') else 1
        self.emit_byte(OpCode.OP_PRINT, line)

    def visit_VarAssignNode(self, node):
        self.compile(node.expr)
        line = node.line if hasattr(node, 'line') else 1
        
        if self.scope_depth > 0:
            idx = self.resolve_local(node.name)
            if idx != -1:
                # Existing local variable update
                self.emit_byte(OpCode.OP_SET_LOCAL, line)
                self.emit_byte(idx, line)
                self.emit_byte(OpCode.OP_POP, line)
            else:
                # Declare new local variable (stays on stack, slot maps to stack height)
                self.locals.append({"name": node.name, "depth": self.scope_depth})
        else:
            # Global assignment
            name_idx = self.add_constant(node.name)
            if node.name not in self.globals_tracked:
                self.globals_tracked.add(node.name)
                self.emit_byte(OpCode.OP_DEFINE_GLOBAL, line)
                self.emit_byte(name_idx, line)
            else:
                self.emit_byte(OpCode.OP_SET_GLOBAL, line)
                self.emit_byte(name_idx, line)
                self.emit_byte(OpCode.OP_POP, line)

    def visit_VarAccessNode(self, node):
        line = node.line if hasattr(node, 'line') else 1
        if self.scope_depth > 0:
            idx = self.resolve_local(node.name)
            if idx != -1:
                self.emit_byte(OpCode.OP_GET_LOCAL, line)
                self.emit_byte(idx, line)
                return
        
        name_idx = self.add_constant(node.name)
        self.emit_byte(OpCode.OP_GET_GLOBAL, line)
        self.emit_byte(name_idx, line)

    def visit_BinOpNode(self, node):
        self.compile(node.left)
        self.compile(node.right)
        
        op_map = {
            "PLUS": OpCode.OP_ADD,
            "MINUS": OpCode.OP_SUB,
            "MUL": OpCode.OP_MUL,
            "DIV": OpCode.OP_DIV,
            "EQ": OpCode.OP_EQ,
            "NEQ": OpCode.OP_NEQ,
            "LT": OpCode.OP_LT,
            "GT": OpCode.OP_GT,
            "LTE": OpCode.OP_LTE,
            "GTE": OpCode.OP_GTE,
        }
        op = op_map.get(node.op.type)
        self.emit_byte(op, node.op.line)

    def visit_LiteralNode(self, node):
        line = node.line if hasattr(node, 'line') else 1
        if node.value is True:
            self.emit_byte(OpCode.OP_TRUE, line)
        elif node.value is False:
            self.emit_byte(OpCode.OP_FALSE, line)
        elif node.value is None:
            self.emit_byte(OpCode.OP_NULL, line)
        else:
            idx = self.add_constant(node.value)
            self.emit_byte(OpCode.OP_CONSTANT, line)
            self.emit_byte(idx, line)

    def visit_IfNode(self, node):
        line = node.line if hasattr(node, 'line') else 1
        self.compile(node.condition)
        
        then_jump = self.emit_jump(OpCode.OP_JUMP_IF_FALSE, line)
        self.emit_byte(OpCode.OP_POP, line)  # Pop condition
        
        self.begin_scope()
        for stmt in node.true_branch:
            self.compile(stmt)
        self.end_scope(line)
        
        else_jump = self.emit_jump(OpCode.OP_JUMP, line)
        self.patch_jump(then_jump)
        self.emit_byte(OpCode.OP_POP, line)  # Pop condition
        
        if node.false_branch is not None:
            self.begin_scope()
            for stmt in node.false_branch:
                self.compile(stmt)
            self.end_scope(line)
            
        self.patch_jump(else_jump)

    def visit_ForNode(self, node):
        line = node.line if hasattr(node, 'line') else 1
        
        self.begin_scope()
        # Compile start value -> leaves on stack as loop var i
        self.compile(node.start_expr)
        i_idx = len(self.locals)
        self.locals.append({"name": node.var_name, "depth": self.scope_depth})
        
        # Compile end value -> leaves on stack as anonymous local
        self.compile(node.end_expr)
        end_idx = len(self.locals)
        self.locals.append({"name": f"_end_{node.var_name}", "depth": self.scope_depth})
        
        # Determine step: push OP_GET_LOCAL i, push OP_GET_LOCAL end, OP_LTE.
        # Jump if false to push -1, else push 1.
        self.emit_byte(OpCode.OP_GET_LOCAL, line)
        self.emit_byte(i_idx, line)
        self.emit_byte(OpCode.OP_GET_LOCAL, line)
        self.emit_byte(end_idx, line)
        self.emit_byte(OpCode.OP_LTE, line)
        
        step_jump = self.emit_jump(OpCode.OP_JUMP_IF_FALSE, line)
        self.emit_byte(OpCode.OP_POP, line)  # Pop condition
        
        # Push step = 1
        one_idx = self.add_constant(1)
        self.emit_byte(OpCode.OP_CONSTANT, line)
        self.emit_byte(one_idx, line)
        
        skip_step_jump = self.emit_jump(OpCode.OP_JUMP, line)
        self.patch_jump(step_jump)
        self.emit_byte(OpCode.OP_POP, line)  # Pop condition
        
        # Push step = -1
        neg_one_idx = self.add_constant(-1)
        self.emit_byte(OpCode.OP_CONSTANT, line)
        self.emit_byte(neg_one_idx, line)
        
        self.patch_jump(skip_step_jump)
        step_idx = len(self.locals)
        self.locals.append({"name": f"_step_{node.var_name}", "depth": self.scope_depth})
        
        # Loop start offset
        loop_start = len(self.current_function.chunk.code)
        
        # Loop condition evaluation: (i - end) * step <= 0
        # 1. Load i
        self.emit_byte(OpCode.OP_GET_LOCAL, line)
        self.emit_byte(i_idx, line)
        # 2. Load end
        self.emit_byte(OpCode.OP_GET_LOCAL, line)
        self.emit_byte(end_idx, line)
        # 3. Sub
        self.emit_byte(OpCode.OP_SUB, line)
        # 4. Load step
        self.emit_byte(OpCode.OP_GET_LOCAL, line)
        self.emit_byte(step_idx, line)
        # 5. Mul
        self.emit_byte(OpCode.OP_MUL, line)
        # 6. Push 0
        zero_idx = self.add_constant(0)
        self.emit_byte(OpCode.OP_CONSTANT, line)
        self.emit_byte(zero_idx, line)
        # 7. LTE
        self.emit_byte(OpCode.OP_LTE, line)
        
        exit_jump = self.emit_jump(OpCode.OP_JUMP_IF_FALSE, line)
        self.emit_byte(OpCode.OP_POP, line)  # Pop condition
        
        # Compile body
        for stmt in node.body:
            self.compile(stmt)
            
        # Increment i: i = i + step
        self.emit_byte(OpCode.OP_GET_LOCAL, line)
        self.emit_byte(i_idx, line)
        self.emit_byte(OpCode.OP_GET_LOCAL, line)
        self.emit_byte(step_idx, line)
        self.emit_byte(OpCode.OP_ADD, line)
        self.emit_byte(OpCode.OP_SET_LOCAL, line)
        self.emit_byte(i_idx, line)
        self.emit_byte(OpCode.OP_POP, line)  # Pop value returned by OP_SET_LOCAL
        
        # Jump back to loop start
        self.emit_loop(loop_start, line)
        
        # Exit label
        self.patch_jump(exit_jump)
        self.emit_byte(OpCode.OP_POP, line)  # Pop loop condition value
        
        # Pop i, end, step
        self.end_scope(line)

    def visit_FuncDefNode(self, node):
        line = node.line if hasattr(node, 'line') else 1
        func_vm = self.compile_function(node)
        func_idx = self.add_constant(func_vm)
        
        if self.scope_depth > 0 or node.name == "anonymous":
            self.emit_byte(OpCode.OP_CONSTANT, line)
            self.emit_byte(func_idx, line)
            if node.name != "anonymous" and self.scope_depth > 0:
                self.locals.append({"name": node.name, "depth": self.scope_depth})
        else:
            # Global function declaration
            self.emit_byte(OpCode.OP_CONSTANT, line)
            self.emit_byte(func_idx, line)
            name_idx = self.add_constant(node.name)
            self.emit_byte(OpCode.OP_DEFINE_GLOBAL, line)
            self.emit_byte(name_idx, line)

    def visit_FuncCallNode(self, node):
        line = node.line if hasattr(node, 'line') else 1
        # Push the function object onto the stack
        if self.scope_depth > 0:
            idx = self.resolve_local(node.name)
            if idx != -1:
                self.emit_byte(OpCode.OP_GET_LOCAL, line)
                self.emit_byte(idx, line)
            else:
                name_idx = self.add_constant(node.name)
                self.emit_byte(OpCode.OP_GET_GLOBAL, line)
                self.emit_byte(name_idx, line)
        else:
            name_idx = self.add_constant(node.name)
            self.emit_byte(OpCode.OP_GET_GLOBAL, line)
            self.emit_byte(name_idx, line)
            
        # Push all arguments
        for arg in node.args:
            self.compile(arg)
            
        # Call instruction
        self.emit_byte(OpCode.OP_CALL, line)
        self.emit_byte(len(node.args), line)

    def visit_ReturnNode(self, node):
        line = node.line if hasattr(node, 'line') else 1
        if node.expr is not None:
            self.compile(node.expr)
        else:
            self.emit_byte(OpCode.OP_NULL, line)
        self.emit_byte(OpCode.OP_RETURN, line)

    def visit_MemberAccessNode(self, node):
        line = node.line if hasattr(node, 'line') else 1
        self.compile(node.obj)
        member_idx = self.add_constant(node.member)
        self.emit_byte(OpCode.OP_GET_MEMBER, line)
        self.emit_byte(member_idx, line)

    def visit_MethodCallNode(self, node):
        line = node.line if hasattr(node, 'line') else 1
        self.compile(node.obj)
        for arg in node.args:
            self.compile(arg)
        method_idx = self.add_constant(node.method)
        self.emit_byte(OpCode.OP_CALL_METHOD, line)
        self.emit_byte(method_idx, line)
        self.emit_byte(len(node.args), line)

    def visit_DictNode(self, node):
        line = node.line if hasattr(node, 'line') else 1
        for k, v in zip(node.keys, node.values):
            self.compile(k)
            self.compile(v)
        self.emit_byte(OpCode.OP_BUILD_DICT, line)
        self.emit_byte(len(node.keys), line)

    def visit_ListNode(self, node):
        line = node.line if hasattr(node, 'line') else 1
        for el in node.elements:
            self.compile(el)
        self.emit_byte(OpCode.OP_BUILD_LIST, line)
        self.emit_byte(len(node.elements), line)

    def compile_class_body(self, class_node):
        fn_compiler = Compiler(self.filename)
        fn_compiler.current_function = NgapakVMFunction(f"__class_body_{class_node.name}", 0)
        fn_compiler.scope_depth = 1
        
        # Slot 0 is class body function itself
        fn_compiler.locals.append({"name": f"__class_body_{class_node.name}", "depth": 0})
        
        for stmt in class_node.body:
            fn_compiler.compile(stmt)
            
        line = class_node.line if hasattr(class_node, 'line') else 1
        defined_locals = [loc for loc in fn_compiler.locals if loc["depth"] == 1]
        
        for idx, loc in enumerate(fn_compiler.locals):
            if loc["depth"] == 1:
                # Key (name)
                name_idx = fn_compiler.add_constant(loc["name"])
                fn_compiler.emit_byte(OpCode.OP_CONSTANT, line)
                fn_compiler.emit_byte(name_idx, line)
                # Value (local slot)
                fn_compiler.emit_byte(OpCode.OP_GET_LOCAL, line)
                fn_compiler.emit_byte(idx, line)
                
        fn_compiler.emit_byte(OpCode.OP_BUILD_DICT, line)
        fn_compiler.emit_byte(len(defined_locals), line)
        fn_compiler.emit_byte(OpCode.OP_RETURN, line)
        
        return fn_compiler.current_function

    def visit_ClassDefNode(self, node):
        line = node.line if hasattr(node, 'line') else 1
        body_fn = self.compile_class_body(node)
        body_fn_idx = self.add_constant(body_fn)
        
        # Call the body function to get attributes dict
        self.emit_byte(OpCode.OP_CONSTANT, line)
        self.emit_byte(body_fn_idx, line)
        self.emit_byte(OpCode.OP_CALL, line)
        self.emit_byte(0, line)
        
        name_idx = self.add_constant(node.name)
        parent_idx = self.add_constant(node.parent_name) if node.parent_name else 0xff
        
        self.emit_byte(OpCode.OP_DEFINE_CLASS, line)
        self.emit_byte(name_idx, line)
        self.emit_byte(parent_idx, line)

    def visit_MemberAssignNode(self, node):
        line = node.line if hasattr(node, 'line') else 1
        self.compile(node.obj)
        self.compile(node.expr)
        member_idx = self.add_constant(node.member)
        self.emit_byte(OpCode.OP_SET_MEMBER, line)
        self.emit_byte(member_idx, line)
