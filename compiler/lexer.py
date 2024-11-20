from lib import Token, CompileError
from constant import *


def lexer(source: list[str], file: str) -> list[Token]:
    tokens: list[Token] = []
    content = ""
    state = ""
    pp, p = "", ""
    file_start = 0
    location = (-1, -1)
    for i, line in enumerate(source):
        if line.startswith("//"):
            tokens.append(Token("file", line[2:], (-1, -1)))
            file_start = i
            continue
        if state == "string":
            raise CompileError("string not closed", file, location, "lexer")
        for j, char in enumerate(line):
            p = pp
            pp = char
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
            elif state == "symbol":
                if content + char in Symbol:
                    tokens.append(Token("symbol", content + char, location))
                    content = ""
                    state = ""
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
                        tokens.append(Token("integer", "0", (i - file_start, j + 1)))
                        content = ""
                        state = ""
                    elif content == "0":
                        tokens.append(Token("integer", "0", (i - file_start, j + 1)))
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
                    if content[-1] == ".":
                        tokens.append(Token("integer", content[:-1], location))
                        tokens.append(Token("symbol", ".", (i - file_start, j + 1)))
                    else:
                        tokens.append(Token("float", content, location))
                    content = ""
                    state = ""

            if char == '"':
                state = "string"
                content = char
                location = (i - file_start, j + 1)
            elif char == "#":
                break
            elif char == "`":
                state = "commant"
            elif char == "-":
                if p in ("[", "(", "=", ",", "!", "+", "-", "*", "/", "|", "&", "==", "!=", ">=", "<=", ">", "<", "<<", ">>"):
                    state = "neg"
                    content = char
                    location = (i - file_start, j + 1)
                else:
                    tokens.append(Token("symbol", "-", location))
            elif char in ("!", "=", ">", "<"):
                state = "symbol"
                content = char
                location = (i - file_start, j + 1)
            elif char in Symbol:
                tokens.append(Token("symbol", char, (i - file_start, j + 1)))
            elif char in Number:
                state = "int"
                content = char
                location = (i - file_start, j + 1)
            elif char in atoZ or char == "_":
                state = "identifier"
                content = char
                location = (i - file_start, j + 1)
            elif char not in (" ", "\t", "\n"):
                raise CompileError(f"illegal symbol '{char}'", file, (i - file_start, j + 1), "lexer")

    if state != "":
        raise CompileError(state, file, location, "lexer")
    return tokens
