from typing import NoReturn

from lib import Token, Tokens, ParsingError, Precedence, Operator
from newjack_ast import *


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

    def main(self, name: str) -> Root:
        class_list: list[Class] = []
        while True:
            self.get()
            if self.now == Token("keyword", "class"):
                class_list.append(self.parse_Class())
            elif self.now == Token("keyword", "EOF"):
                break
            else:
                self.error("missing keyword 'class'")
        return Root(name, class_list)

    def parse_Class(self) -> Class:
        self.get()
        if self.now.type == "identifier":
            name = Identifier(self.now.content)
        else:
            self.error("missing class name")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        s_list: list[Subroutine] = []
        var_list: list[Var_S] = []
        while True:
            self.get()
            if self.now == Tokens("keyword", ("constructor", "function", "method")):
                s_list.append(self.parse_Subroutine())
            elif self.now == Token("keyword", "var"):
                var_list.append(self.parse_Var(_global=True))
            elif self.now == Token("symbol", "}"):
                break
            else:
                self.error("missing symbol '}'")
        return Class(name, var_list, s_list)

    def parse_Subroutine(self) -> Subroutine:
        _attr = False
        if self.now == Token("keyword", "constructor"):
            _attr = True
        elif self.now != Tokens("keyword", ("function", "method")):
            self.error("the subroutine must start with keyword 'constructor', 'method' or 'function'")
        kind = self.now.content
        self.get()
        if self.now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float", "void")) or self.now.type == "identifier":
            type = Identifier(self.now.content)
        else:
            self.error("missing return type")
        self.get()
        if self.now.type == "identifier":
            name = Identifier(self.now.content)
        else:
            self.error("missing subroutine name")
        self.get()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        self.get()
        arg_list: list[Variable] = []
        if self.now == Token("keyword", "pass"):
            self.get()
        elif self.now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float", "void")) or self.now.type == "identifier":
            arg_type = self.now.content
            self.get()
            if self.now.type == "identifier":
                arg_list.append(Variable(Identifier(self.now.content), "argument", Identifier(arg_type)))
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
                    arg_list.append(Variable(Identifier(self.now.content), "argument", Identifier(arg_type)))
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
        return Subroutine(name, kind, type, self.parse_Statements(_attr), arg_list)

    def parse_Statements(self, _attr: bool = False) -> list[Statement]:
        output: list[Statement] = []
        while True:
            self.get()
            if self.now == Token("keyword", "var"):
                output.append(self.parse_Var())
            elif self.now == Token("keyword", "attr") and _attr:
                output.append(self.parse_Var(False, _attr))
            elif self.now == Token("keyword", "let"):
                output.append(self.parse_Let())
            elif self.now == Token("keyword", "do"):
                output.append(self.parse_Do())
            elif self.now == Token("keyword", "if"):
                output.append(self.parse_If())
            elif self.now == Token("keyword", "while"):
                output.append(self.parse_While())
            elif self.now == Token("keyword", "for"):
                output.append(self.parse_For())
            elif self.now == Token("keyword", "return"):
                output.append(self.parse_Return())
            elif self.now == Token("keyword", "break"):
                output.append(self.parse_Break())
            elif self.now == Token("symbol", "}"):
                break
            else:
                self.error(f"unknown {self.now.type} '{self.now.content}'")
        return output

    def parse_Var(self, _global: bool = False, _attr: bool = False) -> Var_S:
        if _attr:
            kind = "attriable"
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
        var_list: list[Variable] = []
        if self.now.type == "identifier":
            var_list.append(Variable(Identifier(self.now.content), kind, Identifier(var_type)))
        else:
            self.error(f"variable name must be identifier, not {self.now.type} '{self.now.content}'")
        self.get()
        while self.now == Token("symbol", ","):
            self.get()
            if self.now.type == "identifier":
                var_list.append(Variable(Identifier(self.now.content), kind, Identifier(var_type)))
            else:
                self.error(f"variable name must be identifier, not {self.now.type} '{self.now.content}'")
            self.get()
        if self.now == Token("symbol", ";"):
            return Var_S(var_list)
        elif self.now == Token("symbol", "="):
            e = self.parse_ExpressionList()
        else:
            self.error("must be symbol ';' or '='")
        if self.now == Token("symbol", ";"):
            return Var_S(var_list, e)
        else:
            self.error("the end must be symbol ';'")

    def parse_Let(self) -> Let_S:
        var = self.parse_Variable()
        if self.now != Token("symbol", "="):
            self.error("missing symbol '='")
        e = self.parse_Expression()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")
        return Let_S(var, e)

    def parse_Do(self) -> Do_S:
        call = self.parse_Call()
        self.get()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")
        return Do_S(call)

    def parse_If(self) -> If_S:
        self.get()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        c0 = self.parse_Expression()
        if self.now != Token("symbol", ")"):
            self.error("missing symbol ')'")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        s0 = self.parse_Statements()
        elif_c: list[Expression] = []
        elif_s: list[list[Statement]] = []
        while True:
            self.get()
            if self.now != Token("keyword", "elif"):
                break
            self.get()
            if self.now != Token("symbol", "("):
                self.error("missing symbol '('")
            elif_c.append(self.parse_Expression())
            if self.now != Token("symbol", ")"):
                self.error("missing symbol ')'")
            self.get()
            if self.now != Token("symbol", "{"):
                self.error("missing symbol '{'")
            elif_s.append(self.parse_Statements())
        if self.next() == Token("keyword", "else"):
            self.get()
            self.get()
            if self.now != Token("symbol", "{"):
                self.error("missing symbol '{'")
            return If_S(c0, s0, len(elif_c), elif_s, elif_c, True, self.parse_Statements())
        else:
            return If_S(c0, s0, len(elif_c), elif_s, elif_c)

    def parse_While(self) -> While_S:
        self.get()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        c = self.parse_Expression()
        if self.now != Token("symbol", ")"):
            self.error("missing symbol ')'")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        s0 = self.parse_Statements()
        if self.next() == Token("keyword", "else"):
            self.get()
            self.get()
            if self.now != Token("symbol", "{"):
                self.error("missing symbol '{'")
            s1 = self.parse_Statements()
            return While_S(c, s0, True, s1)
        else:
            return While_S(c, s0)

    def parse_For(self) -> For_S:
        self.get()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        self.get()
        if self.now.type != "integer":
            self.error("must be integer")
        i_0 = Integer(self.now.content)
        self.get()
        if self.now == Token("symbol", ")"):
            for_range = (Integer("0"), i_0, Integer("1"))
        else:
            if self.now != Token("symbol", ";"):
                self.error("missing symbol ';'")
            self.get()
            if self.now.type != "integer":
                self.error("must be integer")
            i_1 = Integer(self.now.content)
            self.get()
            if self.now != Token("symbol", ";"):
                self.error("missing symbol ';'")
            self.get()
            if self.now.type != "integer":
                self.error("must be integer")
            for_range = (i_0, i_1, Integer(self.now.content))
            self.get()
            if self.now != Token("symbol", ")"):
                self.error("missing symbol ')'")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        s0 = self.parse_Statements()
        if self.next() == Token("keyword", "else"):
            self.get()
            self.get()
            if self.now != Token("symbol", "{"):
                self.error("missing symbol '{'")
            s1 = self.parse_Statements()
            return For_S(for_range, s0, True, s1)
        else:
            return For_S(for_range, s0)

    def parse_Return(self) -> Return_S:
        if self.next() == Token("symbol", ";"):
            self.get()
            return Return_S()
        e = self.parse_Expression()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")
        return Return_S(e)

    def parse_Break(self) -> Break_S:
        self.get()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")
        return Break_S()

    def parse_ExpressionList(self) -> list[Expression]:
        output: list[Expression] = []
        output.append(self.parse_Expression())
        if self.now == Token("symbol", ","):
            while True:
                output.append(self.parse_Expression())
                if self.now != Token("symbol", ","):
                    break
        return output

    def parse_Expression(self) -> Expression:
        symbol: list[Op] = []
        output: list[Term | Op] = []
        output.append(self.parse_Term())
        while self.now == Operator:
            while True:
                if len(symbol) == 0 or Precedence[symbol[-1].content] < Precedence[self.now.content]:
                    if self.now != Operator:
                        self.error("missing operator")
                    symbol.append(Op(self.now.content))
                    break
                output.append(symbol.pop())
            if self.next() == Operator:
                self.error("continuous operator")
            output.append(self.parse_Term())
        while len(symbol) > 0:
            output.append(symbol.pop())
        return Expression(output)

    def parse_Term(self) -> Term:
        self.get()
        if self.now.type == "string":
            if len(self.now.content) == 1:
                output = Term(Char(self.now.content))
            else:
                output = Term(String(self.now.content))
            self.get()
        elif self.now.type == "integer":
            output = Term(Integer(self.now.content))
            self.get()
        elif self.now.type == "float":
            output = Term(Float(self.now.content))
            self.get()
        elif self.now == Tokens("keyword", ("true", "false", "none")):
            if self.now == Token("keyword", "true"):
                output = Term("true")
                self.get()
            elif self.now == Token("keyword", "false"):
                output = Term("false")
                self.get()
            elif self.now == Token("keyword", "none"):
                output = Term("none")
                self.get()
            elif self.now == Token("keyword", "self"):
                output = Term("self")
                self.get()
        elif self.now == Tokens("symbol", ("-", "!", "(")):
            if self.now == Token("symbol", "("):
                output = Term(self.parse_Expression())
                if self.now != Token("symbol", ")"):
                    self.error("missing symbol ')'")
            elif self.now == Token("symbol", "-"):
                output = Term(self.parse_Term(), "-")
            elif self.now == Token("symbol", "!"):
                output = Term(self.parse_Term(), "!")
        elif self.next().type == "identifier" or self.next() == Token("keyword", "self"):
            var = self.parse_Variable()
            if self.now == Token("symbol", "("):
                output = Term(Call(var, self.parse_ExpressionList()))
                if self.now != Token("symbol", ")"):
                    self.error("missing symbol ')'")
            else:
                output = Term(var)
        else:
            self.error(f"unknown Term '{self.now}'")
        return output

    def parse_Variable(self, var: GetVariable = GetVariable(Identifier("none"))) -> GetVariable:
        self.get()
        if self.now.type == "identifier" or self.now == Token("keyword", "self"):
            var = GetVariable(Identifier(self.now.content))
        else:
            self.get()
            if self.now == Tokens("symbol", (".", "[")):
                if self.now == Token("symbol", "."):
                    self.get()
                    if self.now.type == "identifier":
                        var.attr = Identifier(self.now.content)
                    else:
                        self.error("must be identifier")
                elif self.now == Token("symbol", "["):
                    var.index = self.parse_Expression()
                    if self.now != Token("symbol", "]"):
                        self.error("missing symbol ']'")
        self.get()
        if self.now == Tokens("symbol", (".", "[")):
            return self.parse_Variable(var)
        else:
            return var

    def parse_Call(self) -> Call:
        var = self.parse_Variable()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        if self.next() == Token("keyword", "pass"):
            e = []
        else:
            e = self.parse_ExpressionList()
        if self.now != Token("symbol", ")"):
            self.error("missing symbol ')'")
        return Call(var, e)
