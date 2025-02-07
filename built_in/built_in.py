from typing import Literal, Tuple
from compiler.lib import type_void, type_str, type_class
from compiler.AST import Identifier, Type

built_in_function: dict[str, Tuple[Type, Literal["class", "constructor", "function", "method"]]] = {
    "list.append": (type_void, "method"),
    "list.new": (Type(Identifier("list")), "constructor"),
    "print": (type_void, "function"),
    "input": (type_str, "function"),
    "str.format": (type_str, "method"),
    "arr.new": (Type(Identifier("arr")), "constructor"),
}

built_in_class = ("list", "str", "int", "float", "bool", "char", "arr")

built_in_njcode = {
    "float": """

""",
    "char": """

""",
    "str": """

""",
    "list": """

""",
}

built_in_vmcode = {"float": [""]}

for i in built_in_class:
    built_in_function[i] = (type_class, "class")
