# Token types definitions for NgapakIn

# Keywords
T_TULIS = "TULIS"
T_NEK = "NEK"
T_YA = "YA"
T_LIYANE = "LIYANE"
T_RAMPUNG = "RAMPUNG"
T_BALENI = "BALENI"
T_SAKA = "SAKA"
T_NGANTI = "NGANTI"
T_GAWE = "GAWE"
T_BALEKNA = "BALEKNA"
T_BENER = "BENER"
T_SALAH = "SALAH"
T_KOSONG = "KOSONG"
T_KELAS = "KELAS"
T_EXTENDS = "EXTENDS"

# Literals
T_IDENTIFIER = "IDENTIFIER"
T_NUMBER = "NUMBER"
T_STRING = "STRING"

# Operators
T_PLUS = "PLUS"
T_MINUS = "MINUS"
T_MUL = "MUL"
T_DIV = "DIV"
T_ASSIGN = "ASSIGN"
T_EQ = "EQ"
T_NEQ = "NEQ"
T_LT = "LT"
T_GT = "GT"
T_LTE = "LTE"
T_GTE = "GTE"

# Delimiters / Punctuation
T_LPAREN = "LPAREN"
T_RPAREN = "RPAREN"
T_COMMA = "COMMA"
T_NEWLINE = "NEWLINE"
T_DOT = "DOT"
T_LBRACKET = "LBRACKET"
T_RBRACKET = "RBRACKET"
T_COLON = "COLON"
T_EOF = "EOF"

# Keyword mapping for quick check in Lexer
KEYWORDS = {
    "tulis": T_TULIS,
    "nek": T_NEK,
    "ya": T_YA,
    "liyane": T_LIYANE,
    "rampung": T_RAMPUNG,
    "baleni": T_BALENI,
    "saka": T_SAKA,
    "nganti": T_NGANTI,
    "gawe": T_GAWE,
    "balekna": T_BALEKNA,
    "bener": T_BENER,
    "salah": T_SALAH,
    "kosong": T_KOSONG,
    "kelas": T_KELAS,
    "extends": T_EXTENDS,
}

class Token:
    def __init__(self, type_, value=None, line=1, column=1):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        if self.value is not None:
            return f"Token({self.type}, {repr(self.value)}, {self.line}:{self.column})"
        return f"Token({self.type}, {self.line}:{self.column})"
