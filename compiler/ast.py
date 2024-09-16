from typing import Literal, Optional, Self, TypeVar


class Node:
    pass


class Identifier(Node):
    def __init__(self, content: str) -> None:
        self.content = content


class Integer(Node):
    def __init__(self, content: str) -> None:
        self.content = int(content)


class Float(Node):
    def __init__(self, content: str) -> None:
        self.content = float(content)


class String(Node):
    def __init__(self, content: str) -> None:
        self.content = content


class Char(Node):
    def __init__(self, content: str) -> None:
        self.content = content[0]


class Op(Node):
    def __init__(self, content: str) -> None:
        self.content = content


class Term(Node):
    def __init__(
        self,
        content: Integer | Float | Char | String | "Call" | "Variable" | "Expression" | Self | Literal["false", "true", "none", "self"],
        neg: Optional[Literal["-", "~"]] = None,
    ) -> None:
        self.content = content
        self.neg = neg


class Expression(Node):
    def __init__(self, term_list: list[Term], op_list: list[Op]) -> None:
        self.content: list[Term | Op] = [term_list[0]]
        for i in range(len(op_list)):
            self.content.append(op_list[i])
            self.content.append(term_list[i + 1])


class Variable(Node):
    def __init__(self, var: Self | Identifier, subscript: Optional[Expression] = None, attriable: Optional[Self] = None) -> None:
        self.var = var
        self.subscript = None
        self.attriable = None
        if type(var) == Variable:
            if subscript is not None:
                self.subscript = subscript
            elif attriable is not None:
                self.attriable = attriable


class Call(Node):
    def __init__(self, var: Variable, expression_list: Optional[list[Expression]] = None) -> None:
        self.var = var
        self.expression_list = expression_list


class Var_S(Node):
    def __init__(self, var_list: list[Variable], expression_list: list[Expression]) -> None:
        self.var_list = var_list
        self.expression_list = expression_list


class Do_S(Node):
    def __init__(self, call: Call) -> None:
        self.call = call


class Let_S(Node):
    def __init__(self, var: Variable, expression: Expression) -> None:
        self.var = var
        self.expression = expression


class Return_S(Node):
    def __init__(self, expression: Optional[Expression] = None) -> None:
        self.expression = expression


Statement = TypeVar("Statement", Var_S, Do_S, Let_S, Return_S, "For_S", "If_S", "While_S")


class For_S(Node):
    def __init__(
        self,
        for_range: tuple[Integer, Integer, Integer],
        statement_list: list[Statement],
        else_: bool = False,
        else_statement_list: Optional[list[Statement]] = None,
    ) -> None:
        self.for_range = for_range
        self.statement_list = statement_list
        self.else_ = else_
        self.else_statement_list = else_statement_list


class If_S(Node):
    def __init__(
        self,
        if_conditional: Expression,
        if_statement_list: list[Statement],
        elif_n: int = 0,
        elif_statement_list: list[list[Statement]] = [],
        elif_conditional_list: list[Expression] = [],
        else_: bool = False,
        else_statement_list: list[Statement] = [],
    ) -> None:
        self.if_conditional = if_conditional
        self.if_statement_list = if_statement_list
        self.elif_n = elif_n
        self.elif_statement_list = elif_statement_list
        self.elif_conditional_list = elif_conditional_list
        self.else_ = else_
        self.else_statement_list = else_statement_list


class While_S(Node):
    def __init__(
        self, conditional: Expression, statement_list: list[Statement], else_: bool = False, else_statement_list: list[Statement] = []
    ) -> None:
        self.conditional = conditional
        self.statement_list = statement_list
        self.else_ = else_
        self.else_statement_list = else_statement_list


class Subroutine(Node):
    def __init__(
        self, name: Identifier, kind: Literal["constructor", "method", "function"], return_type: Identifier, statement_list: list[Statement]
    ) -> None:
        self.name = name
        self.kind = kind
        self.return_type = return_type
        self.statement_list = statement_list


class Class(Node):
    def __init__(self, name: Identifier, var_list: list[Var_S], subroutine_list: list[Subroutine]) -> None:
        self.name = name
        self.var_list = var_list
        self.subroutine_list = subroutine_list


class Root(Node):
    def __init__(self, name: str, class_list: list[Class]) -> None:
        self.name = name
        self.class_list = class_list
