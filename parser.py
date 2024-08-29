import os.path
from typing import Literal

TokenType = Literal["string", "integer", "symbol", "keyword", "float", "char", "identifier"]
Symbol = ("{", "}", "[", "]", "(", ")", "=", ";", ",", ".", "~", "+", "-", "*", "/", "|", "&", "==", "!=", ">=", "<=", ">", "<")
Number = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")


class Token:
    def __init__(self, content: str, type: TokenType, location: tuple[int, int]) -> None:
        self.content = content
        self.type = type
        self.line = location[0]
        self.index = location[1]

    def __str__(self) -> str:
        return f"<{self.type}> {self.content} </{self.type}>"


def read_from_path(path: str) -> list[str]:
    path = os.path.abspath(path)
    file: list[str] = []
    if os.path.isdir(path):
        for f in os.listdir(path):
            if os.path.isfile(f):
                file.append(f)
    elif os.path.isfile(path):
        file.append(path)
    source: list[str] = []
    for i in file:
        if i.endswith(".nj"):
            with open(i, "r") as f:
                source.append("//" + i.split("\\")[-1])
                source += f.readlines()
    return source


def lexer(source: list[str]) -> list[Token]:
    tokens: list[Token] = []
    content = ""
    state = ""
    location = (-1, -1)
    for i, line in enumerate(source):
        for j, char in enumerate(line):
            if state == "commant":
                if char == "`":
                    state = ""
            elif char == '"':
                if state == "string":
                    tokens.append(Token(content, "string", location))
                    content = ""
                    state = ""
                else:
                    state = "string"
                    content = char
                    location = (i, j)
            elif state == "string":
                content += char
            elif char == "#":
                break
            elif char == "`":
                state = "commant"
            elif char in Symbol and char != "-":
                tokens.append(Token(content, "symbol", location))
            elif char in Number:
                pass
            else:
                pass
    return tokens


if __file__ == "__main__":
    path = input("file(s) path: ")
    source = read_from_path(path)
    tokens = lexer(source)
