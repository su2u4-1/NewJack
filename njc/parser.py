from typing import NoReturn
from lib import CompileError, Token, AST_node, Tokens, STDLIB
from main import source


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

    def parse(self) -> AST_node:
        nodes: list[AST_node] = []
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
        return AST_node("root", *nodes, file=self.file)

    def parse_import(self) -> AST_node:
        self.get()
        if self.now.type == "identifier":
            if self.now.constant in STDLIB:
                lib_name = self.now.constant
                lib_alias = self.now.constant
            else:
                self.error(f"{self.now.constant} does not exist in stdlib", self.now.location)
        elif self.now.type == "string":
            lib_name = self.now.constant
            self.get()
            if self.now != Token("keyword", "as"):
                self.error(f"Expected 'as' after import statement", self.now.location)
            self.get()
            if self.now.type != "identifier":
                self.error(f"Expected identifier after 'as' in import statement", self.now.location)
            lib_alias = self.now.constant
        else:
            self.error(f"Invalid import statement", self.now.location)
        return AST_node("import", name=lib_name, alias=lib_alias)

    def parse_var(self) -> AST_node:
        return AST_node("var")

    def parse_func(self) -> AST_node:
        return AST_node("func")

    def parse_class(self) -> AST_node:
        return AST_node("class")

    def parse_statements(self) -> AST_node:
        return AST_node("statements")
