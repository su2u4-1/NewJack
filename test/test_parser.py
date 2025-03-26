import unittest
from njc.parser import Parser
from njc.lib import Token, ASTNode, source, CompileError


class TestParser(unittest.TestCase):
    def setUp(self):
        # 初始化測試用的 source code
        self.file = "test_file.nj"
        source[self.file] = [
            "var int a = 10;",
            "function int main() {",
            "    return a;",
            "}",
        ]
        self.tokens = [
            Token("keyword", "var", self.file, (1, 0)),
            Token("keyword", "int", self.file, (1, 4)),
            Token("identifier", "a", self.file, (1, 8)),
            Token("symbol", "=", self.file, (1, 10)),
            Token("int", "10", self.file, (1, 12)),
            Token("symbol", ";", self.file, (1, 14)),
            Token("keyword", "function", self.file, (2, 0)),
            Token("keyword", "int", self.file, (2, 9)),
            Token("identifier", "main", self.file, (2, 13)),
            Token("symbol", "(", self.file, (2, 17)),
            Token("symbol", ")", self.file, (2, 18)),
            Token("symbol", "{", self.file, (2, 20)),
            Token("keyword", "return", self.file, (3, 4)),
            Token("identifier", "a", self.file, (3, 11)),
            Token("symbol", ";", self.file, (3, 12)),
            Token("symbol", "}", self.file, (4, 0)),
        ]

    def test_parse_variable_declaration(self):
        parser = Parser(self.tokens, self.file)
        ast = parser.parse()
        expected_ast = ASTNode(
            "root",
            [
                ASTNode(
                    "var",
                    var_type=ASTNode("type", type_a="int", type_b=[]),
                    var_kind="var",
                    name="a",
                    expression=ASTNode("expression", [ASTNode("term", ASTNode("int", "10"))]),
                )
            ],
            file=self.file,
        )
        assert isinstance(ast.args["value"], list)
        assert len(ast.args["value"]) > 0
        assert isinstance(ast.args["value"][0], ASTNode)
        self.assertEqual(ast.args["value"][0], expected_ast)

    def test_parse_function(self):
        parser = Parser(self.tokens, self.file)
        ast = parser.parse()
        expected_ast = ASTNode(
            "root",
            [
                ASTNode(
                    "var",
                    var_type=ASTNode("type", type_a="int", type_b=[]),
                    var_kind="var",
                    name="a",
                    expression=ASTNode("expression", [ASTNode("term", ASTNode("int", "10"))]),
                ),
                ASTNode(
                    "function",
                    constant=False,
                    func_type=ASTNode("type", type_a="int", type_b=[]),
                    type_var=[],
                    name="main",
                    args=[],
                    body=[
                        ASTNode(
                            "return",
                            ASTNode("expression", [ASTNode("term", ASTNode("variable", "a"))]),
                        )
                    ],
                ),
            ],
            file=self.file,
        )
        assert isinstance(ast.args["value"], list)
        assert len(ast.args["value"]) > 1
        assert isinstance(ast.args["value"][0], ASTNode)
        self.assertEqual(ast.args["value"][1], expected_ast)

    def test_invalid_syntax(self):
        source[self.file] = ["var int = ;"]
        tokens = [
            Token("keyword", "var", self.file, (1, 0)),
            Token("keyword", "int", self.file, (1, 4)),
            Token("symbol", "=", self.file, (1, 8)),
            Token("symbol", ";", self.file, (1, 10)),
        ]
        parser = Parser(tokens, self.file)
        with self.assertRaises(CompileError) as context:
            parser.parse()
        self.assertIn("Expected identifier after variable type", str(context.exception))


if __name__ == "__main__":
    unittest.main()
