from typing import NoReturn

from lib import Token, Tokens, ParsingError


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        tokens.append(Token("keyword", "EOF"))
        self.tokens = tokens
        self.index = 0
        self.length = len(tokens)
        self.code: list[str] = []
        self.count: dict[str, int] = {"class": 0, "subroutine": 0, "statement": 0, "var": 0, "let": 0, "do": 0, "if": 0, "while": 0, "for": 0, "return": 0, "expression": 0, "expressionList": 0, "term": 0, "variable": 0, "call": 0}
        self.file = ""
        self.now_class = ""
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

    def main(self) -> list[str]:
        self.count["class"] = 0
        self.count["global"] = 0
        while True:
            self.get()
            if self.now == Token("keyword", "class"):
                self.parse_Class()
            elif self.now == Token("keyword", "EOF"):
                break
            else:
                self.error("missing keyword 'class'")
        return self.code

    def parse_Class(self) -> None:
        n = self.count["class"]
        self.count["class"] += 1
        self.code.append(f"start class {n}")
        self.get()
        if self.now.type == "identifier":
            self.code.append(f"class name {self.now.content}")
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
        self.code.append(f"end class {n}")

    def parse_Subroutine(self) -> None:
        n = self.count["subroutine"]
        self.count["subroutine"] += 1
        self.code.append(f"start subroutine {n}")
        _attr = False
        if self.now == Token("keyword", "constructor"):
            _attr = True
        elif self.now != Tokens("keyword", ("function", "method")):
            self.error("the subroutine must start with keyword 'constructor', 'method' or 'function'")
        self.code.append(f"subroutine type {self.now.content}")
        self.get()
        if self.now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float", "void")) or self.now.type == "identifier":
            self.code.append(f"subroutine return {self.now.content}")
        else:
            self.error("missing return type")
        self.get()
        if self.now.type == "identifier":
            self.code.append(f"subroutine name {self.now.content}")
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
                self.code.append(f"argument {arg_type} {self.now.content}")
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
                    self.code.append(f"argument {arg_type} {self.now.content}")
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
        self.code.append(f"end subroutine {n}")

    def parse_Statements(self, _attr: bool = False) -> None:
        n = self.count["statement"]
        self.count["statement"] += 1
        self.code.append(f"start statement {n}")
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
            elif self.now == Token("symbol", "}"):
                break
            else:
                self.error(f"unknown {self.now.type} '{self.now.content}'")
        self.code.append(f"end statement {n}")

    def parse_Var(self, _global: bool = False, _attr: bool = False) -> None:
        n = self.count["var"]
        self.count["var"] += 1
        self.code.append(f"start var {n}")
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
            self.code.append(f"{kind} {var_type} {self.now.content}")
        else:
            self.error(f"variable name must be identifier, not {self.now.type} '{self.now.content}'")
        self.get()
        while self.now == Token("symbol", ","):
            self.get()
            if self.now.type == "identifier":
                self.code.append(f"{kind} {var_type} {self.now.content}")
            else:
                self.error(f"variable name must be identifier, not {self.now.type} '{self.now.content}'")
            self.get()
        if self.now == Token("symbol", ";"):
            self.code.append(f"end var {n}")
            return
        elif self.now == Token("symbol", "="):
            self.code.append(f"var assign_value_to_variable {n}")
            self.parse_ExpressionList()
        else:
            self.error("must be symbol ';' or '='")
        if self.now == Token("symbol", ";"):
            self.code.append(f"end var {n}")
            return
        else:
            self.error("the end must be symbol ';'")
        self.code.append(f"end var {n}")

    def parse_Let(self) -> None:
        n = self.count["let"]
        self.count["let"] += 1
        self.code.append(f"start let {n}")
        self.parse_Variable()
        if self.now != Token("symbol", "="):
            self.error("missing symbol '='")
        self.code.append(f"let assign_value_to_variable {n}")
        self.parse_Expression()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")
        self.code.append(f"end let {n}")

    def parse_Do(self) -> None:
        n = self.count["do"]
        self.count["do"] += 1
        self.code.append(f"start do {n}")
        self.parse_Call()
        self.get()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")
        self.code.append(f"end do {n}")

    def parse_If(self) -> None:
        n = self.count["if"]
        self.count["if"] += 1
        self.code.append(f"start if {n}")
        self.get()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        self.parse_Expression()
        if self.now != Token("symbol", ")"):
            self.error("missing symbol ')'")
        self.code.append(f"if if_jump {n}")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        self.parse_Statements()
        n1 = 0
        while True:
            self.get()
            if self.now != Token("keyword", "elif"):
                break
            self.code.append(f"start elif {n}-{n1}")
            self.get()
            if self.now != Token("symbol", "("):
                self.error("missing symbol '('")
            self.parse_Expression()
            self.code.append(f"if elif_jump {n}-{n1}")
            if self.now != Token("symbol", ")"):
                self.error("missing symbol ')'")
            self.get()
            if self.now != Token("symbol", "{"):
                self.error("missing symbol '{'")
            self.parse_Statements()
            self.code.append(f"end elif {n}-{n1}")
            n1 += 1
        if self.now == Token("keyword", "else"):
            self.code.append(f"start else {n}")
            self.get()
            if self.now != Token("symbol", "{"):
                self.error("missing symbol '{'")
            self.code.append(f"if else_jump {n}")
            self.parse_Statements()
            self.code.append(f"end else {n}")
        else:
            self.index += 1
        self.code.append(f"end if {n}")

    def parse_While(self) -> None:
        n = self.count["while"]
        self.count["while"] += 1
        self.code.append(f"start while {n}")
        self.get()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        self.parse_Expression()
        if self.now != Token("symbol", ")"):
            self.error("missing symbol ')'")
        self.code.append(f"while while_jump {n}")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        self.parse_Statements()
        if self.next() == Token("keyword", "else"):
            self.get()
            self.code.append(f"start while-else {n}")
            self.get()
            if self.now != Token("symbol", "{"):
                self.error("missing symbol '{'")
            self.parse_Statements()
            self.code.append(f"end while-else {n}")
        self.code.append(f"end while {n}")

    def parse_For(self) -> None:
        n = self.count["for"]
        self.count["for"] += 1
        self.code.append(f"start for {n}")
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
        self.code.append(f"for start {for_range[0]}")
        self.code.append(f"for end {for_range[1]}")
        self.code.append(f"for step {for_range[2]}")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        self.parse_Statements()
        if self.next() == Token("keyword", "else"):
            self.get()
            self.code.append(f"start for-else {n}")
            self.get()
            if self.now != Token("symbol", "{"):
                self.error("missing symbol '{'")
            self.parse_Statements()
            self.code.append(f"end for-else {n}")
        self.code.append(f"end for {n}")

    def parse_Return(self) -> None:
        n = self.count["return"]
        self.count["return"] += 1
        self.code.append(f"start return {n}")
        self.get()
        if self.now == Token("symbol", ";"):
            self.code.append(f"end return {n}")
            return
        self.index -= 1
        self.parse_Expression()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")
        self.code.append(f"end return {n}")

    def parse_ExpressionList(self) -> None:
        n = self.count["expressionList"]
        self.count["expressionList"] += 1
        self.code.append(f"start expressionList {n}")
        self.parse_Expression()
        if self.now == Token("symbol", ","):
            while True:
                self.parse_Expression()
                if self.now != Token("symbol", ","):
                    break
        self.code.append(f"end expressionList {n}")

    def parse_Expression(self) -> None:
        n = self.count["expression"]
        self.count["expression"] += 1
        self.code.append(f"start expression {n}")
        self.parse_Term()
        while self.now == Tokens("symbol", ("+", "-", "*", "/", "==", "!=", ">=", "<=", ">", "<", "|", "&")):
            self.code.append(f"expression op {self.now.content}")
            self.parse_Term()
        self.code.append(f"end expression {n}")

    def parse_Term(self) -> None:
        n = self.count["term"]
        self.count["term"] += 1
        self.code.append(f"start term {n}")
        self.get()
        if self.now.type == "string":
            self.code.append("term add string")
            self.get()
        elif self.now.type == "integer":
            self.code.append("term add integer")
            self.get()
        elif self.now.type == "float":
            self.code.append("term add float")
            self.get()
        elif self.now == Tokens("keyword", ("true", "false", "none")):
            if self.now == Token("keyword", "true"):
                self.code.append("term add true")
                self.get()
            elif self.now == Token("keyword", "false"):
                self.code.append("term add false")
                self.get()
            elif self.now == Token("keyword", "none"):
                self.code.append("term add none")
                self.get()
        elif self.now == Tokens("symbol", ("-", "~", "(")):
            if self.now == Token("symbol", "("):
                self.parse_Expression()
                if self.now != Token("symbol", ")"):
                    self.error("missing symbol ')'")
            elif self.now == Token("symbol", "-"):
                self.code.append("term add -")
                self.parse_Expression()
            elif self.now == Token("symbol", "~"):
                self.code.append("term add ~")
                self.parse_Expression()
        elif self.now.type == "identifier" or self.now == Token("keyword", "self"):
            self.parse_Variable(False)
            if self.now == Token("symbol", "("):
                self.parse_ExpressionList()
                if self.now != Token("symbol", ")"):
                    self.error("missing symbol ')'")
                self.code.append("term add call")
            else:
                self.code.append("term add variable")
        self.code.append(f"end term {n}")

    def parse_Variable(self, f: bool = True) -> None:
        n = self.count["variable"]
        self.count["variable"] += 1
        self.code.append(f"start variable {n}")
        if f:
            self.get()
        if self.now.type == "identifier":
            self.code.append(f"variable get {self.now.content}")
        elif self.now == Token("keyword", "self"):
            self.code.append(f"variable get self")
        else:
            self.error("must be identifier")
        self.get()
        while self.now == Tokens("symbol", (".", "[")):
            if self.now == Token("symbol", "."):
                self.get()
                if self.now.type == "identifier":
                    self.code.append(f"variable point {self.now.content}")
                else:
                    self.error("must be identifier")
            elif self.now == Token("symbol", "["):
                self.parse_Expression()
                self.code.append("variable add index")
                if self.now != Token("symbol", "]"):
                    self.error("missing symbol ']'")
            self.get()
        self.code.append(f"end variable {n}")

    def parse_Call(self) -> None:
        n = self.count["call"]
        self.count["call"] += 1
        self.code.append(f"start call {n}")
        self.parse_Variable()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        if self.next() == Token("keyword", "pass"):
            self.code.append("call arg pass")
        else:
            self.parse_ExpressionList()
        if self.now != Token("symbol", ")"):
            self.error("missing symbol ')'")
        self.code.append(f"end call {n}")
