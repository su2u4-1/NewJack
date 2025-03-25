from njc.lib import ASTNode

ASTNode(
    "root",
    [
        ASTNode("import", name="list", alias="list"),
        ASTNode("import", name='"<path>/userlib"', alias="userlib"),
        ASTNode(
            "var",
            var_type=ASTNode("type", type_a="int", type_b=[]),
            attr=False,
            constant=False,
            global_=False,
            name="a",
            expression=ASTNode("expression", [ASTNode("term", ASTNode("int", "0"))]),
        ),
        ASTNode(
            "var",
            var_type=ASTNode("type", type_a="int", type_b=[]),
            attr=False,
            constant=True,
            global_=False,
            name="b",
            expression=ASTNode("expression", [ASTNode("term", ASTNode("int", "1"))]),
        ),
        ASTNode(
            "var",
            var_type=ASTNode("type", type_a="int", type_b=[]),
            attr=False,
            constant=False,
            global_=True,
            name="c",
            expression=ASTNode("expression", [ASTNode("term", ASTNode("int", "2"))]),
        ),
        ASTNode(
            "var",
            var_type=ASTNode("type", type_a="int", type_b=[]),
            attr=False,
            constant=True,
            global_=True,
            name="d",
            expression=ASTNode(
                "expression",
                [
                    ASTNode("term", ASTNode("variable", "b")),
                    ASTNode("term", ASTNode("variable", "c")),
                    ASTNode("term", ASTNode("variable", "b")),
                    ASTNode("operator", "*"),
                    ASTNode("operator", "+"),
                    ASTNode("term", ASTNode("variable", "a")),
                    ASTNode("operator", "-"),
                ],
            ),
        ),
        ASTNode(
            "var",
            var_type=ASTNode("type", type_a="pointer", type_b=[ASTNode("type", type_a="int", type_b=[])]),
            attr=False,
            constant=False,
            global_=False,
            name="p",
            expression=ASTNode("expression", [ASTNode("term", ASTNode("pointer", ASTNode("term", ASTNode("variable", "a"))))]),
        ),
        ASTNode(
            "var",
            var_type=ASTNode("type", type_a="type", type_b=[]),
            attr=False,
            constant=False,
            global_=False,
            name="T",
            expression=ASTNode(
                "expression",
                [
                    ASTNode(
                        "term",
                        ASTNode(
                            "call",
                            var=ASTNode("variable", "type"),
                            types=[],
                            args=[
                                ASTNode("expression", [ASTNode("term", ASTNode("variable", "pointer"))]),
                                ASTNode("expression", [ASTNode("term", ASTNode("variable", "int"))]),
                            ],
                        ),
                    )
                ],
            ),
        ),
        ASTNode(
            "var",
            var_type=ASTNode("type", type_a="T", type_b=[]),
            attr=False,
            constant=False,
            global_=False,
            name="p2",
            expression=ASTNode("expression", [ASTNode("term", ASTNode("pointer", ASTNode("term", ASTNode("variable", "b"))))]),
        ),
    ],
    file="D:\\NewJack\\example.nj",
)
