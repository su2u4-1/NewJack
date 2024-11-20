import argparse

from lib import read_from_path, get_one_path, CompileError, CompileErrorGroup
from lexer import lexer
from parser import Parser
from Compiler import Compiler
from constant import *


def compile_file(path: str, args: argparse.Namespace) -> None:
    """Compile a NewJack file from path."""
    # Read source code from file
    try:
        source = read_from_path(path)
    except FileNotFoundError as e:
        print(f"input Error: {e}")
        return

    # Tokenization
    try:
        tokens = lexer(source, get_one_path(path, ".nj"))
    except CompileError as e:
        s = e.show(source[source.index("//" + e.file) + e.line])
        print(s[0])
        if args.debug:
            print("-" * s[1])
            raise e
        return

    # Parsing
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

    # Compile
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

        # 寫入檔案
        try:
            with open(get_one_path(path, ".vm"), "w+") as f:
                f.write("\n".join(code))
            print(f"Compile successful: {get_one_path(path, '.vm')}")
        except OSError as e:
            print(f"output Error : {e}")
            return


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Compile NewJack files.")
    parser.add_argument("path", type=str, help="Path to the source file.")
    parser.add_argument("-d", "--debug", action="store_true", help=docs["--debug"])
    parser.add_argument("-a", "--showast", action="store_true", help=docs["--showast"])
    parser.add_argument("-c", "--compile", action="store_true", help=docs["--compile"])
    return parser.parse_args()


def interactive_mode() -> tuple[str, argparse.Namespace]:
    """Handle interactive mode using input()."""
    path = input("File(s) path (input 'exit' to cancel): ")
    if path.lower() == "exit":
        exit()
    path = path.split()
    args: list[str] = []
    for i in path:
        if i.startswith("-"):
            args.append(i)
    path = path[0]

    # 將參數轉換為 argparse Namespace
    return path, argparse.Namespace(
        debug="-d" in args or "--debug" in args,
        showast="-a" in args or "--showast" in args,
        compile="-c" in args or "--compile" in args,
    )


def main():
    """Main function to handle script logic."""
    # args = parse_arguments()
    # path = args.path

    path, args = interactive_mode()

    if path == "exit":
        exit()

    paths = path.split()
    for file_path in paths:
        print(f"Processing file: {file_path}")
        compile_file(file_path, args)


if __name__ == "__main__":
    main()
