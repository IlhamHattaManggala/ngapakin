# Middleware pipeline execution for Larapak

import os
from ngapak import Lexer, Parser, Compiler, NgapakError

class MiddlewarePipeline:
    def __init__(self, middleware_path, vm):
        self.middleware_path = middleware_path
        self.vm = vm
        self.middleware_map = {
            "auth": "AuthMiddleware"  # Map shorthand aliases
        }
        self.loaded_middleware = {}

    def execute_chain(self, middleware_names, req, res, destination):
        """Execute middleware list sequentially, ending at destination controller call."""
        idx = 0
        
        def next_step(current_req, current_res):
            nonlocal idx
            if idx < len(middleware_names):
                name = middleware_names[idx]
                idx += 1
                return self.run_middleware(name, current_req, current_res, next_step)
            else:
                return destination(current_req, current_res)
                
        return next_step(req, res)

    def run_middleware(self, name, req, res, next_cb):
        class_name = self.middleware_map.get(name, name)
        
        # Load and run middleware file once to register its functions
        if class_name not in self.loaded_middleware:
            filepath = os.path.join(self.middleware_path, f"{class_name}.ngpk")
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Middleware '{class_name}' tidak ditemukan di '{filepath}'")
                
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
                
            lexer = Lexer(source, filepath)
            tokens = lexer.tokenize()
            parser = Parser(tokens, filepath)
            ast = parser.parse()
            
            compiler = Compiler(filepath)
            main_fn = compiler.compile(ast)
            
            self.vm.execute_callable(main_fn, [])
            self.loaded_middleware[class_name] = True

        # Middlewares define a global function called 'tangani(req, res, lanjut)'
        if "tangani" not in self.vm.globals:
            return next_cb(req, res)
            
        tangani_fn = self.vm.globals["tangani"]
        
        # Run middleware tangani(req, res, next_cb) on VM.
        # next_cb is passed directly as Python callback.
        res_obj = self.vm.execute_callable(tangani_fn, [req, res, next_cb])
        return res_obj
