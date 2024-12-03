from os.path import isfile, abspath

from lib import read_from_path, get_one_path, CompileError, CompileErrorGroup, Args
from lexer import lexer
from parser import Parser
from Compiler import Compiler


def process_file(file_path: str, args: Args):
    """處理單個檔案，包括語法分析與編譯。"""
    try:
        source = read_from_path(file_path)
    except FileNotFoundError as e:
        print(f"Input Error: {e}")
        return

    try:
        tokens = lexer(source, get_one_path(file_path, ".nj"))
        parser = Parser(tokens)
        ast = parser.main(get_one_path(file_path, ".nj"))
    except CompileError as e:
        # 直接讓錯誤冒泡，讓 traceback 顯示完整路徑
        raise e

    if args.showast:
        print("Abstract Syntax Tree:")
        print(ast)

    if args.compile:
        compiler = Compiler(ast, args.debug)
        try:
            code = compiler.main()
        except CompileErrorGroup as e:
            for error in e.exceptions:
                print(error.show(source[error.line])[0])  # 顯示每個錯誤訊息
            return

        output_path = get_one_path(file_path, ".vm")
        try:
            with open(output_path, "w") as f:
                f.write("\n".join(code))
            print(f"Compile successful: {output_path}")
        except OSError as e:
            print(f"Output Error: {e}")


def parse_arguments() -> tuple[list[str], Args]:
    """解析指令行輸入並返回檔案路徑與參數物件。"""
    input_path = input("File(s) path (input 'exit' to cancel): ")
    if "exit" in input_path.lower():
        exit()

    args = Args()
    paths: list[str] = []
    for part in input_path.split():
        if part.startswith("-"):
            args.process_flag(part)
        elif isfile(abspath(part)):
            paths.append(abspath(part))
        else:
            print(f"Invalid argument or file path: {part}")

    if not paths:
        print("No valid input files provided. Use --help for usage information.")
    return paths, args


def main():
    paths, args = parse_arguments()
    for file_path in paths:
        print(f"Processing file: {file_path}")
        try:
            process_file(file_path, args)
        except CompileError as e:
            print(f"Error during processing {file_path}:")
            print(e)


if __name__ == "__main__":
    main()
