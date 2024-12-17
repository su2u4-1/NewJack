from os.path import isfile, abspath
from sys import argv

from lib import get_path, read_source, get_one_path, format_traceback, CompileError, CompileErrorGroup, Args, Continue
from lexer import lexer
from parser import Parser
from AST import Class, Global, Root
from Compiler import Compiler


def analyze_file(source: list[str], arg: Args, file_path: str, errout: list[str]) -> Root:
    # Tokenize the source code.
    try:
        tokens = lexer(source, file_path)
    except CompileError as e:
        s = e.show(source[e.line])
        errout.append(s[0])
        if arg.debug:
            errout.append("-" * s[1])
            errout.append(format_traceback(e))
            raise
        else:
            raise Continue()

    # Parse tokens into an AST.
    try:
        ast = Parser(tokens, file_path).main()
    except CompileError as e:
        s = e.show(source[e.line])
        errout.append(s[0])
        if arg.debug:
            errout.append("-" * s[1])
            errout.append(format_traceback(e))
            raise
        else:
            raise Continue()

    if arg.showast:
        errout.append("Abstract Syntax Tree:")
        errout.append(str(ast))

    return ast


def compile_all_file(
    class_list: list[Class], global_: Global, arg: Args, source_dict: dict[str, list[str]], errout: list[str]
) -> list[str]:
    failed = False
    compiler = Compiler(global_, errout, arg.debug)
    for ast in class_list:
        try:
            # Add the AST to the compiler for further processing.
            compiler.addfile(ast)
        except CompileErrorGroup as e:
            for i in e.exceptions:
                s = i.show(source_dict[ast.file_path][i.line])
                errout.append(s[0])
                if arg.debug:
                    errout.append("-" * s[1])
                    errout.append(i.traceback)
                    errout.append("-" * s[1])
            failed = True
    if failed:
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
                    print(f"Unrecognized flag: {i}. Please refer to the help section for valid options.")
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


def main() -> tuple[list[str], str]:
    errout: list[str] = []
    # parse arguments
    if len(argv) == 1:
        args = input("File(s) path (input 'exit' to cancel): ")
    else:
        args = " ".join(argv[1:])
    paths, arg = parse_arguments(args)
    if len(paths) == 0:
        print("No valid input files provided. Use --help for usage information.")
        return errout, arg.errout

    # get file path
    try:
        files = get_path(paths)
    except FileNotFoundError as e:
        errout.append(f"input Error: {e}")
        return errout, arg.errout

    # read source
    source_dict: dict[str, list[str]] = {}

    # process source
    failed = False
    class_list: list[Class] = []
    for i in files:
        source = read_source(i)
        print(f"Processing file: {i}")
        try:
            root = analyze_file(source, arg, i, errout)
            class_list.extend(root.class_list)
        except Continue:
            print(f"File {i} processing failed")
            failed = True
        else:
            print(f"File {i} processed successfully")
    if failed:
        return errout, arg.errout

    # compile
    if arg.compile:
        print("compile start")
        code = compile_all_file(class_list, arg, source_dict, errout)
        if code == []:
            print("compile failed")
            return errout, arg.errout
        elif arg.debug:
            return errout, arg.errout
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
            errout.append(f"Compile successful: {f_path}")
        except OSError as e:
            errout.append(f"output Error : {e}")

    return errout, arg.errout


if __name__ == "__main__":
    errout, outpath = main()
    errout = "\n".join(errout)
    if outpath == "":
        print(errout)
    else:
        extension_name = outpath.split(".")[1]
        if extension_name == "":
            extension_name = ".txt"
        with open(get_one_path(outpath, extension_name), "w+") as f:
            f.write(errout)
