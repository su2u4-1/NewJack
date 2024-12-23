from sys import argv


def format_vm(code: list[str]) -> list[str]:
    new_code: list[str] = []
    indent = 0
    for i in code:
        i = i.strip()
        if i == "return" or i.startswith("debug-label end"):
            indent -= 1
        if i == "return":
            new_code.append("    " * (indent + 1) + i)
        else:
            new_code.append("    " * indent + i)
        if i.startswith("label") or i.startswith("debug-label start"):
            indent += 1
    return new_code


def main(path: str, type_: str) -> None:
    new_code = []
    with open(path, "r") as f:
        code = f.readlines()
    if type_ == "vm":
        new_code = format_vm(code)
    with open(path, "w") as f:
        f.write("\n".join(new_code))


def no_arg() -> None:
    path = ""
    type_ = ""
    path = input("file path: ")
    if path.endswith(".vm"):
        type_ = "vm"
    main(path, type_)


def arg() -> None:
    path = ""
    type_ = ""
    if len(argv) >= 2:
        path = argv[1]
    if len(argv) >= 3:
        type_ = argv[2]
    main(path, type_)


if len(argv) > 1:
    arg()
else:
    no_arg()
