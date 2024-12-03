from os.path import isfile, abspath

from lib import get_path, read_source, get_one_path, CompileError, CompileErrorGroup, Args, Continue
from lexer import lexer
from parser import Parser
from AST import Root
from Compiler import Compiler


def process_file(source: list[str], args: Args, file_path: str) -> Root:
    # lexical analysis
    try:
        tokens = lexer(source, file_path)
    except CompileError as e:
        s = e.show(source[e.line])
        print(s[0])
        if args.debug:
            print("-" * s[1])
            raise e
        raise Continue()

    # parsing
    try:
        ast = Parser(tokens, file_path).main()
    except CompileError as e:
        s = e.show(source[e.line])
        print(s[0])
        if args.debug:
            print("-" * s[1])
            raise e
        raise Continue()

    if args.showast:
        print("Abstract Syntax Tree:")
        print(ast)

    return ast


def compile_all_file(ast_list: list[tuple[Root, list[str]]], args: Args) -> list[str]:
    code: list[str] = []
    for ast, source in ast_list:
        # compile
        compiler = Compiler(args.debug)
        try:
            code.extend(compiler.main(ast))
        except CompileErrorGroup as e:
            for i in e.exceptions:
                s = i.show(source[i.line])
                print(s[0])
                if args.debug:
                    print("-" * s[1])
                    print(i.traceback)
                    print("-" * s[1])
            continue
    return code


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
            match i:
                case "-d" | "--debug":
                    args.debug = True
                case "-c" | "--compile":
                    args.compile = True
                case "-s" | "--showast":
                    args.showast = True
                case "-o" | "--outpath":
                    outpath = True
                case "-e" | "--errout":
                    errout = True
                case "-h" | "--help":
                    help = True
                    args.help.append("--help")
                case _:
                    print(f"Unrecognized argument flag: {i}. Please check your input.")
        elif isfile(abspath(i)):
            if outpath:
                args.outpath += abspath(i)
                outpath = False
            elif errout:
                args.errout += abspath(i)
                errout = False
            else:
                paths.append(abspath(i))
    args.print_help()
    return paths, args


def main():
    paths, args = parse_arguments()
    if len(paths) == 0:
        print("No valid input files provided. Use --help for usage information.")
        return

    try:
        files = get_path(paths)
    except FileNotFoundError as e:
        print(f"input Error: {e}")
        return

    ast_list: list[tuple[Root, list[str]]] = []
    for i in files:
        source = read_source(i)
        print(f"Processing file: {i}")
        try:
            ast_list.append((process_file(source, args, i), source))
        except Continue:
            print(f"File {i} processing failed")

    if args.compile:
        print("compile start")
        compile_all_file(ast_list, args)
        print("compile end")

        # TODO: output compiled file
        try:
            with open(get_one_path(path, ".vm"), "w+") as f:
                f.write("\n".join(code))
            print(f"Compile successful: {get_one_path(path, '.vm')}")
        except OSError as e:
            print(f"output Error : {e}")


if __name__ == "__main__":
    main()
