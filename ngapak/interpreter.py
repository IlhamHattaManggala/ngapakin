# Interpreter implementation for NgapakIn

from .ast import *
from .token import *
from .environment import Environment, NgapakFunction, NgapakCallable, ReturnException
from .errors import NgapakRuntimeError
from .builtins import BUILTINS

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        
        # Register built-in functions
        for name, func in BUILTINS.items():
            self.globals.define(name, func)

    def interpret(self, program_node):
        try:
            for stmt in program_node.statements:
                self.execute(stmt)
        except NgapakRuntimeError as e:
            raise e
        except Exception as e:
            raise NgapakRuntimeError(f"Kesalahan sistem saat eksekusi: {str(e)}")

    def execute(self, stmt):
        return stmt.accept(self)

    def evaluate(self, expr):
        return expr.accept(self)

    def execute_block(self, statements, env):
        previous_env = self.environment
        try:
            self.environment = env
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous_env

    def is_truthy(self, val):
        if val is None:
            return False
        if val is False:
            return False
        return True

    def visit_ProgramNode(self, node):
        for stmt in node.statements:
            self.execute(stmt)
        return None

    def visit_TulisNode(self, node):
        value = self.evaluate(node.expr)
        if value is True:
            print("bener")
        elif value is False:
            print("salah")
        elif value is None:
            print("kosong")
        else:
            print(value)
        return None

    def visit_VarAssignNode(self, node):
        value = self.evaluate(node.expr)
        self.environment.assign(node.name, value)
        return value

    def visit_VarAccessNode(self, node):
        try:
            return self.environment.get(node.name)
        except KeyError as e:
            raise NgapakRuntimeError(str(e))

    def visit_BinOpNode(self, node):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        op_type = node.op.type
        line = node.op.line
        col = node.op.column

        if op_type == T_PLUS:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise NgapakRuntimeError(f"Operasi '+' tidak didukung untuk tipe data {type(left).__name__} dan {type(right).__name__}", line, col)
            
        if op_type == T_MINUS:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left - right
            raise NgapakRuntimeError("Operasi '-' hanya didukung untuk angka", line, col)

        if op_type == T_MUL:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left * right
            if isinstance(left, str) and isinstance(right, int):
                return left * right
            if isinstance(left, int) and isinstance(right, str):
                return left * right
            raise NgapakRuntimeError("Operasi '*' hanya didukung untuk perkalian angka (atau perkalian string dengan angka)", line, col)

        if op_type == T_DIV:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                if right == 0:
                    raise NgapakRuntimeError("Pembagian dengan nol tidak diperbolehkan", line, col)
                return left / right
            raise NgapakRuntimeError("Operasi '/' hanya didukung untuk angka", line, col)

        if op_type == T_EQ:
            return left == right
        if op_type == T_NEQ:
            return left != right

        if op_type in (T_LT, T_GT, T_LTE, T_GTE):
            if type(left) != type(right) and not (isinstance(left, (int, float)) and isinstance(right, (int, float))):
                raise NgapakRuntimeError(f"Tidak dapat membandingkan tipe data {type(left).__name__} dengan {type(right).__name__}", line, col)
            
            if op_type == T_LT:
                return left < right
            if op_type == T_GT:
                return left > right
            if op_type == T_LTE:
                return left <= right
            if op_type == T_GTE:
                return left >= right

        raise NgapakRuntimeError(f"Operator tidak dikenal: {node.op.value}", line, col)

    def visit_LiteralNode(self, node):
        return node.value

    def visit_IfNode(self, node):
        condition = self.evaluate(node.condition)
        if self.is_truthy(condition):
            for stmt in node.true_branch:
                self.execute(stmt)
        elif node.false_branch is not None:
            for stmt in node.false_branch:
                self.execute(stmt)
        return None

    def visit_ForNode(self, node):
        start = self.evaluate(node.start_expr)
        end = self.evaluate(node.end_expr)
        
        if not isinstance(start, int) or not isinstance(end, int):
            raise NgapakRuntimeError("Nilai awal dan akhir loop 'baleni' harus berupa angka bulat (integer)")

        previous_env = self.environment
        loop_env = Environment(previous_env)
        self.environment = loop_env

        step = 1 if start <= end else -1
        # inclusive range
        for i in range(start, end + step, step):
            loop_env.define(node.var_name, i)
            for stmt in node.body:
                self.execute(stmt)

        self.environment = previous_env
        return None

    def visit_FuncDefNode(self, node):
        func = NgapakFunction(node, self.environment)
        self.environment.define(node.name, func)
        return None

    def visit_FuncCallNode(self, node):
        try:
            callee = self.environment.get(node.name)
        except KeyError as e:
            raise NgapakRuntimeError(str(e))

        if not isinstance(callee, NgapakCallable):
            raise NgapakRuntimeError(f"'{node.name}' bukan merupakan fungsi yang dapat dipanggil.")

        arguments = [self.evaluate(arg) for arg in node.args]

        if len(arguments) != callee.arity():
            raise NgapakRuntimeError(f"Fungsi '{node.name}' mengharapkan {callee.arity()} argumen, tetapi menerima {len(arguments)}.")

        return callee.call(self, arguments)

    def visit_ReturnNode(self, node):
        value = None
        if node.expr is not None:
            value = self.evaluate(node.expr)
        raise ReturnException(value)
