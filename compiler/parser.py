from typing import NoReturn

from lib import Token, Tokens, Code, ParsingError


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0
        self.length = len(tokens)
        self.code: list[Code] = []
        # [global: {class, global}, class: {function, attr}, subroutine: {arg, local}]
        self.scope: list[dict[str, tuple[str, str, int]]] = []
        self.count: dict[str, int] = {"class": 0, "global": 0, "function": 0, "attr": 0, "arg": 0, "local": 0}
        self.file = ""
        self.now_class = ""
        self.now = tokens[0]

    def error(self, text: str, location: tuple[int, int] = (-1, -1)) -> NoReturn:
        if location == (-1, -1):
            location = self.now.location
        raise ParsingError(self.file, location, text)

    def get(self) -> None:
        self.index += 1
        if self.index >= self.length:
            self.error("Unexpected end of input")
        self.now = self.tokens[self.index - 1]
        if self.now.type == "file":
            self.file = self.now.content
            self.get()

    def main(self) -> list[Code]:
        self.count["class"] = 0
        self.count["global"] = 0
        while True:
            self.get()
            if self.now == Token("keyword", "class"):
                self.compileClass()
            elif self.index >= self.length:
                break
            else:
                self.error("missing keyword 'class'")
        return self.code

    def compileClass(self) -> None:
        self.count["function"] = 0
        self.count["attr"] = 0
        self.get()
        if self.now.type == "identifier":
            self.scope.append({})
            self.scope[-1][self.now.content] = ("class", "class", self.count["class"])
            self.count["class"] += 1
            self.now_class = self.now.content
        else:
            self.error("missing class name")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        while True:
            self.get()
            if self.now == Tokens("keyword", ("constructor", "function", "method")):
                self.compileSubroutine()
            elif self.now == Tokens("keyword", ("var", "attr")):
                self.compileVar(_global=True)
            elif self.now == Token("keyword", "pass"):
                self.get()
                break
            else:
                break
        if self.now != Token("symbol", "}"):
            self.error("missing symbol '}'")

    def compileSubroutine(self) -> None:
        self.count["arg"] = 0
        self.count["local"] = 0
        if self.now == Token("keyword", "constructor"):
            # TODO: allocate memory for attribute
            pass
        elif self.now == Token("keyword", "method"):
            # TODO: add self to arguments list
            pass
        elif self.now != Token("keyword", "function"):
            self.error("the subroutine must start with keyword 'constructor', 'method' or 'function'")
        self.get()
        if self.now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float", "void")) or self.now.type == "identifier":
            return_type = self.now.content
            self.get()
        else:
            self.error("missing return type")
        self.get()
        if self.now.type == "identifier":
            self.scope[-1][self.now.content] = ("function", return_type, self.count["function"])
            self.count["function"] += 1
        else:
            self.error("missing subroutine name")
        self.scope.append({})
        self.get()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        self.get()
        if self.now == Token("keyword", "pass"):
            self.get()
        elif self.now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float", "void")) or self.now.type == "identifier":
            arg_type = self.now.content
            self.get()
            if self.now.type == "identifier":
                arg_name = self.now.content
            else:
                self.error("missing argument name")
            self.scope[-1][arg_name] = ("arg", arg_type, self.count["arg"])
            self.count["arg"] += 1
            self.get()
            while self.now == Token("symbol", ","):
                if self.now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float", "void")) or self.now.type == "identifier":
                    arg_type = self.now.content
                else:
                    self.error("the symbol ',' must be followed by a argument type")
                self.get()
                if self.now.type == "identifier":
                    arg_name = self.now.content
                else:
                    self.error("missing argument name")
                self.scope[-1][arg_name] = ("arg", arg_type, self.count["arg"])
                self.count["arg"] += 1
                self.get()
        else:
            self.error("missing argument type")
        if self.now != Token("symbol", ")"):
            self.error("missing symbol ')'")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        self.compileStatements()

    def compileStatements(self) -> None:
        while True:
            self.get()
            if self.now == Token("keyword", "var"):
                self.compileVar()
            elif self.now == Token("keyword", "let"):
                self.compileLet()
            elif self.now == Token("keyword", "do"):
                self.compileDo()
            elif self.now == Token("keyword", "if"):
                self.compileIf()
            elif self.now == Token("keyword", "while"):
                self.compileWhile()
            elif self.now == Token("keyword", "for"):
                self.compileFor()
            elif self.now == Token("keyword", "return"):
                self.compileReturn()
            elif self.now == Token("symbol", "}"):
                break
            else:
                self.error(f"unkself.now {self.now.type} '{self.now.content}")

    def compileVar(self, _global: bool = False) -> None:
        if self.now == Token("keyword", "var"):
            if _global:
                kind = "global"
            else:
                kind = "local"
        else:
            kind = "attr"
        self.get()
        if self.now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float")) or self.now.type == "identifier":
            type = self.now.content
            self.get()
        else:
            self.error("missing variable type")
        if self.now.type == "identifier":
            if kind == "global":
                self.scope[0][self.now.content] = (kind, type, self.count[kind])
            else:
                self.scope[-1][self.now.content] = (kind, type, self.count[kind])
            self.count[kind] += 1
        else:
            self.error(f"variable name must be identifier, not {self.now.type} '{self.now.content}'")
        self.get()
        while self.now == Token("symbol", ","):
            self.get()
            if self.now.type == "identifier":
                if kind == "global":
                    self.scope[0][self.now.content] = (kind, type, self.count[kind])
                else:
                    self.scope[-1][self.now.content] = (kind, type, self.count[kind])
                self.count[kind] += 1
            else:
                self.error(f"variable name must be identifier, not {self.now.type} '{self.now.content}'")
            self.get()
        if self.now == Token("symbol", ";"):
            return
        elif self.now == Token("symbol", "="):
            self.compileExpression()
            # TODO: assign value to variable
        else:
            self.error("must be symbol ';' or '='")
        if self.now == Token("symbol", ";"):
            return
        else:
            self.error("the end must be symbol ';'")

    def compileLet(self) -> None:
        self.compileVariable()
        self.get()
        if self.now != Token("symbol", "="):
            self.error("missing symbol '='")
        self.compileExpression()
        # TODO: assign value to variable
        self.get()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")

    def compileDo(self) -> None:
        self.compileCall()
        self.get()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")

    def compileIf(self) -> None:
        self.get()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        self.compileExpression()
        # TODO: jump
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        self.compileStatements()
        while True:
            self.get()
            if self.now == Token("keyword", "elif"):
                self.get()
                if self.now != Token("symbol", "{"):
                    self.error("missing symbol '{'")
                self.compileStatements()
            else:
                break
        if self.now == Token("keyword", "else"):
            self.get()
            if self.now != Token("symbol", "{"):
                self.error("missing symbol '{'")
            self.compileStatements()
        else:
            self.index += 1

    def compileWhile(self) -> None:
        pass

    def compileFor(self) -> None:
        pass

    def compileReturn(self) -> None:
        pass

    def compileExpression(self) -> None:
        pass

    def compileVariable(self) -> None:
        pass

    def compileCall(self) -> None:
        pass
