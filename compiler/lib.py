import os.path
from typing import Sequence, Literal
from traceback import format_list, extract_tb

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
    "docs",
    "Token",
    "Tokens",
    "CompileError",
    "CompileErrorGroup",
    "Info",
    "read_source",
    "get_one_path",
]


TokenType = Literal["string", "integer", "symbol", "keyword", "float", "char", "identifier", "file_name"]
Symbol = set("{}[]():;,.!+-*/|&>=<") | {"==", "!=", ">=", "<=", "<<", ">>"}
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
docs = {
    "--debug": "Activates debug mode, providing detailed stack traces and error information when exceptions occur.",
    "--showast": "Displays the Abstract Syntax Tree (AST) generated during the parsing phase.",
    "--compile": "Compiles the program after parsing, producing a .vm file as output.",
    "--help": "Displays help information. If additional arguments follow this flag, detailed descriptions of those specific options are shown. If no arguments are provided, all available options are displayed.",
    "--outpath": "Specifies the output directory for the compiled result. If not provided, the output defaults to the source file's directory.",
    "--errout": "Specifies a file to output error and debug messages. If not provided, these messages are printed to the standard output (stdout).",
}
match_arg = {"-d": "--debug", "-s": "--showast", "-c": "--compile", "-h": "--help", "-o": "--outpath", "-e": "--errout"}


class Token:
    def __init__(self, type: TokenType, content: str, location: tuple[int, int] = (-1, -1)) -> None:
        self.content = content
        self.type = type
        self.line, self.index = location
        self.location = location

    def __str__(self) -> str:
        return f"<{self.type}> {self.content} {self.location}"

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
        self.content = tuple(content)
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
        return f"<{self.type}> " + ", ".join(i for i in self.content)


class CompileError(Exception):
    def __init__(self, text: str, file: str, location: tuple[int, int], kind: str) -> None:
        self.file = file
        self.line, self.index = location
        self.text = text
        self.kind = kind
        self.traceback = ""

    def show(self, source: str) -> tuple[str, int]:
        """
        Formats the error message with detailed context.

        Args:
            source (str): The source code line where the error occurred.

        Returns:
            tuple[str, int]: The formatted error message and its maximum line length for display.
        """
        if source.endswith("\n"):
            source = source[:-1]
        info = [
            f'File "{self.file}", line {self.line}, in {self.index}',
            f"{self.kind} Error: {self.text}",
            source,
            " " * (self.index - 1) + "^",
        ]
        return "\n".join(info), max(len(i) for i in info)


class CompileErrorGroup(Exception):
    def __init__(self, exceptions: Sequence[CompileError]) -> None:
        self.exceptions = exceptions


class Continue(Exception):
    def __init__(self) -> None:
        pass


class Info:
    def __init__(self):
        self.kind: Literal["global", "attribute", "argument", "local", "void", "class", "function", "method", "constructor"] = "void"
        self.type: Type = type_void
        self.code: list[str] = []
        self.name: str = "void"

    def __str__(self) -> str:
        return f"kind: {self.kind}, type: {self.type}, name: {self.name}, code:\n{"\n".join(self.code)}"


class Args:
    def __init__(self) -> None:
        self.debug: bool = False
        self.showast: bool = False
        self.compile: bool = False
        self.outpath: str = ""
        self.errout: str = ""
        self.help: list[str] = []

    def print_help(self) -> None:
        if self.help == ["--help"]:
            for k, v in docs.items():
                print(f"{k:10}", v)
        else:
            for i in self.help:
                if i == "--help" or i == "-h":
                    continue
                elif i in docs:
                    print(f"{i:10}", docs[i])
                elif i in match_arg:
                    print(f"{i:10} Shortcut for {match_arg[i]}.")
                    print(f"{match_arg[i]:10}", docs[match_arg[i]])


def get_path(paths: list[str]) -> list[str]:
    file: list[str] = []
    for path in paths:
        path = os.path.abspath(path)
        if os.path.isdir(path):
            for f in os.listdir(path):
                if os.path.isfile(f):
                    file.append(f)
        elif os.path.isfile(path):
            file.append(path)
    if len(file) == 0:
        raise FileNotFoundError("file not found")
    return file


def read_source(path: str) -> list[str]:
    source = []
    if path.endswith(".nj"):
        with open(path, "r") as f:
            source = f.readlines()
    if len(source) == 0:
        raise FileNotFoundError("NewJack(.nj) file not found")
    return source


def get_one_path(path: str, extension_name: str) -> str:
    if not extension_name.startswith("."):
        extension_name = "." + extension_name
    dir_path, file_name = os.path.split(os.path.abspath(path))
    return os.path.join(dir_path, file_name.split(".")[0] + extension_name)


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
none = Identifier((-1, -1), "None")
