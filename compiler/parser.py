from typing import NoReturn, Optional, List, Tuple, Union

from built_in.built_in import built_in_class
from compiler.lib import Token, Tokens, CompileError, built_in_type, Operator, Precedence
from compiler.AST import *


class Parser:
    def __init__(self, tokens: List[Token], file_path: str) -> None:
        tokens.append(Token("keyword", "EOF"))
        self.tokens = tokens
        self.index = 0
        self.length = len(tokens)
        self.file_path = file_path
        self.now = tokens[0]
        self.attr_list: list[DeclareVar] = []
        self.global_: list[DeclareVar] = []

    def error(self, text: str, location: Tuple[int, int] = (-1, -1)) -> NoReturn:
        if location == (-1, -1):
            location = self.now.location
        raise CompileError(text, self.file_path, location, "parser")

    def get(self) -> None:
        self.index += 1
        if self.index > self.length:
            raise Exception("Unexpected end of input")
        self.now = self.tokens[self.index - 1]
        if self.now.type == "file_name":
            self.get()

    def next(self) -> Token:
        if self.index >= self.length:
            raise Exception("Unexpected end of input")
        return self.tokens[self.index]

    def main(self) -> Root:
        """
        Parses the entire input token list and generates a Root node representing the program's AST.

        Returns:
            Root: The root node of the Abstract Syntax Tree.

        Raises:
            CompileError: If the input does not conform to the grammar rules.
        """
        class_list: list[Class] = []
        while True:
            self.get()
            if self.now == Token("keyword", "class"):
                class_list.append(self.parse_Class())
            elif self.now == Token("keyword", "EOF"):
                break
            else:
                self.error("missing keyword 'class' or 'global'")
        return Root(class_list, self.global_)

    def parse_Class(self) -> Class:
        self.attr_list = []
        location = self.now.location
        self.get()
        if self.now.type == "identifier" or self.now == Tokens("keyword", built_in_class):
            name = Identifier(self.now.content, self.now.location)
        else:
            self.error("missing class name")
        self.get()
        if self.now != Token("symbol", "{"):
            self.error("missing symbol '{'")
        s_list: list[Subroutine] = []
        while True:
            self.get()
            if self.now == Tokens("keyword", ("constructor", "function", "method")):
                s_list.append(self.parse_Subroutine())
            elif self.now == Token("symbol", "}"):
                break
            else:
                self.error("missing symbol '}'")
        for i in s_list:
            i.name.content = name.content + "." + i.name.content
        return Class(name, self.attr_list, s_list, self.file_path, location)

    def parse_Subroutine(self) -> Subroutine:
        location = self.now.location
        if self.now != Tokens("keyword", ("constructor", "function", "method")):
            self.error("the subroutine must start with keyword 'constructor', 'method' or 'function'")
        kind = self.now.content
        self.get()
        if self.now == built_in_type or self.now.type == "identifier":
            type = self.parse_Type()
        else:
            self.error("missing return type")
        if self.now.type == "identifier":
            name = Identifier(self.now.content, self.now.location)
        else:
            self.error("missing subroutine name")
        self.get()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        self.get()
        arg_list: list[DeclareVar] = []
        if self.now == Token("keyword", "pass"):
            self.get()
        elif self.now == built_in_type or self.now.type == "identifier":
            arg_type = self.parse_Type()
            if self.now.type == "identifier":
                arg_list.append(DeclareVar(Identifier(self.now.content, self.now.location), "argument", arg_type, self.now.location))
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
                    arg_list.append(DeclareVar(Identifier(self.now.content, self.now.location), "argument", arg_type, self.now.location))
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
        return Subroutine(name, kind, type, self.parse_Statements(), arg_list, location)  # type: ignore

    def parse_Statements(self) -> List[Statement]:
        output: list[Statement] = []
        while True:
            self.get()
            if self.now == Tokens("keyword", ("var", "attr", "global")):
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
        var_type = Type(Identifier(self.now.content, self.now.location), None, self.now.location)
        self.get()
        if self.now == Token("symbol", "["):
            self.get()
            var_type.inside = self.parse_Type()
            if self.now != Token("symbol", "]"):
                self.error("[ not closed")
            self.get()
        return var_type

    def parse_Var(self) -> Var_S:
        location = self.now.location
        if self.now == Token("keyword", "global"):
            kind = "global"
        elif self.now == Token("keyword", "attr"):
            kind = "attribute"
        else:
            kind = "local"
        self.get()
        if (self.now == built_in_type and self.now != Token("keyword", "void")) or self.now.type == "identifier":
            var_type = self.parse_Type()
        else:
            self.error("missing variable type")
        var_list: list[DeclareVar] = []
        if self.now.type == "identifier":
            var_list.append(DeclareVar(Identifier(self.now.content, self.now.location), kind, var_type, self.now.location))
        else:
            self.error(f"variable name must be identifier, not {self.now.type} '{self.now.content}'")
        self.get()
        while self.now == Token("symbol", ","):
            self.get()
            if self.now.type == "identifier":
                var_list.append(DeclareVar(Identifier(self.now.content, self.now.location), kind, var_type, self.now.location))
            else:
                self.error(f"variable name must be identifier, not {self.now.type} '{self.now.content}'")
            self.get()
        if self.now == Token("symbol", ";"):
            var = Var_S(var_list, [], location)
        elif self.now == Token("symbol", "="):
            e = self.parse_ExpressionList()
            if self.now == Token("symbol", ";"):
                var = Var_S(var_list, e, location)
            else:
                self.error("the end must be symbol ';'")
        else:
            self.error("must be symbol ';' or '='")
        if kind == "attribute":
            self.attr_list.extend(var_list)
        elif kind == "global":
            self.global_.extend(var_list)
        return var

    def parse_Let(self) -> Let_S:
        location = self.now.location
        self.get()
        var = self.parse_Variable()
        if self.now != Token("symbol", "="):
            self.error("missing symbol '='")
        e = self.parse_Expression()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")
        return Let_S(var, e, location)

    def parse_Do(self) -> Do_S:
        location = self.now.location
        self.get()
        call = self.parse_Call()
        self.get()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")
        return Do_S(call, location)

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
            if self.next() != Token("keyword", "elif"):
                break
            self.get()
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
            return If_S(c0, s0, len(elif_c), elif_s, elif_c, True, self.parse_Statements(), location)
        else:
            return If_S(c0, s0, len(elif_c), elif_s, elif_c, location=location)

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
            return While_S(c, s0, True, s1, location)
        else:
            return While_S(c, s0, location=location)

    def parse_For(self) -> For_S:
        location = self.now.location
        self.get()
        if self.now != Token("symbol", "("):
            self.error("missing symbol '('")
        self.get()
        if self.now.type != "identifier":
            self.error("must be identifier")
        for_count_integer = Identifier(self.now.content, self.now.location)
        self.get()
        if self.now != Token("symbol", ","):
            self.error("missing symbol ','")
        i_0 = self.parse_Expression()
        if self.now == Token("symbol", ")"):
            i_1 = Expression([Term(Integer("0", self.now.location), location=self.now.location)], self.now.location)
            i_2 = Expression([Term(Integer("1", self.now.location), location=self.now.location)], self.now.location)
            for_range = (i_1, i_0, i_2)
        else:
            if self.now != Token("symbol", ","):
                self.error("missing symbol ','")
            i_1 = self.parse_Expression()
            if self.now != Token("symbol", ","):
                self.error("missing symbol ','")
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
            return For_S(for_count_integer, for_range, s0, True, s1, location)
        else:
            return For_S(for_count_integer, for_range, s0, location=location)

    def parse_Return(self) -> Return_S:
        location = self.now.location
        if self.next() == Token("symbol", ";"):
            self.get()
            return Return_S(None, self.now.location)
        e = self.parse_Expression()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")
        return Return_S(e, location)

    def parse_Break(self) -> Break_S:
        location = self.now.location
        self.get()
        if self.now.type == "integer":
            n = Integer(self.now.content, self.now.location)
        elif self.now == Token("symbol", ";"):
            n = Integer("1", self.now.location)
        else:
            self.error("missing symbol ';'")
        self.get()
        if self.now != Token("symbol", ";"):
            self.error("missing symbol ';'")
        return Break_S(n, location)

    def parse_ExpressionList(self) -> List[Expression]:
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
        output: list[Union[Term, Op]] = []
        output.append(self.parse_Term())
        while self.now == Operator:
            while True:
                if len(symbol) == 0 or Precedence[symbol[-1].content] < Precedence[self.now.content]:
                    if self.now != Operator:
                        self.error("missing operator")
                    symbol.append(Op(self.now.content, self.now.location))  # type: ignore
                    break
                output.append(symbol.pop())
            if self.next() == Operator:
                self.error("continuous operator")
            output.append(self.parse_Term())
        while len(symbol) > 0:
            output.append(symbol.pop())
        return Expression(output, location)

    def parse_Term(self) -> Term:
        self.get()
        location = self.now.location
        if self.now.type == "string":
            if len(self.now.content) == 1:
                output = Term(Char(self.now.content, self.now.location), None, self.now.location)
            else:
                output = Term(String(self.now.content, self.now.location), None, self.now.location)
            self.get()
        elif self.now.type == "integer":
            output = Term(Integer(self.now.content, self.now.location), None, self.now.location)
            self.get()
        elif self.now.type == "float":
            output = Term(Float(self.now.content, self.now.location), None, self.now.location)
            self.get()
        elif self.now == Tokens("keyword", ("true", "false")):
            if self.now == Token("keyword", "true"):
                output = Term("true", None, self.now.location)
                self.get()
            else:
                output = Term("false", None, self.now.location)
                self.get()
        elif self.now == Tokens("symbol", ("-", "!", "(")):
            if self.now == Token("symbol", "("):
                output = Term(self.parse_Expression(), None, self.now.location)
                if self.now != Token("symbol", ")"):
                    self.error("missing symbol ')'")
                self.get()
            elif self.now == Token("symbol", "-"):
                output = Term(self.parse_Term(), "-", self.now.location)
            else:
                output = Term(self.parse_Term(), "!", self.now.location)
        elif self.now.type == "identifier" or self.now == Token("keyword", "self") or self.now == Tokens("keyword", built_in_class):
            var = self.parse_Variable()
            if self.now == Token("symbol", "("):
                if self.next() == Token("keyword", "pass"):
                    self.get()
                    self.get()
                    e = []
                else:
                    e = self.parse_ExpressionList()
                if self.now != Token("symbol", ")"):
                    self.error("missing symbol ')'")
                output = Term(Call(var, e, self.now.location), None, location)
                self.get()
            else:
                output = Term(var, None, location)
        else:
            self.error(f"Unexpected term encountered: {self.now}")
            output = Term(location, "none")
        return output

    def parse_Variable(self, var: Optional[Variable] = None) -> Variable:
        if var is None and (
            self.now.type == "identifier" or self.now == Token("keyword", "self") or self.now == Tokens("keyword", built_in_class)
        ):
            var = Variable(Identifier(self.now.content, self.now.location), location=self.now.location)
        elif self.now == Tokens("symbol", (".", "[")) and isinstance(var, Variable):
            if var.attr is not None or var.index is not None:
                var = Variable(var, location=var.location)
            if self.now == Token("symbol", "."):
                self.get()
                if self.now.type == "identifier":
                    var.attr = Identifier(self.now.content, self.now.location)
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
        return Call(var, e, location)
