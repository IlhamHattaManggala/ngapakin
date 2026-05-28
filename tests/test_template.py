import unittest
import os
import shutil
from ngapak.vm import VM
from framework.template_engine import TemplateEngine

class TestTemplate(unittest.TestCase):
    def setUp(self):
        self.vm = VM()
        self.tmp_dir = os.path.abspath("tests/tmp_views")
        os.makedirs(self.tmp_dir, exist_ok=True)
        self.engine = TemplateEngine(self.tmp_dir, self.vm)

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def write_view(self, name, content):
        filepath = os.path.join(self.tmp_dir, name)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def test_variable_interpolation(self):
        content = "Halo {{ user.name }}, umur {{ user.age }}."
        context = {
            "user": {
                "name": "Ilham",
                "age": 20
            }
        }
        res = self.engine.evaluate_template(content, context)
        self.assertEqual(res, "Halo Ilham, umur 20.")

    def test_conditionals(self):
        content = """
        @nek nilai >= 75 ya
            Lulus
        @liyane
            Gagal
        @rampung
        """
        # True
        res_true = self.engine.evaluate_template(content, {"nilai": 80}).strip()
        self.assertEqual(res_true, "Lulus")
        
        # False
        res_false = self.engine.evaluate_template(content, {"nilai": 60}).strip()
        self.assertEqual(res_false, "Gagal")

    def test_loops(self):
        content = """
        @baleni idx saka 1 nganti 3
            Item {{ idx }}
        @rampung
        """
        res = self.engine.evaluate_template(content, {}).strip().split()
        self.assertEqual(res, ["Item", "1", "Item", "2", "Item", "3"])

    def test_layouts_and_sections(self):
        # Setup layout
        layout_content = "Layout Start\n@yield \"content\"\nLayout End"
        self.write_view("base.nview", layout_content)
        
        # Setup main view
        view_content = """@layout "base.nview"
        @section "content"
            Tengah
        @rampung
        """
        self.write_view("index.nview", view_content)
        
        res = self.engine.render("index.nview", {})
        self.assertIn("Layout Start", res)
        self.assertIn("Tengah", res)
        self.assertIn("Layout End", res)

if __name__ == '__main__':
    unittest.main()
