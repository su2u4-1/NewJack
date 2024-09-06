import os.path
from typing import Literal, Iterable, NoReturn

TokenType = Literal["string", "integer", "symbol", "keyword", "float", "char", "identifier", "file"]
Label = Literal["filename", "class", "subroutine", "var_s", "argument_list", "statements", "let_S", "do_S", "if_S", "while_S", "for_S", "return_S", "break_S", "continue_S", "expression", "term"]
tokentype = ("string", "integer", "symbol", "keyword", "float", "char", "identifier")
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
                source.append("//" + i)
                source += f.readlines()
    return source


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0
        self.length = len(tokens)
        self.code: list[Code] = []
        # self.error: list[tuple[str, tuple[int, int]]] = []
        self.var: dict[str, tuple[str, str, int]] = {}
        self.var_i = {"attr": 0, "global": 0, "local": 0, "arg": 0}
        self.other: dict[str, tuple[str, str, int, str] | tuple[str, int]] = {}
        self.other_i = {"function": 0, "constructor": 0, "method": 0, "class": 0}
        self.file = ""
        self.now_class = ""

    def error(self, text: str, location: tuple[int, int]) -> NoReturn:
        print(self.file, location)
        print(text)
        exit()

    def get(self) -> Token:
        self.index += 1
        if self.index >= self.length:
            exit()
        t = self.tokens[self.index - 1]
        if t.type == "file":
            self.file = t.content
        return t

    def peek(self) -> Token:
        return self.tokens[self.index - 1]

    def main(self) -> list[Code]:
        while True:
            now = self.get()
            if now == Token("keyword", "class"):
                self.compileClass()
            elif self.index >= self.length:
                break
            else:
                self.error("missing keyword 'class'", now.location)
        return self.code

    def compileClass(self) -> None:
        now = self.get()
        if now.type == "identifier":
            self.other[now.content] = ("class", self.other_i["class"])
            self.other_i["class"] += 1
            self.now_class = now.content
        else:
            self.error("missing class name", now.location)
        now = self.get()
        if now != Token("symbol", "{"):
            self.error("missing symbol '{'", now.location)
        while True:
            now = self.get()
            if now == Tokens("keyword", ("constructor", "function", "method")):
                self.compileSubroutine()
            elif now == Tokens("keyword", ("var", "attr")):
                self.compileVar(_global=True)
            else:
                break
        if now != Token("symbol", "}"):
            self.error("missing symbol '}'", now.location)

    def compileSubroutine(self) -> None:
        self.var_i["arg"] = 0
        now = self.peek()
        if now == Token("keyword", "constructor"):
            # TODO: allocate memory for attribute
            pass
        elif now == Token("keyword", "method"):
            # TODO: add self to arguments list
            pass
        elif now != Token("keyword", "function"):
            self.error("the subroutine must start with keyword 'constructor', 'method' or 'function'", now.location)
        kind = now.content
        now = self.get()
        if now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float", "void")) or now.type == "identifier":
            return_type = now.content
            now = self.get()
        else:
            self.error("missing return type", now.location)
        now = self.get()
        if now.type == "identifier":
            self.other[now.content] = (kind, return_type, self.other_i[kind], self.now_class)
            self.other_i[kind] += 1
        else:
            self.error("missing subroutine name", now.location)
        now = self.get()
        if now != Token("symbol", "("):
            self.error("missing symbol '('", now.location)
        now = self.get()
        if now == Token("keyword", "pass"):
            now = self.get()
        elif now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float", "void")) or now.type == "identifier":
            arg_type = now.content
            now = self.get()
            if now.type == "identifier":
                arg_name = now.content
            else:
                self.error("missing argument name", now.location)
            self.var[arg_name] = ("arg", arg_type, self.var_i["arg"])
            self.var_i["arg"] += 1
            now = self.get()
            while now == Token("symbol", ","):
                if now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float", "void")) or now.type == "identifier":
                    arg_type = now.content
                else:
                    self.error("the symbol ',' must be followed by a argument type", now.location)
                now = self.get()
                if now.type == "identifier":
                    arg_name = now.content
                else:
                    self.error("missing argument name", now.location)
                self.var[arg_name] = ("arg", arg_type, self.var_i["arg"])
                self.var_i["arg"] += 1
                now = self.get()
        else:
            self.error("missing argument type", now.location)
        if now != Token("symbol", ")"):
            self.error("missing symbol ')'", now.location)
        if self.get() != Token("symbol", "{"):
            self.error("missing symbol '{'", now.location)
        while True:
            now = self.get()
            if now == Token("keyword", "var"):
                self.compileVar()
            elif now == Token("keyword", "let"):
                self.compileLet()
            elif now == Token("keyword", "do"):
                self.compileDo()
            elif now == Token("keyword", "if"):
                self.compileIf()
            elif now == Token("keyword", "while"):
                self.compileWhile()
            elif now == Token("keyword", "for"):
                self.compileFor()
            elif now == Token("keyword", "return"):
                self.compileReturn()
            elif now == Token("symbol", "}"):
                break
            else:
                self.error(f"unknow {now.type} '{now.content}", now.location)

    def compileVar(self, _global: bool = False) -> None:
        now = self.peek()
        if now == Token("keyword", "var"):
            if _global:
                kind = "global"
            else:
                kind = "local"
        else:
            kind = "attr"
        now = self.get()
        if now == Tokens("keyword", ("int", "bool", "char", "str", "list", "float")) or now.type == "identifier":
            type = now.content
            now = self.get()
        else:
            self.error("missing variable type", now.location)
        n = 0
        if now.type == "identifier":
            self.var[now.content] = (kind, type, self.var_i[kind])
            self.var_i[kind] += 1
            n += 1
        else:
            self.error(f"variable name must be identifier, not {now.type} '{now.content}'", now.location)
        now = self.get()
        while now == Token("symbol", ","):
            now = self.get()
            if now.type == "identifier":
                self.var[now.content] = (kind, type, self.var_i[kind])
                self.var_i[kind] += 1
                n += 1
            else:
                self.error(f"variable name must be identifier, not {now.type} '{now.content}'", now.location)
            now = self.get()
        if now == Token("symbol", ";"):
            return
        elif now == Token("symbol", "="):
            self.compileExpression()
            # TODO: assign value to variable
        else:
            self.error("must be symbol ';' or '='", now.location)
        if now == Token("symbol", ";"):
            return
        else:
            self.error("the end must be symbol ';'", now.location)

    def compileLet(self) -> None:
        self.compileVariable()
        now = self.get()
        if now != Token("symbol", "="):
            self.error("missing symbol '='", now.location)
        self.compileExpression()
        # TODO: assign value to variable
        now = self.get()
        if now != Token("symbol", ";"):
            self.error("missing symbol ';'", now.location)

    def compileDo(self) -> None:
        pass

    def compileIf(self) -> None:
        pass

    def compileWhile(self) -> None:
        pass

    def compileFor(self) -> None:
        pass

    def compileReturn(self) -> None:
        pass

    def compileExpression(self) -> None:
        pass

    def compileVariable(self) -> None:
        pass


def lexer(source: list[str]) -> list[Token]:
    tokens: list[Token] = []
    content = ""
    state = ""
    location = (-1, -1)
    for i, line in enumerate(source):
        if line.startswith("//"):
            tokens.append(Token("file", line[2:], (-1, -1)))
            continue
        for j, char in enumerate(line):
            if state == "commant":
                if char == "`":
                    state = ""
                continue
            elif state == "string":
                content += char
                if char == '"':
                    tokens.append(Token("string", content, location))
                    content = ""
                    state = ""
                continue
            elif state == "neg":
                if char in Number:
                    content += char
                    state = "int"
                    continue
                else:
                    tokens.append(Token("symbol", content, location))
                    content = ""
                    state = ""
            elif state == "identifier":
                if char in atoZ or char == "_" or char in Number:
                    content += char
                    continue
                elif content in Keyword:
                    tokens.append(Token("keyword", content, location))
                else:
                    tokens.append(Token("identifier", content, location))
                content = ""
                state = ""
            elif state == "int":
                if char in Number:
                    if content == "-0":
                        tokens.append(Token("symbol", "-", location))
                        tokens.append(Token("integer", "0", (i + 1, j + 1)))
                        content = ""
                        state = ""
                    elif char == "0":
                        tokens.append(Token("integer", "0", (i + 1, j + 1)))
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
                    tokens.append(Token("integer", content, location))
                    content = ""
                    state = ""
            elif state == "float":
                if char in Number:
                    content += char
                    continue
                else:
                    tokens.append(Token("float", content, location))
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
                tokens.append(Token("symbol", char, (i + 1, j + 1)))
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
