from os.path import isfile, abspath
from sys import argv

from lib import get_path, read_source, get_one_path, CompileError, CompileErrorGroup, Args, Continue
from lexer import lexer
from parser import Parser
from AST import Root
from Compiler import Compiler


def process_file(source: list[str], arg: Args, file_path: str) -> Root:
    # lexical analysis
    try:
        tokens = lexer(source, file_path)
    except CompileError as e:
        s = e.show(source[e.line])
        print(s[0])
        if arg.debug:
            print("-" * s[1])
            raise e
        raise Continue()

    # parsing
    try:
        ast = Parser(tokens, file_path).main()
    except CompileError as e:
        s = e.show(source[e.line])
        print(s[0])
        if arg.debug:
            print("-" * s[1])
            raise e
        raise Continue()

    if arg.showast:
        print("Abstract Syntax Tree:")
        print(ast)

    return ast


def compile_all_file(ast_list: list[tuple[Root, list[str]]], arg: Args) -> list[str]:
    compiler = Compiler(arg.debug)
    for ast, source in ast_list:
        try:
            compiler.addfile(ast)
        except CompileErrorGroup as e:
            for i in e.exceptions:
                s = i.show(source[i.line])
                print(s[0])
                if arg.debug:
                    print("-" * s[1])
                    print(i.traceback)
                    print("-" * s[1])
            return []
    return compiler.returncode()


def parse_arguments(args: str) -> tuple[list[str], Args]:
    if "exit" in args.lower():
        exit()
    arg = Args()
    paths: list[str] = []
    outpath = False
    errout = False
    help = False
    for i in args.split():
        if help:
            arg.help.append(i)
        elif i.startswith("-"):
            outpath = False
            errout = False
            match i:
                case "-d" | "--debug":
                    arg.debug = True
                case "-c" | "--compile":
                    arg.compile = True
                case "-s" | "--showast":
                    arg.showast = True
                case "-o" | "--outpath":
                    outpath = True
                case "-e" | "--errout":
                    errout = True
                case "-h" | "--help":
                    help = True
                    arg.help.append("--help")
                case _:
                    print(f"Unrecognized argument flag: {i}. Please check your input.")
        elif isfile(abspath(i)):
            if outpath:
                arg.outpath += abspath(i)
                outpath = False
            elif errout:
                arg.errout += abspath(i)
                errout = False
            else:
                paths.append(abspath(i))
    arg.print_help()
    return paths, arg


def main():
    # parse arguments
    if len(argv) == 1:
        args = input("File(s) path (input 'exit' to cancel): ")
    else:
        args = " ".join(argv[1:])
    paths, arg = parse_arguments(args)
    if len(paths) == 0:
        print("No valid input files provided. Use --help for usage information.")
        return

    # get file path
    try:
        files = get_path(paths)
    except FileNotFoundError as e:
        print(f"input Error: {e}")
        return

    # read and process source
    failed = False
    ast_list: list[tuple[Root, list[str]]] = []
    for i in files:
        source = read_source(i)
        print(f"Processing file: {i}")
        try:
            ast_list.append((process_file(source, arg, i), source))
        except Continue:
            print(f"File {i} processing failed")
            failed = True
        else:
            print(f"File {i} processed successfully")
    if failed:
        return

    # compile
    if arg.compile:
        print("compile start")
        code = compile_all_file(ast_list, arg)
        if code == []:
            print("compile failed")
            return
        else:
            print("compile end")

        # output the compiled file
        if arg.outpath == "":
            f_path = get_one_path(paths[0], ".vm")
        else:
            f_path = get_one_path(arg.outpath, ".vm")
        try:
            with open(get_one_path(f_path, ".vm"), "w+") as f:
                f.write("\n".join(code))
            print(f"Compile successful: {f_path}")
        except OSError as e:
            print(f"output Error : {e}")


if __name__ == "__main__":
    main()
