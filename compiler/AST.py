from typing import Literal, Optional, Sequence, Union, Iterable
import os.path


class Identifier:
    def __init__(self, location: tuple[int, int], content: str) -> None:
        self.location = location
        self.content = content

    def show(self) -> list[str]:
        return [str(self)]

    def __str__(self) -> str:
        return self.content


class Integer:
    def __init__(self, location: tuple[int, int], content: str) -> None:
        self.location = location
        self.content = int(content)

    def show(self) -> list[str]:
        return [str(self)]

    def __str__(self) -> str:
        return str(self.content)


class Float:
    def __init__(self, location: tuple[int, int], content: str) -> None:
        self.location = location
        self.a, self.b = content.split(".")

    def show(self) -> list[str]:
        return [str(self)]

    def __str__(self) -> str:
        return f"{self.a}.{self.b}"


class String:
    def __init__(self, location: tuple[int, int], content: str) -> None:
        self.location = location
        self.content = content

    def show(self) -> list[str]:
        return [str(self)]

    def __str__(self) -> str:
        return f'"{self.content}"'


class Char:
    def __init__(self, location: tuple[int, int], content: str) -> None:
        self.location = location
        self.content = content[0]

    def show(self) -> list[str]:
        return [str(self)]

    def __str__(self) -> str:
        return f"'{self.content}'"


class Op:
    def __init__(
        self, location: tuple[int, int], content: Literal["+", "-", "*", "/", "|", "&", "<<", ">>", "==", "!=", ">=", "<=", ">", "<"]
    ) -> None:
        self.location = location
        self.content = content

    def show(self) -> list[str]:
        return [str(self)]

    def __str__(self) -> str:
        return self.content


class Type:
    def __init__(self, location: tuple[int, int], outside: Identifier, inside: Optional["Type"] = None) -> None:
        self.location = location
        self.outside = outside
        self.inside = inside

    def show(self) -> list[str]:
        return [str(self)]

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
        location: tuple[int, int],
        content: Union[Integer, Float, Char, String, "Call", "GetVariable", "Expression", "Term", Literal["false", "true", "self"]],
        neg: Optional[Literal["-", "!"]] = None,
    ) -> None:
        self.location = location
        self.content = content
        self.neg = neg

    def show(self) -> list[str]:
        return [str(self)]

    def __str__(self) -> str:
        if self.neg is None:
            return str(self.content)
        else:
            return f"{self.neg}({self.content})"


class Expression:
    def __init__(self, location: tuple[int, int], content: Sequence[Term | Op]) -> None:
        """content: Stores Op and Term sequences converted to reverse Polish notation"""
        self.location = location
        self.content = content

    def show(self) -> list[str]:
        return [str(self)]

    def __str__(self) -> str:
        return " ".join(str(i) for i in self.content)


class GetVariable:
    def __init__(
        self,
        location: tuple[int, int],
        var: "GetVariable | Identifier",
        index: Optional[Expression] = None,
        attr: Optional[Identifier] = None,
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
        return [str(self)]

    def __str__(self) -> str:
        if self.attr is None and self.index is None:
            return str(self.var)
        elif self.attr is None:
            return f"{self.var}.{self.attr}"
        else:
            return f"{self.var}[{self.index}]"


class Call:
    def __init__(self, location: tuple[int, int], var: GetVariable, expression_list: list[Expression] = []) -> None:
        self.location = location
        self.var = var
        self.expression_list = expression_list

    def show(self) -> list[str]:
        return [str(self)]

    def __str__(self) -> str:
        return f"{self.var}({", ".join(str(i) for i in self.expression_list)})"


class Variable:
    def __init__(
        self, location: tuple[int, int], name: Identifier, kind: Literal["global", "argument", "attriable", "local"], type: Type
    ) -> None:
        self.location = location
        self.name = name
        self.kind: Literal["global", "argument", "attriable", "local"] = kind
        self.type = type

    def show(self) -> list[str]:
        return [str(self)]

    def __str__(self) -> str:
        return f"{self.kind} {self.name}: {self.type}"


class Var_S:
    def __init__(self, location: tuple[int, int], var_list: list[Variable], expression_list: list[Expression] = []) -> None:
        self.location = location
        self.var_list = var_list
        self.expression_list = expression_list

    def show(self) -> list[str]:
        t = ["var_s:"]
        for v, e in zip(self.var_list, self.expression_list):
            t.append(f"    {v} = {e}")
        return t

    def __str__(self) -> str:
        return "\n".join(self.show())


class Do_S:
    def __init__(self, location: tuple[int, int], call: Call) -> None:
        self.location = location
        self.call = call

    def show(self) -> list[str]:
        return ["do " + self.call.show()[0]]

    def __str__(self) -> str:
        return self.show()[0]


class Let_S:
    def __init__(self, location: tuple[int, int], var: GetVariable, expression: Expression) -> None:
        self.location = location
        self.var = var
        self.expression = expression

    def show(self) -> list[str]:
        return ["let_s:", f"    {self.var} = {self.expression}"]

    def __str__(self) -> str:
        return "\n".join(self.show())


class Return_S:
    def __init__(self, location: tuple[int, int], expression: Optional[Expression] = None) -> None:
        self.location = location
        self.expression = expression

    def show(self) -> list[str]:
        return [str(self)]

    def __str__(self) -> str:
        return f"return {self.expression}"


class Break_S:
    def __init__(self, location: tuple[int, int], n: Integer) -> None:
        self.location = location
        self.n = n

    def show(self) -> list[str]:
        return [str(self)]

    def __str__(self) -> str:
        return f"break {self.n}"


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


Statement = Var_S | Do_S | Let_S | Return_S | Break_S | For_S | If_S | While_S


class Subroutine:
    def __init__(
        self,
        location: tuple[int, int],
        name: Identifier,
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

    def show(self) -> list[str]:
        t = [f"{self.kind} {self.name}({", ".join(str(i) for i in self.argument_list)}) -> {self.return_type}"]
        for s in self.statement_list:
            t.extend(ident(s.show()))
        return t

    def __str__(self) -> str:
        return "\n".join(self.show())


class Class:
    def __init__(
        self, location: tuple[int, int], name: Identifier, attr_list: list[tuple[str, Type]], subroutine_list: list[Subroutine]
    ) -> None:
        self.location = location
        self.name = name
        self.attr_list = attr_list
        self.subroutine_list = subroutine_list

    def show(self) -> list[str]:
        t = [f"class({self.name})"]
        t.append("    attr:")
        for a in self.attr_list:
            t.append(f"        {a[0]}: {a[1]}")
        t.append("    subroutine:")
        for s in self.subroutine_list:
            t.extend(ident(ident(s.show())))
        return t

    def __str__(self) -> str:
        return "\n".join(self.show())


class Root:
    def __init__(self, location: tuple[int, int], file: str, class_list: list[Class]) -> None:
        self.location = location
        self.name = os.path.split(os.path.abspath(file))[1].split(".")[0]
        self.file = file
        self.class_list = class_list

    def show(self) -> list[str]:
        t = [f"file: {self.file}"]
        for c in self.class_list:
            t.extend(c.show())
        return t

    def __str__(self) -> str:
        return "\n".join(self.show())


def ident(content: Iterable[str]) -> Iterable[str]:
    return ("    " + i for i in content)
