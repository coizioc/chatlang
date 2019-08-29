from chat_interpreter.tokens import TokenType
from chat_interpreter.ast import NodeVisitor


class ReturnError(Exception):
    def __init__(self, expr):
        self.expr = expr


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.scopes = {}
        self.anchors = {}
        self.prev_scope = None
        self.curr_scope = None
        self.curr_msg = 0

    def format_output(self, out):
        if type(out) == float:
            # Convert integer-valued floats to ints for printing.
            if int(out) == out:
                out = int(out)
        return out

    def interpret(self):
        tree = self.parser.parse()
        if tree is not None:
            return self.visit(tree)

    def visit_Anchor(self, node):
        return node.value

    def visit_AnchorDecl(self, node):
        self.anchors[self.visit(node.value)] = node.stmt_num

    def visit_BinaryOp(self, node):
        if node.op == TokenType.ADD:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op == TokenType.SUBTRACT:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op == TokenType.MULTIPLY:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op == TokenType.DIVIDE:
            return self.visit(node.left) / self.visit(node.right)
        elif node.op == TokenType.REMAIN:
            return self.visit(node.left) % self.visit(node.right)

    def visit_Compound(self, node):
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_FuncCall(self, node):
        func_decl = self.visit(node.name)
        if not func_decl:
            raise NameError(node.name)
        block = func_decl.block_node

        if node.args:
            arg_values = []
            for arg in node.args:
                arg_values.append(self.visit(arg.expr))
            for arg_value, param in zip(arg_values,  func_decl.params):
                self.scopes[self.curr_scope][param.var_node.value] = arg_value

        try:
            self.visit(block)
        except ReturnError as e:
            return_val = self.visit(e.expr)
            return return_val
        return None

    def visit_FuncCallStmt(self, node):
        ret = self.visit(node.func_call)
        if ret:
            ret = self.format_output(ret)
            print(ret)

    def visit_FuncDecl(self, node):
        self.scopes[self.curr_scope][node.name.value] = node

    def visit_GotoStmt(self, node):
        self.curr_msg = self.anchors[self.visit(node.anchor)] - 1

    def visit_IfElse(self, node):
        if self.visit(node.condition):
            self.visit(node.if_block)
        elif node.else_block:
            self.visit(node.else_block)

    def visit_Logical(self, node):
        res = False
        if not node.op:
            res = self.visit(node.left) != 0
        elif node.op == TokenType.AND:
            return self.visit(node.left) and self.visit(node.right)
        elif node.op == TokenType.OR:
            return self.visit(node.left) or self.visit(node.right)
        elif node.op == TokenType.EQUAL:
            res = self.visit(node.left) == self.visit(node.right)
        elif node.op == TokenType.GREATER:
            res = self.visit(node.left) > self.visit(node.right)
        elif node.op == TokenType.LESS:
            res = self.visit(node.left) < self.visit(node.right)
        elif node.op == TokenType.MOST:
            res = self.visit(node.left) <= self.visit(node.right)
        elif node.op == TokenType.LEAST:
            res = self.visit(node.left) >= self.visit(node.right)

        if node.negate:
            res = not res
        return res

    def visit_Message(self, node):
        timestamp = self.visit(node.timestamp)
        if timestamp not in self.anchors.keys():
            self.anchors[timestamp] = self.curr_msg
        self.visit(node.stmts)

    def visit_NoOp(self, node):
        pass

    def visit_Num(self, node):
        return node.value

    def visit_PoeticNum(self, node):
        return node.value

    def visit_Program(self, node):
        while self.curr_msg < len(node.msgs):
            self.prev_scope = self.curr_scope
            self.curr_scope = self.visit(node.msgs[self.curr_msg].scope)

            self.visit(node.msgs[self.curr_msg])
            self.curr_msg += 1

    def visit_ScopeCall(self, node):
        scope_name = self.visit(node.scope)
        if scope_name not in self.scopes.keys():
            self.scopes[scope_name] = {}
            self.scopes[scope_name]['i'] = 0
        if node.var:
            return self.scopes[scope_name][node.var.value]
        else:
            return self.scopes[scope_name]['i']

    def visit_ScopeName(self, node):
        return node.value

    def visit_ScopePrev(self, node):
        if node.var:
            return self.scopes[self.prev_scope][node.var.value]
        else:
            return self.scopes[self.prev_scope]['i']

    def visit_ScopeSelf(self, node):
        return self.visit(node.var)

    def visit_Stmt(self, node):
        if self.curr_scope not in self.scopes.keys():
            self.scopes[self.curr_scope] = {}
            self.scopes[self.curr_scope]['i'] = 0
        self.visit(node.stmt)

    def visit_PrintStmt(self, node):
        out = self.visit(node.value)
        out = self.format_output(out)
        print(out)

    def visit_ReturnStmt(self, node):
        raise ReturnError(node.expr)

    def visit_String(self, node):
        return node.value

    def visit_Timestamp(self, node):
        return f'{self.visit(node.hh)}:{self.visit(node.mm)}'

    def visit_Var(self, node):
        try:
            return self.scopes[self.curr_scope][node.value]
        except KeyError:
            self.scopes[self.curr_scope][node.value] = 0
            return 0

    def visit_VarDecl(self, node):
        self.scopes[self.curr_scope][node.var.value.lower()] = self.visit(node.value)