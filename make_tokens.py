import re

pattern = re.compile('[\W_]+')

# coding=utf-8
def make_token():
    with open('keywords.txt', 'r') as f:
        lines = f.read().splitlines()

    keywords = set()
    for line in lines:
        for word in line.split():
            keywords.add(word)

    program = """from enum import Enum, auto


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
"""

    keywords_program = """from tokens import TokenType

KEYWORDS = {
"""

    for keyword in sorted(list(keywords)):
        const_name = pattern.sub('', keyword).upper()
        program += f"    {const_name} = auto()\n"
        keywords_program += f"    \"{keyword.lower()}\": TokenType.{const_name},\n"

    program += """

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
"""

    keywords_program = keywords_program[:-2] + '\n}\n'

    with open('tokens.py', 'w+') as f:
        f.write(program)

    with open('keywords.py', 'w+') as f:
        f.write(keywords_program)

if __name__ == '__main__':
    make_token()
