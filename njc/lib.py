symbol = set("()[]{},;.+-*/%<>&|=@^!") | set(("==", "!=", "<=", ">=", "&&", "||", "+=", "-=", "*=", "/=", "%=", "**", "<<", ">>"))
digit = set("0123456789")
atoz = set("abcdefghijklmnopqrstuvwxyz")
AtoZ = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
keyword = set(
    (
        "if",
        "elif",
        "else",
        "for",
        "in",
        "while",
        "return",
        "break",
        "continue",
        "import",
        "constant",
        "global",
        "public",
        "function",
        "method",
        "class",
        "var",
        "int",
        "char",
        "bool",
        "void",
        "str",
        "float",
        "arr",
        "pointer",
        "range",
        "type",
        "tuple",
        "dict",
        "true",
        "false",
        "NULL",
    )
)


class Token:
    def __init__(self, type: str, constant: str, location: tuple[int, int]) -> None:
        self.type = type
        self.constant = constant
        self.location = location
