from lib import atoz, AtoZ, digit, keyword, symbol, Token


def error(message: str, location: tuple[int, int], file: str) -> None:
    print(f"Error: {message} at {location} in {file}")
    exit(1)


def lexer(source: list[str], file: str) -> list[Token]:
    tokens: list[Token] = []
    state = ""
    content = ""
    p = ""
    # pp = ""
    location = (-1, -1)
    for i, line in enumerate(source):
        for j, char in enumerate(line):
            if state == "comment_1":
                content += char
                if p == "*" and char == "/":
                    tokens.append(Token("comment", content, location))
                    content = ""
                    state = ""
                p = char
                continue
            if p == "+" or p == "%":
                if char == "=":
                    tokens.append(Token("symbol", p + "=", (i + 1, j - 1)))
                    p = char
                    continue
                else:
                    tokens.append(Token("symbol", p, (i + 1, j - 1)))
            elif p == "-":
                if char in digit:
                    state = "integer"
                    content = p + char
                    location = (i + 1, j - 1)
                    p = char
                    continue
                elif char == "=":
                    tokens.append(Token("symbol", p + "=", (i + 1, j - 1)))
                    p = char
                    continue
                else:
                    tokens.append(Token("symbol", p, (i + 1, j - 1)))
            elif p == "*":
                if char == "=":
                    tokens.append(Token("symbol", p + "=", (i + 1, j - 1)))
                    p = char
                    continue
                elif char == "*":
                    tokens.append(Token("symbol", p + "*", (i + 1, j - 1)))
                    p = char
                    continue
                else:
                    tokens.append(Token("symbol", p, (i + 1, j - 1)))
            elif p == "/":
                if char == "/":
                    state = "comment_0"
                    content = "//"
                    location = (i + 1, j - 1)
                    p = char
                    continue
                elif char == "*":
                    state = "comment_1"
                    content = "/*"
                    location = (i + 1, j - 1)
                    p = char
                    continue
                else:
                    tokens.append(Token("symbol", p, (i + 1, j - 1)))
            elif p == ">":
                if char == "=":
                    tokens.append(Token("symbol", ">=", (i + 1, j - 1)))
                    p = char
                    continue
                elif char == ">":
                    tokens.append(Token("symbol", ">>", (i + 1, j - 1)))
                    p = char
                    continue
                else:
                    tokens.append(Token("symbol", ">", (i + 1, j - 1)))
            elif p == "<":
                if char == "=":
                    tokens.append(Token("symbol", "<=", (i + 1, j - 1)))
                    p = char
                    continue
                elif char == "<":
                    tokens.append(Token("symbol", "<<", (i + 1, j - 1)))
                    p = char
                    continue
                else:
                    tokens.append(Token("symbol", "<", (i + 1, j - 1)))
            elif p == "=":
                if char == "=":
                    tokens.append(Token("symbol", "==", (i + 1, j - 1)))
                    p = char
                    continue
                else:
                    tokens.append(Token("symbol", "=", (i + 1, j - 1)))
            elif p == "!":
                if char == "=":
                    tokens.append(Token("symbol", "!=", (i + 1, j - 1)))
                    p = char
                    continue
                else:
                    tokens.append(Token("symbol", "!", (i + 1, j - 1)))
            elif p == "&":
                if char == "&":
                    tokens.append(Token("symbol", "&&", (i + 1, j - 1)))
                    p = char
                    continue
                else:
                    tokens.append(Token("symbol", "&", (i + 1, j - 1)))
            elif p == "|":
                if char == "|":
                    tokens.append(Token("symbol", "||", (i + 1, j - 1)))
                    p = char
                    continue
                else:
                    tokens.append(Token("symbol", "|", (i + 1, j - 1)))

            if state == "char":
                if char != "'":
                    if len(content) == 0:
                        content = char
                    else:
                        error("Character constant too long", (i + 1, j), file)
                elif char == "'":
                    if len(content) == 1:
                        tokens.append(Token("char", "'" + content + "'", (i + 1, j)))
                        state = ""
                        content = ""
                    else:
                        error("Character constant too long or too short", (i + 1, j), file)
                else:
                    error("Empty character constant", (i + 1, j), file)
                p = char
                continue
            elif state == "string":
                if char == '"':
                    tokens.append(Token("string", '"' + content + '"', location))
                    state = ""
                    content = ""
                else:
                    content += char
                p = char
                continue
            elif state == "integer":
                if char in digit:
                    content += char
                    p = char
                    continue
                elif char == ".":
                    state = "float"
                    content += char
                    p = char
                    continue
                else:
                    tokens.append(Token("integer", content, location))
                    state = ""
                    content = ""
            elif state == "comment_0":
                content += char
                p = char
                continue
            if state == "identifier":
                if char in atoz or char in AtoZ or char in digit or char == "_":
                    content += char
                    p = char
                    continue
                else:
                    if content in keyword:
                        tokens.append(Token("keyword", content, location))
                    else:
                        tokens.append(Token("identifier", content, location))
                    state = ""
                    content = ""

            if char in symbol:
                if char in "+-*/%>=<!&|":
                    state = "symbol"
                else:
                    tokens.append(Token("symbol", char, (i + 1, j)))
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
            # pp = p
            p = char
        if state == "comment_0":
            tokens.append(Token("comment", content, location))
            state = ""
            content = ""
    return tokens
