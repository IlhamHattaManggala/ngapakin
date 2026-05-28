import unittest
from ngapak.lexer import Lexer
from ngapak.parser import Parser
from ngapak.compiler import Compiler
from ngapak.vm import VM

class TestVMFeatures(unittest.TestCase):
    def setUp(self):
        self.vm = VM()

    def run_source(self, source):
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        main_fn = compiler.compile(ast)
        self.vm.run(main_fn)

    def test_dict_literal(self):
        source = """
        d = ["name": "Hatta", "age": 20]
        tulis d.name
        tulis d.age
        """
        # Let's inspect variable state
        self.run_source(source)
        d = self.vm.globals["d"]
        self.assertEqual(d, {"name": "Hatta", "age": 20})

    def test_member_and_method_calls(self):
        # We define a custom object in globals
        class TestObj:
            def __init__(self):
                self.val = "Halo"
            def sapa(self, name):
                return f"{self.val} {name}"
                
        self.vm.globals["obj"] = TestObj()
        
        source = """
        tulis obj.val
        res = obj.sapa("Ilham")
        tulis res
        """
        self.run_source(source)
        self.assertEqual(self.vm.globals["res"], "Halo Ilham")

    def test_anonymous_function(self):
        source = """
        func = gawe(a)
            balekna a + 10
        rampung
        res = func(5)
        tulis res
        """
        self.run_source(source)
        self.assertEqual(self.vm.globals["res"], 15)

    def test_list_literal(self):
        source = """
        arr = ["Ilham", "Hatta", "Manggala"]
        tulis arr
        """
        self.run_source(source)
        self.assertEqual(self.vm.globals["arr"], ["Ilham", "Hatta", "Manggala"])

    def test_class_definition(self):
        source = """
        kelas Kucing
            tabel = "kucing"
            
            gawe anyar(isi, nama, umur)
                isi.nama = nama
                isi.umur = umur
            rampung
            
            gawe meong(isi)
                balekna isi.nama + " muni meong"
            rampung
        rampung
        
        pus = Kucing("Blacky", 3)
        res_nama = pus.nama
        res_tabel = pus.tabel
        res_meong = pus.meong()
        """
        self.run_source(source)
        self.assertEqual(self.vm.globals["res_nama"], "Blacky")
        self.assertEqual(self.vm.globals["res_tabel"], "kucing")
        self.assertEqual(self.vm.globals["res_meong"], "Blacky muni meong")

if __name__ == '__main__':
    unittest.main()
