# Template Engine implementation for Larapak (Blade-like)

import os
import re
from ngapak import Lexer, Parser, Compiler, NgapakError

class TemplateEngine:
    def __init__(self, views_path, vm):
        self.views_path = views_path
        self.vm = vm
        self.sections = {}
        self.layout = None

    def render(self, view_name, context):
        if not view_name.endswith(".nview"):
            view_name += ".nview"
            
        filepath = os.path.join(self.views_path, view_name)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Template view '{view_name}' tidak ditemukan di '{filepath}'")
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Temporarily inject context into VM globals
        prev_globals = dict(self.vm.globals)
        for k, v in context.items():
            self.vm.globals[k] = v

        try:
            rendered = self.evaluate_template(content, context)
            
            if self.layout:
                layout_name = self.layout
                self.layout = None  # Reset layout state
                rendered = self.render(layout_name, context)
        finally:
            self.vm.globals = prev_globals

        return rendered

    def evaluate_expression(self, expr_str):
        lexer = Lexer(expr_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        main_fn = compiler.compile(ast)
        
        # Execute expression on VM
        res = self.vm.execute_callable(main_fn, [])
        if res is True:
            return "bener"
        if res is False:
            return "salah"
        if res is None:
            return ""
        return str(res)

    def evaluate_template(self, content, context):
        # Temporarily inject context into VM globals
        prev_globals = dict(self.vm.globals)
        for k, v in context.items():
            self.vm.globals[k] = v

        try:
            lines = content.splitlines()
            output = []
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                # 1. Layout directive
                if line.startswith("@layout"):
                    match = re.match(r'@layout\s+"([^"]+)"', line)
                    if match:
                        self.layout = match.group(1)
                    i += 1
                    continue
                    
                # 2. Section directive
                elif line.startswith("@section"):
                    match = re.match(r'@section\s+"([^"]+)"', line)
                    if match:
                        section_name = match.group(1)
                        section_lines = []
                        i += 1
                        nest_depth = 1
                        while i < len(lines):
                            sub_line = lines[i].strip()
                            if sub_line.startswith("@section"):
                                nest_depth += 1
                            elif sub_line == "@rampung":
                                nest_depth -= 1
                                if nest_depth == 0:
                                    break
                            section_lines.append(lines[i])
                            i += 1
                        self.sections[section_name] = self.evaluate_template("\n".join(section_lines), context)
                    i += 1
                    continue
                    
                # 3. Yield directive
                elif line.startswith("@yield"):
                    match = re.match(r'@yield\s+"([^"]+)"', line)
                    if match:
                        section_name = match.group(1)
                        output.append(self.sections.get(section_name, ""))
                    i += 1
                    continue
                    
                # 4. Include directive
                elif line.startswith("@include"):
                    match = re.match(r'@include\s+"([^"]+)"', line)
                    if match:
                        inc_name = match.group(1)
                        inc_content = self.render(inc_name, context)
                        output.append(inc_content)
                    i += 1
                    continue
                    
                # 5. Nek (conditional) directive
                elif line.startswith("@nek"):
                    expr_str = line[4:].strip()
                    if expr_str.endswith("ya"):
                        expr_str = expr_str[:-2].strip()
                        
                    cond_val = self.evaluate_expression(expr_str)
                    is_true = cond_val not in ("", "salah", "kosong", "0", "False", "None")
                    
                    then_lines = []
                    else_lines = []
                    in_else = False
                    i += 1
                    nest = 1
                    
                    while i < len(lines):
                        sub_line = lines[i].strip()
                        if sub_line.startswith("@nek") or sub_line.startswith("@baleni"):
                            nest += 1
                        elif sub_line == "@rampung":
                            nest -= 1
                            if nest == 0:
                                break
                        elif sub_line == "@liyane" and nest == 1:
                            in_else = True
                            i += 1
                            continue
                            
                        if in_else:
                            else_lines.append(lines[i])
                        else:
                            then_lines.append(lines[i])
                        i += 1
                        
                    branch_content = "\n".join(then_lines) if is_true else "\n".join(else_lines)
                    output.append(self.evaluate_template(branch_content, context))
                    i += 1
                    continue
                    
                # 6. Baleni (loop) directive
                elif line.startswith("@baleni"):
                    match = re.match(r'@baleni\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+saka\s+(.+)\s+nganti\s+(.+)', line)
                    if match:
                        var_name = match.group(1)
                        start_expr = match.group(2)
                        end_expr = match.group(3)
                        
                        body_lines = []
                        i += 1
                        nest = 1
                        while i < len(lines):
                            sub_line = lines[i].strip()
                            if sub_line.startswith("@nek") or sub_line.startswith("@baleni"):
                                nest += 1
                            elif sub_line == "@rampung":
                                nest -= 1
                                if nest == 0:
                                    break
                            body_lines.append(lines[i])
                            i += 1
                            
                        body_str = "\n".join(body_lines)
                        
                        start_val = int(float(self.evaluate_expression(start_expr)))
                        end_val = int(float(self.evaluate_expression(end_expr)))
                        
                        step = 1 if start_val <= end_val else -1
                        for val in range(start_val, end_val + step, step):
                            self.vm.globals[var_name] = val
                            output.append(self.evaluate_template(body_str, context))
                            if var_name in self.vm.globals:
                                del self.vm.globals[var_name]
                    i += 1
                    continue
                    
                # 7. Normal line (process interpolations)
                else:
                    raw_line = lines[i]
                    def repl(match):
                        expr = match.group(1).strip()
                        try:
                            return self.evaluate_expression(expr)
                        except NgapakError as e:
                            return f"{{{{ Error: {str(e)} }}}}"
                    
                    interpolated = re.sub(r'\{\{\s*(.*?)\s*\}\}', repl, raw_line)
                    output.append(interpolated)
                    i += 1
                    
            return "\n".join(output)
        finally:
            self.vm.globals = prev_globals
