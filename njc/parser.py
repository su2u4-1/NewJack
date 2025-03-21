from typing import NoReturn

from lib import CompileError, Token, ASTNode, Tokens, STDLIB, source


class Parser:
    def __init__(self, tokens: list[Token], file: str) -> None:
        self.tokens = tokens
        self.file = file
        self.index = -1
        self.now = Token("", "")

    def error(self, message: str, location: tuple[int, int]) -> NoReturn:
        raise CompileError(message, self.file, source[self.file][location[0]], location)

    def get(self) -> None:
        self.index += 1
        if self.index < len(self.tokens):
            self.now = self.tokens[self.index]
        else:
            raise Exception(f"Unexpected EOF in {self.file}")

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
                nodes.append(self.parse_var())
            elif self.now == Token("keyword", "func"):
                nodes.append(self.parse_func())
            elif self.now == Token("keyword", "class"):
                nodes.append(self.parse_class())
            elif self.now == Tokens("keyword", ("if", "for", "while")):
                nodes.append(self.parse_statements())
            else:
                print(self.now)
        return ASTNode("root", *nodes, file=self.file)

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
            if self.now.type != "identifier":
                self.error(f"Expected identifier after 'as' in import statement", self.now.location)
            lib_alias = self.now.constant
        elif self.now.type == "identifier":
            self.error(f"{self.now.constant} does not exist in stdlib", self.now.location)
        else:
            self.error(f"Invalid import statement", self.now.location)
        return ASTNode("import", name=lib_name, alias=lib_alias)

    def parse_var(self) -> ASTNode:
        self.get()
        constant_var = False
        global_var = False
        if self.now == Token("keyword", "constant"):
            constant_var = True
            self.get()
        if self.now == Token("keyword", "global"):
            global_var = True
            self.get()
        if self.now.type == "identifier" or self.now in STDLIB:
            self.parse_type()
        else:
            self.error(f"Invalid variable declaration", self.now.location)
        # TODO: parse variable declaration
        return ASTNode("var")

    def parse_func(self) -> ASTNode:
        return ASTNode("func")

    def parse_class(self) -> ASTNode:
        return ASTNode("class")

    def parse_statements(self) -> ASTNode:
        return ASTNode("statements")

    def parse_type(self) -> ASTNode:
        return ASTNode("type")
