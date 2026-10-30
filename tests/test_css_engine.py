import unittest
import os
import tempfile
import shutil
from framework.css_engine import CSSEngine, compile_rikat_css

class TestCSSEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.views_dir = os.path.join(self.temp_dir, "views")
        self.css_dir = os.path.join(self.temp_dir, "public", "css")
        os.makedirs(self.views_dir, exist_ok=True)
        os.makedirs(self.css_dir, exist_ok=True)
        self.output_css = os.path.join(self.css_dir, "rikat.css")
        self.engine = CSSEngine(views_dir=self.views_dir, output_file=self.output_css)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_core_tokens(self):
        tokens = self.engine.get_core_tokens()
        self.assertIn(":root", tokens)
        self.assertIn("--bg-base:", tokens)
        self.assertIn("--bg-surface:", tokens)
        self.assertIn("--accent-primary:", tokens)
        self.assertIn("--color-success:", tokens)
        self.assertIn(".light", tokens)
        self.assertIn("box-sizing: border-box", tokens)

    def test_core_utilities(self):
        utilities = self.engine.get_core_utilities()
        # Flexbox & Grid
        self.assertIn(".flex { display: flex; }", utilities)
        self.assertIn(".grid { display: grid; }", utilities)
        self.assertIn(".grid-cols-12", utilities)
        self.assertIn(".items-center", utilities)
        self.assertIn(".justify-between", utilities)
        # Spacing
        self.assertIn(".p-4", utilities)
        self.assertIn(".m-2", utilities)
        # Sizing
        self.assertIn(".w-full", utilities)
        self.assertIn(".h-screen", utilities)
        # Typography & Colors
        self.assertIn(".text-sm", utilities)
        self.assertIn(".font-bold", utilities)
        self.assertIn(".text-accent", utilities)
        self.assertIn(".bg-surface", utilities)
        # Borders & Shadows
        self.assertIn(".rounded-md", utilities)
        self.assertIn(".shadow-lg", utilities)

    def test_smart_components(self):
        components = self.engine.get_smart_components()
        self.assertIn(".btn {", components)
        self.assertIn(".btn-primary {", components)
        self.assertIn(".card {", components)
        self.assertIn(".input {", components)
        self.assertIn(".table {", components)
        self.assertIn(".badge {", components)
        self.assertIn(".alert {", components)

    def test_arbitrary_value_and_jit_scanning(self):
        # Create a sample view with custom arbitrary Tailwind-like classes
        sample_view = os.path.join(self.views_dir, "dashboard.nview")
        with open(sample_view, "w", encoding="utf-8") as f:
            f.write("""
            <div class="w-[320px] max-w-[960px] h-[480px] bg-[#f58220] text-[#ffffff] p-[16px] m-[24px]">
                <span class="text-[20px] gap-[12px] rounded-[10px] z-[99]">Custom Badge</span>
                <button class="hover:bg-accent md:flex lg:grid-cols-3">Click Me</button>
            </div>
            """)

        jit_rules = self.engine.scan_arbitrary_classes()
        self.assertIn("width: 320px;", jit_rules)
        self.assertIn("max-width: 960px;", jit_rules)
        self.assertIn("height: 480px;", jit_rules)
        self.assertIn("background-color: #f58220;", jit_rules)
        self.assertIn("color: #ffffff;", jit_rules)
        self.assertIn("padding: 16px;", jit_rules)
        self.assertIn("margin: 24px;", jit_rules)
        self.assertIn("font-size: 20px;", jit_rules)
        self.assertIn("border-radius: 10px;", jit_rules)
        self.assertIn("z-index: 99;", jit_rules)
        self.assertIn(":hover", jit_rules)
        self.assertIn("@media (min-width: 768px)", jit_rules)
        self.assertIn("@media (min-width: 1024px)", jit_rules)

    def test_compile_generates_both_rikat_and_larapak_css(self):
        compiled = self.engine.compile()
        self.assertTrue(os.path.exists(self.output_css))
        self.assertGreater(os.path.getsize(self.output_css), 1000)

        # Verify alias larapak.css
        alias_css = os.path.join(self.css_dir, "larapak.css")
        self.assertTrue(os.path.exists(alias_css))
        self.assertEqual(os.path.getsize(self.output_css), os.path.getsize(alias_css))

    def test_compile_rikat_css_helper(self):
        out = compile_rikat_css(views_dir=self.views_dir, output_file=self.output_css)
        self.assertIn("Rikat CSS", out)
        self.assertTrue(os.path.exists(self.output_css))

if __name__ == "__main__":
    unittest.main()

