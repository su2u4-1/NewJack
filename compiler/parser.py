from typing import NoReturn

from lib import Token, Tokens, Code, ParsingError


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0
        self.length = len(tokens)
        self.code: list[Code] = []
        self.var: dict[str, tuple[str, str, int]] = {}
        self.var_i = {"attr": 0, "global": 0, "local": 0, "arg": 0}
        self.other: dict[str, tuple[str, str, int, str] | tuple[str, int]] = {}
        self.other_i = {"function": 0, "constructor": 0, "method": 0, "class": 0}
        self.file = ""
        self.now_class = ""

    def error(self, text: str, location: tuple[int, int] = (-1, -1)) -> NoReturn:
        if location == (-1, -1):
            location = self.now.location
        raise ParsingError(self.file, location, text)

    def get(self) -> None:
        self.index += 1
        if self.index >= self.length:
            exit()
        self.now = self.tokens[self.index - 1]
        if self.now.type == "file":
            self.file = self.now.content
            self.get()

    def peek(self) -> Token:
        return self.tokens[self.index - 1]

    def main(self) -> list[Code]:
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
        self.get()
        if self.now.type == "identifier":
            self.other[self.now.content] = ("class", self.other_i["class"])
            self.other_i["class"] += 1
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
            else:
                break
        if self.now != Token("symbol", "}"):
            self.error("missing symbol '}'")

    def compileSubroutine(self) -> None:
        self.var_i["arg"] = 0
        self.now = self.peek()
        if self.now == Token("keyword", "constructor"):
            # TODO: allocate memory for attribute
            pass
        elif self.now == Token("keyword", "method"):
            # TODO: add self to arguments list
            pass
        elif self.now != Token("keyword", "function"):
            self.error("the subroutine must start with keyword 'constructor', 'method' or 'function'")
        kind = self.now.content
        self.get()
        if self.now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float", "void")) or self.now.type == "identifier":
            return_type = self.now.content
            self.get()
        else:
            self.error("missing return type")
        self.get()
        if self.now.type == "identifier":
            self.other[self.now.content] = (kind, return_type, self.other_i[kind], self.now_class)
            self.other_i[kind] += 1
        else:
            self.error("missing subroutine name")
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
            self.var[arg_name] = ("arg", arg_type, self.var_i["arg"])
            self.var_i["arg"] += 1
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
                self.var[arg_name] = ("arg", arg_type, self.var_i["arg"])
                self.var_i["arg"] += 1
                self.get()
        else:
            self.error("missing argument type")
        if self.now != Token("symbol", ")"):
            self.error("missing symbol ')'")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
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
        self.now = self.peek()
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
        n = 0
        if self.now.type == "identifier":
            self.var[self.now.content] = (kind, type, self.var_i[kind])
            self.var_i[kind] += 1
            n += 1
        else:
            self.error(f"variable name must be identifier, not {self.now.type} '{self.now.content}'")
        self.get()
        while self.now == Token("symbol", ","):
            self.get()
            if self.now.type == "identifier":
                self.var[self.now.content] = (kind, type, self.var_i[kind])
                self.var_i[kind] += 1
                n += 1
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
        pass

    def compileIf(self) -> None:
        pass

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
