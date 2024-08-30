import os.path
from typing import Literal

TokenType = Literal["string", "integer", "symbol", "keyword", "float", "char", "identifier"]
Label = Literal["filename", "class", "subroutine", "var_s", "argument_list", "statements", "let_S", "do_S", "if_S", "while_S", "for_S", "return_S", "break_S", "continue_S", "expression", "term"]
tokentype = ("string", "integer", "symbol", "keyword", "float", "char", "identifier")
Symbol = ("{", "}", "[", "]", "(", ")", "=", ";", ",", ".", "~", "+", "-", "*", "/", "|", "&", "==", "!=", ">=", "<=", ">", "<")
Number = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
atoZ = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
Keyword = ("class", "var", "attr", "constructor", "function", "method", "void", "pass", "let", "do", "if", "if else", "else", "while", "return", "for", "break", "continue", "false", "true", "none", "self", "int", "bool", "char", "str", "list", "float")


class Token:
    def __init__(self, content: str, type: TokenType | Label, location: tuple[int, int]) -> None:
        self.content = content
        self.type = type
        self.line = location[0]
        self.index = location[1]

    def __str__(self) -> str:
        return f"<{self.type}> {self.content} </{self.type}>"


class XmlToken:
    def __init__(self, t: Token, ident: int) -> None:
        self.content = t.content
        self.type = t.type
        self.line = t.line
        self.index = t.index
        self.ident = ident
        if t.type in tokentype:
            self.kind = 0
        else:
            self.kind = 1

    def __str__(self) -> str:
        if self.kind == 0 or self.type == "filename":
            return "    " * self.ident + f"<{self.type}> {self.content} </{self.type}>"
        else:
            return "    " * self.ident + f"<{self.type}>"


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


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0
        self.ident = 0
        self.length = len(tokens)
        self.code: list[XmlToken] = []

    def get(self) -> Token:
        self.index += 1
        if self.index >= self.length:
            exit()
        return self.tokens[self.index - 1]

    def main(self) -> list[XmlToken]:
        while True:
            now = self.get()
            if now.type == "keyword" and now.content == "class":
                self.compileClass()
            elif self.index:
                pass

    def compileClass(self) -> None:
        pass


def lexer(source: list[str]) -> list[Token]:
    tokens: list[Token] = []
    content = ""
    state = ""
    location = (-1, -1)
    for i, line in enumerate(source):
        if line.startswith("//"):
            tokens.append(Token(line[2:], "filename", (-1, -1)))
            continue
        for j, char in enumerate(line):
            if state == "commant":
                if char == "`":
                    state = ""
                continue
            elif state == "string":
                content += char
                if char == '"':
                    tokens.append(Token(content, "string", location))
                    content = ""
                    state = ""
                continue
            elif state == "neg":
                if char in Number:
                    content += char
                    state = "int"
                    continue
                else:
                    tokens.append(Token(content, "symbol", location))
                    content = ""
                    state = ""
            elif state == "identifier":
                if char in atoZ or char == "_" or char in Number:
                    content += char
                    continue
                elif content in Keyword:
                    tokens.append(Token(content, "keyword", location))
                else:
                    tokens.append(Token(content, "identifier", location))
                content = ""
                state = ""
            elif state == "int":
                if char in Number:
                    if content == "-0":
                        tokens.append(Token("-", "symbol", location))
                        tokens.append(Token("0", "integer", (i + 1, j + 1)))
                        content = ""
                        state = ""
                    elif char == "0":
                        tokens.append(Token("0", "integer", (i + 1, j + 1)))
                        content = ""
                        state = ""
                    else:
                        content += char
                        continue
                elif char == ".":
                    content += char
                    state = "float"
                    continue
                else:
                    tokens.append(Token(content, "integer", location))
                    content = ""
                    state = ""
            elif state == "float":
                if char in Number:
                    content += char
                    continue
                else:
                    tokens.append(Token(content, "float", location))
                    content = ""
                    state = ""

            if char == '"':
                state = "string"
                content = char
                location = (i + 1, j + 1)
            elif char == "#":
                break
            elif char == "`":
                state = "commant"
            elif char == "-":
                state = "neg"
                content = char
                location = (i + 1, j + 1)
            elif char in Symbol:
                tokens.append(Token(char, "symbol", (i + 1, j + 1)))
            elif char in Number:
                state = "int"
                content = char
                location = (i + 1, j + 1)
            elif char in atoZ or char == "_":
                state = "identifier"
                content = char
                location = (i + 1, j + 1)
    if state != "":
        print("error:", state)
        print("location:", location)
        exit()
    return tokens


if __name__ == "__main__":
    path = input("file(s) path: ")
    source = read_from_path(path)
    tokens = lexer(source)
    parser = Parser(tokens)
    xmlcode = parser.main()
