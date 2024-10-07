from typing import Literal, Optional, Self, Sequence, Union
import os.path

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
    def __init__(self, location: tuple[int, int], content: str) -> None:
        self.location = location
        self.content = content

    def show(self) -> list[str]:
        if self.content in Keyword:
            return ["keyword: " + self.content]
        else:
            return ["identifier: " + self.content]

    def __str__(self) -> str:
        return self.content


class Integer:
    def __init__(self, location: tuple[int, int], content: str) -> None:
        self.location = location
        self.content = int(content)

    def show(self) -> list[str]:
        return [f"integer: {self.content}"]

    def __str__(self) -> str:
        return str(self.content)


class Float:
    def __init__(self, location: tuple[int, int], content: str) -> None:
        self.location = location
        self.a, self.b = content.split(".")

    def show(self) -> list[str]:
        return [f"float: {self.a}.{self.b}"]

    def __str__(self) -> str:
        return f"{self.a}.{self.b}"


class String:
    def __init__(self, location: tuple[int, int], content: str) -> None:
        self.location = location
        self.content = content

    def show(self) -> list[str]:
        return ["string: " + self.content]

    def __str__(self) -> str:
        return self.content


class Char:
    def __init__(self, location: tuple[int, int], content: str) -> None:
        self.location = location
        self.content = content[0]

    def show(self) -> list[str]:
        return ["char: " + self.content]

    def __str__(self) -> str:
        return self.content


class Op:
    def __init__(
        self, location: tuple[int, int], content: Literal["+", "-", "*", "/", "|", "&", "<<", ">>", "==", "!=", ">=", "<=", ">", "<"]
    ) -> None:
        self.location = location
        self.content = content

    def show(self) -> list[str]:
        return ["operator: " + self.content]

    def __str__(self) -> str:
        return self.content


class Term:
    def __init__(
        self,
        location: tuple[int, int],
        content: Union[Integer, Float, Char, String, "Call", "GetVariable", "Expression", Self, Literal["false", "true", "self"]],
        neg: Optional[Literal["-", "!"]] = None,
    ) -> None:
        self.location = location
        self.content = content
        self.neg = neg

    def show(self) -> list[str]:
        s = ["term:"]
        if self.neg is not None:
            s[0] += " neg: " + self.neg
        if isinstance(self.content, str):
            s.extend(indent([f"integer: {self.content}"]))
        else:
            s.extend(indent(self.content.show()))
        return s


class Expression:
    def __init__(self, location: tuple[int, int], content: Sequence[Term | Op]) -> None:
        """content: Stores Op and Term sequences converted to reverse Polish notation"""
        self.location = location
        self.content = content

    def show(self) -> list[str]:
        s = ["expression:"]
        for i in self.content:
            s.extend(indent(i.show()))
        return s


class GetVariable:
    def __init__(
        self, location: tuple[int, int], var: Self | Identifier, index: Optional[Expression] = None, attr: Optional[Identifier] = None
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

    def show(self) -> list[str]:
        s = ["getVar:"]
        s.extend(indent(self.var.show()))
        if self.index is not None:
            s.append("└─index:")
            s.extend(indent(self.index.show()))
        elif self.attr is not None:
            s.append("└─attr:")
            s.extend(indent(self.attr.show()))
        return s


class Call:
    def __init__(self, location: tuple[int, int], var: GetVariable, expression_list: list[Expression] = []) -> None:
        self.location = location
        self.var = var
        self.expression_list = expression_list

    def show(self) -> list[str]:
        s = ["call:"]
        s.extend(indent(self.var.show()))
        s.append("└─arg:")
        for i in self.expression_list:
            s.extend(indent(i.show()))
        return s


class Variable:
    def __init__(
        self, location: tuple[int, int], name: Identifier, kind: Literal["global", "argument", "attriable", "local"], type: Identifier
    ) -> None:
        self.location = location
        self.name = name
        self.kind: Literal["global", "argument", "attriable", "local"] = kind
        self.type = type

    def show(self) -> list[str]:
        s = [f"var: kind:{self.kind} type:{self.type} name:{self.name}"]
        return s


class Var_S:
    def __init__(self, location: tuple[int, int], var_list: list[Variable], expression_list: list[Expression] = []) -> None:
        self.location = location
        self.var_list = var_list
        self.expression_list = expression_list

    def show(self) -> list[str]:
        s = ["var_S:"]
        s.append("└─var_list:")
        for i in self.var_list:
            s.extend(indent(i.show()))
        s.append("└─expression_list:")
        for i in self.expression_list:
            s.extend(indent(i.show()))
        return s


class Do_S:
    def __init__(self, location: tuple[int, int], call: Call) -> None:
        self.location = location
        self.call = call

    def show(self) -> list[str]:
        return ["do_S:"] + indent(self.call.show())


class Let_S:
    def __init__(self, location: tuple[int, int], var: GetVariable, expression: Expression) -> None:
        self.location = location
        self.var = var
        self.expression = expression

    def show(self) -> list[str]:
        s = ["let_S:"]
        s.append("└─var:")
        s.extend(indent(self.var.show()))
        s.append("└─expression:")
        s.extend(indent(self.expression.show()))
        return s


class Return_S:
    def __init__(self, location: tuple[int, int], expression: Optional[Expression] = None) -> None:
        self.location = location
        self.expression = expression

    def show(self) -> list[str]:
        if self.expression is None:
            return ["return_S"]
        else:
            return ["return_S:"] + indent(self.expression.show())


class Break_S:
    def __init__(self, location: tuple[int, int], n: Integer) -> None:
        self.location = location
        self.n = n

    def show(self) -> list[str]:
        return ["break_S"]


class For_S:
    def __init__(
        self,
        location: tuple[int, int],
        for_count_integer: Identifier,
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

    def show(self) -> list[str]:
        s = ["for_S:"]
        s.append("└─range:")
        for i in self.for_range:
            s.extend(indent(i.show()))
        s.append("└─statement:")
        for i in self.statement_list:
            s.extend(indent(i.show()))
        if self.else_:
            s.append("└─else_statements:")
            for i in self.else_statement_list:
                s.extend(indent(i.show()))
        return s


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

    def show(self) -> list[str]:
        s = ["if_S:"]
        s.append("└─if_conditional:")
        s.extend(indent(self.if_conditional.show()))
        s.append("└─if_statement:")
        for i in self.if_statement_list:
            s.extend(indent(i.show()))
        for n in range(self.elif_n):
            s.append("elif:")
            s.append("└─elif_conditional:")
            s.extend(indent(self.elif_conditional_list[n].show()))
            s.append("└─elif_statement:")
            for i in self.elif_statement_list[n]:
                s.extend(indent(i.show()))
        if self.else_:
            s.append("└─else_statement:")
            for i in self.else_statement_list:
                s.extend(indent(i.show()))
        return s


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

    def show(self) -> list[str]:
        s = ["while_S:"]
        s.append("└─conditional:")
        s.extend(indent(self.conditional.show()))
        s.append("└─statement:")
        for i in self.statement_list:
            s.extend(indent(i.show()))
        if self.else_:
            s.append("└─else_statement:")
            for i in self.else_statement_list:
                s.extend(indent(i.show()))
        return s


Statement = Var_S | Do_S | Let_S | Return_S | Break_S | For_S | If_S | While_S


class Subroutine:
    def __init__(
        self,
        location: tuple[int, int],
        name: Identifier,
        kind: Literal["constructor", "method", "function"],
        return_type: Identifier,
        statement_list: list[Statement],
        argument_list: list[Variable] = [],
    ) -> None:
        self.location = location
        self.name = name
        self.kind = kind
        self.return_type = return_type
        self.statement_list = statement_list
        self.argument_list = argument_list

    def show(self) -> list[str]:
        s = [f"subroutine: kind:{self.kind} type:{self.return_type} name:{self.name}"]
        s.append("└─arg_list:")
        for i in self.argument_list:
            s.extend(indent(i.show()))
        s.append("└─statement:")
        for i in self.statement_list:
            s.extend(indent(i.show()))
        return s


class Class:
    def __init__(self, location: tuple[int, int], name: Identifier, var_list: list[Var_S], subroutine_list: list[Subroutine]) -> None:
        self.location = location
        self.name = name
        self.var_list = var_list
        self.subroutine_list = subroutine_list

    def show(self) -> list[str]:
        s = [f"class: name:{self.name}"]
        s.append("└─arg_list:")
        for i in self.var_list:
            s.extend(indent(i.show()))
        s.append("└─subroutine:")
        for i in self.subroutine_list:
            s.extend(indent(i.show()))
        return s


class Root:
    def __init__(self, location: tuple[int, int], file: str, class_list: list[Class]) -> None:
        self.location = location
        self.name = os.path.split(os.path.abspath(self.file))[1].split(".")[0]
        self.file = file
        self.class_list = class_list

    def show(self) -> list[str]:
        s = [f"Root: path:{self.file}"]
        for i in self.class_list:
            s.extend(indent(i.show()))
        return s


def indent(s: list[str]) -> list[str]:
    return ["    " + i for i in s]
