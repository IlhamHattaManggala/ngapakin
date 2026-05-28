import unittest
from ngapak.token import *
from ngapak.lexer import Lexer
from ngapak.errors import NgapakSyntaxError

class TestLexer(unittest.TestCase):
    def test_basic_tokens(self):
        source = "tulis + - * / = == != < > <= >= ( ) ,"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            T_TULIS, T_PLUS, T_MINUS, T_MUL, T_DIV, T_ASSIGN, T_EQ, T_NEQ,
            T_LT, T_GT, T_LTE, T_GTE, T_LPAREN, T_RPAREN, T_COMMA, T_EOF
        ]
        
        self.assertEqual(len(tokens), len(expected_types))
        for t, expected in zip(tokens, expected_types):
            self.assertEqual(t.type, expected)

    def test_identifiers_and_keywords(self):
        source = "nek ya liyane rampung baleni saka nganti gawe balekna bener salah kosong variabel_ku"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            T_NEK, T_YA, T_LIYANE, T_RAMPUNG, T_BALENI, T_SAKA, T_NGANTI,
            T_GAWE, T_BALEKNA, T_BENER, T_SALAH, T_KOSONG, T_IDENTIFIER, T_EOF
        ]
        
        self.assertEqual(len(tokens), len(expected_types))
        for t, expected in zip(tokens, expected_types):
            self.assertEqual(t.type, expected)
        self.assertEqual(tokens[-2].value, "variabel_ku")

    def test_literals(self):
        source = '20 3.14 "Halo Banyumas" \'Ngapak\''
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        self.assertEqual(tokens[0].type, T_NUMBER)
        self.assertEqual(tokens[0].value, 20)
        
        self.assertEqual(tokens[1].type, T_NUMBER)
        self.assertEqual(tokens[1].value, 3.14)
        
        self.assertEqual(tokens[2].type, T_STRING)
        self.assertEqual(tokens[2].value, "Halo Banyumas")
        
        self.assertEqual(tokens[3].type, T_STRING)
        self.assertEqual(tokens[3].value, "Ngapak")

    def test_comments(self):
        source = """
        # ini komentar
        x = 10 # komentar lagi
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Should only get x, =, 10
        expected = [T_IDENTIFIER, T_ASSIGN, T_NUMBER, T_EOF]
        self.assertEqual([t.type for t in tokens], expected)

    def test_invalid_character(self):
        lexer = Lexer("x = @")
        with self.assertRaises(NgapakSyntaxError):
            lexer.tokenize()

    def test_unterminated_string(self):
        lexer = Lexer('x = "halo')
        with self.assertRaises(NgapakSyntaxError):
            lexer.tokenize()

if __name__ == '__main__':
    unittest.main()
