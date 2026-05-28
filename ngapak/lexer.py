# Lexer implementation for NgapakIn

from .token import *
from .errors import NgapakSyntaxError

class Lexer:
    def __init__(self, source, filename="<stdin>"):
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.column = 1
        self.char = self.source[0] if len(self.source) > 0 else None

    def advance(self):
        if self.char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
            
        self.pos += 1
        if self.pos < len(self.source):
            self.char = self.source[self.pos]
        else:
            self.char = None

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos < len(self.source):
            return self.source[peek_pos]
        return None

    def tokenize(self):
        tokens = []
        while self.char is not None:
            # Skip spaces and carriage returns
            if self.char in ' \t\r':
                self.advance()
            elif self.char == '\n':
                # Collapse consecutive newlines and ignore leading newlines
                if tokens and tokens[-1].type != T_NEWLINE:
                    tokens.append(Token(T_NEWLINE, line=self.line, column=self.column))
                self.advance()
            elif self.char == '#':
                self.skip_comment()
            elif self.char == '"' or self.char == "'":
                tokens.append(self.make_string(self.char))
            elif self.char.isdigit() or (self.char == '.' and self.peek() is not None and self.peek().isdigit()):
                tokens.append(self.make_number())
            elif self.char.isalpha() or self.char == '_':
                tokens.append(self.make_identifier())
            elif self.char == '=':
                start_col = self.column
                self.advance()
                if self.char == '=':
                    tokens.append(Token(T_EQ, line=self.line, column=start_col))
                    self.advance()
                else:
                    tokens.append(Token(T_ASSIGN, line=self.line, column=start_col))
            elif self.char == '!':
                start_col = self.column
                self.advance()
                if self.char == '=':
                    tokens.append(Token(T_NEQ, line=self.line, column=start_col))
                    self.advance()
                else:
                    raise NgapakSyntaxError("Karakter '!' harus diikuti '=' untuk operator tidak sama dengan (!=)", self.line, start_col, self.filename)
            elif self.char == '<':
                start_col = self.column
                self.advance()
                if self.char == '=':
                    tokens.append(Token(T_LTE, line=self.line, column=start_col))
                    self.advance()
                else:
                    tokens.append(Token(T_LT, line=self.line, column=start_col))
            elif self.char == '>':
                start_col = self.column
                self.advance()
                if self.char == '=':
                    tokens.append(Token(T_GTE, line=self.line, column=start_col))
                    self.advance()
                else:
                    tokens.append(Token(T_GT, line=self.line, column=start_col))
            elif self.char == '+':
                tokens.append(Token(T_PLUS, line=self.line, column=self.column))
                self.advance()
            elif self.char == '-':
                tokens.append(Token(T_MINUS, line=self.line, column=self.column))
                self.advance()
            elif self.char == '*':
                tokens.append(Token(T_MUL, line=self.line, column=self.column))
                self.advance()
            elif self.char == '/':
                tokens.append(Token(T_DIV, line=self.line, column=self.column))
                self.advance()
            elif self.char == '(':
                tokens.append(Token(T_LPAREN, line=self.line, column=self.column))
                self.advance()
            elif self.char == ')':
                tokens.append(Token(T_RPAREN, line=self.line, column=self.column))
                self.advance()
            elif self.char == ',':
                tokens.append(Token(T_COMMA, line=self.line, column=self.column))
                self.advance()
            elif self.char == '.':
                tokens.append(Token(T_DOT, line=self.line, column=self.column))
                self.advance()
            elif self.char == '[':
                tokens.append(Token(T_LBRACKET, line=self.line, column=self.column))
                self.advance()
            elif self.char == ']':
                tokens.append(Token(T_RBRACKET, line=self.line, column=self.column))
                self.advance()
            elif self.char == ':':
                tokens.append(Token(T_COLON, line=self.line, column=self.column))
                self.advance()
            else:
                raise NgapakSyntaxError(f"Karakter tidak dikenal: {repr(self.char)}", self.line, self.column, self.filename)
        
        # Clean trailing newline if any
        if tokens and tokens[-1].type == T_NEWLINE:
            tokens.pop()
            
        tokens.append(Token(T_EOF, line=self.line, column=self.column))
        return tokens

    def skip_comment(self):
        # Comment starts with # and ends with newline or EOF
        while self.char is not None and self.char != '\n':
            self.advance()

    def make_string(self, quote_char):
        start_line = self.line
        start_col = self.column
        self.advance()  # Skip opening quote
        string_chars = []
        
        while self.char is not None and self.char != quote_char:
            if self.char == '\\':
                self.advance()
                if self.char == 'n':
                    string_chars.append('\n')
                elif self.char == 't':
                    string_chars.append('\t')
                elif self.char == '\\':
                    string_chars.append('\\')
                elif self.char == quote_char:
                    string_chars.append(quote_char)
                elif self.char is None:
                    raise NgapakSyntaxError("String literal tidak ditutup", start_line, start_col, self.filename)
                else:
                    string_chars.append('\\')
                    string_chars.append(self.char)
            else:
                string_chars.append(self.char)
            self.advance()
            
        if self.char is None:
            raise NgapakSyntaxError("String literal tidak ditutup", start_line, start_col, self.filename)
            
        self.advance()  # Skip closing quote
        return Token(T_STRING, "".join(string_chars), start_line, start_col)

    def make_number(self):
        start_col = self.column
        num_str = []
        dot_count = 0
        
        while self.char is not None and (self.char.isdigit() or self.char == '.'):
            if self.char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            num_str.append(self.char)
            self.advance()
            
        val_str = "".join(num_str)
        if dot_count == 0:
            return Token(T_NUMBER, int(val_str), self.line, start_col)
        else:
            return Token(T_NUMBER, float(val_str), self.line, start_col)

    def make_identifier(self):
        start_col = self.column
        id_chars = []
        while self.char is not None and (self.char.isalnum() or self.char == '_'):
            id_chars.append(self.char)
            self.advance()
            
        id_str = "".join(id_chars)
        tok_type = KEYWORDS.get(id_str, T_IDENTIFIER)
        return Token(tok_type, id_str, self.line, start_col)
