from AST import *
from lib import Tokens

__all__ = [
    "type_class",
    "type_subroutine",
    "type_int",
    "type_argument",
    "type_void",
    "Operator",
    "built_in_type",
    "TokenType",
    "Symbol",
    "Number",
    "atoz",
    "AtoZ",
    "atoZ",
    "Keyword",
    "Precedence",
    "docs",
]

type_class = Type((-1, -1), Identifier((-1, -1), "class"))
type_subroutine = {
    "constructor": Type((-1, -1), Identifier((-1, -1), "constructor")),
    "function": Type((-1, -1), Identifier((-1, -1), "function")),
    "method": Type((-1, -1), Identifier((-1, -1), "method")),
}
type_int = Type((-1, -1), Identifier((-1, -1), "int"))
type_argument = Type((-1, -1), Identifier((-1, -1), "argument"))
type_void = Type((-1, -1), Identifier((-1, -1), "void"))

Operator = Tokens("symbol", ("+", "-", "*", "/", "==", "!=", ">=", "<=", ">", "<", "|", "&"))
built_in_type = Tokens("keyword", ("int", "bool", "char", "str", "list", "float", "void"))


TokenType = Literal["string", "integer", "symbol", "keyword", "float", "char", "identifier", "file"]
Symbol = {
    "{",
    "}",
    "[",
    "]",
    "(",
    ")",
    "=",
    ";",
    ",",
    ".",
    "!",
    "+",
    "-",
    "*",
    "/",
    "|",
    "&",
    "==",
    "!=",
    ">=",
    "<=",
    ">",
    "<",
    "<<",
    ">>",
    ":",
}
Number = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
atoz = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"}
AtoZ = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"}
atoZ = atoz | AtoZ
Keyword = {
    "class",
    "var",
    "describe",
    "constructor",
    "function",
    "method",
    "void",
    "pass",
    "let",
    "do",
    "if",
    "if else",
    "else",
    "while",
    "return",
    "for",
    "break",
    "continue",
    "false",
    "true",
    "self",
    "int",
    "bool",
    "char",
    "str",
    "list",
    "float",
}
Precedence = {
    "!": 6,
    "~": 6,
    "*": 5,
    "/": 5,
    "+": 4,
    "-": 4,
    "<<": 3,
    ">>": 3,
    "<": 2,
    "<=": 2,
    ">": 2,
    ">=": 2,
    "==": 2,
    "!=": 2,
    "&": 1,
    "|": 1,
}
docs = {
    "--debug": "Enables debug mode, showing detailed stack traces and errors when exceptions occur.",
    "--showast": "Displays the Abstract Syntax Tree (AST) generated during parsing.",
    "--compile": "Proceeds to compile the program after parsing, generating .vm output.",
    "--help": "Displays the help message for all or specific command-line options.",
}
