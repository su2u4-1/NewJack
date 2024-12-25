from os import listdir
from os.path import isfile, isdir, join
from sys import argv

from compiler.lexer import lexer


def format_nj(code: list[str]) -> list[str]:
    new_code: list[str] = []
    tokens = lexer(code, "format.nj")
    indent = 0
    line: list[str] = []
    for i in tokens:
        if i.type == "symbol" and i.content == "{":
            line.append("{")
            new_code.append("    " * indent + " ".join(line))
            indent += 1
            line = []
        elif i.type == "symbol" and i.content == "}":
            new_code.append("    " * indent + " ".join(line))
            indent -= 1
            line = ["}"]
        elif i.type in ("string", "integer", "symbol", "keyword", "float", "char", "identifier"):
            line.append(i.content)
    return new_code


def format_vm(code: list[str]) -> list[str]:
    new_code: list[str] = []
    indent = 0
    f = False
    for i in code:
        i = i.strip()
        if f and (i.startswith("label") or i.startswith("debug-label start")):
            indent -= 1
        f = False
        if i.startswith("debug-label end"):
            indent -= 1
        elif i == "return":
            f = True
        new_code.append("    " * indent + i)
        if i.startswith("label") or i.startswith("debug-label start"):
            indent += 1
    return new_code


def main(path: str, type_: str) -> None:
    new_code = []
    if isfile(path):
        paths = [path]
    elif isdir(path):
        paths = [join(path, i) for i in listdir(path)]
    else:
        print("Invalid path")
        return

    for i in paths:
        if type_ == "":
            if i.endswith(".vm"):
                type_ = "vm"
            elif i.endswith(".nj"):
                type_ = "nj"
        with open(i, "r") as f:
            code = f.readlines()
        if type_ == "vm":
            new_code = format_vm(code)
        elif type_ == "nj":
            new_code = format_nj(code)
        else:
            print("Invalid type")
            continue
        with open(i, "w") as f:
            f.write("\n".join(new_code))


def no_arg() -> None:
    main(*input("file path: ").split(maxsplit=1))


def arg() -> None:
    if len(argv) >= 2:
        path = argv[1]
    else:
        print("file path is required")
        return
    type_ = ""
    if len(argv) >= 3:
        type_ = argv[2]
    main(path, type_)


if len(argv) > 1:
    arg()
else:
    no_arg()
