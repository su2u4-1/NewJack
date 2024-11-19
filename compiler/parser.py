from typing import NoReturn
from inspect import stack

from lib import Token, Tokens, CompileError, Precedence, Operator, built_in_type
from AST import *


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        tokens.append(Token("keyword", "EOF"))
        self.tokens = tokens
        self.index = 0
        self.length = len(tokens)
        self.file = ""
        self.now = tokens[0]
        self.debug_flag = False

    def error(self, text: str, location: tuple[int, int] = (-1, -1)) -> NoReturn:
        if location == (-1, -1):
            location = self.now.location
        raise CompileError(text, self.file, location, "parser")

    def get(self) -> None:
        self.index += 1
        if self.index > self.length:
            raise Exception("Unexpected end of input")
        self.now = self.tokens[self.index - 1]
        if self.now.type == "file":
            self.file = self.now.content
            self.get()
        if self.debug_flag:
            print(stack()[1].function, self.now)

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
        return Root(self.now.location, name, class_list)

    def parse_Class(self) -> Class:
        location = self.now.location
        self.get()
        if self.now.type == "identifier":
            name = Identifier(self.now.location, self.now.content)
        else:
            self.error("missing class name")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        s_list: list[Subroutine] = []
        attr_list: list[tuple[str, Type]] = []
        # var_list: list[Var_S] = []
        while True:
            self.get()
            if self.now == Token("keyword", "describe"):
                self.get()
                if self.now != Token("symbol", "{"):
                    self.error("must be symbol '{'")
                self.get()
                while self.now != Token("symbol", "}"):
                    if self.now.type != "identifier":
                        self.error(f"must be identifier, not {self.now.type} '{self.now.content}'")
                    attr_name = self.now.content
                    self.get()
                    if self.now != Token("symbol", ":"):
                        self.error(f"must be symbol ':', not {self.now.type} '{self.now.content}'")
                    self.get()
                    if self.now != built_in_type or self.now.type == "identifier":
                        self.error("must be built-in type or identifier")
                    attr_list.append((attr_name, self.parse_Type()))
                    if self.now != Token("symbol", ";"):
                        self.error("missing symbol ';'")
                    self.get()
            elif self.now == Tokens("keyword", ("constructor", "function", "method")):
                s_list.append(self.parse_Subroutine())
            elif self.now == Token("symbol", "}"):
                break
            else:
                self.error("missing symbol '}'")
        return Class(location, name, attr_list, s_list)

    def parse_Subroutine(self) -> Subroutine:
        location = self.now.location
        if self.now != Tokens("keyword", ("constructor", "function", "method")):
            self.error("the subroutine must start with keyword 'constructor', 'method' or 'function'")
        kind = self.now.content
        self.get()
        if self.now == built_in_type or self.now.type == "identifier":
            type = Identifier(self.now.location, self.now.content)
        else:
            self.error("missing return type")
        self.get()
        if self.now.type == "identifier":
            name = Identifier(self.now.location, self.now.content)
        else:
            self.error("missing subroutine name")
        self.get()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        self.get()
        arg_list: list[Variable] = []
        if self.now == Token("keyword", "pass"):
            self.get()
        elif self.now == built_in_type or self.now.type == "identifier":
            arg_type = self.parse_Type()
            if self.now.type == "identifier":
                arg_list.append(Variable(self.now.location, Identifier(self.now.location, self.now.content), "argument", arg_type))
            else:
                self.error("missing argument name")
            self.get()
            while self.now == Token("symbol", ","):
                self.get()
                if self.now == built_in_type or self.now.type == "identifier":
                    arg_type = self.parse_Type()
                else:
                    self.error("the symbol ',' must be followed by a argument type")
                if self.now.type == "identifier":
                    arg_list.append(Variable(self.now.location, Identifier(self.now.location, self.now.content), "argument", arg_type))
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
        return Subroutine(location, name, kind, type, self.parse_Statements(), arg_list)  # type: ignore

    def parse_Statements(self) -> list[Statement]:
        output: list[Statement] = []
        while True:
            self.get()
            if self.now == Token("keyword", "var"):
                output.append(self.parse_Var())
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
            elif self.now == Token("keyword", "pass"):
                self.get()
                if self.now != Token("symbol", ";"):
                    self.error("missing symbol ';'")
            else:
                self.error(f"unknown {self.now.type} '{self.now.content}'")
        return output

    def parse_Type(self) -> Type:
        var_type = Type(self.now.location, Identifier(self.now.location, self.now.content))
        self.get()
        if self.now == Token("symbol", "["):
            var_type.inside = self.parse_Type()
            if self.now != Token("symbol", "]"):
                self.error("[ not closed")
            self.get()
        return var_type

    def parse_Var(self) -> Var_S:
        location = self.now.location
        self.get()
        if self.now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float")) or self.now.type == "identifier":
            var_type = self.parse_Type()
        else:
            self.error("missing variable type")
        var_list: list[Variable] = []
        if self.now.type == "identifier":
            var_list.append(Variable(self.now.location, Identifier(self.now.location, self.now.content), "local", var_type))
        else:
            self.error(f"variable name must be identifier, not {self.now.type} '{self.now.content}'")
        self.get()
        while self.now == Token("symbol", ","):
            self.get()
            if self.now.type == "identifier":
                var_list.append(Variable(self.now.location, Identifier(self.now.location, self.now.content), "local", var_type))
            else:
                self.error(f"variable name must be identifier, not {self.now.type} '{self.now.content}'")
            self.get()
        if self.now == Token("symbol", ";"):
            return Var_S(location, var_list)
        elif self.now == Token("symbol", "="):
            e = self.parse_ExpressionList()
        else:
            self.error("must be symbol ';' or '='")
        if self.now == Token("symbol", ";"):
            return Var_S(location, var_list, e)
        else:
            self.error("the end must be symbol ';'")

    def parse_Let(self) -> Let_S:
        location = self.now.location
        var = self.parse_Variable()
        if self.now != Token("symbol", "="):
            self.error("missing symbol '='")
        e = self.parse_Expression()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")
        return Let_S(location, var, e)

    def parse_Do(self) -> Do_S:
        location = self.now.location
        call = self.parse_Call()
        self.get()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")
        return Do_S(location, call)

    def parse_If(self) -> If_S:
        location = self.now.location
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
            return If_S(location, c0, s0, len(elif_c), elif_s, elif_c, True, self.parse_Statements())
        else:
            return If_S(location, c0, s0, len(elif_c), elif_s, elif_c)

    def parse_While(self) -> While_S:
        location = self.now.location
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
            return While_S(location, c, s0, True, s1)
        else:
            return While_S(location, c, s0)

    def parse_For(self) -> For_S:
        location = self.now.location
        self.get()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        self.get()
        if self.now.type != "identifier":
            self.error("must be identifier")
        for_count_integer = Identifier(self.now.location, self.now.content)
        i_0 = self.parse_Expression()
        if self.now == Token("symbol", ")"):
            i_1 = Expression(self.now.location, [Term(self.now.location, Integer(self.now.location, "0"))])
            i_2 = Expression(self.now.location, [Term(self.now.location, Integer(self.now.location, "1"))])
            for_range = (i_1, i_0, i_2)
        else:
            if self.now != Token("symbol", ";"):
                self.error("missing symbol ';'")
            i_1 = self.parse_Expression()
            if self.now != Token("symbol", ";"):
                self.error("missing symbol ';'")
            i_2 = self.parse_Expression()
            for_range = (i_0, i_1, i_2)
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
            return For_S(location, for_count_integer, for_range, s0, True, s1)
        else:
            return For_S(location, for_count_integer, for_range, s0)

    def parse_Return(self) -> Return_S:
        location = self.now.location
        if self.next() == Token("symbol", ";"):
            self.get()
            return Return_S(self.now.location)
        e = self.parse_Expression()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")
        return Return_S(location, e)

    def parse_Break(self) -> Break_S:
        location = self.now.location
        self.get()
        if self.now.type == "integer":
            n = Integer(self.now.location, self.now.content)
        elif self.now == Token("symbol", ";"):
            n = Integer(self.now.location, "1")
        else:
            self.error("missing symbol ';'")
        return Break_S(location, n)

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
        location = self.next().location
        symbol: list[Op] = []
        output: list[Term | Op] = []
        output.append(self.parse_Term())
        while self.now == Operator:
            while True:
                if len(symbol) == 0 or Precedence[symbol[-1].content] < Precedence[self.now.content]:
                    if self.now != Operator:
                        self.error("missing operator")
                    symbol.append(Op(self.now.location, self.now.content))  # type: ignore
                    break
                output.append(symbol.pop())
            if self.next() == Operator:
                self.error("continuous operator")
            output.append(self.parse_Term())
        while len(symbol) > 0:
            output.append(symbol.pop())
        return Expression(location, output)

    def parse_Term(self) -> Term:
        self.get()
        location = self.now.location
        if self.now.type == "string":
            if len(self.now.content) == 1:
                output = Term(self.now.location, Char(self.now.location, self.now.content))
            else:
                output = Term(self.now.location, String(self.now.location, self.now.content))
            self.get()
        elif self.now.type == "integer":
            output = Term(self.now.location, Integer(self.now.location, self.now.content))
            self.get()
        elif self.now.type == "float":
            output = Term(self.now.location, Float(self.now.location, self.now.content))
            self.get()
        elif self.now == Tokens("keyword", ("true", "false", "self")):
            if self.now == Token("keyword", "true"):
                output = Term(self.now.location, "true")
                self.get()
            elif self.now == Token("keyword", "false"):
                output = Term(self.now.location, "false")
                self.get()
            else:  # self.now == Token("keyword", "self")
                output = Term(self.now.location, "self")
                self.get()
        elif self.now == Tokens("symbol", ("-", "!", "(")):
            if self.now == Token("symbol", "("):
                output = Term(self.now.location, self.parse_Expression())
                if self.now != Token("symbol", ")"):
                    self.error("missing symbol ')'")
            elif self.now == Token("symbol", "-"):
                output = Term(self.now.location, self.parse_Term(), "-")
            else:  # self.now == Token("symbol", "!")
                output = Term(self.now.location, self.parse_Term(), "!")
        elif self.now.type == "identifier" or self.now == Token("keyword", "self"):
            self.debug_flag = True
            var = self.parse_Variable(GetVariable(self.now.location, Identifier(self.now.location, self.now.content)))
            if self.now == Token("symbol", "("):
                if self.next() == Token("keyword", "pass"):
                    self.get()
                    self.get()
                    e = []
                else:
                    e = self.parse_ExpressionList()
                if self.now != Token("symbol", ")"):
                    self.error("missing symbol ')'")
                output = Term(location, Call(self.now.location, var, e))
                self.get()
            else:
                output = Term(location, var)
            self.debug_flag = False
        else:
            self.error(f"unknown Term '{self.now}'")
            output = Term(location, "none")
        return output

    def parse_Variable(self, var: Optional[GetVariable] = None) -> GetVariable:
        if self.now.type == "identifier" or self.now == Token("keyword", "self"):
            self.get()
            var = GetVariable(self.now.location, Identifier(self.now.location, self.now.content))
        elif self.now == Tokens("symbol", (".", "[")) and isinstance(var, GetVariable):
            if self.now == Token("symbol", "."):
                self.get()
                if self.now.type == "identifier":
                    var.attr = Identifier(self.now.location, self.now.content)
                else:
                    self.error("must be identifier")
            elif self.now == Token("symbol", "["):
                var.index = self.parse_Expression()
                if self.now != Token("symbol", "]"):
                    self.error("missing symbol ']'")
        else:
            self.error(f"must be identifier or keyword 'self', not {self.now.type} '{self.now.content}'")
        self.get()
        if self.now == Tokens("symbol", (".", "[")):
            var = self.parse_Variable(var)
        return var

    def parse_Call(self) -> Call:
        location = self.now.location
        var = self.parse_Variable()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        if self.next() == Token("keyword", "pass"):
            self.get()
            self.get()
            e = []
        else:
            e = self.parse_ExpressionList()
        if self.now != Token("symbol", ")"):
            self.error("missing symbol ')'")
        return Call(location, var, e)
