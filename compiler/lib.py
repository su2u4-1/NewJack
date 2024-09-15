import os.path
from typing import Literal, Iterable

TokenType = Literal["string", "integer", "symbol", "keyword", "float", "char", "identifier", "file"]
Label = Literal["filename", "class", "subroutine", "var_s", "argument_list", "statements", "let_S", "do_S", "if_S", "while_S", "for_S", "return_S", "break_S", "continue_S", "expression", "term"]
Symbol = ("{", "}", "[", "]", "(", ")", "=", ";", ",", ".", "~", "+", "-", "*", "/", "|", "&", "==", "!=", ">=", "<=", ">", "<", "<<", ">>")
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
    def __init__(self, kind: str, info: dict[str, str]) -> None:
        self.kind = kind
        self.info = info
        self.content: list[Code] = []

    def __str__(self) -> str:
        return str(self.kind) + ", " + str(self.info)


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


def write_to_a_file(path: str, content: Iterable[str], extension_name: str) -> None:
    dir_path, file_name = os.path.split(os.path.abspath(path))
    with open(os.path.join(dir_path, file_name.split(".")[0] + extension_name), "w+") as f:
        f.write("\n".join(content))


def format_vmcode(code: Iterable[str]) -> list[str]:
    ind = 0
    new_code: list[str] = []
    for i in code:
        if i.startswith("end"):
            ind -= 1
        new_code.append("    " * ind + i)
        if i.startswith("start"):
            ind += 1
    return new_code
