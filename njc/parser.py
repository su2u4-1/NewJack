from typing import Callable, NoReturn, TypeVar

from lib import ASTNode, BUILTINTYPE, CompileError, OPERATOR, PRECEDENCE, source, STDLIB, Token, Tokens

T = TypeVar("T")
log: list[str] = []


def log_function(func: Callable[..., T]) -> Callable[..., T]:
    def wrapper(*args: ..., **kwargs: ...) -> T:
        log.append(f"into-> {func.__name__}")
        result = func(*args, **kwargs)
        log.append(f"<-exit {func.__name__}")
        return result

    return wrapper


class Parser:
    def __init__(self, tokens: list[Token], file: str) -> None:
        self.tokens = tokens
        self.file = file
        self.index = -1
        self.now = Token("", "")

    def error(self, message: str, location: tuple[int, int]) -> NoReturn:
        raise CompileError(message, self.file, source[self.file][location[0] - 1], location)
        # print(CompileError(message, self.file, source[self.file][location[0] - 1], location))
        # exit()

    def get(self) -> None:
        self.index += 1
        if self.index < len(self.tokens):
            self.now = self.tokens[self.index]
            if self.now.type == "comment":
                self.get()
            else:
                log.append(str(self.now))
        else:
            raise Exception(f"Unexpected EOF in {self.file}")
            # self.now = Token("EOF", "EOF")

    def next(self, a: int = 1) -> Token:
        if self.index + a < len(self.tokens):
            return self.tokens[self.index + a]
        else:
            return Token("EOF", "EOF")

    def parse(self) -> ASTNode:
        nodes: list[ASTNode] = []
        try:
            while True:
                try:
                    self.get()
                except Exception:
                    break
                if self.now == Token("keyword", "import"):
                    nodes.append(self.parse_import())
                elif self.now == Token("keyword", "function"):
                    nodes.append(self.parse_function())
                elif self.now == Token("keyword", "class"):
                    nodes.append(self.parse_class())
                elif self.now == Tokens("keyword", ("if", "for", "while", "var", "constant", "attr", "static")):
                    nodes.extend(self.parse_statement())
                else:
                    pass  # TODO: error
        except Exception as e:
            for i in log:
                print(i)
            print(ASTNode("root", nodes, file=self.file))
            raise e
        return ASTNode("root", nodes, file=self.file)

    @log_function
    def parse_import(self) -> ASTNode:
        self.get()
        if self.now in STDLIB:
            lib_name = self.now.content
            lib_alias = self.now.content
        elif self.now.type == "string":
            lib_name = self.now.content
            self.get()
            if self.now != Token("keyword", "as"):
                self.error(f"Expected 'as' after import statement", self.now.location)
            self.get()
            if self.now.type != "identifier":  # type: ignore
                self.error(f"Expected identifier after 'as' in import statement", self.now.location)
            lib_alias = self.now.content
        elif self.now.type == "identifier":
            self.error(f"{self.now.content} does not exist in stdlib", self.now.location)
        else:
            self.error(f"Invalid import statement", self.now.location)
        return ASTNode("import", name=lib_name, alias=lib_alias)

    @log_function
    def parse_var(self) -> list[ASTNode]:
        assert self.now in Tokens("keyword", ("var", "constant", "attr", "static"))
        var_kind = self.now.content
        self.get()
        if self.now == Token("keyword", "global"):
            self.get()
            var_kind += " global"
        type_var = self.parse_type()
        self.get()
        if self.now.type != "identifier":
            self.error(f"Expected identifier after variable type", self.now.location)
        declare_var: list[ASTNode] = []
        var_name = self.now.content
        self.get()
        var_expression = ASTNode("None", "None")
        if self.now == Token("symbol", "="):
            self.get()
            var_expression = self.parse_expression()
        declare_var.append(
            ASTNode(
                "var",
                var_type=type_var,
                var_kind=var_kind,
                name=var_name,
                expression=var_expression,
            )
        )
        if self.now == Token("symbol", ";"):
            return declare_var
        elif self.now == Token("symbol", ","):
            # while self.now == Token("symbol", ";"):
            while True:
                self.get()
                if self.now.type != "identifier":
                    self.error(f"Expected identifier after ',' in variable declaration", self.now.location)
                var_name = self.now.content
                self.get()
                var_expression = ASTNode("None", "None")
                if self.now == Token("symbol", "="):
                    self.get()
                    var_expression = self.parse_expression()
                declare_var.append(
                    ASTNode(
                        "var",
                        var_type=type_var,
                        var_kind=var_kind,
                        name=var_name,
                        expression=var_expression,
                    )
                )
                if self.now == Token("symbol", ";"):
                    return declare_var
                elif self.now != Token("symbol", ","):
                    self.error(f"Invalid variable declaration", self.now.location)
        else:
            self.error(f"Invalid variable declaration", self.now.location)
        return declare_var

    @log_function
    def parse_type(self) -> ASTNode:
        if self.now in BUILTINTYPE or self.now.type == "identifier":
            type_a = self.now.content
        else:
            self.error(f"Invalid type declaration", self.now.location)
        type_b: list[ASTNode] = []
        if self.next() == Token("symbol", "<"):
            self.get()
            self.get()
            type_b.append(self.parse_type())
            self.get()
            if self.now == Token("symbol", ","):
                while True:
                    type_b.append(self.parse_type())
                    self.get()
                    if self.now == Token("symbol", ">"):
                        break
                    elif self.now != Token("symbol", ","):
                        self.error(f"Expected '>' after type declaration", self.now.location)
                    self.get()
            if self.now != Token("symbol", ">"):
                self.error(f"Expected '>' after type declaration", self.now.location)
        return ASTNode("type", type_a=type_a, type_b=type_b)

    @log_function
    def parse_expression(self) -> ASTNode:
        input: list[ASTNode] = []
        output: list[ASTNode] = []
        stack: list[ASTNode] = []
        input.append(self.parse_term())
        self.get()
        while True:
            if self.now in OPERATOR:
                input.append(ASTNode("operator", self.now.content))
                self.get()
            else:
                break
            input.append(self.parse_term())
            self.get()
        for i in input:
            if i.type == "operator":
                while len(stack) > 0:
                    assert "value" in i.args
                    assert "value" in stack[-1].args
                    assert isinstance(i.args["value"], str)
                    assert isinstance(stack[-1].args["value"], str)
                    if PRECEDENCE[i.args["value"]] >= PRECEDENCE[stack[-1].args["value"]]:
                        output.append(stack.pop())
                    else:
                        break
                stack.append(i)
            else:
                assert i.type == "term"
                output.append(i)
        while len(stack) > 0:
            output.append(stack.pop())
        return ASTNode("expression", output)

    @log_function
    def parse_term(self) -> ASTNode:
        if self.now.type == "symbol" and self.now.content in ("-", "^", "!", "@"):
            t = ""
            if self.now.content == "@":
                t = "pointer"
            elif self.now.content == "!":
                t = "not"
            elif self.now.content == "-":
                t = "neg"
            elif self.now.content == "^":
                t = "depointer"
            assert t != ""
            self.get()
            return ASTNode("term", ASTNode(t, self.parse_term()))
        elif self.now == Token("symbol", "("):
            term = self.parse_tuple()
            assert "value" in term.args
            assert isinstance(term.args["value"], list)
            assert len(term.args["value"]) >= 1
            assert isinstance(term.args["value"][0], ASTNode)
            assert term.args["value"][0].type == "expression"
            if len(term.args["value"]) == 1:
                return ASTNode("term", ASTNode("expression", term.args["value"][0]))
            else:
                return ASTNode("term", ASTNode("tuple", term.args["value"]))
        elif self.now == Token("symbol", "["):
            return ASTNode("term", self.parse_arr())
        elif self.now == Token("symbol", "{"):
            return ASTNode("term", self.parse_dict())
        elif self.now.type == "identifier":
            return ASTNode("term", self.parse_variable())
        elif self.now.type in ("int", "float", "string", "char"):
            return ASTNode("term", ASTNode(self.now.type, self.now.content))
        elif self.now.type == "keyword":
            if self.now.content in ("true", "false"):
                return ASTNode("term", ASTNode("bool", self.now.content))
            elif self.now.content == "NULL":
                return ASTNode("term", ASTNode("void", "NULL"))
            elif self.now in BUILTINTYPE:
                return ASTNode("term", self.parse_variable())
            else:
                self.error(f"The keyword '{self.now.content}' does not exist in term", self.now.location)
        else:
            self.error("Invalid term", self.now.location)
        return ASTNode("term")

    @log_function
    def parse_variable(self) -> ASTNode:
        # TODO: parse variable
        if self.now.type != "identifier" and self.now not in BUILTINTYPE:
            self.error("Expected identifier in variable", self.now.location)
        var_name = self.now.content
        if self.next() == Token("symbol", "["):
            self.get()
            self.get()
            index = self.parse_expression()
            if self.now != Token("symbol", "]"):
                self.error("Expected ']' after index in variable", self.now.location)
            var = ASTNode("variable", var_name, index=index)
        elif self.next() == Token("symbol", "."):
            self.get()
            self.get()
            var = ASTNode("variable", var_name, attr=self.parse_variable())
        else:
            var = ASTNode("variable", var_name)
        if self.next() == Tokens("symbol", ("(", "<")):
            self.get()
            var = self.parse_call(var)
        return var

    @log_function
    def parse_call(self, var: ASTNode) -> ASTNode:
        types: list[ASTNode] = []
        if self.now == "<":
            self.get()
            types.append(self.parse_type())
            self.get()
            if self.now == Token("symbol", ","):
                while True:
                    types.append(self.parse_type())
                    self.get()
                    if self.now == Token("symbol", ">"):
                        break
                    elif self.now != Token("symbol", ","):
                        self.error("Expected '>' after type declaration", self.now.location)
                    self.get()
            if self.now != Token("symbol", ">"):
                self.error("Expected '>' after type declaration", self.now.location)
            self.get()
        if self.now != Token("symbol", "("):
            self.error("Expected '(' after function call", self.now.location)
        self.get()
        args: list[ASTNode] = []
        if self.now != Token("symbol", ")"):
            args.append(self.parse_expression())
            while self.now == Token("symbol", ","):
                self.get()
                args.append(self.parse_expression())
            if self.now != Token("symbol", ")"):
                self.error("Expected ')' after function call", self.now.location)
        return ASTNode("call", var=var, types=types, args=args)

    @log_function
    def parse_arr(self) -> ASTNode:
        arr: list[ASTNode] = []
        assert self.now == Token("symbol", "[")
        self.get()
        if self.now != Token("symbol", "]"):
            arr.append(self.parse_expression())
            while self.now == Token("symbol", ","):
                self.get()
                arr.append(self.parse_expression())
            if self.now != Token("symbol", "]"):
                self.error("Expected ']' after array declaration", self.now.location)
        return ASTNode("arr", arr)

    @log_function
    def parse_tuple(self) -> ASTNode:
        t: list[ASTNode] = []
        assert self.now == Token("symbol", "(")
        self.get()
        if self.now != Token("symbol", ")"):
            t.append(self.parse_expression())
            while self.now == Token("symbol", ","):
                self.get()
                t.append(self.parse_expression())
            if self.now != Token("symbol", ")"):
                self.error("Expected ')' after tuple declaration", self.now.location)
        return ASTNode("tuple", t)

    @log_function
    def parse_dict(self) -> ASTNode:
        d: list[tuple[ASTNode, ASTNode]] = []
        assert self.now == Token("symbol", "{")
        self.get()
        if self.now != Token("symbol", "}"):
            a = self.parse_expression()
            if self.now != Token("symbol", ":"):
                self.error("Expected ':' after key in dict declaration", self.now.location)
            self.get()
            b = self.parse_expression()
            d.append((a, b))
            while self.now == Token("symbol", ","):
                a = self.parse_expression()
                if self.now != Token("symbol", ":"):
                    self.error("Expected ':' after key in dict declaration", self.now.location)
                self.get()
                b = self.parse_expression()
                d.append((a, b))
            if self.now != Token("symbol", "}"):
                self.error("Expected '}' after array declaration", self.now.location)
        return ASTNode("dict")

    @log_function
    def parse_function(self) -> ASTNode:
        assert self.now == Token("keyword", "function")
        self.get()
        constant = False
        if self.now == Token("keyword", "constant"):
            constant = True
            self.get()
        func_type = self.parse_type()
        self.get()
        if self.now.type != "identifier":
            self.error("Expected identifier after function type", self.now.location)
        func_name = self.now.content
        self.get()
        types: list[ASTNode] = []
        if self.now == Token("symbol", "<"):
            self.get()
            if self.now.type != "identifier":
                self.error("Expected identifier after '<' in function declaration", self.now.location)
            types.append(
                ASTNode(
                    "var",
                    var_type=ASTNode("type", type_a="type", type_b=[]),
                    var_kind="typevar",
                    name=self.now.content,
                    expression=ASTNode("None", "None"),
                )
            )
            self.get()
            if self.now == Token("symbol", ","):
                while True:
                    if self.now.type != "identifier":
                        self.error("Expected identifier after '<' in function declaration", self.now.location)
                    types.append(
                        ASTNode(
                            "var",
                            var_type=ASTNode("type", type_a="type", type_b=[]),
                            var_kind="typevar",
                            name=self.now.content,
                            expression=ASTNode("None", "None"),
                        )
                    )
                    self.get()
                    if self.now == Token("symbol", ">"):
                        break
                    elif self.now != Token("symbol", ","):
                        self.error("Expected '>' after type declaration", self.now.location)
                    self.get()
            if self.now != Token("symbol", ">"):
                self.error("Expected '>' after type declaration", self.now.location)
            self.get()
        if self.now != Token("symbol", "("):
            self.error("Expected '(' after function name", self.now.location)
        args = self.parse_args()
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("Expected '{' after function declaration", self.now.location)
        self.get()
        func_body: list[ASTNode] = []
        while self.now != Token("symbol", "}"):
            func_body.extend(self.parse_statement())
            self.get()
        return ASTNode("function", constant=constant, func_type=func_type, type_var=types, name=func_name, args=args, body=func_body)

    @log_function
    def parse_class(self) -> ASTNode:
        return ASTNode("class")

    @log_function
    def parse_statement(self) -> list[ASTNode]:
        if self.now == Token("keyword", "if"):
            return [self.parse_if()]
        elif self.now == Token("keyword", "for"):
            return [self.parse_for()]
        elif self.now == Token("keyword", "while"):
            return [self.parse_while()]
        elif self.now == Token("keyword", "break"):
            return [self.parse_break()]
        elif self.now == Token("keyword", "return"):
            return [self.parse_return()]
        elif self.now == Tokens("keyword", ("var", "constant")):
            return self.parse_var()
        elif self.now == Tokens("keyword", ("attr", "static")):
            self.error("declare attr not in function", self.now.location)
        elif self.now == Token("keyword", "continue"):
            self.get()
            if self.now != Token("symbol", ";"):
                self.error("Expected ';' after continue statement", self.now.location)
            return [ASTNode("continue")]
        elif self.now == Token("keyword", "pass"):
            self.get()
            if self.now != Token("symbol", ";"):
                self.error("Expected ';' after continue statement", self.now.location)
            return [ASTNode("pass")]
        else:
            t = self.parse_expression()
            if self.now != Token("symbol", ";"):
                self.error("Expected ';' after continue statement", self.now.location)
            return [t]

    @log_function
    def parse_if(self) -> ASTNode:
        return ASTNode("if")

    @log_function
    def parse_for(self) -> ASTNode:
        return ASTNode("for")

    @log_function
    def parse_while(self) -> ASTNode:
        return ASTNode("while")

    @log_function
    def parse_break(self) -> ASTNode:
        return ASTNode("break")

    @log_function
    def parse_return(self) -> ASTNode:
        assert self.now == Token("keyword", "return")
        self.get()
        t = ASTNode("None", "None")
        if self.now != Token("symbol", ";"):
            t = self.parse_expression()
        if self.now != Token("symbol", ";"):
            self.error("Expected ';' after return statement", self.now.location)
        return ASTNode("return", t)

    @log_function
    def parse_args(self) -> list[ASTNode]:
        assert self.now == Token("symbol", "(")
        self.get()
        args: list[ASTNode] = []
        if self.now != Token("symbol", ")"):
            arg_type = self.parse_type()
            self.get()
            if self.now.type != "identifier":
                self.error("Expected identifier after argument type", self.now.location)
            args.append(
                ASTNode(
                    "var",
                    var_type=arg_type,
                    var_kind="arg",
                    name=self.now.content,
                    expression=ASTNode("None", "None"),
                )
            )
            self.get()
            while self.now == Token("symbol", ","):
                self.get()
                arg_type = self.parse_type()
                self.get()
                if self.now.type != "identifier":
                    self.error("Expected identifier after argument type", self.now.location)
                args.append(
                    ASTNode(
                        "var",
                        var_type=arg_type,
                        var_kind="arg",
                        name=self.now.content,
                        expression=ASTNode("None", "None"),
                    )
                )
                self.get()
            if self.now != Token("symbol", ")"):
                self.error("Expected ')' after subroutine arguments", self.now.location)
        return args
