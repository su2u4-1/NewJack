from lib import Token, Symbol, Number, atoZ, Keyword


def lexer(source: list[str]) -> list[Token]:
    tokens: list[Token] = []
    content = ""
    state = ""
    file_start = 0
    location = (-1, -1)
    for i, line in enumerate(source):
        if line.startswith("//"):
            tokens.append(Token("file", line[2:], (-1, -1)))
            file_start = i
            continue
        if state == "string":
            print("error: string not closed\nlocation:", location)
            exit()
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
            elif state == "equal":
                if char == "=":
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
                state = "neg"
                content = char
                location = (i - file_start, j + 1)
            elif char in ("!", "=", ">", "<"):
                state = "equal"
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
            else:
                print(f"error: illegal symbol '{char}'\nlocation:", (i - file_start, j + 1))
                exit()

    if state != "":
        print("error:", state)
        print("location:", location)
        exit()
    return tokens
