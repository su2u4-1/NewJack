from .lib import atoz, AtoZ, digit, keyword, symbol, Token, CompileError, source


class Lexer:
    def __init__(self, file: str) -> None:
        self.source = source[file]
        self.source[-1] += " "
        self.file = file

    def error(self, message: str, location: tuple[int, int]) -> None:
        raise CompileError(message, self.file, self.source[location[0] - 1], location)

    def lex(self) -> list[Token]:
        tokens: list[Token] = []
        state = ""
        content = ""
        p = ""
        pp = ""
        location = (-1, -1)
        for i, line in enumerate(self.source):
            for j, char in enumerate(line):
                p = pp
                pp = char
                if state == "comment_1":
                    content += char
                    if p == "*" and char == "/":
                        tokens.append(Token("comment", content, self.file, location))
                        content = ""
                        state = ""
                    continue
                if state == "+" or state == "%":
                    state = ""
                    if char == "=":
                        tokens.append(Token("symbol", p + "=", self.file, (i + 1, j - 1)))
                        continue
                    else:
                        tokens.append(Token("symbol", p, self.file, (i + 1, j - 1)))
                elif state == "-":
                    state = ""
                    if char in digit:
                        state = "integer"
                        content = p + char
                        location = (i + 1, j - 1)
                        continue
                    elif char == "=":
                        tokens.append(Token("symbol", "-=", self.file, (i + 1, j - 1)))
                        continue
                    else:
                        tokens.append(Token("symbol", "-", self.file, (i + 1, j - 1)))
                elif state == "*":
                    state = ""
                    if char == "=":
                        tokens.append(Token("symbol", "*=", self.file, (i + 1, j - 1)))
                        continue
                    elif char == "*":
                        tokens.append(Token("symbol", "**", self.file, (i + 1, j - 1)))
                        continue
                    else:
                        tokens.append(Token("symbol", "*", self.file, (i + 1, j - 1)))
                elif state == "/":
                    state = ""
                    if char == "/":
                        state = "comment_0"
                        content = "//"
                        location = (i + 1, j - 1)
                        continue
                    elif char == "*":
                        state = "comment_1"
                        content = "/*"
                        location = (i + 1, j - 1)
                        continue
                    elif char == "=":
                        tokens.append(Token("symbol", "/=", self.file, (i + 1, j - 1)))
                        continue
                    else:
                        tokens.append(Token("symbol", "/", self.file, (i + 1, j - 1)))
                elif state == ">":
                    state = ""
                    if char == "=":
                        tokens.append(Token("symbol", ">=", self.file, (i + 1, j - 1)))
                        continue
                    elif char == ">":
                        tokens.append(Token("symbol", ">>", self.file, (i + 1, j - 1)))
                        continue
                    else:
                        tokens.append(Token("symbol", ">", self.file, (i + 1, j - 1)))
                elif state == "<":
                    state = ""
                    if char == "=":
                        tokens.append(Token("symbol", "<=", self.file, (i + 1, j - 1)))
                        continue
                    elif char == "<":
                        tokens.append(Token("symbol", "<<", self.file, (i + 1, j - 1)))
                        continue
                    else:
                        tokens.append(Token("symbol", "<", self.file, (i + 1, j - 1)))
                elif state == "=":
                    state = ""
                    if char == "=":
                        tokens.append(Token("symbol", "==", self.file, (i + 1, j - 1)))
                        continue
                    else:
                        tokens.append(Token("symbol", "=", self.file, (i + 1, j - 1)))
                elif state == "!":
                    state = ""
                    if char == "=":
                        tokens.append(Token("symbol", "!=", self.file, (i + 1, j - 1)))
                        continue
                    else:
                        tokens.append(Token("symbol", "!", self.file, (i + 1, j - 1)))
                elif state == "&":
                    state = ""
                    if char == "&":
                        tokens.append(Token("symbol", "&&", self.file, (i + 1, j - 1)))
                        continue
                    else:
                        tokens.append(Token("symbol", "&", self.file, (i + 1, j - 1)))
                elif state == "|":
                    state = ""
                    if char == "|":
                        tokens.append(Token("symbol", "||", self.file, (i + 1, j - 1)))
                        continue
                    else:
                        tokens.append(Token("symbol", "|", self.file, (i + 1, j - 1)))
                elif state == "char":
                    if char != "'":
                        if len(content) == 0:
                            content = char
                        else:
                            self.error("Character constant too long", (i + 1, j))
                    elif char == "'":
                        if len(content) == 1:
                            tokens.append(Token("char", "'" + content + "'", self.file, (i + 1, j)))
                            state = ""
                            content = ""
                        else:
                            self.error("Character constant too long or too short", (i + 1, j))
                    else:
                        self.error("Empty character constant", (i + 1, j))
                    continue
                elif state == "string":
                    if char == '"':
                        tokens.append(Token("string", '"' + content + '"', self.file, location))
                        state = ""
                        content = ""
                    else:
                        content += char
                    continue
                elif state == "integer":
                    if char in digit:
                        content += char
                        continue
                    elif char == ".":
                        state = "float"
                        content += char
                        continue
                    else:
                        tokens.append(Token("int", content, self.file, location))
                        state = ""
                        content = ""
                elif state == "float":
                    if char in digit:
                        content += char
                        continue
                    else:
                        tokens.append(Token("float", content, self.file, location))
                        state = ""
                        content = ""
                elif state == "comment_0":
                    if char != "\n":
                        content += char
                    else:
                        tokens.append(Token("comment", content, self.file, location))
                        state = ""
                        content = ""
                    continue
                if state == "identifier":
                    if char in atoz or char in AtoZ or char in digit or char == "_":
                        content += char
                        continue
                    else:
                        if content in keyword:
                            tokens.append(Token("keyword", content, self.file, location))
                        else:
                            tokens.append(Token("identifier", content, self.file, location))
                        state = ""
                        content = ""

                if char in symbol:
                    if char in "+-*/%>=<!&|":
                        state = char
                    else:
                        tokens.append(Token("symbol", char, self.file, (i + 1, j)))
                elif char == "'":
                    state = "char"
                elif char == '"':
                    state = "string"
                    location = (i + 1, j + 1)
                elif char in digit:
                    state = "integer"
                    location = (i + 1, j)
                    content = char
                elif char == "#":
                    state = "comment_0"
                    content = "#"
                    location = (i + 1, j)
                elif char in atoz or char in AtoZ or char == "_":
                    state = "identifier"
                    location = (i + 1, j)
                    content = char
                else:
                    if not char.isspace():
                        self.error(f"Invalid character {char}", (i + 1, j))
        return tokens
