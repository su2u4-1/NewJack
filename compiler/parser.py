from typing import NoReturn

from lib import Token, Tokens, ParsingError, Code


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        tokens.append(Token("keyword", "EOF"))
        self.tokens = tokens
        self.index = 0
        self.length = len(tokens)
        self.file = ""
        self.now = tokens[0]

    def error(self, text: str, location: tuple[int, int] = (-1, -1)) -> NoReturn:
        if location == (-1, -1):
            location = self.now.location
        raise ParsingError(self.file, location, text)

    def get(self) -> None:
        self.index += 1
        if self.index > self.length:
            raise Exception("Unexpected end of input")
        self.now = self.tokens[self.index - 1]
        if self.now.type == "file":
            self.file = self.now.content
            self.get()

    def next(self) -> Token:
        if self.index >= self.length:
            raise Exception("Unexpected end of input")
        return self.tokens[self.index]

    def main(self) -> None:
        while True:
            self.get()
            if self.now == Token("keyword", "class"):
                self.parse_Class()
            elif self.now == Token("keyword", "EOF"):
                break
            else:
                self.error("missing keyword 'class'")

    def parse_Class(self) -> None:
        self.get()
        if self.now.type == "identifier":
            (self.now.content)  # name
        else:
            self.error("missing class name")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        while True:
            self.get()
            if self.now == Tokens("keyword", ("constructor", "function", "method")):
                self.parse_Subroutine()
            elif self.now == Token("keyword", "var"):
                self.parse_Var(_global=True)
            elif self.now == Token("symbol", "}"):
                break
            else:
                self.error("missing symbol '}'")

    def parse_Subroutine(self) -> None:
        _attr = False
        if self.now == Token("keyword", "constructor"):
            _attr = True
        elif self.now != Tokens("keyword", ("function", "method")):
            self.error("the subroutine must start with keyword 'constructor', 'method' or 'function'")
        (self.now.content)  # kind
        self.get()
        if self.now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float", "void")) or self.now.type == "identifier":
            (self.now.content)  # return type
        else:
            self.error("missing return type")
        self.get()
        if self.now.type == "identifier":
            (self.now.content)  # name
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
                (arg_type, self.now.content)  # (arg type, arg name)
            else:
                self.error("missing argument name")
            self.get()
            while self.now == Token("symbol", ","):
                self.get()
                if self.now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float", "void")) or self.now.type == "identifier":
                    arg_type = self.now.content
                else:
                    self.error("the symbol ',' must be followed by a argument type")
                self.get()
                if self.now.type == "identifier":
                    (arg_type, self.now.content)  # (type, name)
                else:
                    self.error("missing argument name")
            self.get()
        else:
            self.error("missing argument type")
        if self.now != Token("symbol", ")"):
            self.error("missing symbol ')'")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        self.parse_Statements(_attr)

    def parse_Statements(self, _attr: bool = False) -> None:
        while True:
            self.get()
            if self.now == Token("keyword", "var"):
                self.parse_Var()
            elif self.now == Token("keyword", "attr") and _attr:
                self.parse_Var(False, _attr)
            elif self.now == Token("keyword", "let"):
                self.parse_Let()
            elif self.now == Token("keyword", "do"):
                self.parse_Do()
            elif self.now == Token("keyword", "if"):
                self.parse_If()
            elif self.now == Token("keyword", "while"):
                self.parse_While()
            elif self.now == Token("keyword", "for"):
                self.parse_For()
            elif self.now == Token("keyword", "return"):
                self.parse_Return()
            elif self.now == Token("keyword", "break"):
                self.parse_Break()
            elif self.now == Token("symbol", "}"):
                break
            else:
                self.error(f"unknown {self.now.type} '{self.now.content}'")

    def parse_Var(self, _global: bool = False, _attr: bool = False) -> None:
        if _attr:
            kind = "attr"
        elif _global:
            kind = "global"
        else:
            kind = "local"
        self.get()
        if self.now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float")) or self.now.type == "identifier":
            var_type = self.now.content
            self.get()
        else:
            self.error("missing variable type")
        if self.now.type == "identifier":
            (kind, var_type, self.now.content)  # (kind, type, name)
        else:
            self.error(f"variable name must be identifier, not {self.now.type} '{self.now.content}'")
        self.get()
        while self.now == Token("symbol", ","):
            self.get()
            if self.now.type == "identifier":
                (kind, var_type, self.now.content)  # (kind, type, name)
            else:
                self.error(f"variable name must be identifier, not {self.now.type} '{self.now.content}'")
            self.get()
        if self.now == Token("symbol", ";"):
            return
        elif self.now == Token("symbol", "="):
            self.parse_ExpressionList()
        else:
            self.error("must be symbol ';' or '='")
        if self.now == Token("symbol", ";"):
            return
        else:
            self.error("the end must be symbol ';'")

    def parse_Let(self) -> None:
        self.parse_Variable()
        if self.now != Token("symbol", "="):
            self.error("missing symbol '='")
        self.parse_Expression()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")

    def parse_Do(self) -> None:
        self.parse_Call()
        self.get()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")

    def parse_If(self) -> None:
        self.get()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        self.parse_Expression()
        if self.now != Token("symbol", ")"):
            self.error("missing symbol ')'")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        self.parse_Statements()
        n1 = 0
        while True:
            self.get()
            if self.now != Token("keyword", "elif"):
                break
            self.get()
            if self.now != Token("symbol", "("):
                self.error("missing symbol '('")
            self.parse_Expression()
            if self.now != Token("symbol", ")"):
                self.error("missing symbol ')'")
            self.get()
            if self.now != Token("symbol", "{"):
                self.error("missing symbol '{'")
            self.parse_Statements()
            n1 += 1
        if self.next() == Token("keyword", "else"):
            self.get()
            self.get()
            if self.now != Token("symbol", "{"):
                self.error("missing symbol '{'")
            self.parse_Statements()

    def parse_While(self) -> None:
        self.get()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        self.parse_Expression()
        if self.now != Token("symbol", ")"):
            self.error("missing symbol ')'")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        self.parse_Statements()
        if self.next() == Token("keyword", "else"):
            self.get()
            self.get()
            if self.now != Token("symbol", "{"):
                self.error("missing symbol '{'")
            self.parse_Statements()

    def parse_For(self) -> None:
        self.get()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        self.get()
        if self.now.type != "integer":
            self.error("must be integer")
        i_0 = self.now.content
        self.get()
        if self.now == Token("symbol", ")"):
            for_range = (0, i_0, 1)
        else:
            if self.now != Token("symbol", ";"):
                self.error("missing symbol ';'")
            self.get()
            if self.now.type != "integer":
                self.error("must be integer")
            i_1 = self.now.content
            self.get()
            if self.now != Token("symbol", ";"):
                self.error("missing symbol ';'")
            self.get()
            if self.now.type != "integer":
                self.error("must be integer")
            for_range = (i_0, i_1, self.now.content)
            self.get()
            if self.now != Token("symbol", ")"):
                self.error("missing symbol ')'")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        self.parse_Statements()
        if self.next() == Token("keyword", "else"):
            self.get()
            self.get()
            if self.now != Token("symbol", "{"):
                self.error("missing symbol '{'")
            self.parse_Statements()

    def parse_Return(self) -> None:
        if self.next() == Token("symbol", ";"):
            self.get()
            return
        self.parse_Expression()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")

    def parse_Break(self) -> None:
        self.get()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")

    def parse_ExpressionList(self) -> None:
        self.parse_Expression()
        if self.now == Token("symbol", ","):
            while True:
                self.parse_Expression()
                if self.now != Token("symbol", ","):
                    break

    def parse_Expression(self) -> None:
        self.parse_Term()
        if self.now == Tokens("symbol", ("+", "-", "*", "/", "==", "!=", ">=", "<=", ">", "<", "|", "&")):
            self.parse_Expression()

    def parse_Term(self) -> None:
        self.get()
        if self.now.type == "string":
            self.get()
        elif self.now.type == "integer":
            self.get()
        elif self.now.type == "float":
            self.get()
        elif self.now == Tokens("keyword", ("true", "false", "none")):
            if self.now == Token("keyword", "true"):
                self.get()
            elif self.now == Token("keyword", "false"):
                self.get()
            elif self.now == Token("keyword", "none"):
                self.get()
        elif self.now == Tokens("symbol", ("-", "~", "(")):
            if self.now == Token("symbol", "("):
                self.parse_Expression()
                if self.now != Token("symbol", ")"):
                    self.error("missing symbol ')'")
            elif self.now == Token("symbol", "-"):
                self.parse_Expression()
            elif self.now == Token("symbol", "~"):
                self.parse_Expression()
        elif self.now.type == "identifier" or self.now == Token("keyword", "self"):
            self.parse_Variable(False)
            if self.now == Token("symbol", "("):
                self.parse_ExpressionList()
                if self.now != Token("symbol", ")"):
                    self.error("missing symbol ')'")

    def parse_Variable(self, f: bool = True) -> None:
        if f:
            self.get()
        if self.now.type == "identifier":
            var = self.now.content
        elif self.now == Token("keyword", "self"):
            var = "self"
        else:
            self.error("must be identifier")
        self.get()
        while self.now == Tokens("symbol", (".", "[")):
            if self.now == Token("symbol", "."):
                self.get()
                if self.now.type == "identifier":
                    func = self.now.content
                else:
                    self.error("must be identifier")
            elif self.now == Token("symbol", "["):
                self.parse_Expression()
                if self.now != Token("symbol", "]"):
                    self.error("missing symbol ']'")
            self.get()

    def parse_Call(self) -> None:
        self.parse_Variable()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        if self.next() != Token("keyword", "pass"):
            self.parse_ExpressionList()
        if self.now != Token("symbol", ")"):
            self.error("missing symbol ')'")
