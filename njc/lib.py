from os.path import abspath
from typing import Optional, Union


symbol = set("()[]{},;.+-*/%<>&|=@^!") | set(("==", "!=", "<=", ">=", "&&", "||", "+=", "-=", "*=", "/=", "%=", "**", "<<", ">>"))
digit = set("0123456789")
atoz = set("abcdefghijklmnopqrstuvwxyz")
AtoZ = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
keyword = (
    "arr",
    "as",
    "bool",
    "break",
    "char",
    "class",
    "constant",
    "continue",
    "dict",
    "elif",
    "else",
    "false",
    "float",
    "for",
    "function",
    "global",
    "if",
    "import",
    "in",
    "int",
    "method",
    "NULL",
    "pointer",
    "public",
    "range",
    "return",
    "str",
    "true",
    "tuple",
    "type",
    "var",
    "void",
    "while",
)

source: dict[str, list[str]] = {}


class Token:
    def __init__(self, type: str, constant: str, file: str = "", location: tuple[int, int] = (-1, -1)) -> None:
        self.type = type
        self.constant = constant
        self.file = file
        self.line = location[0] - 1
        self.location = location

    def __str__(self) -> str:
        return f"<{self.type}> {self.constant} {self.location}"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Token):
            return NotImplemented
        return self.type == o.type and self.constant == o.constant

    def __repr__(self) -> str:
        return f"Token('{self.type}', '{self.constant}', '{self.file}', {self.location})"


class Tokens:
    def __init__(self, type: str, constants: tuple[str, ...]) -> None:
        self.type = type
        self.constants = constants

    def __str__(self) -> str:
        return f"<{self.type}> {self.constants}"

    def __eq__(self, o: object) -> bool:
        return self.__contains__(o)

    def __contains__(self, o: object) -> bool:
        if isinstance(o, Tokens):
            return self.type == o.type and self.constants == o.constants
        elif isinstance(o, Token):
            return self.type == o.type and o.constant in self.constants
        else:
            return NotImplemented

    def __repr__(self) -> str:
        return f"Tokens('{self.type}', {self.constants})"


class Args:
    def __init__(self, path: str = "", flags: Optional[list[str]] = None, args: Optional[list[str]] = None) -> None:
        if flags is None:
            flags = []
        if args is None:
            args = []
        self.path = path
        self.flags = flags
        self.args = args

    def __str__(self) -> str:
        return f"Path: {self.path}, Flags: {self.flags}, Args: {self.args}"

    def __repr__(self) -> str:
        return f"Args('{self.path}', {self.flags}, {self.args})"


class ASTNode:
    def __init__(self, type: str, *args: "ASTNode", **kwargs: Union[str, float]) -> None:
        self.type = type
        self.children: tuple[ASTNode, ...] = args
        self.args: dict[str, Union[str, float]] = kwargs

    def __str__(self) -> str:
        return f"<{self.type}> ({', '.join(f'{i} = {self.args[i]}' for i in self.args)}): [{self.children}]"

    def __repr__(self) -> str:
        return (
            f"AST_node('{self.type}'{', '.join(repr(i) for i in self.children)}, {', '.join(f'{i} = {self.args[i]}' for i in self.args)})"
        )


class CompileError(Exception):
    def __init__(self, message: str, file: str, source_code: str, location: tuple[int, int]) -> None:
        super().__init__(message)
        self.file = abspath(file)
        self.source_code = source_code
        self.location = location

    def __str__(self) -> str:
        return f'File "{self.file}", line {self.location[0]}, in {self.location[1]}\n{self.source_code}\n' + " " * self.location[1] + "^"


STDLIB = Tokens("keyword", ("list", "math", "random"))
