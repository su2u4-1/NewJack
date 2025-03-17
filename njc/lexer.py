from lib import Token, symbol, digit, atoz, AtoZ, keyword


def error(message: str, location: tuple[int, int], file: str) -> None:
    pass


def lexer(source: list[str], file: str) -> list[Token]:
    tokens: list[Token] = []
    state = ""
    content = ""
    p = ""
    pp = ""
    location = (-1, -1)
    for i, line in enumerate(source):
        for j, char in enumerate(line):
            if state == "-":
                if char in digit:
                    state = "integer"
                    content = p + char
                    location = (i + 1, j - 1)
                    continue
                else:
                    tokens.append(Token("symbol", p, (i + 1, j - 1)))
                    state = ""
            elif state == "char":
                if char != "'":
                    if len(content) == 0:
                        content = char
                    else:
                        error("Character constant too long", (i + 1, j), file)
                elif char == "'":
                    if len(content) == 1:
                        tokens.append(Token("char", content, (i + 1, j)))
                        state = ""
                        content = ""
                    else:
                        error("Character constant too long or too short", (i + 1, j), file)
                else:
                    error("Empty character constant", (i + 1, j), file)
                continue
            elif state == "string":
                if char == '"':
                    tokens.append(Token("string", '"' + content + '"', location))
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
                    pass  # TODO: int -> float
                else:
                    tokens.append(Token("integer", content, location))
                    state = ""
                    content = ""
            elif state == "comment_0":
                content += char
                continue
            elif state == "comment_1":
                content += char
                continue
            if state == "identifier":
                if char in atoz or char in AtoZ or char in digit or char == "_":
                    content += char
                    continue
                else:
                    if content in keyword:
                        tokens.append(Token("keyword", content, location))
                    else:
                        tokens.append(Token("identifier", content, location))
                    state = ""
                    content = ""

            if char.isspace():
                pass
            elif char in symbol:
                if char in "-/><=!+-*/%&|":
                    state = char
            elif char == "'":
                state = "char"
            elif char == '"':
                state = "string"
                location = (i + 1, j + 1)
            elif char in digit:
                state = "integer"
                location = (i + 1, j)
            elif char == "#":
                state = "comment_0"
                content = "#"
                location = (i + 1, j)
            elif char in atoz or char in AtoZ or char == "_":
                state = "identifier"
                location = (i + 1, j)
            pp = p
            p = char
        if state == "comment_0":
            tokens.append(Token("comment", content, location))
            state = ""
            content = ""
    return tokens
