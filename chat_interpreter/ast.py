class AST(object):
    pass


class Anchor(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.lexeme


class AnchorDecl(AST):
    def __init__(self, stmt_num, value):
        self.stmt_num = stmt_num
        self.value = value


class Arg(AST):
    def __init__(self, expr):
        self.expr = expr


class BinaryOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class Compound(AST):
    def __init__(self, stmts):
        self.stmts = stmts


class FuncCall(AST):
    def __init__(self, name, args):
        self.name = name
        self.args = args  # a list of Arg nodes
        self.return_val = None


class FuncCallStmt(AST):
    def __init__(self, func_call):
        self.func_call = func_call


class FuncDecl(AST):
    def __init__(self, name, params, block_node):
        self.name = name
        self.params = params  # a list of Param nodes
        self.block_node = block_node

    def __repr__(self):
        return f'func {self.name} taking {[p.var_node.value for p in self.params]}'

    def __str__(self):
        return self.__repr__()


class GotoStmt(AST):
    def __init__(self, anchor):
        self.anchor = anchor


class IfElse(AST):
    def __init__(self, condition, if_block, else_block):
        self.condition = condition
        self.if_block = if_block
        self.else_block = else_block


class IncrementOp(AST):
    def __init__(self, left, op):
        self.left = left
        self.op = op


class Logical(AST):
    def __init__(self, left, negate, op, right):
        self.left = left
        self.negate = negate
        self.op = op
        self.right = right


class Message(AST):
    def __init__(self, timestamp, scope, stmts):
        self.timestamp = timestamp
        self.scope = scope
        self.stmts = stmts


class NoOp(AST):
    pass


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.literal


class Param(AST):
    def __init__(self, var_node):
        self.var_node = var_node


class PoeticNum(AST):
    def __init__(self, value):
        self.value = value


class PrintStmt(AST):
    def __init__(self, value):
        self.value = value


class Program(AST):
    def __init__(self, msgs):
        self.msgs = msgs


class ReturnStmt(AST):
    def __init__(self, expr):
        self.expr = expr


class ScopeCall(AST):
    def __init__(self, scope, var):
        self.scope = scope
        self.var = var

    def __repr__(self):
        if self.var:
            return f'{self.scope}\'s {self.var.value}'
        else:
            return f"{self.scope.value}\s i"


class ScopeName(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.lexeme


class ScopeSelf(AST):
    def __init__(self, var):
        self.token = var.token
        self.value = var.value
        self.var = var

    def __repr__(self):
        if self.var:
            return f'my {self.var.value}'
        else:
            return "i"

    def __str__(self):
        return self.__repr__()


class ScopePrev(AST):
    def __init__(self, var):
        self.var = var

    def __repr__(self):
        if self.var:
            return f'your {self.var.value}'
        else:
            return "you"

    def __str__(self):
        return self.__repr__()


class Stmt(AST):
    def __init__(self, stmt):
        self.stmt = stmt


class String(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.literal


class Timestamp(AST):
    def __init__(self, hh, mm):
        self.hh = hh
        self.mm = mm


class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.lexeme

    def __repr__(self):
        return f'Variable {self.token}'

    def __str__(self):
        return self.__repr__()


class VarDecl(AST):
    def __init__(self, var, value):
        self.var = var
        self.value = value
