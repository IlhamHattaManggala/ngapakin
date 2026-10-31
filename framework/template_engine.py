# Template Engine implementation for Larapak (Blade-like)

import os
import re
import html
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

    def evaluate_expression_raw(self, expr_str):
        lexer = Lexer(expr_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        main_fn = compiler.compile(ast)
        return self.vm.execute_callable(main_fn, [])

    def evaluate_expression(self, expr_str):
        res = self.evaluate_expression_raw(expr_str)
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
                            if sub_line.startswith("@section") or sub_line.startswith("@nek") or sub_line.startswith("@baleni") or sub_line.startswith("@error") or sub_line.startswith("@kleru"):
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
                    
                # 4. Include directive (@include atau @mlebui)
                elif line.startswith("@include") or line.startswith("@mlebui"):
                    match = re.match(r'@(?:include|mlebui)\s+"([^"]+)"', line)
                    if match:
                        inc_name = match.group(1)
                        inc_content = self.render(inc_name, context)
                        output.append(inc_content)
                    i += 1
                    continue

                # 5. CSRF directive (@csrf)
                elif line == "@csrf":
                    from framework.csrf import CSRF
                    token = ""
                    if "sesi" in self.vm.globals:
                        session_obj = self.vm.globals["sesi"]
                        token = CSRF.token(session_obj)
                    output.append(f'<input type="hidden" name="_token" value="{token}">')
                    i += 1
                    continue

                # 6. Error directive (@error atau @kleru)
                elif line.startswith("@error") or line.startswith("@kleru"):
                    match = re.match(r'@(?:error|kleru)\s*(?:\("([^"]+)"\)|"([^"]+)")', line)
                    field = match.group(1) or match.group(2) if match else None
                    has_error = False
                    error_msg = ""
                    err_dict = context.get("errors") or (self.vm.globals.get("errors") if "errors" in self.vm.globals else None)
                    if err_dict and isinstance(err_dict, dict) and field in err_dict:
                        has_error = True
                        error_msg = err_dict[field]

                    err_lines = []
                    i += 1
                    nest = 1
                    while i < len(lines):
                        sub_line = lines[i].strip()
                        if sub_line.startswith("@error") or sub_line.startswith("@kleru") or sub_line.startswith("@nek") or sub_line.startswith("@baleni"):
                            nest += 1
                        elif sub_line == "@rampung":
                            nest -= 1
                            if nest == 0:
                                break
                        err_lines.append(lines[i])
                        i += 1

                    if has_error:
                        context_with_err = dict(context)
                        context_with_err["message"] = error_msg
                        context_with_err["pesan"] = error_msg
                        output.append(self.evaluate_template("\n".join(err_lines), context_with_err))
                    i += 1
                    continue
                    
                # 7. Nek (conditional) directive
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
                        if sub_line.startswith("@nek") or sub_line.startswith("@baleni") or sub_line.startswith("@error") or sub_line.startswith("@kleru"):
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
                    
                # 8. Baleni (loop) directive
                elif line.startswith("@baleni"):
                    match_foreach = re.match(r'@baleni\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+neng\s+(.+)', line)
                    match_range = re.match(r'@baleni\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+saka\s+(.+)\s+nganti\s+(.+)', line)
                    
                    body_lines = []
                    i += 1
                    nest = 1
                    while i < len(lines):
                        sub_line = lines[i].strip()
                        if sub_line.startswith("@nek") or sub_line.startswith("@baleni") or sub_line.startswith("@error") or sub_line.startswith("@kleru"):
                            nest += 1
                        elif sub_line == "@rampung":
                            nest -= 1
                            if nest == 0:
                                break
                        body_lines.append(lines[i])
                        i += 1
                        
                    body_str = "\n".join(body_lines)
                    
                    if match_foreach:
                        var_name = match_foreach.group(1)
                        coll_expr = match_foreach.group(2)
                        coll_val = self.evaluate_expression_raw(coll_expr)
                        if coll_val and hasattr(coll_val, '__iter__'):
                            for item in coll_val:
                                self.vm.globals[var_name] = item
                                output.append(self.evaluate_template(body_str, context))
                                if var_name in self.vm.globals:
                                    del self.vm.globals[var_name]
                    elif match_range:
                        var_name = match_range.group(1)
                        start_expr = match_range.group(2)
                        end_expr = match_range.group(3)
                        
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
                    
                # 9. Normal line (process interpolations: {!! raw !!} and {{ escaped }})
                else:
                    raw_line = lines[i]
                    def raw_repl(match):
                        expr = match.group(1).strip()
                        try:
                            return self.evaluate_expression(expr)
                        except NgapakError as e:
                            return f"{{{{ Error: {str(e)} }}}}"

                    def escaped_repl(match):
                        expr = match.group(1).strip()
                        try:
                            val = self.evaluate_expression(expr)
                            return html.escape(str(val))
                        except NgapakError as e:
                            return f"{{{{ Error: {str(e)} }}}}"
                    
                    # Unescaped raw interpolation first
                    processed = re.sub(r'\{!!\s*(.*?)\s*!!\}', raw_repl, raw_line)
                    # Escaped interpolation second
                    interpolated = re.sub(r'\{\{\s*(.*?)\s*\}\}', escaped_repl, processed)
                    output.append(interpolated)
                    i += 1
                    
            return "\n".join(output)
        finally:
            self.vm.globals = prev_globals