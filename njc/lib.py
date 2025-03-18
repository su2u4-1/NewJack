symbol = set("()[]{},;.+-*/%<>&|=@^!") | set(("==", "!=", "<=", ">=", "&&", "||", "+=", "-=", "*=", "/=", "%=", "**", "<<", ">>"))
digit = set("0123456789")
atoz = set("abcdefghijklmnopqrstuvwxyz")
AtoZ = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
keyword = set(
    (
        "arr",
        "as",
        "bool",
        "break",
        "char",
        "class",
        "constant",
        "continue",
        "dict",
        "elif",
        "else",
        "false",
        "float",
        "for",
        "function",
        "global",
        "if",
        "import",
        "in",
        "int",
        "method",
        "NULL",
        "pointer",
        "public",
        "range",
        "return",
        "str",
        "true",
        "tuple",
        "type",
        "var",
        "void",
        "while",
    )
)


class Token:
    def __init__(self, type: str, constant: str, location: tuple[int, int]) -> None:
        self.type = type
        self.constant = constant
        self.location = location

    def __str__(self) -> str:
        return f"<{self.type}> {self.constant} {self.location}"
