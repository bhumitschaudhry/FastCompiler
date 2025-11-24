from lexer import tokenize, Token
from ast import *
class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type != 'NEWLINE']
        self.pos = 0
    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else Token('EOF', '')
    def next(self):
        t = self.peek()
        self.pos += 1
        return t
    def expect(self, tp):
        t = self.next()
        if t.type != tp:
            raise RuntimeError(f'Expected {tp}, got {t}')
        return t
    def parse(self):
        stmts = []
        while self.peek().type != 'EOF':
            stmts.append(self.parse_statement())
        return Program(stmts)
    def parse_statement(self):
        t = self.peek()
        if t.type == 'LET':
            self.next()
            name = self.expect('IDENT').value
            self.expect('EQ')
            expr = self.parse_expr()
            return Let(name, expr)
        elif t.type == 'PRINT':
            self.next()
            self.expect('LPAREN')
            expr = self.parse_expr()
            self.expect('RPAREN')
            return Print(expr)
        elif t.type == 'FOR':
            self.next()
            var = self.expect('IDENT').value
            self.expect('IN')
            start = self.parse_expr()
            self.expect('RANGE')
            end = self.parse_expr()
            self.expect('LBRACE')
            body = []
            while self.peek().type != 'RBRACE':
                body.append(self.parse_statement())
            self.expect('RBRACE')
            return ForLoop(var, start, end, body)
        elif t.type == 'IF':
            self.next()
            cond = self.parse_expr()
            self.expect('LBRACE')
            then_block = []
            while self.peek().type != 'RBRACE':
                then_block.append(self.parse_statement())
            self.expect('RBRACE')
            else_block = None
            if self.peek().type == 'ELSE':
                self.next()
                self.expect('LBRACE')
                else_block = []
                while self.peek().type != 'RBRACE':
                    else_block.append(self.parse_statement())
                self.expect('RBRACE')
            return If(cond, then_block, else_block)
        else:
            return self.parse_expr()
    def parse_expr(self):
        node = self.parse_term()
        while self.peek().type == 'OP' and self.peek().value in ('+', '-'):
            op = self.next().value
            right = self.parse_term()
            node = BinOp(op, node, right)
        return node
    def parse_term(self):
        node = self.parse_factor()
        while self.peek().type == 'OP' and self.peek().value in ('*', '/'):
            op = self.next().value
            right = self.parse_factor()
            node = BinOp(op, node, right)
        return node
    def parse_factor(self):
        t = self.peek()
        if t.type == 'NUMBER':
            self.next()
            return Number(t.value)
        elif t.type == 'IDENT':
            self.next()
            return Var(t.value)
        elif t.type == 'LPAREN':
            self.next()
            node = self.parse_expr()
            self.expect('RPAREN')
            return node
        else:
            raise RuntimeError(f'Unexpected token in expression: {t}')