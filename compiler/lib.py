import os
from traceback import format_list, extract_tb
from typing import Sequence, Literal

from AST import Type, Identifier

__all__ = [
    "type_class",
    "type_subroutine",
    "type_int",
    "type_argument",
    "type_void",
    "Operator",
    "built_in_type",
    "TokenType",
    "Symbol",
    "Number",
    "atoz",
    "AtoZ",
    "atoZ",
    "Keyword",
    "Precedence",
    # "docs",
    "Token",
    "Tokens",
    "CompileError",
    "CompileErrorGroup",
    "Info",
    "read_from_path",
    "get_one_path",
    "Args",
]

TokenType = Literal["string", "integer", "symbol", "keyword", "float", "char", "identifier", "file"]
Symbol = set("{}[]()=;,.!+-*/|&><:") | {"==", "!=", ">=", "<=", "<<", ">>"}
Number = set("0123456789")
atoz = set("abcdefghijklmnopqrstuvwxyz")
AtoZ = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
atoZ = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
Keyword = {
    "class",
    "var",
    "describe",
    "constructor",
    "function",
    "method",
    "void",
    "pass",
    "let",
    "do",
    "if",
    "if else",
    "else",
    "while",
    "return",
    "for",
    "break",
    "continue",
    "false",
    "true",
    "self",
    "int",
    "bool",
    "char",
    "str",
    "list",
    "float",
}
Precedence = {
    "!": 6,
    "~": 6,
    "*": 5,
    "/": 5,
    "+": 4,
    "-": 4,
    "<<": 3,
    ">>": 3,
    "<": 2,
    "<=": 2,
    ">": 2,
    ">=": 2,
    "==": 2,
    "!=": 2,
    "&": 1,
    "|": 1,
}


class Token:
    def __init__(self, type: TokenType, content: str, location: tuple[int, int] = (-1, -1)) -> None:
        self.content = content
        self.type = type
        self.line, self.index = location
        self.location = location

    def __str__(self) -> str:
        return f"<{self.type}> {self.content} ({self.line}, {self.index})"

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Token):
            return self.type == value.type and self.content == value.content
        elif isinstance(value, Tokens):
            if self.type == value.type:
                for i in value.content:
                    if i == self.content:
                        return True
            return False
        else:
            return NotImplemented


class Tokens:
    def __init__(self, type: TokenType, content: Sequence[str]) -> None:
        self.content = content
        self.type = type

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Token):
            if self.type == value.type:
                for i in self.content:
                    if i == value.content:
                        return True
            return False
        else:
            return NotImplemented

    def __str__(self) -> str:
        return f"<{self.type}> {', '.join(self.content)}"


class CompileError(Exception):
    def __init__(self, text: str, file: str, location: tuple[int, int], kind: str) -> None:
        self.text = text
        self.file = file
        self.line, self.index = location
        self.kind = kind
        self.traceback = ""

    def show(self, source: str) -> tuple[str, int]:
        """格式化錯誤訊息顯示。"""
        info = [
            f'File "{self.file}", line {self.line}, in {self.index}',
            f"{self.kind} Error: {self.text}",
            source.rstrip("\n"),
            " " * (self.index - 1) + "^",
        ]
        return "\n".join(info), max(len(line) for line in info)


class CompileErrorGroup(Exception):
    def __init__(self, exceptions: Sequence[CompileError]) -> None:
        self.exceptions = exceptions


class Info:
    def __init__(self):
        self.kind: Literal["global", "attribute", "argument", "local", "void", "class", "function", "method", "constructor"] = "void"
        self.type: Type = type_void
        self.code: list[str] = []
        self.name: str = "void"


class Args:
    def __init__(self) -> None:
        self.debug = False
        self.showast = False
        self.compile = False
        self.outpath = ""
        self.errout = ""
        self.help_flags: list[str] = []

    def process_flag(self, flag: str) -> None:
        """根據標誌設置參數。"""
        match flag:
            case "-d" | "--debug":
                self.debug = True
            case "-s" | "--showast":
                self.showast = True
            case "-c" | "--compile":
                self.compile = True
            case "-o" | "--outpath":
                self.outpath = True
            case "-e" | "--errout":
                self.errout = True
            case _:
                self.help_flags.append(flag)


def read_from_path(path: str) -> list[str]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path not found: {path}")
    if os.path.isfile(path) and path.endswith(".nj"):
        with open(path, "r") as f:
            return f.readlines()
    raise FileNotFoundError("NewJack(.nj) file not found.")


def get_one_path(path: str, extension: str) -> str:
    """根據路徑替換副檔名。"""
    dir_path, file_name = os.path.split(os.path.abspath(path))
    return os.path.join(dir_path, os.path.splitext(file_name)[0] + extension)


def format_traceback(e: BaseException) -> str:
    return "Traceback (most recent call last):\n" + "".join(format_list(extract_tb(e.__traceback__)))


Operator = Tokens("symbol", ("+", "-", "*", "/", "==", "!=", ">=", "<=", ">", "<", "|", "&"))
built_in_type = Tokens("keyword", ("int", "bool", "char", "str", "list", "float", "void"))


type_class = Type((-1, -1), Identifier((-1, -1), "class"))
type_subroutine = {
    "constructor": Type((-1, -1), Identifier((-1, -1), "constructor")),
    "function": Type((-1, -1), Identifier((-1, -1), "function")),
    "method": Type((-1, -1), Identifier((-1, -1), "method")),
}
type_int = Type((-1, -1), Identifier((-1, -1), "int"))
type_argument = Type((-1, -1), Identifier((-1, -1), "argument"))
type_void = Type((-1, -1), Identifier((-1, -1), "void"))
