import os.path
from typing import Sequence, Literal

from constant import TokenType, type_void
from AST import Type


class Token:
    def __init__(self, type: TokenType, content: str, location: tuple[int, int] = (-1, -1)) -> None:
        self.content = content
        self.type = type
        self.line = location[0]
        self.index = location[1]
        self.location = location

    def __str__(self) -> str:
        return f"<{self.type}> {self.content} ({self.line}, {self.index})"

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
    def __init__(self, type: TokenType, content: Sequence[str]) -> None:
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


class CompileError(Exception):
    def __init__(self, text: str, file: str, location: tuple[int, int], kind: str) -> None:
        self.file = file
        self.line = location[0]
        self.index = location[1]
        self.text = text
        self.kind = kind
        self.traceback = ""

    def show(self, source: str) -> tuple[str, int]:
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


class Info:
    def __init__(self, kind: Literal["global", "attribute", "argument", "local", "void"] = "void", type: Type = type_void):
        self.kind = kind
        self.type = type
        self.code: list[str] = []
