import unittest

from njc.lexer import Lexer
from njc.lib import Token, source, CompileError


class TestLexer(unittest.TestCase):
    def setUp(self):
        # 初始化測試用的 source code
        self.file = "test_file.nj"
        source[self.file] = [
            "var int a = 10;",
            "if (a > 5) {",
            '    print("Hello, World!");',
            "}",
        ]

    def test_variable_declaration(self):
        lexer = Lexer(self.file)
        tokens = lexer.lex()
        expected_tokens = [
            Token("keyword", "var", self.file, (1, 0)),
            Token("keyword", "int", self.file, (1, 4)),
            Token("identifier", "a", self.file, (1, 8)),
            Token("symbol", "=", self.file, (1, 10)),
            Token("int", "10", self.file, (1, 12)),
            Token("symbol", ";", self.file, (1, 14)),
        ]
        self.assertEqual(tokens[:6], expected_tokens)

    def test_if_statement(self):
        lexer = Lexer(self.file)
        tokens = lexer.lex()
        expected_tokens = [
            Token("keyword", "if", self.file, (2, 0)),
            Token("symbol", "(", self.file, (2, 3)),
            Token("identifier", "a", self.file, (2, 4)),
            Token("symbol", ">", self.file, (2, 6)),
            Token("int", "5", self.file, (2, 8)),
            Token("symbol", ")", self.file, (2, 9)),
            Token("symbol", "{", self.file, (2, 11)),
        ]
        self.assertEqual(tokens[6:13], expected_tokens)

    def test_print_statement(self):
        lexer = Lexer(self.file)
        tokens = lexer.lex()
        expected_tokens = [
            Token("identifier", "print", self.file, (3, 4)),
            Token("symbol", "(", self.file, (3, 9)),
            Token("string", '"Hello, World!"', self.file, (3, 10)),
            Token("symbol", ")", self.file, (3, 25)),
            Token("symbol", ";", self.file, (3, 26)),
        ]
        self.assertEqual(tokens[13:18], expected_tokens)

    def test_invalid_character(self):
        source[self.file] = ["var int a = @;"]
        lexer = Lexer(self.file)
        with self.assertRaises(CompileError) as context:
            lexer.lex()
        self.assertIn("Invalid character @", str(context.exception))


if __name__ == "__main__":
    unittest.main()
