import os.path
from typing import Literal, Iterable

TokenType = Literal["string", "integer", "symbol", "keyword", "float", "char", "identifier", "file"]
Label = Literal["filename", "class", "subroutine", "var_s", "argument_list", "statements", "let_S", "do_S", "if_S", "while_S", "for_S", "return_S", "break_S", "continue_S", "expression", "term"]
Symbol = ("{", "}", "[", "]", "(", ")", "=", ";", ",", ".", "~", "+", "-", "*", "/", "|", "&", "==", "!=", ">=", "<=", ">", "<")
Number = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
atoZ = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
Keyword = ("class", "var", "attr", "constructor", "function", "method", "void", "pass", "let", "do", "if", "if else", "else", "while", "return", "for", "break", "continue", "false", "true", "none", "self", "int", "bool", "char", "str", "list", "float")


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


class Code:
    def __init__(self, command: str, arg_1: str = "", arg_2: str = "") -> None:
        self.command = command
        self.arg1 = arg_1
        self.arg2 = arg_2

    def __str__(self) -> str:
        if self.arg1 == "":
            return self.command
        elif self.arg2 == "":
            return self.command + " " + self.arg1
        else:
            return self.command + " " + self.arg1 + " " + self.arg2


class ParsingError(Exception):
    def __init__(self, file: str, location: tuple[int, int], text: str) -> None:
        self.file = file
        self.line = location[0]
        self.index = location[1]
        self.text = text


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
