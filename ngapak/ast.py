# Abstract Syntax Tree (AST) node definitions for NgapakIn

class ASTNode:
    def accept(self, visitor):
        raise NotImplementedError()

class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_ProgramNode(self)

class TulisNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_TulisNode(self)

class VarAssignNode(ASTNode):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_VarAssignNode(self)

class VarAccessNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_VarAccessNode(self)

class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op  # This will be the Token itself to access operator type/line info
        self.right = right

    def accept(self, visitor):
        return visitor.visit_BinOpNode(self)

class LiteralNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_LiteralNode(self)

class IfNode(ASTNode):
    def __init__(self, condition, true_branch, false_branch=None):
        self.condition = condition
        self.true_branch = true_branch  # list of statements
        self.false_branch = false_branch  # list of statements or None

    def accept(self, visitor):
        return visitor.visit_IfNode(self)

class ForNode(ASTNode):
    def __init__(self, var_name, start_expr, end_expr, body):
        self.var_name = var_name
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.body = body  # list of statements

    def accept(self, visitor):
        return visitor.visit_ForNode(self)

class FuncDefNode(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params  # list of parameter names as strings
        self.body = body  # list of statements

    def accept(self, visitor):
        return visitor.visit_FuncDefNode(self)

class FuncCallNode(ASTNode):
    def __init__(self, name, args):
        self.name = name  # name of the function as a string
        self.args = args  # list of argument expressions

    def accept(self, visitor):
        return visitor.visit_FuncCallNode(self)

class ReturnNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr  # expression node or None

    def accept(self, visitor):
        return visitor.visit_ReturnNode(self)

class MemberAccessNode(ASTNode):
    def __init__(self, obj, member):
        self.obj = obj        # expression representing the object
        self.member = member  # string representing the attribute/field name

    def accept(self, visitor):
        return visitor.visit_MemberAccessNode(self)

class MethodCallNode(ASTNode):
    def __init__(self, obj, method, args):
        self.obj = obj        # expression representing the object
        self.method = method  # string representing the method name
        self.args = args      # list of argument expressions

    def accept(self, visitor):
        return visitor.visit_MethodCallNode(self)

class DictNode(ASTNode):
    def __init__(self, keys, values):
        self.keys = keys      # list of key expressions
        self.values = values  # list of value expressions

    def accept(self, visitor):
        return visitor.visit_DictNode(self)

class ListNode(ASTNode):
    def __init__(self, elements):
        self.elements = elements  # list of element expressions

    def accept(self, visitor):
        return visitor.visit_ListNode(self)

class ClassDefNode(ASTNode):
    def __init__(self, name, parent_name, body):
        self.name = name
        self.parent_name = parent_name
        self.body = body

    def accept(self, visitor):
        return visitor.visit_ClassDefNode(self)

class MemberAssignNode(ASTNode):
    def __init__(self, obj, member, expr):
        self.obj = obj
        self.member = member
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_MemberAssignNode(self)
