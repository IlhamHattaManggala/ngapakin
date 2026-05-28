import unittest
from ngapak.lexer import Lexer
from ngapak.parser import Parser
from ngapak.ast import *

class TestParser(unittest.TestCase):
    def test_parse_tulis(self):
        source = 'tulis "Halo"'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertIsInstance(ast, ProgramNode)
        self.assertEqual(len(ast.statements), 1)
        self.assertIsInstance(ast.statements[0], TulisNode)
        self.assertIsInstance(ast.statements[0].expr, LiteralNode)
        self.assertEqual(ast.statements[0].expr.value, "Halo")

    def test_parse_assignment(self):
        source = 'x = 10 + 5'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertIsInstance(ast.statements[0], VarAssignNode)
        self.assertEqual(ast.statements[0].name, "x")
        self.assertIsInstance(ast.statements[0].expr, BinOpNode)

    def test_operator_precedence(self):
        source = 'x = 1 + 2 * 3'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        # 1 + (2 * 3)
        assign = ast.statements[0]
        plus_op = assign.expr
        self.assertEqual(plus_op.op.type, "PLUS")
        self.assertIsInstance(plus_op.left, LiteralNode)
        self.assertEqual(plus_op.left.value, 1)
        self.assertIsInstance(plus_op.right, BinOpNode)
        self.assertEqual(plus_op.right.op.type, "MUL")

    def test_parse_if(self):
        source = """
        nek x == 10 ya
            tulis "sepuluh"
        liyane
            tulis "bukan"
        rampung
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertIsInstance(ast.statements[0], IfNode)
        self.assertEqual(len(ast.statements[0].true_branch), 1)
        self.assertEqual(len(ast.statements[0].false_branch), 1)

    def test_parse_for(self):
        source = """
        baleni i saka 1 nganti 5
            tulis i
        rampung
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertIsInstance(ast.statements[0], ForNode)
        self.assertEqual(ast.statements[0].var_name, "i")
        self.assertEqual(len(ast.statements[0].body), 1)

    def test_parse_func(self):
        source = """
        gawe kali(a, b)
            balekna a * b
        rampung
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertIsInstance(ast.statements[0], FuncDefNode)
        self.assertEqual(ast.statements[0].name, "kali")
        self.assertEqual(ast.statements[0].params, ["a", "b"])
        self.assertEqual(len(ast.statements[0].body), 1)

if __name__ == '__main__':
    unittest.main()
