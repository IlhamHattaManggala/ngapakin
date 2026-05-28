import unittest
import io
import sys
from ngapak.lexer import Lexer
from ngapak.parser import Parser
from ngapak.compiler import Compiler
from ngapak.vm import VM
from ngapak.errors import NgapakRuntimeError

class TestVM(unittest.TestCase):
    def setUp(self):
        self.vm = VM()

    def run_source(self, source):
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        main_fn = compiler.compile(ast)
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            self.vm.run(main_fn)
        finally:
            sys.stdout = sys.__stdout__
            
        return captured_output.getvalue()

    def test_vm_arithmetic(self):
        source = "tulis (10 + 5) * 2 - 4 / 2"
        # (15 * 2) - 2 = 28
        output = self.run_source(source).strip()
        self.assertEqual(float(output), 28.0)

    def test_vm_global_variables(self):
        source = """
        x = 50
        y = x + 25
        tulis y
        """
        output = self.run_source(source).strip()
        self.assertEqual(int(output), 75)

    def test_vm_conditional_branching(self):
        source = """
        nilai = 80
        nek nilai >= 75 ya
            tulis "Lulus"
        liyane
            tulis "Gagal"
        rampung
        """
        output = self.run_source(source).strip()
        self.assertEqual(output, "Lulus")

    def test_vm_loops_forward(self):
        source = """
        baleni i saka 1 nganti 3
            tulis i
        rampung
        """
        output = self.run_source(source).strip().split()
        self.assertEqual(output, ["1", "2", "3"])

    def test_vm_loops_backward(self):
        source = """
        baleni i saka 3 nganti 1
            tulis i
        rampung
        """
        output = self.run_source(source).strip().split()
        self.assertEqual(output, ["3", "2", "1"])

    def test_vm_function_calls(self):
        source = """
        gawe pangkat(x)
            balekna x * x
        rampung
        
        tulis pangkat(5)
        """
        output = self.run_source(source).strip()
        self.assertEqual(int(output), 25)

    def test_vm_recursion(self):
        source = """
        gawe faktorial(n)
            nek n <= 1 ya
                balekna 1
            liyane
                balekna n * faktorial(n - 1)
            rampung
        rampung
        
        tulis faktorial(5)
        """
        output = self.run_source(source).strip()
        self.assertEqual(int(output), 120)

    def test_vm_div_by_zero_error(self):
        source = "tulis 10 / 0"
        with self.assertRaises(NgapakRuntimeError):
            self.run_source(source)

if __name__ == '__main__':
    unittest.main()
