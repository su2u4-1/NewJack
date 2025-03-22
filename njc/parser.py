from typing import NoReturn, Callable, Any

from lib import CompileError, Token, ASTNode, Tokens, STDLIB, source, BUILTINTYPE, OPERATOR


def log_function(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"-> {func.__name__}")
        result = func(*args, **kwargs)
        print(f"<- {func.__name__}")
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
            raise Exception(f"Unexpected EOF in {self.file}")
            # self.now = Token("EOF", "EOF")
        print(self.now)

    def next(self, a: int = 1) -> Token:
        if self.index + a < len(self.tokens):
            return self.tokens[self.index + a]
        else:
            return Token("EOF", "EOF")

    def parse(self) -> ASTNode:
        nodes: list[ASTNode] = []
        while True:
            try:
                self.get()
            except Exception:
                break
            if self.now == Token("keyword", "import"):
                nodes.append(self.parse_import())
            elif self.now == Token("keyword", "var"):
                nodes.extend(self.parse_var())
            elif self.now == Token("keyword", "func"):
                nodes.append(self.parse_func())
            elif self.now == Token("keyword", "class"):
                nodes.append(self.parse_class())
            elif self.now == Tokens("keyword", ("if", "for", "while")):
                nodes.append(self.parse_statements())
            else:
                pass  # TODO: error
        return ASTNode("root", *nodes, file=self.file)

    @log_function
    def parse_import(self) -> ASTNode:
        self.get()
        if self.now in STDLIB:
            lib_name = self.now.constant
            lib_alias = self.now.constant
        elif self.now.type == "string":
            lib_name = self.now.constant
            self.get()
            if self.now != Token("keyword", "as"):
                self.error(f"Expected 'as' after import statement", self.now.location)
            self.get()
            if self.now.type != "identifier":  # type: ignore
                self.error(f"Expected identifier after 'as' in import statement", self.now.location)
            lib_alias = self.now.constant
        elif self.now.type == "identifier":
            self.error(f"{self.now.constant} does not exist in stdlib", self.now.location)
        else:
            self.error(f"Invalid import statement", self.now.location)
        return ASTNode("import", name=lib_name, alias=lib_alias)

    @log_function
    def parse_var(self) -> list[ASTNode]:
        constant_var = False
        global_var = False
        if self.next() == Token("keyword", "constant"):
            self.get()
            constant_var = True
        if self.next() == Token("keyword", "global"):
            self.get()
            global_var = True
        type_var = self.parse_type()
        self.get()
        if self.now.type != "identifier":
            self.error(f"Expected identifier after variable type", self.now.location)
        declare_var: list[ASTNode] = []
        var_name = self.now.constant
        self.get()
        var_expression = ASTNode("None", "None")
        if self.now == Token("symbol", "="):
            self.get()
            var_expression = self.parse_expression()
            self.get()
        declare_var.append(
            ASTNode("var", var_type=type_var, constant=constant_var, global_=global_var, name=var_name, expression=var_expression)
        )
        if self.now == Token("symbol", ";"):
            return declare_var
        elif self.now == Token("symbol", ","):
            # while self.now == Token("symbol", ";"):
            while True:
                self.get()
                if self.now.type != "identifier":
                    self.error(f"Expected identifier after ',' in variable declaration", self.now.location)
                var_name = self.now.constant
                self.get()
                var_expression = ASTNode("None", "None")
                if self.now == Token("symbol", "="):
                    self.get()
                    var_expression = self.parse_expression()
                    self.get()
                declare_var.append(
                    ASTNode("var", var_type=type_var, constant=constant_var, global_=global_var, name=var_name, expression=var_expression)
                )
                if self.now == Token("symbol", ";"):
                    return declare_var
                elif self.now != Token("symbol", ","):
                    self.error(f"Invalid variable declaration", self.now.location)
        else:
            self.error(f"Invalid variable declaration", self.now.location)
        return declare_var

    @log_function
    def parse_func(self) -> ASTNode:
        return ASTNode("func")

    @log_function
    def parse_class(self) -> ASTNode:
        return ASTNode("class")

    @log_function
    def parse_statements(self) -> ASTNode:
        return ASTNode("statements")

    @log_function
    def parse_type(self) -> ASTNode:
        self.get()
        if self.now in BUILTINTYPE or self.now.type == "identifier":
            type_a = self.now.constant
        else:
            self.error(f"Invalid type declaration", self.now.location)
        type_b: list[ASTNode] = []
        if self.next() == Token("symbol", "<"):
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
            if self.now != Token("symbol", ">"):
                self.error(f"Expected '>' after type declaration", self.now.location)
        return ASTNode("type", type_a=type_a, type_b=type_b)

    @log_function
    def parse_expression(self) -> ASTNode:
        terms: list[ASTNode] = []
        operators: list[Token] = []
        terms.append(self.parse_term())
        self.get()
        while True:
            if self.now in OPERATOR:
                operators.append(self.now)
            else:
                break
            terms.append(self.parse_term())
            self.get()
        # TODO: parse expression

    @log_function
    def parse_term(self) -> ASTNode:
        # TODO: parse term
        return ASTNode("term")
