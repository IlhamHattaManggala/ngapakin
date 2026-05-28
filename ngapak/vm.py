# Stack Virtual Machine implementation for NgapakIn

from .opcode import OpCode
from .frame import CallFrame
from .errors import NgapakRuntimeError
from .bytecode import NgapakVMFunction
from .environment import NgapakCallable
from .builtins import BUILTINS
from .debugger import disassemble_instruction

class NgapakClass:
    def __init__(self, name, parent_class, attributes):
        self.name = name
        self.parent_class = parent_class
        self.attributes = attributes

    def __call__(self, *args):
        return NgapakInstance(self)

    def __repr__(self):
        return f"<Kelas {self.name}>"

class NgapakInstance:
    def __init__(self, ngapak_class):
        self.ngapak_class = ngapak_class
        self.fields = {}

    @property
    def class_attributes(self):
        attrs = {}
        if isinstance(self.ngapak_class.parent_class, NgapakClass):
            attrs.update(self.ngapak_class.parent_class.class_attributes)
        elif self.ngapak_class.parent_class:
            # Python base class attributes
            for attr_name in dir(self.ngapak_class.parent_class):
                if not attr_name.startswith("__"):
                    attrs[attr_name] = getattr(self.ngapak_class.parent_class, attr_name)
        attrs.update(self.ngapak_class.attributes)
        return attrs

    def __repr__(self):
        return f"<Instance of {self.ngapak_class.name}>"

class VM:
    def __init__(self):
        self.globals = {}
        self.stack = []
        self.frames = []
        self.debug_mode = False
        self.filename = "<stdin>"

        # Register built-in functions in globals
        for name, func in BUILTINS.items():
            self.globals[name] = func

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        if not self.stack:
            raise NgapakRuntimeError("VM stack underflow.")
        return self.stack.pop()

    def peek(self, distance=0):
        if len(self.stack) < distance + 1:
            raise NgapakRuntimeError("VM stack underflow during peek.")
        return self.stack[-(distance + 1)]

    def run(self, main_function, debug_mode=False, filename="<stdin>"):
        self.debug_mode = debug_mode
        self.filename = filename
        self.stack = []
        self.frames = []
        
        # Injects VM reference into router global if present
        if "rute" in self.globals:
            self.globals["rute"].vm = self
            
        # Slot 0 on stack is reserved for the main function
        self.push(main_function)
        
        # Top-level call frame
        self.frames.append(CallFrame(main_function, ip=0, slots=0))
        
        return self.execute()

    def execute_callable(self, callee, arguments):
        """Executes a VM function in-place with isolated stack context."""
        prev_stack = list(self.stack)
        prev_frames = list(self.frames)
        
        self.stack = []
        self.frames = []
        
        self.push(callee)
        for arg in arguments:
            self.push(arg)
            
        self.frames.append(CallFrame(callee, ip=0, slots=0))
        self.execute()
        
        res = self.pop() if self.stack else None
        
        self.stack = prev_stack
        self.frames = prev_frames
        return res

    def execute(self):
        while len(self.frames) > 0:
            frame = self.frames[-1]
            chunk = frame.function.chunk
            
            if frame.ip >= len(chunk.code):
                # Implicit return if IP reaches end of chunk
                self.frames.pop()
                continue
                
            if self.debug_mode:
                print(f"\n[Debugger] IP: {frame.ip} | Baris: {line} | Fungsi: {frame.function.name}")
                print(f"  Stack: {repr(self.stack)}")
                disassemble_instruction(chunk, frame.ip)
                while True:
                    cmd = input("dbg> ").strip().lower()
                    if not cmd or cmd in ("s", "step"):
                        break
                    elif cmd in ("c", "continue"):
                        self.debug_mode = False
                        break
                    elif cmd in ("st", "stack"):
                        print(f"Stack: {repr(self.stack)}")
                    elif cmd in ("l", "locals"):
                        print(f"Locals (slots from stack index {frame.slots}):")
                        for idx, val in enumerate(self.stack[frame.slots:]):
                            print(f"  Slot {idx}: {repr(val)}")
                    elif cmd in ("g", "globals"):
                        print("Globals:")
                        for k, v in self.globals.items():
                            print(f"  {k}: {repr(v)}")
                    elif cmd in ("q", "quit", "exit"):
                        import sys
                        sys.exit(0)
                    else:
                        print("Perintah tidak dikenal. Gunakan: s (step), c (continue), st (stack), l (locals), g (globals), q (quit)")

                
            # Read opcode
            opcode = chunk.code[frame.ip]
            line = chunk.lines[frame.ip]
            frame.ip += 1
            
            try:
                if opcode == OpCode.OP_CONSTANT:
                    const_idx = chunk.code[frame.ip]
                    frame.ip += 1
                    self.push(chunk.constants[const_idx])
                    
                elif opcode == OpCode.OP_TRUE:
                    self.push(True)
                    
                elif opcode == OpCode.OP_FALSE:
                    self.push(False)
                    
                elif opcode == OpCode.OP_NULL:
                    self.push(None)
                    
                elif opcode == OpCode.OP_POP:
                    self.pop()
                    
                elif opcode == OpCode.OP_DEFINE_GLOBAL:
                    name_idx = chunk.code[frame.ip]
                    frame.ip += 1
                    name = chunk.constants[name_idx]
                    val = self.pop()
                    self.globals[name] = val
                    
                elif opcode == OpCode.OP_GET_GLOBAL:
                    name_idx = chunk.code[frame.ip]
                    frame.ip += 1
                    name = chunk.constants[name_idx]
                    if name not in self.globals:
                        raise NgapakRuntimeError(f"Variabel atau fungsi '{name}' tidak didefinisikan.", line)
                    self.push(self.globals[name])
                    
                elif opcode == OpCode.OP_SET_GLOBAL:
                    name_idx = chunk.code[frame.ip]
                    frame.ip += 1
                    name = chunk.constants[name_idx]
                    if name not in self.globals:
                        raise NgapakRuntimeError(f"Variabel '{name}' belum didefinisikan.", line)
                    val = self.peek(0)
                    self.globals[name] = val
                    
                elif opcode == OpCode.OP_GET_LOCAL:
                    slot = chunk.code[frame.ip]
                    frame.ip += 1
                    self.push(self.stack[frame.slots + slot])
                    
                elif opcode == OpCode.OP_SET_LOCAL:
                    slot = chunk.code[frame.ip]
                    frame.ip += 1
                    val = self.peek(0)
                    self.stack[frame.slots + slot] = val
                    
                elif opcode == OpCode.OP_ADD:
                    b = self.pop()
                    a = self.pop()
                    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                        self.push(a + b)
                    elif isinstance(a, str) and isinstance(b, str):
                        self.push(a + b)
                    else:
                        raise NgapakRuntimeError(f"Operasi '+' tidak didukung untuk tipe data {type(a).__name__} dan {type(b).__name__}.", line)
                        
                elif opcode == OpCode.OP_SUB:
                    b = self.pop()
                    a = self.pop()
                    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                        self.push(a - b)
                    else:
                        raise NgapakRuntimeError("Operasi '-' hanya didukung untuk angka.", line)
                        
                elif opcode == OpCode.OP_MUL:
                    b = self.pop()
                    a = self.pop()
                    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                        self.push(a * b)
                    elif isinstance(a, str) and isinstance(b, int):
                        self.push(a * b)
                    elif isinstance(a, int) and isinstance(b, str):
                        self.push(a * b)
                    else:
                        raise NgapakRuntimeError("Operasi '*' hanya didukung untuk perkalian angka (atau string dengan angka).", line)
                        
                elif opcode == OpCode.OP_DIV:
                    b = self.pop()
                    a = self.pop()
                    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                        if b == 0:
                            raise NgapakRuntimeError("Pembagian dengan nol tidak diperbolehkan.", line)
                        self.push(a / b)
                    else:
                        raise NgapakRuntimeError("Operasi '/' hanya didukung untuk angka.", line)
                        
                elif opcode == OpCode.OP_EQ:
                    b = self.pop()
                    a = self.pop()
                    self.push(a == b)
                    
                elif opcode == OpCode.OP_NEQ:
                    b = self.pop()
                    a = self.pop()
                    self.push(a != b)
                    
                elif opcode == OpCode.OP_LT:
                    b = self.pop()
                    a = self.pop()
                    self.push(a < b)
                    
                elif opcode == OpCode.OP_GT:
                    b = self.pop()
                    a = self.pop()
                    self.push(a > b)
                    
                elif opcode == OpCode.OP_LTE:
                    b = self.pop()
                    a = self.pop()
                    self.push(a <= b)
                    
                elif opcode == OpCode.OP_GTE:
                    b = self.pop()
                    a = self.pop()
                    self.push(a >= b)
                    
                elif opcode == OpCode.OP_JUMP:
                    high = chunk.code[frame.ip]
                    low = chunk.code[frame.ip + 1]
                    frame.ip += 2
                    offset = (high << 8) | low
                    frame.ip += offset
                    
                elif opcode == OpCode.OP_JUMP_IF_FALSE:
                    high = chunk.code[frame.ip]
                    low = chunk.code[frame.ip + 1]
                    frame.ip += 2
                    offset = (high << 8) | low
                    cond = self.peek(0)
                    if not cond:  # falsy check
                        frame.ip += offset
                        
                elif opcode == OpCode.OP_LOOP:
                    high = chunk.code[frame.ip]
                    low = chunk.code[frame.ip + 1]
                    frame.ip += 2
                    offset = (high << 8) | low
                    frame.ip -= offset
                    
                elif opcode == OpCode.OP_CALL:
                    arity = chunk.code[frame.ip]
                    frame.ip += 1
                    callee = self.peek(arity)
                    
                    if isinstance(callee, NgapakVMFunction):
                        if arity != callee.arity:
                            raise NgapakRuntimeError(f"Fungsi '{callee.name}' mengharapkan {callee.arity} argumen, tetapi menerima {arity}.", line)
                        
                        slots_offset = len(self.stack) - 1 - arity
                        new_frame = CallFrame(callee, ip=0, slots=slots_offset)
                        self.frames.append(new_frame)
                        
                    elif isinstance(callee, NgapakClass):
                        # Instantiate Class: User(args)
                        instance = NgapakInstance(callee)
                        constructor = callee.attributes.get("anyar")
                        
                        args = []
                        for _ in range(arity):
                            args.append(self.pop())
                        args.reverse()
                        self.pop()  # Pop the class object itself
                        
                        if constructor:
                            if isinstance(constructor, NgapakVMFunction):
                                self.execute_callable(constructor, [instance] + args)
                            elif callable(constructor):
                                constructor(instance, *args)
                                
                        self.push(instance)
                        
                    elif isinstance(callee, NgapakCallable):
                        if arity != callee.arity():
                            raise NgapakRuntimeError(f"Fungsi bawaan mengharapkan {callee.arity()} argumen, tetapi menerima {arity}.", line)
                        
                        args = []
                        for _ in range(arity):
                            args.append(self.pop())
                        args.reverse()
                        
                        self.pop()  # Pop the function object
                        res = callee.call(self, args)
                        self.push(res)
                    elif callable(callee):
                        # Support standard Python functions and methods as callbacks
                        args = []
                        for _ in range(arity):
                            args.append(self.pop())
                        args.reverse()
                        
                        self.pop()  # Pop the function object
                        res = callee(*args)
                        self.push(res)
                    else:
                        raise NgapakRuntimeError("Hanya fungsi atau kelas yang dapat dipanggil.", line)
                        
                elif opcode == OpCode.OP_RETURN:
                    result = self.pop()
                    old_frame = self.frames.pop()
                    
                    # Pop all local variables and the function object
                    while len(self.stack) > old_frame.slots:
                        self.pop()
                        
                    self.push(result)
                    
                elif opcode == OpCode.OP_PRINT:
                    val = self.pop()
                    if val is True:
                        print("bener")
                    elif val is False:
                        print("salah")
                    elif val is None:
                        print("kosong")
                    else:
                        print(val)
                        
                elif opcode == OpCode.OP_GET_MEMBER:
                    name_idx = chunk.code[frame.ip]
                    frame.ip += 1
                    name = chunk.constants[name_idx]
                    obj = self.pop()
                    
                    val = None
                    if isinstance(obj, dict):
                        val = obj.get(name)
                    elif isinstance(obj, NgapakInstance):
                        if name in obj.fields:
                            val = obj.fields[name]
                        elif name in obj.class_attributes:
                            val = obj.class_attributes[name]
                        elif obj.ngapak_class.parent_class and hasattr(obj.ngapak_class.parent_class, name):
                            val = getattr(obj.ngapak_class.parent_class, name)
                        else:
                            val = None
                    elif isinstance(obj, NgapakClass):
                        if name in obj.attributes:
                            val = obj.attributes[name]
                        elif obj.parent_class and hasattr(obj.parent_class, name):
                            val = getattr(obj.parent_class, name)
                        else:
                            val = None
                    else:
                        try:
                            val = getattr(obj, name)
                        except AttributeError:
                            val = None
                    self.push(val)
                    
                elif opcode == OpCode.OP_CALL_METHOD:
                    name_idx = chunk.code[frame.ip]
                    arity = chunk.code[frame.ip + 1]
                    frame.ip += 2
                    name = chunk.constants[name_idx]
                    
                    obj = self.peek(arity)
                    
                    method = None
                    if isinstance(obj, dict):
                        method = obj.get(name) if name not in dir(obj) else getattr(obj, name)
                    elif isinstance(obj, NgapakInstance):
                        if name in obj.class_attributes:
                            method = obj.class_attributes[name]
                        elif obj.ngapak_class.parent_class and hasattr(obj.ngapak_class.parent_class, name):
                            method = getattr(obj.ngapak_class.parent_class, name)
                    elif isinstance(obj, NgapakClass):
                        if name in obj.attributes:
                            method = obj.attributes[name]
                        elif obj.parent_class:
                            if hasattr(obj.parent_class, name):
                                method = getattr(obj.parent_class, name)
                    else:
                        try:
                            method = getattr(obj, name)
                        except AttributeError:
                            raise NgapakRuntimeError(f"Objek tipe '{type(obj).__name__}' tidak memiliki metode '{name}'.", line)
                            
                    if isinstance(method, NgapakVMFunction):
                        # Class method: stack currently has: [obj, arg1, ..., argN]
                        # We want to change it to: [method, obj, arg1, ..., argN]
                        obj_pos = len(self.stack) - 1 - arity
                        self.stack.insert(obj_pos, method)
                        new_frame = CallFrame(method, ip=0, slots=obj_pos)
                        self.frames.append(new_frame)
                    elif callable(method):
                        args = []
                        for _ in range(arity):
                            args.append(self.pop())
                        args.reverse()
                        
                        self.pop()  # Pop the object
                        if isinstance(obj, (NgapakInstance, NgapakClass)):
                            func = method
                            if hasattr(method, '__func__'):
                                func = method.__func__
                            res = func(obj, *args)
                        else:
                            res = method(*args)
                        self.push(res)
                    else:
                        raise NgapakRuntimeError(f"Metode '{name}' tidak dapat dipanggil.", line)
                        
                elif opcode == OpCode.OP_BUILD_DICT:
                    arity = chunk.code[frame.ip]
                    frame.ip += 1
                    
                    d = {}
                    pairs = []
                    for _ in range(arity):
                        val = self.pop()
                        key = self.pop()
                        pairs.append((key, val))
                    pairs.reverse()
                    for k, v in pairs:
                        d[k] = v
                    self.push(d)
                    
                elif opcode == OpCode.OP_BUILD_LIST:
                    arity = chunk.code[frame.ip]
                    frame.ip += 1
                    
                    lst = []
                    for _ in range(arity):
                        lst.append(self.pop())
                    lst.reverse()
                    self.push(lst)

                elif opcode == OpCode.OP_DEFINE_CLASS:
                    name_idx = chunk.code[frame.ip]
                    parent_idx = chunk.code[frame.ip + 1]
                    frame.ip += 2
                    
                    name = chunk.constants[name_idx]
                    parent_name = chunk.constants[parent_idx] if parent_idx != 0xff else None
                    
                    attributes = self.pop()
                    if not isinstance(attributes, dict):
                        attributes = {}
                        
                    parent_class = None
                    if parent_name:
                        parent_class = self.globals.get(parent_name)
                        if not parent_class:
                            raise NgapakRuntimeError(f"Kelas induk '{parent_name}' tidak ditemukan.", line)
                            
                    cls_obj = NgapakClass(name, parent_class, attributes)
                    self.globals[name] = cls_obj

                elif opcode == OpCode.OP_SET_MEMBER:
                    name_idx = chunk.code[frame.ip]
                    frame.ip += 1
                    name = chunk.constants[name_idx]
                    
                    val = self.pop()
                    obj = self.pop()
                    
                    if isinstance(obj, dict):
                        obj[name] = val
                    elif isinstance(obj, NgapakInstance):
                        obj.fields[name] = val
                    else:
                        try:
                            setattr(obj, name, val)
                        except AttributeError:
                            raise NgapakRuntimeError(f"Tidak dapat mengubah properti '{name}' pada objek tipe '{type(obj).__name__}'.", line)
                    self.push(val)
                    
                else:
                    raise NgapakRuntimeError(f"Instruksi VM tidak dikenal: {opcode}.", line)
                    
            except NgapakRuntimeError as e:
                if e.filename is None:
                    e.filename = self.filename
                raise e
            except Exception as e:
                raise NgapakRuntimeError(f"Runtime VM error: {str(e)}", line, filename=self.filename)
                
        return None
