from njc.lib import ASTNode

ASTNode(
    "root",
    [
        ASTNode("import", name="list", alias="list"),
        ASTNode("import", name='"<path>/userlib"', alias="userlib"),
        ASTNode(
            "var",
            var_type=ASTNode("type", type_a="int", type_b=[]),
            var_kind="var",
            name="a",
            expression=ASTNode("expression", [ASTNode("term", ASTNode("int", "0"))]),
        ),
        ASTNode(
            "var",
            var_type=ASTNode("type", type_a="int", type_b=[]),
            var_kind="constant",
            name="b",
            expression=ASTNode("expression", [ASTNode("term", ASTNode("int", "1"))]),
        ),
        ASTNode(
            "var",
            var_type=ASTNode("type", type_a="int", type_b=[]),
            var_kind="var global",
            name="c",
            expression=ASTNode("expression", [ASTNode("term", ASTNode("int", "2"))]),
        ),
        ASTNode(
            "var",
            var_type=ASTNode("type", type_a="int", type_b=[]),
            var_kind="constant global",
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
            var_kind="var",
            name="p",
            expression=ASTNode("expression", [ASTNode("term", ASTNode("pointer", ASTNode("term", ASTNode("variable", "a"))))]),
        ),
        ASTNode(
            "var",
            var_type=ASTNode("type", type_a="type", type_b=[]),
            var_kind="var",
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
            var_kind="var",
            name="p2",
            expression=ASTNode("expression", [ASTNode("term", ASTNode("pointer", ASTNode("term", ASTNode("variable", "b"))))]),
        ),
        ASTNode(
            "var",
            var_type=ASTNode("type", type_a="arr", type_b=[ASTNode("type", type_a="T", type_b=[])]),
            var_kind="var",
            name="p_arr",
            expression=ASTNode(
                "expression",
                [
                    ASTNode(
                        "term",
                        ASTNode(
                            "arr",
                            [
                                ASTNode("expression", [ASTNode("term", ASTNode("variable", "p"))]),
                                ASTNode("expression", [ASTNode("term", ASTNode("variable", "p2"))]),
                            ],
                        ),
                    )
                ],
            ),
        ),
        ASTNode(
            "function",
            constant=False,
            func_type=ASTNode("type", type_a="int", type_b=[]),
            type_var=[
                ASTNode(
                    "var",
                    var_type=ASTNode("type", type_a="type", type_b=[]),
                    var_kind="typevar",
                    name="T",
                    expression=ASTNode("None", "None"),
                )
            ],
            name="main",
            args=[
                ASTNode(
                    "var", var_type=ASTNode("type", type_a="T", type_b=[]), var_kind="arg", name="a", expression=ASTNode("None", "None")
                )
            ],
            body=[
                ASTNode(
                    "var",
                    var_type=ASTNode("type", type_a="int", type_b=[]),
                    var_kind="var",
                    name="e",
                    expression=ASTNode("expression", [ASTNode("term", ASTNode("int", "4"))]),
                ),
                ASTNode(
                    "var",
                    var_type=ASTNode("type", type_a="int", type_b=[]),
                    var_kind="constant",
                    name="f",
                    expression=ASTNode("expression", [ASTNode("term", ASTNode("int", "5"))]),
                ),
                ASTNode(
                    "var",
                    var_type=ASTNode("type", type_a="int", type_b=[]),
                    var_kind="var global",
                    name="g",
                    expression=ASTNode("expression", [ASTNode("term", ASTNode("int", "6"))]),
                ),
                ASTNode(
                    "var",
                    var_type=ASTNode("type", type_a="int", type_b=[]),
                    var_kind="constant global",
                    name="h",
                    expression=ASTNode("expression", [ASTNode("term", ASTNode("int", "7"))]),
                ),
                ASTNode(
                    "var",
                    var_type=ASTNode("type", type_a="pointer", type_b=[ASTNode("type", type_a="T", type_b=[])]),
                    var_kind="var",
                    name="p3",
                    expression=ASTNode("expression", [ASTNode("term", ASTNode("pointer", ASTNode("term", ASTNode("variable", "a"))))]),
                ),
                ASTNode("return", ASTNode("expression", [ASTNode("term", ASTNode("int", "0"))])),
            ],
        ),
        ASTNode(
            "class",
        ),
    ],
    file="D:\\NewJack\\example.nj",
)
