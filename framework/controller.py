# Controller resolution and loader for Larapak

import os
from ngapak import Lexer, Parser, Compiler, NgapakError

class ControllerLoader:
    def __init__(self, controllers_path, vm):
        self.controllers_path = controllers_path
        self.vm = vm
        self.loaded_controllers = {}

    def call_action(self, action_str, req, res):
        """Invoke controller action method (e.g. 'HomeController@index') on VM."""
        parts = action_str.split("@")
        if len(parts) < 2:
            raise ValueError(f"Format aksi controller tidak valid: '{action_str}'")
            
        controller_name = parts[0]
        action_name = parts[1]

        # Load and run controller file once to register its functions in VM globals
        if controller_name not in self.loaded_controllers:
            filepath = os.path.join(self.controllers_path, f"{controller_name}.ngpk")
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Controller '{controller_name}' tidak ditemukan di '{filepath}'")
                
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
                
            lexer = Lexer(source, filepath)
            tokens = lexer.tokenize()
            parser = Parser(tokens, filepath)
            ast = parser.parse()
            
            compiler = Compiler(filepath)
            main_fn = compiler.compile(ast)
            
            # Execute the controller file main scope to define functions
            self.vm.execute_callable(main_fn, [])
            self.loaded_controllers[controller_name] = True

        # Retrieve action function from VM globals
        if action_name not in self.vm.globals:
            raise AttributeError(f"Aksi '{action_name}' tidak ditemukan di Controller '{controller_name}'.")
            
        action_fn = self.vm.globals[action_name]

        # Call the controller function on VM: action(req, res)
        # Returns the Response object modified or returned by the function
        result_response = self.vm.execute_callable(action_fn, [req, res])
        return result_response
