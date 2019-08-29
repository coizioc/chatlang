import traceback

from chat_interpreter.ast import *
from chat_interpreter.tokens import TokenType

SCOPE_PREV_TOKENTYPES = [TokenType.YOU, TokenType.YOUR, TokenType.YOURSELF]
SCOPE_SELF_TOKENTYPES = [TokenType.I, TokenType.ME, TokenType.MY, TokenType.MYSELF]

class Parser():
    def __init__(self, scanner):
        self.tokens = scanner.tokens
        self.filename = scanner.filename
        self.current_scope = None
        self.current_token_index = 0
        self.current_token = self.tokens[0]
        self.current_msg = 0
        self.has_error = False

    def print_error(self, token, message):
        print(f"[{self.filename}, line {token.line}:{token.pos}] Error: {message}")
        self.has_error = True

    def eat(self, token_type=None):
        if token_type is None:
            token_value = self.current_token.literal
            self.get_next_token()
            return token_value
        elif self.current_token.type == token_type:
            token_value = self.current_token.literal
            self.get_next_token()
            return token_value
        else:
            self.print_error(self.current_token, f"Expected token {TokenType(token_type).name} "
                                                      f"(got {self.current_token.type}).")
            traceback.print_stack()
            raise TypeError

    def eat_from_list(self, token_types: list):
        token = self.current_token
        for e in token_types:
            if type(e) == TokenType:
                if token.type == e:
                    self.eat(e)
                    return e
            else:
                for token_type in e:
                    self.eat(token_type)
        else:
            self.print_error(self.current_token.line, f"Expected token in list {token_types}.")

    def get_next_token(self, ignore_whitespace=True):
        self.current_token_index += 1
        try:
            self.current_token = self.tokens[self.current_token_index]
            if ignore_whitespace:
                if self.current_token.type == TokenType.WHITESPACE:
                    self.get_next_token()
        except IndexError:
            self.print_error(self.tokens[self.current_token_index - 1].line, "Run out of tokens for expr.")

    def parse(self):
        node = self.program()
        if self.current_token.type != TokenType.EOF:
            self.print_error(self.current_token.line,
                             f"Finished parsing before EOF. (current token: {self.current_token})")
            return None
        else:
            return node

    def anchor(self):
        """
        anchor : HASH IDENTIFIER
        """
        self.eat(TokenType.HASH)
        node = Anchor(self.current_token)
        self.eat(TokenType.IDENTIFIER)
        return node

    def arg(self):
        """
        arg : [operation | string]
        """
        token = self.current_token
        if token.type == TokenType.STR:
            return Arg(self.string())
        else:
            return Arg(self.operation())

    def args_list(self):
        """
        args_list : arg
                  | arg COMMA args_list
        """
        args = [self.arg()]

        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            args.append(self.arg())

        return args

    def compound_statement(self):
        """
        compound_statement : statement PUNCT (statement PUNCT)*
        """

        stmts = [self.statement()]
        self.eat(TokenType.PUNCT)

        while self.current_token.type not in [TokenType.LBRACE, TokenType.DONE, TokenType.EOF]:
            stmts.append(self.statement())
            self.eat(TokenType.PUNCT)

        node = Compound(stmts)
        return node

    def condition(self):
        """
        condition : logic_or
        """
        node = self.logic_or()
        return node

    def func_call(self):
        """
        func_call : CALL [scope_call | scope_prev | scope_self | variable] (WITH args_list)
        """
        self.eat(TokenType.CALL)

        token = self.current_token
        if token.type in SCOPE_PREV_TOKENTYPES:
            var = self.scope_prev()
        elif token.type == TokenType.ATSYM:
            var = self.scope_call()
        elif token.type in SCOPE_SELF_TOKENTYPES:
            var = self.scope_self()
        else:
            var = self.variable()

        if self.current_token.type == TokenType.WITH:
            self.eat(TokenType.WITH)
            args = self.args_list()
        else:
            args = []

        node = FuncCall(var, args)
        return node

    def func_decl(self):
        """
        func_decl : MAKE [scope_self | variable] DO (WITH params_list) COLON compound_statement DONE
        """
        self.eat(TokenType.MAKE)
        token = self.current_token
        if token.type in SCOPE_SELF_TOKENTYPES:
            func_name = self.scope_self()
        else:
            func_name = self.variable()

        self.eat(TokenType.DO)

        if self.current_token.type == TokenType.WITH:
            self.eat(TokenType.WITH)
            params = self.params_list()
        else:
            params = []

        # if self.current_token.type == TokenType.THE:
        #     self.eat(TokenType.THE)
        #     self.eat(TokenType.FOLLOWING)

        self.eat(TokenType.COLON)

        func_body = self.compound_statement()

        self.eat(TokenType.DONE)

        node = FuncDecl(func_name, params, func_body)
        return node

    def ifelse(self):
        """
        ifelse : [IF | WHEN] condition COMMA statement (COMMA [OR ELSE | OTHERWISE] COMMA statement)
        """
        self.eat_from_list([TokenType.IF, TokenType.WHEN])

        cond = self.condition()

        self.eat(TokenType.COMMA)

        if_stmt = self.statement()

        if self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)

            token = self.current_token
            if token.type == TokenType.OR:
                self.eat(TokenType.OR)
                self.eat(TokenType.ELSE)
            elif token.type == TokenType.OTHERWISE:
                self.eat(TokenType.OTHERWISE)

            self.eat(TokenType.COMMA)

            else_stmt = self.statement()
        else:
            else_stmt = None


        node = IfElse(cond, if_stmt, else_stmt)
        return node

    def logic_and(self):
        """
        logic_and : logic_eq (AND logic_eq)*
        """
        node = self.logic_eq()

        while self.current_token.type == TokenType.AND:
            token = self.current_token
            self.eat(TokenType.AND)

            node = Logical(node, None, token, self.logic_and())

        return node

    def logic_or(self):
        """
        logic_or : logic_and (OR logic_and)*
        """
        node = self.logic_and()

        while self.current_token.type == TokenType.OR:
            token = self.current_token
            self.eat(TokenType.OR)

            node = Logical(node, None, token, self.logic_or())

        return node

    def logic_eq(self):
        """
        logic_eq : operation ([AM | IS | ARE | WAS | WERE] (NOT) ([EQUAL TO | LESS THAN | AT MOST |
                                                              GREATER THAN | AT LEAST]) operation)
        """
        left = self.operation()

        if self.current_token.type in [TokenType.AM, TokenType.IS, TokenType.ARE, TokenType.WAS, TokenType.WERE]:
            self.eat_from_list([TokenType.AM, TokenType.IS, TokenType.ARE, TokenType.WAS, TokenType.WERE])

            if self.current_token.type == TokenType.NOT:
                negate = True
                self.eat(TokenType.NOT)
            else:
                negate = False

            token = self.current_token
            if token.type == TokenType.EQUAL:
                op = TokenType.EQUAL
                self.eat(TokenType.EQUAL)
                self.eat(TokenType.TO)
            elif token.type == TokenType.GREATER:
                op = TokenType.GREATER
                self.eat(TokenType.GREATER)
                self.eat(TokenType.THAN)
            elif token.type == TokenType.LESS:
                op = TokenType.LESS
                self.eat(TokenType.LESS)
                self.eat(TokenType.THAN)
            elif token.type == TokenType.AT:
                self.eat(TokenType.AT)
                token = self.current_token
                if token.type == TokenType.MOST:
                    op = token
                    self.eat(TokenType.MOST)
                elif token.type == TokenType.LEAST:
                    op = token
                    self.eat(TokenType.LEAST)
            else:
                op = TokenType.EQUAL

            right = self.operation()
        else:
            negate = False
            op = None
            right = None

        node = Logical(left, negate, op, right)
        return node

    def message(self):
        """
        message : timestamp scope_name COLON compound_statement
        """
        timestamp = self.timestamp()
        scope_name = self.scope_name()
        self.current_scope = scope_name
        self.eat(TokenType.COLON)
        stmts = self.compound_statement()
        node = Message(timestamp, scope_name, stmts)
        return node

    def num(self):
        """
        num : NUM
        """
        node = Num(self.current_token)
        self.eat(TokenType.NUM)
        return node

    def operation(self):
        """
        operation : infix_operation
                    prefix_operation
        """
        token = self.current_token
        if token.type in [TokenType.ADD, TokenType.SUBTRACT, TokenType.MULTIPLY, TokenType.DIVIDE]:
            node = self.prefix_operation()
        else:
            node = self.infix_operation()
        return node

    def infix_operation(self):
        """
        infix_operation : term ([PLUS | AND | ADDED TO | MINUS | WITHOUT | TIMES | MULTIPLIED WITH | DIVIDED BY |
                                 REMAIN | REMAINS] term)*
        """
        node = self.term()

        while self.current_token.type in [TokenType.PLUS, TokenType.AND, TokenType.ADDED, TokenType.MINUS,
                                          TokenType.WITHOUT, TokenType.TIMES, TokenType.MULTIPLIED, TokenType.DIVIDED,
                                          TokenType.REMAINS, TokenType.REMAIN]:
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
                op = TokenType.ADD
            elif token.type == TokenType.AND:
                self.eat(TokenType.AND)
                op = TokenType.ADD
            elif token.type == TokenType.ADDED:
                self.eat(TokenType.ADDED)
                self.eat(TokenType.TO)
                op = TokenType.ADD
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
                op = TokenType.SUBTRACT
            elif token.type == TokenType.WITHOUT:
                self.eat(TokenType.WITHOUT)
                op = TokenType.SUBTRACT
            elif token.type == TokenType.TIMES:
                self.eat(TokenType.TIMES)
                op = TokenType.MULTIPLY
            elif token.type == TokenType.MULTIPLIED:
                self.eat(TokenType.MULTIPLIED)
                self.eat(TokenType.WITH)
                op = TokenType.MULTIPLY
            elif token.type == TokenType.DIVIDED:
                self.eat(TokenType.DIVIDED)
                self.eat(TokenType.BY)
                op = TokenType.DIVIDE
            elif token.type == TokenType.REMAINS:
                self.eat(TokenType.REMAINS)
                op = TokenType.REMAIN
            elif token.type == TokenType.REMAIN:
                self.eat(TokenType.REMAIN)
                op = TokenType.REMAIN

            right = self.term()

            node = BinaryOp(node, op, right)
        return node

    def prefix_operation(self):
        """
        prefix_operation : ADD term AND term
                           SUBTRACT term [AND | FROM] term
                           MULTIPLY term AND term
                           DIVIDE term [AND | BY] term
        """
        op = self.eat_from_list([TokenType.ADD, TokenType.SUBTRACT, TokenType.MULTIPLY, TokenType.DIVIDE])

        left = self.term()

        token = self.current_token
        if op == TokenType.SUBTRACT and token.type == TokenType.FROM:
            self.eat(TokenType.FROM)
        elif op == TokenType.DIVIDE and token.type == TokenType.BY:
            self.eat(TokenType.BY)
        else:
            self.eat(TokenType.AND)

        right = self.term()

        node = BinaryOp(left, op, right)
        return node

    def param(self):
        """
        param : variable
        """
        return Param(self.variable())

    def params_list(self):
        """
        params_list : param
                    | param COMMA params_list
        """
        params = [self.param()]

        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            params.append(self.param())

        return params

    def poetic_num(self):
        """
        poetic_num : [IDENTIFIER | KEYWORD] ([IDENTIFIER | KEYWORD])*
        """
        total = 0
        while self.current_token.type != TokenType.PUNCT:
            tok = self.eat()
            for word in tok.split():
                total *= 10
                total += len(word) % 10
        node = PoeticNum(total)
        return node

    def program(self):
        """
        program : message (message)*
        """

        msgs = [self.message()]

        while self.current_token.type == TokenType.LBRACE:
            self.current_msg += 1
            msgs.append(self.message())

        node = Program(msgs)
        return node

    def scope_call(self):
        """
        scope_call : ATSYM scope_name (APOST_S variable)
        """
        self.eat(TokenType.ATSYM)
        scope = self.scope_name()
        if self.current_token.type == TokenType.APOST_S:
            self.eat(TokenType.APOST_S)
            var = self.variable()
        else:
            var = None
        node = ScopeCall(scope, var)
        return node

    def scope_name(self):
        """
        variable : IDENT
        """
        node = ScopeName(self.current_token)
        self.eat(TokenType.IDENTIFIER)
        return node

    def scope_self(self):
        """
        scope_self : I | ME | MYSELF | MY variable
        """
        token = self.current_token
        if token.type == TokenType.I:
            var = Var(token)
            var.value = 'i'
            self.eat(TokenType.I)
        elif token.type == TokenType.ME:
            var = Var(token)
            var.value = 'i'
            self.eat(TokenType.ME)
        elif token.type == TokenType.MYSELF:
            var = Var(token)
            var.value = 'i'
            self.eat(TokenType.MYSELF)
        elif token.type == TokenType.MY:
            self.eat(TokenType.MY)
            var = self.variable()
        node = ScopeSelf(var)
        return node

    def scope_prev(self):
        """
        scope_prev : YOU | YOURSELF | YOUR variable
        """
        token = self.current_token
        if token.type == TokenType.YOU:
            self.eat(TokenType.YOU)
            var = None
        elif token.type == TokenType.YOURSELF:
            self.eat(TokenType.YOURSELF)
            var = None
        elif token.type == TokenType.YOUR:
            self.eat(TokenType.YOUR)
            var = self.variable()
        node = ScopePrev(var)
        return node

    def statement(self):
        """
        statement : empty
                    anchor_statement
                    declaration_statement
                    func_call_statement
                    goto_statement
                    ifelse
                    print_statement
        """
        token = self.current_token
        if token.type == TokenType.SAY:
            stmt = self.print_statement()
        elif token.type == TokenType.HASH:
            stmt = self.anchor_statement()
        elif token.type == TokenType.IF:
            stmt = self.ifelse()
        elif token.type == TokenType.CALL:
            stmt = self.func_call_statement()
        elif token.type == TokenType.MAKE:
            stmt = self.func_decl()
        elif token.type in [TokenType.GIVE, TokenType.RETURN]:
            stmt = self.return_statement()
        elif token.type in [TokenType.GO, TokenType.REMEMBER]:
            stmt = self.goto_statement()
        elif token.type in [TokenType.LET, TokenType.PUT]:
            stmt = self.assignment_statement()
        elif token.type in [TokenType.I, TokenType.IM, TokenType.MY, TokenType.IDENTIFIER]:
            stmt = self.declaration_statement()
        else:
            stmt = NoOp()
        stmt_node = Stmt(stmt)
        return stmt_node

    def anchor_statement(self):
        """
        anchor_statement : anchor
        """
        node = AnchorDecl(self.current_msg, self.anchor())
        return node

    def assignment_statement(self):
        """
        assignment_statement : LET [variable | scope_self | scope_call] BE operation
                               PUT operation IN [variable | scope_self | scope_call]
        """
        token = self.current_token

        if token.type == TokenType.LET:
            self.eat(TokenType.LET)

            token = self.current_token
            if token.type in SCOPE_SELF_TOKENTYPES:
                var = self.scope_self()
            elif token.type == TokenType.ATSYM:
                var = self.scope_call()
            else:
                var = self.variable()

            self.eat(TokenType.BE)
            value = self.operation()
        elif token.type == TokenType.PUT:
            self.eat(TokenType.PUT)
            var = self.operation()
            self.eat(TokenType.IN)

            token = self.current_token
            if token.type in SCOPE_SELF_TOKENTYPES:
                value = self.scope_self()
            elif token.type == TokenType.ATSYM:
                value = self.scope_call()
            else:
                value = self.variable()

        node = VarDecl(var, value)
        return node

    def declaration_statement(self):
        """
        declaration_statement : [I AM | IM | (MY) variable [IS | ARE | WAS | WERE]] [operation | poetic_num |
                                                                                string | WHETHER condition]
        """
        token = self.current_token
        if token.type == TokenType.IM:
            var = Var(self.current_token)
            var.token = TokenType.I
            var.value = 'i'
            self.eat(TokenType.IM)
        elif token.type == TokenType.I:
            var = self.scope_self()
            self.eat(TokenType.AM)
        elif token.type == TokenType.MY:
            var = self.scope_self()
            self.eat_from_list([TokenType.IS, TokenType.ARE, TokenType.WAS, TokenType.WERE])
        else:
            var = self.variable()
            self.eat_from_list([TokenType.IS, TokenType.ARE, TokenType.WAS, TokenType.WERE])

        token = self.current_token
        if token.type in SCOPE_PREV_TOKENTYPES + SCOPE_SELF_TOKENTYPES + [TokenType.NUM, TokenType.ATSYM]:
            value = self.operation()
        elif token.type == TokenType.WHETHER:
            self.eat(TokenType.WHETHER)
            value = self.condition()
        elif token.type == TokenType.STR:
            value = self.string()
        else:
            value = self.poetic_num()
        node = VarDecl(var, value)
        return node

    def func_call_statement(self):
        """
        func_call_statement : func_call
        """
        func_call = self.func_call()
        node = FuncCallStmt(func_call)
        return node

    def goto_statement(self):
        """
        goto_statement : [REMEMBER | GO TO] [anchor | timestamp]
        """
        token = self.current_token
        if token.type == TokenType.GO:
            self.eat(TokenType.GO)
            self.eat(TokenType.TO)
        elif token.type == TokenType.REMEMBER:
            self.eat(TokenType.REMEMBER)

        token = self.current_token
        if token.type == TokenType.HASH:
            goto = self.anchor()
        elif token.type == TokenType.LBRACE:
            goto = self.timestamp()

        node = GotoStmt(goto)
        return node

    def print_statement(self):
        """
        print_statement : SAY [operation | string]
        """
        token = self.current_token
        if token.type == TokenType.SAY:
            self.eat(TokenType.SAY)

        token = self.current_token
        if token.type == TokenType.STR:
            value = self.string()
        else:
            value = self.operation()

        node = PrintStmt(value)
        return node

    def return_statement(self):
        """
        return_statement : [GIVE BACK | RETURN] [operation | string]
        """
        token = self.current_token
        if token.type == TokenType.GIVE:
            self.eat(TokenType.GIVE)
            self.eat(TokenType.BACK)
        elif token.type == TokenType.RETURN:
            self.eat(TokenType.RETURN)

        token = self.current_token
        if token.type == TokenType.STR:
            value = self.string()
        else:
            value = self.operation()

        node = ReturnStmt(value)
        return node

    def string(self):
        """
        string : STR
        """
        node = String(self.current_token)
        self.eat(TokenType.STR)
        return node

    def term(self):
        """
        term : [num | variable | scope_call | scope_self | scope_prev | func_call]
        """
        token = self.current_token
        if token.type == TokenType.NUM:
            node = self.num()
        elif token.type == TokenType.ATSYM:
            node = self.scope_call()
        elif token.type in SCOPE_SELF_TOKENTYPES:
            node = self.scope_self()
        elif token.type in SCOPE_PREV_TOKENTYPES:
            node = self.scope_prev()
        elif token.type == TokenType.CALL:
            node = self.func_call()
        else:
            node = self.variable()
        return node

    def timestamp(self):
        """
        timestamp : LBRACE NUM COLON NUM ([AM | PM]) RBRACE
        """
        self.eat(TokenType.LBRACE)
        hh = self.num()
        self.eat(TokenType.COLON)
        mm = self.num()

        token = self.current_token

        # Optional conversion from 12-hour time to 24-hour time.
        if token.type == TokenType.AM:
            self.eat(TokenType.AM)
        elif token.type == TokenType.PM:
            self.eat(TokenType.PM)
            hh.value += 12

        self.eat(TokenType.RBRACE)
        node = Timestamp(hh, mm)
        return node

    def variable(self):
        """
        variable : IDENT
        """
        node = Var(self.current_token)
        self.eat(TokenType.IDENTIFIER)
        return node
