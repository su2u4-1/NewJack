from typing import Literal, Optional, Self

from lib import Keyword

__all__ = [
    "Identifier",
    "Integer",
    "Float",
    "String",
    "Char",
    "Op",
    "Term",
    "Expression",
    "GetVariable",
    "Call",
    "Variable",
    "Var_S",
    "Do_S",
    "Let_S",
    "Return_S",
    "Break_S",
    "For_S",
    "If_S",
    "While_S",
    "Statement",
    "Subroutine",
    "Class",
    "Root",
]


class Identifier:
    def __init__(self, content: str) -> None:
        self.content = content

    def show(self, indent: int) -> str:
        if self.content in Keyword:
            return "    " * indent + "keyword: " + self.content
        else:
            return "    " * indent + "identifier: " + self.content


class Integer:
    def __init__(self, content: str) -> None:
        self.content = int(content)


class Float:
    def __init__(self, content: str) -> None:
        self.content = float(content)


class String:
    def __init__(self, content: str) -> None:
        self.content = content


class Char:
    def __init__(self, content: str) -> None:
        self.content = content[0]


class Op:
    def __init__(self, content: Literal["+", "-", "*", "/", "|", "&", "<<", ">>", "==", "!=", ">=", "<=", ">", "<"]) -> None:
        self.content = content


class Term:
    def __init__(
        self,
        content: Integer | Float | Char | String | "Call" | "GetVariable" | "Expression" | Self | Literal["false", "true", "none", "self"],
        neg: Optional[Literal["-", "!"]] = None,
    ) -> None:
        self.content = content
        self.neg = neg


class Expression:
    def __init__(self, content: list[Term | Op]) -> None:
        self.content = content  # postfix


class GetVariable:
    def __init__(self, var: Self | Identifier, index: Optional[Expression] = None, attr: Optional[Identifier] = None) -> None:
        self.var = var
        self.index = None
        self.attr = None
        if type(var) == GetVariable:
            if index is not None:
                self.index = index
            elif attr is not None:
                self.attr = attr


class Call:
    def __init__(self, var: GetVariable, expression_list: Optional[list[Expression]] = None) -> None:
        self.var = var
        self.expression_list = expression_list


class Variable:
    def __init__(self, name: Identifier, kind: Literal["global", "argument", "attriable", "local"], type: Identifier) -> None:
        self.name = name
        self.kind = kind
        self.type = type


class Var_S:
    def __init__(self, var_list: list[Variable], expression_list: list[Expression] = []) -> None:
        self.var_list = var_list
        self.expression_list = expression_list


class Do_S:
    def __init__(self, call: Call) -> None:
        self.call = call


class Let_S:
    def __init__(self, var: GetVariable, expression: Expression) -> None:
        self.var = var
        self.expression = expression


class Return_S:
    def __init__(self, expression: Optional[Expression] = None) -> None:
        self.expression = expression


class Break_S:
    def __init__(self) -> None:
        pass


class For_S:
    def __init__(
        self,
        for_range: tuple[Integer, Integer, Integer],
        statement_list: list["Statement"],
        else_: bool = False,
        else_statement_list: Optional[list["Statement"]] = None,
    ) -> None:
        self.for_range = for_range
        self.statement_list = statement_list
        self.else_ = else_
        self.else_statement_list = else_statement_list


class If_S:
    def __init__(
        self,
        if_conditional: Expression,
        if_statement_list: list["Statement"],
        elif_n: int = 0,
        elif_statement_list: list[list["Statement"]] = [],
        elif_conditional_list: list[Expression] = [],
        else_: bool = False,
        else_statement_list: list["Statement"] = [],
    ) -> None:
        self.if_conditional = if_conditional
        self.if_statement_list = if_statement_list
        self.elif_n = elif_n
        self.elif_statement_list = elif_statement_list
        self.elif_conditional_list = elif_conditional_list
        self.else_ = else_
        self.else_statement_list = else_statement_list


class While_S:
    def __init__(
        self, conditional: Expression, statement_list: list["Statement"], else_: bool = False, else_statement_list: list["Statement"] = []
    ) -> None:
        self.conditional = conditional
        self.statement_list = statement_list
        self.else_ = else_
        self.else_statement_list = else_statement_list


Statement = Var_S | Do_S | Let_S | Return_S | Break_S | For_S | If_S | While_S


class Subroutine:
    def __init__(
        self,
        name: Identifier,
        kind: Literal["constructor", "method", "function"],
        return_type: Identifier,
        statement_list: list[Statement],
        argument_list: list[Variable] = [],
    ) -> None:
        self.name = name
        self.kind = kind
        self.return_type = return_type
        self.statement_list = statement_list
        self.argument_list = argument_list


class Class:
    def __init__(self, name: Identifier, var_list: list[Var_S], subroutine_list: list[Subroutine]) -> None:
        self.name = name
        self.var_list = var_list
        self.subroutine_list = subroutine_list


class Root:
    def __init__(self, name: str, class_list: list[Class]) -> None:
        self.name = name
        self.class_list = class_list
