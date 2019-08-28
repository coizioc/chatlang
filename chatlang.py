import sys

from lexer import Lexer
from token_parser import Parser
from interpreter import Interpreter
from make_tokens import make_token

make_token()

def run_file(filename):
    with open(filename, 'r') as f:
        had_error = run(f.read(), filename)
    if had_error:
        sys.exit(65)


def run_prompt():
    while True:
        source = input("> ")
        run(source, "")


def run(source, filename):
    scanner = Lexer(source, filename)
    scanner.scan_tokens()
    # print(scanner)
    if scanner.has_error:
        return True

    parser = Parser(scanner)
    interpreter = Interpreter(parser)
    interpreter.interpret()

    # print(interpreter.scopes)
    return False

if __name__ == '__main__':
    if len(sys.argv) > 2:
        print("Usage: python chatlang.py [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_prompt()
