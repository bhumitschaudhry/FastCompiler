class ASTNode:
    pass
class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements
class Let(ASTNode):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
class Print(ASTNode):
    def __init__(self, expr):
        self.expr = expr
class BinOp(ASTNode):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
class Number(ASTNode):
    def __init__(self, value):
        self.value = value
class Var(ASTNode):
    def __init__(self, name):
        self.name = name
class ForLoop(ASTNode):
    def __init__(self, var, start_expr, end_expr, body):
        self.var = var
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.body = body
class If(ASTNode):
    def __init__(self, cond, then_block, else_block=None):
        self.cond = cond
        self.then_block = then_block
        self.else_block = else_block