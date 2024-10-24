from lib import read_from_path, get_one_path, CompileError, CompileErrorGroup
from lexer import lexer
from parser import Parser
from Compiler import Compiler

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
        ast = parser.main(get_one_path(path, ".nj"))
    except CompileError as e:
        print(e.show(source[source.index("//" + e.file) + e.line]))
        exit()
    compiler = Compiler(ast)
    try:
        code = compiler.main()
    except CompileErrorGroup as e:
        for i in e.exceptions:
            print(i.show(source[source.index("//" + i.file) + i.line]))
        exit()
    with open(get_one_path(path, ".vm"), "w+") as f:
        f.write("\n".join(code))
