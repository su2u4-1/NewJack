from lib import read_from_path
from lexer import lexer
from parser import Parser

if __name__ == "__main__":
    path = input("file(s) path: ")
    source = read_from_path(path)
    tokens = lexer(source)
    parser = Parser(tokens)
    xmlcode = parser.main()
