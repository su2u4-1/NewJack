from typing import Literal, Tuple
from compiler.lib import type_void, type_str
from compiler.AST import Type

built_in_function: dict[str, Tuple[Type, Literal["class", "constructor", "function", "method"]]] = {
    "list.append": (type_void, "method"),
    "print": (type_void, "function"),
    "input": (type_str, "function"),
    "str.format": (type_str, "method"),
}

built_in_class = ["list", "str", "int", "float", "bool"]

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
