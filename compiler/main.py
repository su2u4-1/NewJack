from lib import read_from_path, get_one_path, CompileError, CompileErrorGroup, docs
from lexer import lexer
from parser import Parser
from Compiler import Compiler

# 修改建議: https://chatgpt.com/share/673c4288-c0bc-8013-83df-a25c86eceac9

if __name__ == "__main__":
    path = input("file(s) path (input 'exit' cancel): ")
    if path == "exit":
        exit()
    path = path.split()
    arg: list[str] = []
    for i in path:
        if i.startswith("-"):
            arg.append(i)
    path = path[0]
    if "-h" in arg or "--help" in arg:
        if len(arg) == 1:
            for k, v in docs.items():
                print(f"{k}  {v}")
        else:
            for i in arg:
                if i in docs:
                    print(f"{i}  {docs[i]}")
        exit()
    try:
        source = read_from_path(path)
    except FileNotFoundError as e:
        print(e)
        exit()
    tokens = lexer(source)
    parser = Parser(tokens)
    try:
        ast = parser.main(get_one_path(path, ".nj"))
    except CompileError as e:
        s = e.show(source[source.index("//" + e.file) + e.line])
        print(s[0])
        if "--debug" in arg or "-d" in arg:
            print("-" * s[1])
            raise e
        exit()
    if "--showast" in arg or "-a" in arg:
        print(ast)
    if "--compile" in arg or "-c" in arg:
        compiler = Compiler(ast)
        try:
            code = compiler.main()
        except CompileErrorGroup as e:
            for i in e.exceptions:
                print(i.show(source[source.index("//" + i.file) + i.line]))
            exit()
        with open(get_one_path(path, ".vm"), "w+") as f:
            f.write("\n".join(code))
