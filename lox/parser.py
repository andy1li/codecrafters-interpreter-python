from typing import NamedTuple, Optional
from lox.scanner import Token, TokenType


class ParseError(Exception): pass

class Binary(NamedTuple):
    left: 'Expr'
    op: Token
    right: 'Expr'

class Grouping(NamedTuple):
    expr: 'Expr'

class Literal(NamedTuple):
    value: object

class Unary(NamedTuple):
    op: Token
    right: 'Expr'

Expr = Binary | Grouping | Literal | Unary


class Parser:
    @staticmethod
    def print_ast(ast):
        def repr(expr: Expr):
            match expr:
                case Binary(left, op, right): return f'({op.lexeme} {repr(left)} {repr(right)})'
                case Grouping(expr)         : return f'(group {repr(expr)})'
                case Literal(value)         : return value
                case Unary(op, right)       : return f'({op.lexeme} {repr(right)})'
        print(repr(ast))
 
    def __init__(self, lox, tokens: list[Token]):
       self._lox = lox
       self._tokens = tokens
       self._current = 0

    def parse(self) -> Optional[Expr]:
        try:
            return self._expression()
        except ParseError:
            return None

    def _advance(self) -> Token:
        if not self._is_at_end(): self._current +=1
        return self._previous()

    def _check(self, type: TokenType) -> bool:
        if self._is_at_end(): return False
        return self._peek().type == type
    
    def _consume(self, type: TokenType, message: str) -> Token:
        if self._check(type): return self._advance()
        raise self._error(self._peek(), message)

    def _error(self, token: Token, message: str) -> ParseError:
        self._lox.error_token(token, message)
        return ParseError()

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF
    
    def _match(self, *types: TokenType) -> bool:
        for type in types:
            if self._check(type):
                self._advance()
                return True
        return False
    
    def _peek(self) -> Token:
        return self._tokens[self._current]
    
    def _previous(self) -> Token:
        return self._tokens[self._current - 1]

    # Grammar
    def _expression(self) -> Expr:
        return self._equality()
    
    def _equality(self) -> Expr:
        expr = self._comparison()
        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            op = self._previous()
            right = self._comparison()
            expr = Binary(expr, op, right)
        return expr
    
    def _comparison(self) -> Expr:
        expr = self._term()
        while self._match(
            TokenType.GREATER, TokenType.GREATER_EQUAL, 
            TokenType.LESS, TokenType.LESS_EQUAL
        ):
            op = self._previous()
            right = self._term()
            expr = Binary(expr, op, right)
        return expr
    
    def _term(self) -> Expr:
        expr = self._factor()
        while self._match(TokenType.MINUS, TokenType.PLUS):
            op = self._previous()
            right = self._factor()
            expr = Binary(expr, op, right)
        return expr
    
    def _factor(self) -> Expr:
        expr = self._unary()
        while self._match(TokenType.SLASH, TokenType.STAR):
            op = self._previous()
            right = self._unary()
            expr = Binary(expr, op, right)
        return expr
    
    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            op = self._previous()
            right = self._unary()
            return Unary(op, right)
        return self._primary()
    
    def _primary(self):
        if self._match(TokenType.FALSE): return Literal('false')
        if self._match(TokenType.TRUE) : return Literal('true')
        if self._match(TokenType.NIL)  : return Literal('nil')
        
        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)
        
        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        
        self._error(self._peek(), 'Expect expression.')
