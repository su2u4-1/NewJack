import os.path
from typing import Literal, Iterable

from newjack_ast import *

TokenType = Literal["string", "integer", "symbol", "keyword", "float", "char", "identifier", "file"]
Symbol = {"{", "}", "[", "]", "(", ")", "=", ";", ",", ".", "!", "+", "-", "*", "/", "|", "&", "==", "!=", ">=", "<=", ">", "<", "<<", ">>"}
Number = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
atoz = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z")
AtoZ = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
atoZ = set(atoz + AtoZ)
Keyword = {
    "class",
    "var",
    "attr",
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
    "none",
    "self",
    "int",
    "bool",
    "char",
    "str",
    "list",
    "float",
}
Precedence = {
    "!": 8,
    "~": 8,
    "*": 7,
    "/": 7,
    "+": 6,
    "-": 6,
    "<<": 5,
    ">>": 5,
    "<": 4,
    "<=": 4,
    ">": 4,
    ">=": 4,
    "==": 3,
    "!=": 3,
    "&": 2,
    "|": 1,
}


class Token:
    def __init__(self, type: TokenType, content: str, location: tuple[int, int] = (-1, -1)) -> None:
        self.content = content
        self.type = type
        self.line = location[0]
        self.index = location[1]
        self.location = location

    def __str__(self) -> str:
        return f"<{self.type}> {self.content} [{self.line}, {self.index}]"

    def __eq__(self, value: object) -> bool:
        if type(value) == Token:
            return self.type == value.type and self.content == value.content
        elif type(value) == Tokens:
            if self.type == value.type:
                for i in value.content:
                    if i == self.content:
                        return True
            return False
        else:
            return NotImplemented


class Tokens:
    def __init__(self, type: TokenType, content: Iterable[str]) -> None:
        self.content = content
        self.type = type

    def __eq__(self, value: object) -> bool:
        if type(value) == Token:
            if self.type == value.type:
                for i in self.content:
                    if i == value.content:
                        return True
            return False
        else:
            return NotImplemented

    def __str__(self) -> str:
        return f"<{self.type}> " + ", ".join(i for i in self.content)


class ParsingError(Exception):
    def __init__(self, file: str, location: tuple[int, int], text: str) -> None:
        self.file = file
        self.line = location[0]
        self.index = location[1]
        self.text = text


Operator = Tokens("symbol", ("+", "-", "*", "/", "==", "!=", ">=", "<=", ">", "<", "|", "&"))


def read_from_path(path: str) -> list[str]:
    path = os.path.abspath(path)
    file: list[str] = []
    if os.path.isdir(path):
        for f in os.listdir(path):
            if os.path.isfile(f):
                file.append(f)
    elif os.path.isfile(path):
        file.append(path)
    if len(file) == 0:
        raise FileNotFoundError("NewJack(.nj) file not found")
    source: list[str] = []
    for i in file:
        if i.endswith(".nj"):
            with open(i, "r") as f:
                source.append("//" + i)
                source += f.readlines()
    return source


def get_one_path(path: str, extension_name: str) -> str:
    dir_path, file_name = os.path.split(os.path.abspath(path))
    return os.path.join(dir_path, file_name.split(".")[0] + extension_name)
