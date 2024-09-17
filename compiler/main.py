from lib import read_from_path, ParsingError, get_one_path
from lexer import lexer
from parser import Parser

if __name__ == "__main__":
    while True:
        path = input("file(s) path (input 'exit' cancel): ")
        if path == "exit":
            exit()
        try:
            source = read_from_path(path)
            break
        except FileNotFoundError as e:
            print(e)
    tokens = lexer(source)
    parser = Parser(tokens)
    try:
        ast = parser.main(get_one_path(path, ""))
    except ParsingError as e:
        print(f'File "{e.file}", line {e.line}, in {e.index}')
        print(e.text)
        t = source[source.index("//" + e.file) + e.line]
        if t.endswith("\n"):
            t = t[:-1]
        print(t)
        print(" " * (e.index - 1) + "^")
        exit()
    print(ast.show())
