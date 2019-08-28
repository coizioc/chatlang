from tokens import Token, TokenType
from keywords import KEYWORDS


class Lexer():
    def __init__(self, source, filename):
        self.source = source#.replace("'", '')
        self.filename = filename
        self.start = 0
        self.current = 0
        self.line = 1
        self.pos = 0
        self.tokens = []
        self.has_error = False

    def print_error(self, line, pos, message):
        print(f"[{self.filename}, line {line}:{pos}] Error: {message}")
        self.has_error = True

    def advance(self):
        self.current += 1
        self.pos += 1
        return self.source[self.current - 1]

    def match(self, expected):
        # Advances current if match is expected, otherwise current is unchanged.
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self):
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self):
        if self.current + 2 > len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def handle_comment(self):
        start_pos = self.pos
        while self.peek() != ')' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        if self.is_at_end():
            self.print_error(self.line, start_pos, "Unterminated comment block.")
            return
        # Consume the trailing ')'
        self.advance()

    def handle_identifier(self):
        identifier = self.source[self.start:self.current].lower()
        while (self.peek().isalnum() or self.peek() == "'") and not self.is_at_end():
            # Break if next characters are 's.
            if self.peek() == "'" and self.peek_next() == 's':
                break
            # Advance while current character is an alphanumeric character or an apostrophe.
            while (self.peek().isalnum() or self.peek() == "'") and not self.is_at_end():
                # Break if next characters are 's.
                if self.peek() == "'" and self.peek_next() == 's':
                    break
                self.advance()
            identifier = self.source[self.start:self.current]

            # Determine if the last word is an identifier or a keyword.
            last_word = identifier.split()[-1].lower()
            for keyword in KEYWORDS.keys():
                if last_word == keyword:
                    # If so, all words before the last word is an identifier.
                    # Have to manually set self.start and self.current before adding the tokens.
                    keyword_start_index = self.start + len(identifier) - len(last_word) - 1
                    keyword_end_index = self.current
                    self.current = keyword_start_index
                    if len(identifier.split()) > 1:
                        self.add_token(TokenType.IDENTIFIER, ' '.join(identifier.split()[:-1]).lower())

                    self.start = keyword_start_index + 1
                    self.current = keyword_end_index
                    self.add_token(KEYWORDS[last_word], last_word)
                    return
            # If no keywords match, parse a new word.
            else:
                if self.peek() in [' ', '\r', '\t']:
                    self.advance()
        if identifier != "":
            for keyword in KEYWORDS.keys():
                if identifier == keyword:
                    self.add_token(KEYWORDS[identifier])
                    return
            else:
                self.add_token(TokenType.IDENTIFIER, identifier)

    def handle_number(self):
        # Advance while current is a digit.
        while self.peek().isdigit():
            self.advance()

        # Handle floats.
        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()
        self.add_token(TokenType.NUM, float(self.source[self.start:self.current]))

    def handle_string(self):
        start_pos = self.pos
        # Advance until terminating " or EOF is found.
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            self.print_error(self.line, start_pos, "Unterminated string.")
            return

        # The closing "
        self.advance()

        # Trim the surrounding quotes
        value = self.source[self.start + 1: self.current - 1]
        self.add_token(TokenType.STR, value)

    def is_at_end(self):
        return self.current >= len(self.source)

    def add_token(self, tok, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(tok, text, literal, self.line, self.pos))

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line, self.pos))

    def scan_token(self):
        curr_tok = None
        curr_char = self.advance()

        # Punctuation
        if curr_char == '.':
            curr_tok = TokenType.PUNCT
        elif curr_char == '!':
            curr_tok = TokenType.PUNCT
        elif curr_char == '?':
            curr_tok = TokenType.PUNCT

        # Single-character tokens
        elif curr_char == '@':
            curr_tok = TokenType.ATSYM
        elif curr_char == '[':
            curr_tok = TokenType.LBRACE
        elif curr_char == ']':
            curr_tok = TokenType.RBRACE
        elif curr_char == ':':
            curr_tok = TokenType.COLON
        elif curr_char == ',':
            curr_tok = TokenType.COMMA
        elif curr_char == '#':
            curr_tok = TokenType.HASH

        # Multiple-character tokens
        elif curr_char == "'":
            curr_tok = TokenType.APOST_S if self.match('s') else TokenType.APOST

        # Handle comments.
        elif curr_char == '(':
            self.handle_comment()
            return

        # Handle literals
        elif curr_char == '"':
            self.handle_string()
            return
        elif curr_char.isdigit():
            self.handle_number()
            return
        elif curr_char.isalpha():
            self.handle_identifier()
            return

        # Handle whitespace
        elif curr_char in [' ', '\r', '\t']:
            return
        elif curr_char == '\n':
            self.line += 1
            self.pos = 0
            return
        else:
            self.print_error(self.line, self.pos, f"Unexpected character. ({curr_char})")
            return
        if curr_tok is not None:
            self.add_token(curr_tok)

    def __repr__(self):
        out = ""
        for token in self.tokens:
            out += f"{token}\n"
        return out

    def __str__(self):
        return self.__repr__()
