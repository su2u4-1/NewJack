from os.path import abspath, isfile
from sys import argv

from lexer import lexer
from lib import Args


def parse_args(args: list[str]) -> Args:
    path = ""
    flags: list[str] = []
    arg: list[str] = []
    for i in args:
        if isfile(abspath(i)):
            path = abspath(i)
        elif i.startswith("-"):
            flags.append(i)
        else:
            arg.append(i)
    return Args(path, flags, arg)


def main(args: Args) -> None:
    with open(args.path, "r") as f:
        code = f.readlines()
    tokens = lexer(code, args.path)

    # output result
    for i in tokens:
        print(i)


if len(argv) <= 1:
    args = input("Enter file path and other flag & args: ").split()
else:
    args = argv[1:]
main(parse_args(args))
