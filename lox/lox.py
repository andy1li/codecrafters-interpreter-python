import sys
from lox.parser import Parser
from lox.scanner import Scanner, Token, TokenType

class Lox:
    def __init__(self, filename: str):
        self._tokens: list[Token] = []
        self._ast = None
        self._had_error = False

        with open(filename) as f:
            self._source = f.read()
        
    def error_line(self, line: int, message: str):
        self._error_report(line, '', message)

    def error_token(self, token: Token, message: str):
        where = ' at ' + ('end' if token.type == TokenType.EOF else f"'{token.lexeme}'")
        self._error_report(token.line, where, message)

    def parse(self):
        self.scan(False)
        parser = Parser(self, self._tokens)
        self._ast = parser.parse()
        if self._had_error: sys.exit(65)
        Parser.print_ast(self._ast)

    def scan(self, should_print=True):
        scanner = Scanner(self, self._source)
        self._tokens = scanner.scan_tokens()
        if should_print: print(*self._tokens, sep='\n')
        if self._had_error: sys.exit(65)

    def _error_report(self, line: int, where: str, message: str):
        self._had_error = True
        output = f'[line {line}] Error{where}: {message}'
        print(output, file=sys.stderr)
