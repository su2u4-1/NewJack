from os.path import isfile, abspath

from lib import read_from_path, get_one_path, CompileError, CompileErrorGroup, Args
from lexer import lexer
from parser import Parser
from Compiler import Compiler


def compile_file(path: str, args: Args) -> None:
    try:
        source = read_from_path(path)
    except FileNotFoundError as e:
        print(f"input Error: {e}")
        return

    try:
        tokens = lexer(source, get_one_path(path, ".nj"))
    except CompileError as e:
        s = e.show(source[source.index("//" + e.file) + e.line])
        print(s[0])
        if args.debug:
            print("-" * s[1])
            raise e
        return

    parser = Parser(tokens)
    try:
        ast = parser.main(get_one_path(path, ".nj"))
    except CompileError as e:
        s = e.show(source[source.index("//" + e.file) + e.line])
        print(s[0])
        if args.debug:
            print("-" * s[1])
            raise e
        return

    if args.showast:
        print("Abstract Syntax Tree:")
        print(ast)

    if args.compile:
        compiler = Compiler(ast, args.debug)
        try:
            code = compiler.main()
        except CompileErrorGroup as e:
            for i in e.exceptions:
                s = i.show(source[source.index("//" + i.file) + i.line])
                print(s[0])
                if args.debug:
                    print("-" * s[1])
                    print(i.traceback)
                    print("-" * s[1])
            return

        try:
            with open(get_one_path(path, ".vm"), "w+") as f:
                f.write("\n".join(code))
            print(f"Compile successful: {get_one_path(path, '.vm')}")
        except OSError as e:
            print(f"output Error : {e}")
            return


def parse_arguments() -> tuple[list[str], Args]:
    path = input("File(s) path (input 'exit' to cancel): ")
    if "exit" in path.lower():
        exit()
    args = Args()
    paths: list[str] = []
    outpath = False
    errout = False
    help = False
    for i in path.split():
        if help:
            args.help.append(i)
        elif i.startswith("-"):
            outpath = False
            errout = False
            if i in ("-d", "--debug"):
                args.debug = True
            elif i in ("-c", "--compile"):
                args.compile = True
            elif i in ("-s", "--showast"):
                args.showast = True
            elif i in ("-o", "--outpath"):
                outpath = True
            elif i in ("-e", "--errout"):
                errout = True
            elif i in ("-h", "--help"):
                help = True
                args.help.append("--help")
        elif isfile(abspath(i)):
            if outpath:
                args.outpath += abspath(i)
                outpath = False
            elif errout:
                args.errout += abspath(i)
                errout = False
            else:
                paths.append(abspath(i))
    return paths, args


def main():
    paths, args = parse_arguments()
    for file_path in paths:
        print(f"Processing file: {file_path}")
        compile_file(file_path, args)


if __name__ == "__main__":
    main()
