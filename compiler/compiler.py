from newjack_ast import *
from lib import CompileError


class Compiler:
    def __init__(self, ast: Root) -> None:
        self.ast = ast
        self.scope = {}

    def main(self) -> list[str]:
        code: list[str] = []
        for i in self.ast.class_list:
            code.extend(self.compileClass(i))
        return code

    def compileClass(self, class_: Class) -> list[str]:
        code: list[str] = []
        for i in class_.var_list:
            code.extend(self.compileVar_S(i))
        for i in class_.subroutine_list:
            code.extend(self.compileSubroutine(i))
        return code

    def compileSubroutine(self, subroutine: Subroutine) -> list[str]:
        code: list[str] = []
        for i in subroutine.argument_list:
            code.extend(self.compileVariable(i))
        for i in subroutine.statement_list:
            code.extend(self.compileStatement(i))
        return code

    def compileStatement(self, statement: Statement) -> list[str]:
        if type(statement) == Var_S:
            return self.compileVar_S(statement)
        elif type(statement) == Do_S:
            return self.compileDo_S(statement)
        elif type(statement) == Let_S:
            return self.compileLet_S(statement)
        elif type(statement) == If_S:
            return self.compileIf_S(statement)
        elif type(statement) == While_S:
            return self.compileWhile_S(statement)
        elif type(statement) == Return_S:
            return self.compileReturn_S(statement)
        elif type(statement) == Break_S:
            return self.compileBreak_S(statement)
        else:
            raise CompileError(f"unknown statement {statement}", self.ast.name, (0, 0))

    def compileVar_S(self, var: Var_S) -> list[str]:
        code: list[str] = []

        return code

    def compileVariable(self, var: Variable) -> list[str]:
        code: list[str] = []
        # TODO: add code
        return code

    def compileDo_S(self, do: Do_S) -> list[str]:
        code: list[str] = []
        return code

    def compileLet_S(self, let: Let_S) -> list[str]:
        code: list[str] = []
        return code

    def compileIf_S(self, if_: If_S) -> list[str]:
        code: list[str] = []
        return code

    def compileWhile_S(self, while_: While_S) -> list[str]:
        code: list[str] = []
        return code

    def compileReturn_S(self, return_: Return_S) -> list[str]:
        code: list[str] = []
        return code

    def compileBreak_S(self, break_: Break_S) -> list[str]:
        code: list[str] = []
        return code
