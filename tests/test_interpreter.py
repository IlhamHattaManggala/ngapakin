import unittest
import io
import sys
from ngapak.lexer import Lexer
from ngapak.parser import Parser
from ngapak.interpreter import Interpreter
from ngapak.errors import NgapakRuntimeError

class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self.interpreter = Interpreter()

    def run_source(self, source):
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            self.interpreter.interpret(ast)
        finally:
            sys.stdout = sys.__stdout__
            
        return captured_output.getvalue()

    def test_arithmetic(self):
        source = "tulis 10 + 5 * 2 - 4 / 2"
        # 10 + 10 - 2 = 18
        output = self.run_source(source).strip()
        self.assertEqual(float(output), 18.0)

    def test_variable_assignment(self):
        source = """
        x = 5
        y = x + 10
        tulis y
        """
        output = self.run_source(source).strip()
        self.assertEqual(int(output), 15)

    def test_conditionals(self):
        source = """
        umur = 20
        nek umur >= 17 ya
            tulis "dewasa"
        liyane
            tulis "anak"
        rampung
        """
        output = self.run_source(source).strip()
        self.assertEqual(output, "dewasa")

    def test_loops(self):
        source = """
        baleni i saka 1 nganti 3
            tulis i
        rampung
        """
        output = self.run_source(source).strip().split()
        self.assertEqual(output, ["1", "2", "3"])

    def test_functions(self):
        source = """
        gawe pangkat(x)
            balekna x * x
        rampung
        
        hasil = pangkat(4)
        tulis hasil
        """
        output = self.run_source(source).strip()
        self.assertEqual(int(output), 16)

    def test_builtins(self):
        source = """
        nama = "ilham"
        tulis dowo(nama)
        tulis teks(bener)
        tulis angka("12.5")
        """
        output = self.run_source(source).strip().split()
        self.assertEqual(output, ["5", "bener", "12.5"])

    def test_runtime_error_div_zero(self):
        source = "tulis 5 / 0"
        with self.assertRaises(NgapakRuntimeError):
            self.run_source(source)

if __name__ == '__main__':
    unittest.main()
