from enum import Enum, auto


class TokenType(Enum):
    EOF = auto()
    WHITESPACE = auto()

    # Single character tokens
    APOST = auto()
    ATSYM = auto()
    LBRACE = auto()
    RBRACE = auto()
    COLON = auto()
    COMMA = auto()
    DOT = auto()
    HASH = auto()
    QMARK = auto()
    
    # Multi-character tokens
    APOST_S = auto()

    # Identifiers, types, and literals
    IDENTIFIER = auto()
    NUM = auto()
    CHAR = auto()
    STR = auto()
    BOOL = auto()
    NULL = auto()        # Keyword "nothing"
    PUNCT = auto()       # [./!/?/‽/…/:]

    # Keywords
    I = auto()
    IM = auto()
    ADD = auto()
    ADDED = auto()
    AM = auto()
    AND = auto()
    ARE = auto()
    AT = auto()
    BACK = auto()
    BE = auto()
    BY = auto()
    CALL = auto()
    DIVIDE = auto()
    DIVIDED = auto()
    DO = auto()
    DONE = auto()
    ELSE = auto()
    EQUAL = auto()
    FOLLOWING = auto()
    FROM = auto()
    GIVE = auto()
    GO = auto()
    GREATER = auto()
    IF = auto()
    IN = auto()
    IS = auto()
    LEAST = auto()
    LESS = auto()
    LET = auto()
    MAKE = auto()
    ME = auto()
    MINUS = auto()
    MOST = auto()
    MULTIPLIED = auto()
    MULTIPLY = auto()
    MY = auto()
    MYSELF = auto()
    NOT = auto()
    OR = auto()
    OTHERWISE = auto()
    PLUS = auto()
    PM = auto()
    PUT = auto()
    REMAIN = auto()
    REMAINS = auto()
    REMEMBER = auto()
    REMOVE = auto()
    RETURN = auto()
    SAID = auto()
    SAY = auto()
    SO = auto()
    SUBTRACT = auto()
    THAN = auto()
    TIMES = auto()
    TO = auto()
    WAS = auto()
    WERE = auto()
    WHEN = auto()
    WHETHER = auto()
    WITH = auto()
    WITHOUT = auto()
    YOU = auto()
    YOUR = auto()
    YOURSELF = auto()


class Token():
    def __init__(self, token_type, lexeme, literal, line, pos):
        self.type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.pos = pos

    def __repr__(self):
        return f"[line {self.line}:{self.pos}] {TokenType(self.type).name} {self.lexeme} {self.literal}"

    def __str__(self):
        return self.__repr__()
