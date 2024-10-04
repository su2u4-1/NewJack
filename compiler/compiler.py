from compiler.newjack_ast import *
from compiler.lib import CompileError, CompileErrorGroup


class Compiler:
    def __init__(self, ast: Root) -> None:
        self.ast = ast
        self.scope: dict[str, dict[str, tuple[str, int]]] = {"global": {}, "argument": {}, "attriable": {}}
        self.err_list: list[CompileError] = []
        self.count: dict[str, int] = {"global": 0, "argument": 0, "attriable": 0, "local": 0, "subroutine": 0, "class": 0, "loop": 0}
        self.now: dict[str, str] = {}
        self.obj_attr: dict[str, dict[str, tuple[str, int]]] = {}

    def error(self, text: str, location: tuple[int, int]) -> None:
        self.err_list.append(CompileError(text, self.ast.file, location))

    def main(self) -> list[str]:
        code: list[str] = ["label start"]
        for i in self.ast.class_list:
            code.extend(self.compileClass(i))
        if len(self.err_list) > 0:
            raise CompileErrorGroup(self.err_list)
        return code

    def compileClass(self, class_: Class) -> list[str]:
        code: list[str] = [f"label {self.ast.name}.{class_.name}"]
        n = self.count["class"]
        self.count["class"] += 1
        self.now["class_name"] = class_.name.content
        for i in class_.var_list:
            code.extend(self.compileVar_S(i))
        for i in class_.subroutine_list:
            code.extend(self.compileSubroutine(i))
        code.insert(1, f"alloc heap {self.count["global"]}")
        return code

    def compileSubroutine(self, subroutine: Subroutine) -> list[str]:
        code: list[str] = [f"label {self.ast.name}.{subroutine.name}"]
        n = self.count["subroutine"]
        self.count["subroutine"] += 1
        self.now["subroutine_name"] = subroutine.name.content
        if subroutine.kind == "method":
            self.scope["argument"]["self"] = ("argument", 0)
            self.count["argument"] += 1
        for i in subroutine.argument_list:
            code.extend(self.compileVariable(i))
        for i in subroutine.statement_list:
            code.extend(self.compileStatement(i))
        if subroutine.kind == "constructor":
            code.insert(1, f"alloc heap {self.count["attriable"]}")
            self.obj_attr[self.now["class_name"]] = self.scope["attriable"]
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
            self.error(f"unknown statement", statement.location)
            return []

    def compileVar_S(self, var: Var_S) -> list[str]:
        code: list[str] = []
        if len(var.var_list) < len(var.expression_list):
            self.error("'value' redundant 'variable'", var.location)
        for i, j in zip(var.var_list, var.expression_list):
            code.extend(self.compileExpression(j))
            if i.kind == "global":
                t = "global"
            elif i.kind == "argument":
                t = self.now["class_name"]
            elif i.kind == "attriable":
                t = self.now["class_name"]
            else:
                t = self.now["subroutine_name"]
            code.append(f"pop {i.kind} {self.count[i.kind]}")
            self.scope[t][i.name.content] = (i.type.content, self.count[i.kind])
            self.count[i.kind] += 1
        if len(var.var_list) > len(var.expression_list):
            for i in var.var_list[len(var.expression_list) :]:
                if i.kind == "global":
                    t = "global"
                elif i.kind == "argument":
                    t = self.now["class_name"]
                elif i.kind == "attriable":
                    t = self.now["class_name"]
                else:
                    t = self.now["subroutine_name"]
                if i.type.content in ("int", "bool", "float", "char"):
                    code.append("push constant 0")
                else:
                    code.append(f"call {i.type.content}.init")
                code.append(f"pop {i.kind} {self.count[i.kind]}")
                self.scope[t][i.name.content] = (i.type.content, self.count[i.kind])
                self.count[i.kind] += 1
        return code

    def compileDo_S(self, do: Do_S) -> list[str]:
        result = self.compileCall(do.call)
        result.append("pop term 0")
        return result

    def compileLet_S(self, let: Let_S) -> list[str]:
        code: list[str] = []
        code.extend(self.compileGetVariable(let.var))
        code.extend(self.compileExpression(let.expression))
        code.append("pop term 0\npop address 0\npush term 0\npop memory 0")
        return code

    def compileIf_S(self, if_: If_S) -> list[str]:
        code: list[str] = []
        n = self.count["loop"]
        self.count["loop"] += 1
        code.extend(self.compileExpression(if_.if_conditional))
        code.append(f"goto if_false_{n} false")
        code.extend(self.compileStatement(if_.if_statement_list))
        code.append(f"goto if_end_{n} all")
        code.append(f"label if_false_{n}")
        for i in range(if_.elif_n):
            code.extend(self.compileExpression(if_.elif_conditional_list[i]))
            code.append(f"goto elif_{i}_{n} false")
            code.extend(self.ccompileStatement(if_.elif_statement_list[i]))
            code.append(f"goto if_end_{n} all")
            code.append(f"label elif_{i}_{n}")
        if if_.else_:
            code.extend(self.compileStatement(if_.else_statement))
        code.append(f"label if_end_{n}")
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

    def compileVariable(self, var: Variable) -> list[str]:
        code: list[str] = []
        return code

    def compileExpression(self, expression: Expression) -> list[str]:
        code: list[str] = []
        return code

    def compileCall(self, call: Call) -> list[str]:
        code: list[str] = []
        var_info = self.compileGetVariable(call.var)
        if var_info["kind"] == "method":
            code.append("\n".join(var_info["code"].split("\n")[:-2]))
        elif var_info["kind"] != "function" and var_info["kind"] != "constructor":
            self.error("variable is not method, function or constructor", call.var.location)
        for i in call.expression_list:
            code.extend(self.compileExpression(i))
        code.append(f"call {var_info["type"]}.{var_info["name"]} {len(call.expression_list)}")
        return code

    def compileGetVariable(self, var: GetVariable) -> dict[str, str]:
        var_info = {"kind": "", "type": "", "name": "", "code": ""}
        if isinstance(var.var, Identifier):
            for i in (self.now["subroutine_name"], "argument", "attriable", "global"):
                if var.var.content in self.scope[i]:
                    t = "local" if i == self.now["subroutine_name"] else i
                    var_info["code"] = f"push {t} {self.scope[i][var.var.content][1]}"
                    break
            else:
                self.error("unknown identifier", var.var.location)
        else:
            var_info = self.compileGetVariable(var.var)
        if var.index is not None:
            var_info["code"] += "\n" + "\n".join(self.compileExpression(var.index)) + "\nadd"
        elif var.attr is not None:
            var_info["code"] += f"\n{self.obj_attr[var_info["type"]][var.attr.content][1]}\nadd"
        return var_info
