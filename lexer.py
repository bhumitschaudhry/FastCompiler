import re
from collections import namedtuple
Token = namedtuple('Token', ['type', 'value'])
TOKEN_SPEC = [
    ('NUMBER', r'\d+'),
    ('LET', r'\blet\b'),
    ('PRINT', r'\bprint\b'),
    ('FOR', r'\bfor\b'),
    ('IN', r'\bin\b'),
    ('IF', r'\bif\b'),
    ('ELSE', r'\belse\b'),
    ('RANGE', r'\.\.'),
    ('IDENT', r'[A-Za-z_][A-Za-z0-9_]*'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('EQ', r'='),
    ('OP', r'[\+\-\*/]'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
    ('MISMATCH', r'.'),
]
TOK_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC)
def tokenize(code):
    for mo in re.finditer(TOK_REGEX, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            yield Token('NUMBER', int(value))
        elif kind in ('LET', 'PRINT', 'FOR', 'IN', 'IF', 'ELSE'):
            yield Token(kind, value)
        elif kind == 'IDENT':
            yield Token('IDENT', value)
        elif kind == 'RANGE':
            yield Token('RANGE', value)
        elif kind in ('LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'EQ', 'OP'):
            yield Token(kind, value)
        elif kind == 'NEWLINE':
            yield Token('NEWLINE', value)
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected char: {value!r}')