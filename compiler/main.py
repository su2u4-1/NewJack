from compiler.lib import read_from_path, get_one_path, CompileError
from compiler.lexer import lexer
from compiler.parser import Parser
from compiler.compiler import Compiler

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
    except CompileError as e:
        print(e.show(source[source.index("//" + e.file) + e.line]))
        exit()
    compiler = Compiler(ast)
    try:
        code = compiler.main()
    except CompileError as e:
        print(e.show(source[source.index("//" + e.file) + e.line]))
        exit()
