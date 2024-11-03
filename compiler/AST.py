from typing import Literal, Optional, Sequence, Union
import os.path

from lib import Token


class Float:
    def __init__(self, location: tuple[int, int], content: str) -> None:
        self.location = location
        self.a, self.b = content.split(".")

    def __str__(self) -> str:
        return f"{self.a}.{self.b}"


class String:
    def __init__(self, location: tuple[int, int], content: str) -> None:
        self.location = location
        self.content = content


class Char:
    def __init__(self, location: tuple[int, int], content: str) -> None:
        self.location = location
        self.content = content[0]


class Op:
    def __init__(
        self, location: tuple[int, int], content: Literal["+", "-", "*", "/", "|", "&", "<<", ">>", "==", "!=", ">=", "<=", ">", "<"]
    ) -> None:
        self.location = location
        self.content = content


class Type:
    def __init__(self, location: tuple[int, int], outside: str, inside: Optional["Type"] = None) -> None:
        self.location = location
        self.outside = outside
        self.inside = inside

    def __repr__(self) -> str:
        if self.inside is None:
            return self.outside
        else:
            return f"{self.outside}[{self.inside}]"


class Term:
    def __init__(
        self,
        location: tuple[int, int],
        content: Union[int, Float, Char, String, "Call", "GetVariable", "Expression", "Term", Literal["false", "true", "self"], Token],
        neg: Optional[Literal["-", "!"]] = None,
    ) -> None:
        self.location = location
        if isinstance(content, Token):
            if content.type == "string":
                self.content = content.content
            elif content.type == "char":
                self.content = Char((-1, -1), content.content)
            elif content.type == "integer":
                self.content = int(content.content)
            elif content.type == "float":
                self.content = Float(content.location, content.content)
        else:
            self.content = content
        self.neg = neg


class Expression:
    def __init__(self, location: tuple[int, int], content: Sequence[Term | Op]) -> None:
        """content: Stores Op and Term sequences converted to reverse Polish notation"""
        self.location = location
        self.content = content


class GetVariable:
    def __init__(
        self,
        location: tuple[int, int],
        var: "GetVariable | str",
        index: Optional[Expression] = None,
        attr: Optional[str] = None,
    ) -> None:
        self.location = location
        self.var = var
        self.index = None
        self.attr = None
        if isinstance(var, GetVariable):
            if index is not None:
                self.index = index
            elif attr is not None:
                self.attr = attr


class Call:
    def __init__(self, location: tuple[int, int], var: GetVariable, expression_list: list[Expression] = []) -> None:
        self.location = location
        self.var = var
        self.expression_list = expression_list


class Variable:
    def __init__(self, location: tuple[int, int], name: str, kind: Literal["global", "argument", "attriable", "local"], type: Type) -> None:
        self.location = location
        self.name = name
        self.kind: Literal["global", "argument", "attriable", "local"] = kind
        self.type = type


class Var_S:
    def __init__(self, location: tuple[int, int], var_list: list[Variable], expression_list: list[Expression] = []) -> None:
        self.location = location
        self.var_list = var_list
        self.expression_list = expression_list


class Do_S:
    def __init__(self, location: tuple[int, int], call: Call) -> None:
        self.location = location
        self.call = call


class Let_S:
    def __init__(self, location: tuple[int, int], var: GetVariable, expression: Expression) -> None:
        self.location = location
        self.var = var
        self.expression = expression


class Return_S:
    def __init__(self, location: tuple[int, int], expression: Optional[Expression] = None) -> None:
        self.location = location
        self.expression = expression


class Break_S:
    def __init__(self, location: tuple[int, int], n: int) -> None:
        self.location = location
        self.n = n


class For_S:
    def __init__(
        self,
        location: tuple[int, int],
        for_count_integer: str,
        for_range: tuple[Expression, Expression, Expression],
        statement_list: list["Statement"],
        else_: bool = False,
        else_statement_list: list["Statement"] = [],
    ) -> None:
        self.location = location
        self.for_count_integer = for_count_integer
        self.for_range = for_range
        self.statement_list = statement_list
        self.else_ = else_
        self.else_statement_list = else_statement_list


class If_S:
    def __init__(
        self,
        location: tuple[int, int],
        if_conditional: Expression,
        if_statement_list: list["Statement"],
        elif_n: int = 0,
        elif_statement_list: list[list["Statement"]] = [],
        elif_conditional_list: list[Expression] = [],
        else_: bool = False,
        else_statement_list: list["Statement"] = [],
    ) -> None:
        self.location = location
        self.if_conditional = if_conditional
        self.if_statement_list = if_statement_list
        self.elif_n = elif_n
        self.elif_statement_list = elif_statement_list
        self.elif_conditional_list = elif_conditional_list
        self.else_ = else_
        self.else_statement_list = else_statement_list


class While_S:
    def __init__(
        self,
        location: tuple[int, int],
        conditional: Expression,
        statement_list: list["Statement"],
        else_: bool = False,
        else_statement_list: list["Statement"] = [],
    ) -> None:
        self.location = location
        self.conditional = conditional
        self.statement_list = statement_list
        self.else_ = else_
        self.else_statement_list = else_statement_list


Statement = Var_S | Do_S | Let_S | Return_S | Break_S | For_S | If_S | While_S


class Subroutine:
    def __init__(
        self,
        location: tuple[int, int],
        name: str,
        kind: Literal["constructor", "method", "function"],
        return_type: Type,
        statement_list: list[Statement],
        argument_list: list[Variable] = [],
    ) -> None:
        self.location = location
        self.name = name
        self.kind = kind
        self.return_type = return_type
        self.statement_list = statement_list
        self.argument_list = argument_list


class Class:
    def __init__(self, location: tuple[int, int], name: str, attr_list: list[tuple[str, Type]], subroutine_list: list[Subroutine]) -> None:
        self.location = location
        self.name = name
        self.attr_list = attr_list
        self.subroutine_list = subroutine_list


class Root:
    def __init__(self, location: tuple[int, int], file: str, class_list: list[Class]) -> None:
        self.location = location
        self.name = os.path.split(os.path.abspath(file))[1].split(".")[0]
        self.file = file
        self.class_list = class_list


type_int = Type((-1, -1), "int")
type_argument = Type((-1, -1), "argument")
