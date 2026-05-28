import unittest
from ngapak.lexer import Lexer
from ngapak.parser import Parser
from ngapak.compiler import Compiler
from ngapak.opcode import OpCode

class TestCompiler(unittest.TestCase):
    def compile_source(self, source):
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        return compiler.compile(ast)

    def test_compile_constant(self):
        func = self.compile_source("tulis 42")
        code = func.chunk.code
        
        # Expecting: OP_CONSTANT, index, OP_PRINT
        self.assertEqual(code[0], OpCode.OP_CONSTANT)
        const_idx = code[1]
        self.assertEqual(func.chunk.constants[const_idx], 42)
        self.assertEqual(code[2], OpCode.OP_PRINT)

    def test_compile_binary_ops(self):
        func = self.compile_source("tulis 10 + 5")
        code = func.chunk.code
        
        # Expecting OP_CONSTANT (10), OP_CONSTANT (5), OP_ADD, OP_PRINT
        self.assertIn(OpCode.OP_ADD, code)
        self.assertEqual(code[-2], OpCode.OP_ADD)
        self.assertEqual(code[-1], OpCode.OP_PRINT)

    def test_compile_globals(self):
        func = self.compile_source("""
        x = 100
        tulis x
        """)
        code = func.chunk.code
        
        # Expect OP_CONSTANT, OP_DEFINE_GLOBAL, OP_GET_GLOBAL, OP_PRINT
        self.assertIn(OpCode.OP_DEFINE_GLOBAL, code)
        self.assertIn(OpCode.OP_GET_GLOBAL, code)

    def test_compile_locals(self):
        func = self.compile_source("""
        gawe test()
            x = 10
            tulis x
        rampung
        """)
        # We need to look inside the compiled function object constants
        nested_func = None
        for const in func.chunk.constants:
            if hasattr(const, 'chunk'):
                nested_func = const
                break
                
        self.assertIsNotNone(nested_func)
        code = nested_func.chunk.code
        
        # Locals compilation should use OP_GET_LOCAL or assign to locals
        # Slot 0: function itself, slot 1: x
        # Should push 10, define local (just stays on stack), OP_GET_LOCAL slot 1, OP_PRINT
        self.assertIn(OpCode.OP_GET_LOCAL, code)

if __name__ == '__main__':
    unittest.main()
