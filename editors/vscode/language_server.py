# Simple Language Server Protocol (LSP) diagnostics server for NgapakLang

import sys
import os
import json

# Add project root directory to path to enable importing ngapak
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ngapak.lexer import Lexer
from ngapak.parser import Parser
from ngapak.compiler import Compiler
from ngapak.errors import NgapakError

def check_syntax(source_code, filepath="<diagnostics>"):
    """Run Lexer, Parser, and Compiler on source code and return list of diagnostics."""
    diagnostics = []
    try:
        lexer = Lexer(source_code, filepath)
        tokens = lexer.tokenize()
        parser = Parser(tokens, filepath)
        ast = parser.parse()
        compiler = Compiler(filepath)
        compiler.compile(ast)
    except NgapakError as e:
        line = (e.line or 1) - 1 # LSP uses 0-indexed lines
        col = (e.column or 1) - 1 # LSP uses 0-indexed columns
        diagnostics.append({
            "range": {
                "start": {"line": line, "character": col},
                "end": {"line": line, "character": col + 5}
            },
            "severity": 1, # Error
            "source": "ngapak-compiler",
            "message": e.message
        })
    except Exception as e:
        diagnostics.append({
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 0, "character": 1}
            },
            "severity": 1,
            "source": "ngapak-compiler",
            "message": str(e)
        })
    return diagnostics

def send_response(writer, payload):
    body = json.dumps(payload)
    header = f"Content-Length: {len(body)}\r\n\r\n"
    writer.write(header + body)
    writer.flush()

def serve_stdio():
    # Read headers
    import io
    stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    while True:
        try:
            line = stdin.readline()
            if not line:
                break
            if line.startswith("Content-Length:"):
                length = int(line.split(":")[1].strip())
                # skip empty lines until we reach content
                while True:
                    empty_line = stdin.readline()
                    if empty_line == "\r\n" or empty_line == "\n" or empty_line.strip() == "":
                        break
                
                content = stdin.read(length)
                request = json.loads(content)
                method = request.get("method")
                req_id = request.get("id")
                
                if method == "initialize":
                    # Send response
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "capabilities": {
                                "textDocumentSync": 1, # Full sync
                            }
                        }
                    }
                    send_response(stdout, response)
                elif method in ("textDocument/didOpen", "textDocument/didChange", "textDocument/didSave"):
                    params = request.get("params", {})
                    text_document = params.get("textDocument", {})
                    uri = text_document.get("uri", "")
                    content_changes = params.get("contentChanges", [])
                    if content_changes:
                        text = content_changes[0].get("text", "")
                    elif "text" in text_document:
                        text = text_document.get("text", "")
                    else:
                        continue
                    
                    diagnostics = check_syntax(text, uri)
                    
                    # Publish diagnostics notification
                    notification = {
                        "jsonrpc": "2.0",
                        "method": "textDocument/publishDiagnostics",
                        "params": {
                            "uri": uri,
                            "diagnostics": diagnostics
                        }
                    }
                    send_response(stdout, notification)
                elif method == "shutdown":
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": None
                    }
                    send_response(stdout, response)
                elif method == "exit":
                    break
        except Exception as e:
            sys.stderr.write(f"LSP error: {str(e)}\n")
            sys.stderr.flush()

def main():
    if len(sys.argv) > 1:
        # CLI Mode (validate single file and output diagnostics)
        filepath = sys.argv[1]
        if not os.path.exists(filepath):
            print(json.dumps({"error": f"File not found: {filepath}"}))
            sys.exit(1)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        diagnostics = check_syntax(content, filepath)
        print(json.dumps(diagnostics, indent=4))
    else:
        # LSP Mode
        serve_stdio()

if __name__ == "__main__":
    main()
