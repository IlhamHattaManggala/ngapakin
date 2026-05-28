# Parser implementation for NgapakIn

from .token import *
from .ast import *
from .errors import NgapakSyntaxError

class Parser:
    def __init__(self, tokens, filename="<stdin>"):
        self.tokens = tokens
        self.filename = filename
        self.pos = 0
        self.current_token = self.tokens[self.pos] if len(self.tokens) > 0 else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def check(self, type_):
        if self.current_token is None:
            return False
        return self.current_token.type == type_

    def match(self, *types):
        for type_ in types:
            if self.check(type_):
                self.advance()
                return True
        return False

    def consume(self, type_, message):
        if self.check(type_):
            tok = self.current_token
            self.advance()
            return tok
        raise NgapakSyntaxError(message, self.current_token.line, self.current_token.column, self.filename)

    def error(self, message):
        raise NgapakSyntaxError(message, self.current_token.line, self.current_token.column, self.filename)

    def parse(self):
        statements = []
        # Consume leading newlines
        while self.match(T_NEWLINE):
            pass
            
        while not self.check(T_EOF):
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
            
            # Consume newlines between statements
            if not self.check(T_EOF) and not self.check(T_NEWLINE) and self.pos > 0 and self.tokens[self.pos-1].type != T_NEWLINE:
                if not (self.check(T_RAMPUNG) or self.check(T_LIYANE)):
                    self.error("Harus ada baris baru setelah pernyataan")
            
            while self.match(T_NEWLINE):
                pass
                
        # Top-level program node
        prog_node = ProgramNode(statements)
        prog_node.line = 1
        prog_node.column = 1
        return prog_node

    def statement(self):
        start_tok = self.current_token
        node = None
        
        if self.match(T_TULIS):
            expr = self.expression()
            node = TulisNode(expr)
            
        elif self.match(T_NEK):
            node = self.if_statement()
            
        elif self.match(T_BALENI):
            node = self.for_statement()
            
        elif self.match(T_GAWE):
            node = self.func_def_statement()
            
        elif self.match(T_BALEKNA):
            expr = None
            if not (self.check(T_NEWLINE) or self.check(T_EOF) or self.check(T_RAMPUNG) or self.check(T_LIYANE)):
                expr = self.expression()
            node = ReturnNode(expr)

        elif self.match(T_KELAS):
            node = self.class_def_statement()

        # Expression statement or Assignment (variable or member)
        else:
            expr = self.expression()
            if self.match(T_ASSIGN):
                if isinstance(expr, VarAccessNode):
                    node = VarAssignNode(expr.name, self.expression())
                elif isinstance(expr, MemberAccessNode):
                    node = MemberAssignNode(expr.obj, expr.member, self.expression())
                else:
                    self.error("Sisi kiri penugasan tidak valid")
            else:
                node = expr

        if node and start_tok:
            node.line = start_tok.line
            node.column = start_tok.column
        return node

    def if_statement(self):
        condition = self.expression()
        self.consume(T_YA, "Diharapkan keyword 'ya' setelah kondisi 'nek'")
        
        while self.match(T_NEWLINE):
            pass
            
        true_branch = []
        while not self.check(T_EOF) and not self.check(T_LIYANE) and not self.check(T_RAMPUNG):
            stmt = self.statement()
            if stmt:
                true_branch.append(stmt)
            while self.match(T_NEWLINE):
                pass

        false_branch = None
        if self.match(T_LIYANE):
            while self.match(T_NEWLINE):
                pass
            false_branch = []
            while not self.check(T_EOF) and not self.check(T_RAMPUNG):
                stmt = self.statement()
                if stmt:
                    false_branch.append(stmt)
                while self.match(T_NEWLINE):
                    pass

        self.consume(T_RAMPUNG, "Diharapkan keyword 'rampung' untuk menutup blok 'nek'")
        return IfNode(condition, true_branch, false_branch)

    def for_statement(self):
        var_tok = self.consume(T_IDENTIFIER, "Diharapkan nama variabel setelah 'baleni'")
        self.consume(T_SAKA, "Diharapkan keyword 'saka' setelah variabel loop")
        start_expr = self.expression()
        self.consume(T_NGANTI, "Diharapkan keyword 'nganti' setelah nilai awal loop")
        end_expr = self.expression()
        
        while self.match(T_NEWLINE):
            pass
            
        body = []
        while not self.check(T_EOF) and not self.check(T_RAMPUNG):
            stmt = self.statement()
            if stmt:
                body.append(stmt)
            while self.match(T_NEWLINE):
                pass
                
        self.consume(T_RAMPUNG, "Diharapkan keyword 'rampung' untuk menutup blok 'baleni'")
        return ForNode(var_tok.value, start_expr, end_expr, body)

    def func_def_statement(self):
        if self.check(T_LPAREN):
            name = "anonymous"
        else:
            name_tok = self.consume(T_IDENTIFIER, "Diharapkan nama fungsi setelah 'gawe'")
            name = name_tok.value
            
        self.consume(T_LPAREN, "Diharapkan '(' setelah nama atau keyword fungsi")
        
        params = []
        if not self.check(T_RPAREN):
            param_tok = self.consume(T_IDENTIFIER, "Diharapkan nama parameter")
            params.append(param_tok.value)
            while self.match(T_COMMA):
                param_tok = self.consume(T_IDENTIFIER, "Diharapkan nama parameter setelah koma")
                params.append(param_tok.value)
                
        self.consume(T_RPAREN, "Diharapkan ')' setelah daftar parameter")
        
        while self.match(T_NEWLINE):
            pass
            
        body = []
        while not self.check(T_EOF) and not self.check(T_RAMPUNG):
            stmt = self.statement()
            if stmt:
                body.append(stmt)
            while self.match(T_NEWLINE):
                pass
                
        self.consume(T_RAMPUNG, "Diharapkan keyword 'rampung' untuk menutup fungsi")
        return FuncDefNode(name, params, body)

    def class_def_statement(self):
        name_tok = self.consume(T_IDENTIFIER, "Diharapkan nama kelas setelah 'kelas'")
        parent_name = None
        if self.match(T_EXTENDS):
            parent_tok = self.consume(T_IDENTIFIER, "Diharapkan nama kelas induk setelah 'extends'")
            parent_name = parent_tok.value
            
        while self.match(T_NEWLINE):
            pass
            
        body = []
        while not self.check(T_EOF) and not self.check(T_RAMPUNG):
            stmt = self.statement()
            if stmt:
                body.append(stmt)
            while self.match(T_NEWLINE):
                pass
                
        self.consume(T_RAMPUNG, "Diharapkan keyword 'rampung' untuk menutup kelas")
        return ClassDefNode(name_tok.value, parent_name, body)

    def expression(self):
        return self.comparison()

    def comparison(self):
        expr = self.term()
        
        while self.match(T_EQ, T_NEQ, T_LT, T_GT, T_LTE, T_GTE):
            op_tok = self.tokens[self.pos - 1]
            right = self.term()
            node = BinOpNode(expr, op_tok, right)
            node.line = op_tok.line
            node.column = op_tok.column
            expr = node
            
        return expr

    def term(self):
        expr = self.factor()
        
        while self.match(T_PLUS, T_MINUS):
            op_tok = self.tokens[self.pos - 1]
            right = self.factor()
            node = BinOpNode(expr, op_tok, right)
            node.line = op_tok.line
            node.column = op_tok.column
            expr = node
            
        return expr

    def factor(self):
        expr = self.primary()
        
        while self.match(T_MUL, T_DIV):
            op_tok = self.tokens[self.pos - 1]
            right = self.primary()
            node = BinOpNode(expr, op_tok, right)
            node.line = op_tok.line
            node.column = op_tok.column
            expr = node
            
        return expr

    def primary(self):
        start_tok = self.current_token
        expr = self.base_primary()
        
        while self.match(T_DOT):
            dot_tok = self.tokens[self.pos - 1]
            if self.current_token and (self.check(T_IDENTIFIER) or self.current_token.type in (T_TULIS, T_NEK, T_YA, T_LIYANE, T_RAMPUNG, T_BALENI, T_SAKA, T_NGANTI, T_GAWE, T_BALEKNA, T_BENER, T_SALAH, T_KOSONG, T_KELAS, T_EXTENDS)):
                name_tok = self.current_token
                self.advance()
            else:
                self.error("Diharapkan nama properti/metode setelah '.'")
            if self.match(T_LPAREN):
                args = []
                if not self.check(T_RPAREN):
                    args.append(self.expression())
                    while self.match(T_COMMA):
                        args.append(self.expression())
                self.consume(T_RPAREN, "Diharapkan ')' setelah daftar argumen")
                expr = MethodCallNode(expr, name_tok.value, args)
            else:
                expr = MemberAccessNode(expr, name_tok.value)
            expr.line = dot_tok.line
            expr.column = dot_tok.column
            
        return expr

    def base_primary(self):
        start_tok = self.current_token
        node = None
        
        if self.match(T_BENER):
            node = LiteralNode(True)
        elif self.match(T_SALAH):
            node = LiteralNode(False)
        elif self.match(T_KOSONG):
            node = LiteralNode(None)
            
        elif self.match(T_NUMBER, T_STRING):
            node = LiteralNode(self.tokens[self.pos - 1].value)
            
        elif self.match(T_LBRACKET):
            if self.check(T_RBRACKET):
                self.consume(T_RBRACKET, "Diharapkan ']'")
                node = ListNode([])
            else:
                expr1 = self.expression()
                if self.match(T_COLON):
                    keys = [expr1]
                    values = [self.expression()]
                    while self.match(T_COMMA):
                        k = self.expression()
                        self.consume(T_COLON, "Diharapkan ':' setelah kunci kamus")
                        v = self.expression()
                        keys.append(k)
                        values.append(v)
                    self.consume(T_RBRACKET, "Diharapkan ']' untuk menutup kamus")
                    node = DictNode(keys, values)
                else:
                    elements = [expr1]
                    while self.match(T_COMMA):
                        elements.append(self.expression())
                    self.consume(T_RBRACKET, "Diharapkan ']' untuk menutup daftar")
                    node = ListNode(elements)

        elif self.check(T_IDENTIFIER):
            id_tok = self.consume(T_IDENTIFIER, "Diharapkan nama variabel/fungsi")
            
            if self.match(T_LPAREN):
                args = []
                if not self.check(T_RPAREN):
                    args.append(self.expression())
                    while self.match(T_COMMA):
                        args.append(self.expression())
                self.consume(T_RPAREN, "Diharapkan ')' setelah daftar argumen")
                node = FuncCallNode(id_tok.value, args)
            else:
                node = VarAccessNode(id_tok.value)
                
        elif self.match(T_GAWE):
            node = self.func_def_statement()
            
        elif self.match(T_LPAREN):
            node = self.expression()
            self.consume(T_RPAREN, "Diharapkan ')' setelah ekspresi")
            
        else:
            if self.current_token:
                self.error(f"Sintaksis tidak valid pada token '{self.current_token.value}'")
            else:
                self.error("Sintaksis tidak valid di akhir berkas")

        if node and start_tok:
            node.line = start_tok.line
            node.column = start_tok.column
        return node
