"""
AST (Abstract Syntax Tree) module for the NewJack language.

This module defines classes and structures used to represent the abstract syntax tree.
Each class corresponds to a syntactic construct in the language, such as expressions, statements, and subroutines.
"""

from typing import Literal, Optional, Sequence, Union, Iterable, List, Tuple
import os.path

__all__ = [
    "Identifier",
    "Integer",
    "Float",
    "String",
    "Char",
    "Op",
    "Type",
    "Term",
    "Expression",
    "Variable",
    "Call",
    "DeclareVar",
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
    def __init__(self, content: str, location: Tuple[int, int] = (-1, -1)) -> None:
        self.location = location
        self.content = content

    def show(self) -> List[str]:
        return [str(self)]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return self.content

    def __eq__(self, value: object) -> bool:
        return str(self) == str(value)


class Integer:
    def __init__(self, content: str, location: Tuple[int, int] = (-1, -1)) -> None:
        self.location = location
        self.content = int(content)

    def show(self) -> List[str]:
        return [str(self)]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return str(self.content)

    def __int__(self) -> int:
        return self.content


class Float:
    def __init__(self, content: str, location: Tuple[int, int] = (-1, -1)) -> None:
        self.location = location
        self.a, self.b = content.split(".")

    def show(self) -> List[str]:
        return [str(self)]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.a}.{self.b}"


class String:
    def __init__(self, content: str, location: Tuple[int, int] = (-1, -1)) -> None:
        self.location = location
        self.content = content

    def show(self) -> List[str]:
        return [str(self)]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'"{self.content}"'


class Char:
    def __init__(self, content: str, location: Tuple[int, int] = (-1, -1)) -> None:
        self.location = location
        self.content = content[0]

    def show(self) -> List[str]:
        return [str(self)]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"'{self.content}'"


class Op:
    def __init__(
        self,
        content: Literal["+", "-", "*", "/", "|", "&", "<<", ">>", "==", "!=", ">=", "<=", ">", "<"],
        location: Tuple[int, int] = (-1, -1),
    ) -> None:
        self.location = location
        self.content = content

    def show(self) -> List[str]:
        return [str(self)]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return self.content

    def __eq__(self, value: object) -> bool:
        return str(value) == str(self)


class Type:
    def __init__(self, outside: Identifier, inside: Optional["Type"] = None, location: Tuple[int, int] = (-1, -1)) -> None:
        self.location = location
        self.outside = outside
        self.inside = inside

    def show(self) -> List[str]:
        return [str(self)]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        if self.inside is None:
            return str(self.outside)
        else:
            return f"{self.outside}[{self.inside}]"

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Type):
            if self.outside == value.outside and self.inside == value.inside:
                return True
        return False


class Term:
    def __init__(
        self,
        content: Union[Integer, Float, Char, String, "Call", "Variable", "Expression", "Term", Literal["false", "true", "self"]],
        neg: Optional[Literal["-", "!"]] = None,
        location: Tuple[int, int] = (-1, -1),
    ) -> None:
        self.location = location
        self.content = content
        self.neg = neg

    def show(self) -> List[str]:
        return [str(self)]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        if self.neg is None:
            return str(self.content)
        else:
            return f"{self.neg}({self.content})"


class Expression:
    def __init__(self, content: Sequence[Union[Term, Op]], location: Tuple[int, int] = (-1, -1)) -> None:
        """content: Stores Op and Term sequences converted to Reverse Polish Notation (RPN)"""
        self.location = location
        self.content = content

    def show(self) -> List[str]:
        return [str(self)]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return " ".join(str(i) for i in self.content)


class Variable:
    def __init__(
        self,
        var: "Variable | Identifier",
        index: Optional[Expression] = None,
        attr: Optional[Identifier] = None,
        location: Tuple[int, int] = (-1, -1),
    ) -> None:
        self.location = location
        self.var = var
        self.index = None
        self.attr = None
        if isinstance(var, Variable):
            if index is not None:
                self.index = index
            elif attr is not None:
                self.attr = attr

    def show(self) -> List[str]:
        return [str(self)]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        if self.attr is None and self.index is None:
            return str(self.var)
        elif self.attr is None:
            return f"{self.var}[{self.index}]"
        else:
            return f"{self.var}.{self.attr}"


class Call:
    def __init__(self, var: Variable, expression_list: Optional[List[Expression]] = None, location: Tuple[int, int] = (-1, -1)) -> None:
        self.location = location
        self.var = var
        if expression_list is None:
            self.expression_list = []
        else:
            self.expression_list = expression_list

    def show(self) -> List[str]:
        return [str(self)]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.var}({', '.join(str(i) for i in self.expression_list)})"


class DeclareVar:
    def __init__(
        self,
        name: Identifier,
        kind: Literal["class", "constructor", "function", "method", "global", "argument", "attribute", "local"],
        type: Type,
        location: Tuple[int, int] = (-1, -1),
    ) -> None:
        self.location = location
        self.name = name
        self.kind = kind
        self.type = type

    def show(self) -> List[str]:
        return [str(self)]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.kind} {self.name}: {self.type}"


class Var_S:
    def __init__(
        self, var_list: List[DeclareVar], expression_list: Optional[List[Expression]] = None, location: Tuple[int, int] = (-1, -1)
    ) -> None:
        self.location = location
        self.var_list = var_list
        if expression_list is None:
            self.expression_list = []
        else:
            self.expression_list = expression_list

    def show(self) -> List[str]:
        t = ["var_s:"]
        for v, e in zip(self.var_list, self.expression_list):
            t.append(f"    {v} = {e}")
        return t

    def __str__(self) -> str:
        return "\n".join(self.show())


class Do_S:
    def __init__(self, call: Call, location: Tuple[int, int] = (-1, -1)) -> None:
        self.location = location
        self.call = call

    def show(self) -> List[str]:
        return ["do " + self.call.show()[0]]

    def __str__(self) -> str:
        return self.show()[0]

    def __repr__(self) -> str:
        return str(self)


class Let_S:
    def __init__(self, var: Variable, expression: Expression, location: Tuple[int, int] = (-1, -1)) -> None:
        self.location = location
        self.var = var
        self.expression = expression

    def show(self) -> List[str]:
        return ["let_s:", f"    {self.var} = {self.expression}"]

    def __str__(self) -> str:
        return "\n".join(self.show())


class Return_S:
    def __init__(self, expression: Optional[Expression] = None, location: Tuple[int, int] = (-1, -1)) -> None:
        self.location = location
        self.expression = expression

    def show(self) -> List[str]:
        return [str(self)]

    def __str__(self) -> str:
        if self.expression is None:
            return "return void"
        else:
            return f"return {self.expression}"

    def __repr__(self) -> str:
        return str(self)


class Break_S:
    def __init__(self, n: Integer, location: Tuple[int, int] = (-1, -1)) -> None:
        self.location = location
        self.n = n

    def show(self) -> List[str]:
        return [str(self)]

    def __str__(self) -> str:
        return f"break {self.n}"

    def __repr__(self) -> str:
        return str(self)


class For_S:
    def __init__(
        self,
        for_count_integer: Identifier,
        for_range: Tuple[Expression, Expression, Expression],
        statement_list: List["Statement"],
        else_: bool = False,
        else_statement_list: Optional[List["Statement"]] = None,
        location: Tuple[int, int] = (-1, -1),
    ) -> None:
        self.location = location
        self.for_count_integer = for_count_integer
        self.for_range = for_range
        self.statement_list = statement_list
        self.else_ = else_
        if else_statement_list is None:
            self.else_statement_list = []
        else:
            self.else_statement_list = else_statement_list

    def show(self) -> List[str]:
        t = [f"for({self.for_count_integer}, {self.for_range[0]}; {self.for_range[1]}; {self.for_range[2]})"]
        for s in self.statement_list:
            t.extend(ident(s.show()))
        if self.else_:
            t.append("for-else")
            for s in self.else_statement_list:
                t.extend(ident(s.show()))
        return t

    def __str__(self) -> str:
        return "\n".join(self.show())


class If_S:
    def __init__(
        self,
        if_conditional: Expression,
        if_statement_list: List["Statement"],
        elif_n: int = 0,
        elif_statement_list: Optional[List[List["Statement"]]] = None,
        elif_conditional_list: Optional[List[Expression]] = None,
        else_: bool = False,
        else_statement_list: Optional[List["Statement"]] = None,
        location: Tuple[int, int] = (-1, -1),
    ) -> None:
        self.location = location
        self.if_conditional = if_conditional
        self.if_statement_list = if_statement_list
        self.elif_n = elif_n
        self.else_ = else_
        if elif_statement_list is None:
            self.elif_statement_list = []
        else:
            self.elif_statement_list = elif_statement_list
        if elif_conditional_list is None:
            self.elif_conditional_list = []
        else:
            self.elif_conditional_list = elif_conditional_list
        if else_statement_list is None:
            self.else_statement_list = []
        else:
            self.else_statement_list = else_statement_list

    def show(self) -> List[str]:
        t = [f"if({self.if_conditional})"]
        for s in self.if_statement_list:
            t.extend(ident(s.show()))
        for i in range(self.elif_n):
            t.append(f"elif({self.elif_conditional_list[i]})")
            for s in self.elif_statement_list[i]:
                t.extend(ident(s.show()))
        if self.else_:
            t.append("else")
            for s in self.else_statement_list:
                t.extend(ident(s.show()))
        return t

    def __str__(self) -> str:
        return "\n".join(self.show())


class While_S:
    def __init__(
        self,
        conditional: Expression,
        statement_list: List["Statement"],
        else_: bool = False,
        else_statement_list: Optional[List["Statement"]] = None,
        location: Tuple[int, int] = (-1, -1),
    ) -> None:
        self.location = location
        self.conditional = conditional
        self.statement_list = statement_list
        self.else_ = else_
        if else_statement_list is None:
            self.else_statement_list = []
        else:
            self.else_statement_list = else_statement_list

    def show(self) -> List[str]:
        t = [f"while({self.conditional})"]
        for s in self.statement_list:
            t.extend(ident(s.show()))
        if self.else_:
            t.append("while-else")
            for s in self.else_statement_list:
                t.extend(ident(s.show()))
        return t

    def __str__(self) -> str:
        return "\n".join(self.show())


Statement = Union[Var_S, Do_S, Let_S, Return_S, Break_S, For_S, If_S, While_S]


class Subroutine:
    def __init__(
        self,
        name: Identifier,
        kind: Literal["constructor", "method", "function"],
        return_type: Type,
        statement_list: List[Statement],
        argument_list: Optional[List[DeclareVar]] = None,
        location: Tuple[int, int] = (-1, -1),
    ) -> None:
        self.location = location
        self.name = name
        self.kind = kind
        self.return_type = return_type
        self.statement_list = statement_list
        if argument_list is None:
            self.argument_list = []
        else:
            self.argument_list = argument_list

    def show(self) -> List[str]:
        t = [f"{self.kind} {self.name}({', '.join(str(i) for i in self.argument_list)}) -> {self.return_type}"]
        for s in self.statement_list:
            t.extend(ident(s.show()))
        return t

    def __str__(self) -> str:
        return "\n".join(self.show())


class Class:
    def __init__(
        self,
        name: Identifier,
        attr_list: List[DeclareVar],
        subroutine_list: List[Subroutine],
        file_path: str,
        location: Tuple[int, int] = (-1, -1),
    ) -> None:
        self.location = location
        self.name = name
        self.attr_list = attr_list
        self.subroutine_list = subroutine_list
        self.file_path = file_path
        self.file_name = os.path.split(os.path.abspath(file_path))[1].split(".")[0]

    def show(self) -> List[str]:
        t = [f"class({self.name}), file: {self.file_path}"]
        t.append("    attr:")
        for a in self.attr_list:
            t.append(f"        {a}")
        t.append("    subroutine:")
        for s in self.subroutine_list:
            t.extend(ident(ident(s.show())))
        return t

    def __str__(self) -> str:
        return "\n".join(self.show())


class Root:
    def __init__(self, class_list: List[Class], global_: List[DeclareVar]) -> None:
        self.class_list = class_list
        self.global_ = global_

    def show(self) -> list[str]:
        t = ["class list:"]
        for c in self.class_list:
            t.extend(ident(c.show()))
        return t

    def __str__(self) -> str:
        return "\n".join(self.show())


def ident(content: Iterable[str]) -> Iterable[str]:
    return ("    " + i for i in content)
