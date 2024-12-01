from traceback import format_stack

from AST import *
from lib import CompileError, CompileErrorGroup, Info, type_class, type_subroutine, type_int, type_void, type_argument


class Compiler:
    def __init__(self, ast: Root, debug_flag: bool = False) -> None:
        self.ast = ast
        self.global_: dict[str, tuple[Type, int]] = {}
        self.attribute: dict[str, dict[str, tuple[Type, int]]] = {}
        self.argument: dict[str, tuple[Type, int]] = {}
        self.local: dict[str, tuple[Type, int]] = {}
        self.err_list: list[CompileError] = []
        self.count: dict[str, int] = {
            "global": 0,
            "argument": 0,
            "attribute": 0,
            "local": 0,
            "subroutine": 0,
            "class": 0,
            "loop": 0,
            "if": 0,
        }
        none = Identifier((-1, -1), "None")
        self.now_class: Class = Class((-1, -1), none, [], [])
        self.now_subroutine: Subroutine = Subroutine((-1, -1), none, "method", Type((-1, -1), none), [], [])
        self.loop: list[int] = []
        self.debug_flag = debug_flag

    def error(self, text: str, location: tuple[int, int]) -> None:
        i = CompileError(text, self.ast.file, location, "compiler")
        i.traceback = "Traceback (most recent call last):\n" + "".join(format_stack())
        self.err_list.append(i)

    def main(self) -> list[str]:
        try:
            code: list[str] = ["label start"]
            for i, c in enumerate(self.ast.class_list):
                self.count["attribute"] = 0
                self.attribute[c.name.content] = {}
                self.global_[c.name.content] = (type_class, i)
                for a in c.attr_list:
                    self.attribute[c.name.content][a[0]] = (a[1], self.count["attribute"])
                    self.count["attribute"] += 1
                for s in c.subroutine_list:
                    self.global_[f"{c.name.content}.{s.name.content}"] = (type_subroutine[s.kind], self.count["subroutine"])
                    self.count["subroutine"] += 1
            for i in self.ast.class_list:
                code.extend(self.compileClass(i))
        except Exception as e:
            if self.debug_flag:
                self.printinfo()
            raise e
        if len(self.err_list) > 0:
            raise CompileErrorGroup(self.err_list)
        if self.debug_flag:
            self.printinfo()
            exit()
        return code

    def printinfo(self) -> None:
        print("-------------")
        for k, v in self.__dict__.items():
            print(f"{k}:\n{v}\n-------------")

    def compileClass(self, class_: Class) -> list[str]:
        code: list[str] = [f"label {self.ast.name}.{class_.name}"]
        self.now_class = class_
        for i in class_.subroutine_list:
            code.extend(self.compileSubroutine(i))
        code.insert(1, f"alloc heap {self.count["global"]}")
        return code

    def compileSubroutine(self, subroutine: Subroutine) -> list[str]:
        code: list[str] = [f"label {self.ast.name}.{subroutine.name}"]
        self.now_subroutine = subroutine
        self.local = {}
        if subroutine.kind == "method":
            self.argument["self"] = (type_argument, 0)
            self.count["argument"] += 1
        elif subroutine.kind == "constructor":
            n = 0
            for i in subroutine.statement_list:
                if isinstance(i, Var_S):
                    n += len(i.var_list)
            code.append(f"alloc heap {n}")
            code.append("pop term 1")
        for i in subroutine.argument_list:
            self.compileVariable(i)
        for i in subroutine.statement_list:
            code.extend(self.compileStatement(i))
        if subroutine.kind == "constructor":
            code.extend(f"alloc {len(self.attribute[self.now_class.name.content])}")
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
            t = self.compileVariable(i)
            code.extend(self.compileExpression(j))
            code.append(f"pop {i.kind} {t}")
            self.count[i.kind] += 1
        if len(var.var_list) > len(var.expression_list):
            for i in var.var_list[len(var.expression_list) :]:
                if i.kind == "global":
                    self.global_[i.name.content] = (i.type, self.count[i.kind])
                elif i.kind == "attribute":
                    self.attribute[self.now_class.name.content][i.name.content] = (i.type, self.count[i.kind])
                elif i.kind == "argument":
                    self.argument[i.name.content] = (i.type, self.count[i.kind])
                else:
                    self.local[i.name.content] = (i.type, self.count[i.kind])
                code.append("push constant 0")
                code.append(f"pop {i.kind} {self.count[i.kind]}")
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
        code.append("pop term 0")
        code.append("pop address 0")
        code.append("push term 0")
        code.append("pop memory 0")
        return code

    def compileIf_S(self, if_: If_S) -> list[str]:
        code: list[str] = []
        n = self.count["if"]
        self.count["if"] += 1
        code.extend(self.compileExpression(if_.if_conditional))
        code.append(f"goto if_false_{n} false")
        for s in if_.if_statement_list:
            code.extend(self.compileStatement(s))
        code.append(f"goto if_end_{n} all")
        code.append(f"label if_false_{n}")
        for i in range(if_.elif_n):
            code.extend(self.compileExpression(if_.elif_conditional_list[i]))
            code.append(f"goto elif_{i}_{n} false")
            for s in if_.elif_statement_list[i]:
                code.extend(self.compileStatement(s))
            code.append(f"goto if_end_{n} all")
            code.append(f"label elif_{i}_{n}")
        if if_.else_:
            for s in if_.else_statement_list:
                code.extend(self.compileStatement(s))
        code.append(f"label if_end_{n}")
        return code

    def compileWhile_S(self, while_: While_S) -> list[str]:
        code: list[str] = []
        n = self.count["loop"]
        self.count["loop"] += 1
        self.loop.append(n)
        code.append(f"label while_start_{n}")
        code.extend(self.compileExpression(while_.conditional))
        if while_.else_:
            code.append(f"goto while_end_{n} false")
        else:
            code.append(f"goto loop_end_{n} false")
        for s in while_.statement_list:
            code.extend(self.compileStatement(s))
        code.append(f"goto while_start_{n} all")
        if while_.else_:
            code.append(f"lable while_end_{n}")
            for s in while_.else_statement_list:
                code.extend(self.compileStatement(s))
        code.append(f"label loop_end_{n}")
        if self.loop.pop() != n:
            self.error("loop level error", while_.location)
        return code

    def compileFor_S(self, for_: For_S) -> list[str]:
        code: list[str] = []
        n = self.count["loop"]
        self.count["loop"] += 1
        self.loop.append(n)
        cn = self.count["local"]
        self.count["local"] += 1
        self.local[for_.for_count_integer.content] = (type_int, cn)
        code.extend(self.compileExpression(for_.for_range[0]))
        code.append(f"push local {cn}")
        code.append("pop address 0")
        code.append("pop memory 0")
        code.append(f"label for_start_{n}")
        for s in for_.statement_list:
            code.extend(self.compileStatement(s))
        code.extend(self.compileExpression(for_.for_range[2]))
        code.append(f"push local {cn}")
        code.append("pop address 0")
        code.append("push memory 0")
        code.append("add")
        code.append("pop memory 0")
        code.extend(self.compileExpression(for_.for_range[1]))
        code.append(f"goto for_start_{n} true")
        if for_.else_:
            for s in for_.else_statement_list:
                code.extend(self.compileStatement(s))
        code.append(f"label loop_end_{n}")
        if self.loop.pop() != n:
            self.error("loop level error", for_.location)
        return code

    def compileReturn_S(self, return_: Return_S) -> list[str]:
        code: list[str] = []
        if return_.expression is None:
            if self.now_subroutine.return_type == type_void:
                code.append("push constant 0")
            else:
                self.error(f"muse be return {self.now_subroutine.return_type}", return_.location)
        else:
            code.extend(self.compileExpression(return_.expression))
        code.append("return")
        return code

    def compileBreak_S(self, break_: Break_S) -> list[str]:
        if len(self.loop) < break_.n.content:
            self.error("The break statement must be inside a loop", break_.location)
            return []
        else:
            self.loop = self.loop[: -break_.n.content]
            return [f"goto loop_end_{self.loop[-break_.n.content]} all"]

    def compileVariable(self, var: Variable) -> int:
        if var.kind == "global":
            self.global_[var.name.content] = (var.type, self.count[var.kind])
        elif var.kind == "attribute":
            self.attribute[self.now_class.name.content][var.name.content] = (var.type, self.count[var.kind])
        elif var.kind == "argument":
            self.argument[var.name.content] = (var.type, self.count[var.kind])
        else:
            self.local[var.name.content] = (var.type, self.count[var.kind])
        t = self.count[var.kind]
        self.count[var.kind] += 1
        return t

    def compileExpression(self, expression: Expression) -> list[str]:
        code: list[str] = []
        for i in expression.content:
            if isinstance(i, Term):
                code.extend(self.compileTerm(i))
            else:
                code.extend(self.compileOp(i))
        return code

    def compileTerm(self, term: Term) -> list[str]:
        code: list[str] = []
        if isinstance(term.content, Integer):
            code.append(f"push constant {term.content.content}")
        elif isinstance(term.content, Float):
            code.append(f"push constant {term.content.a}")
            code.append(f"push constant {term.content.b}")
            code.append("call built_in.float 2")
        elif isinstance(term.content, Char):
            code.append(f"push constant {ord(term.content.content)}")
            code.append("call built_in.char 1")
        elif isinstance(term.content, String):
            for i in term.content.content:
                code.append(f"push constant {ord(i)}")
            code.append(f"call built_in.string {len(term.content.content)}")
        elif isinstance(term.content, Call):
            code.extend(self.compileCall(term.content))
        elif isinstance(term.content, GetVariable):
            code.extend(self.compileGetVariable(term.content))
        elif isinstance(term.content, Expression):
            code.extend(self.compileExpression(term.content))
        elif isinstance(term.content, Term):
            code.extend(self.compileTerm(term.content))
        else:
            if term.content == "false":
                code.append("push constant 0")
            elif term.content == "true":
                code.append("push constant 1")
            elif term.content == "self":
                if "self" in self.argument:
                    code.append("push argument 0")
                elif self.now_subroutine.kind == "constructor":
                    code.append("push term 1")
                    code.append("pop address 0")
                    code.append("push memory 0")
                else:
                    self.error("self must be in method or constructor", term.location)
            else:
                self.error(f"unknown keyword {term.content}", term.location)
        if term.neg is not None:
            if term.neg == "-":
                code.append("call built_in.neg 1")
            elif term.neg == "!":
                code.append("call built_in.invert 1")
        return code

    def compileOp(self, op: Op) -> list[str]:
        if op.content == "+":
            return ["call built_in.add 2"]
        elif op.content == "-":
            return ["call built_in.sub 2"]
        elif op.content == "*":
            return ["call built_in.mul 2"]
        elif op.content == "/":
            return ["call built_in.div 2"]
        elif op.content == "|":
            return ["call built_in.or 2"]
        elif op.content == "&":
            return ["call built_in.and 2"]
        elif op.content == "<<":
            return ["call built_in.lm 2"]
        elif op.content == ">>":
            return ["call built_in.rm 2"]
        elif op.content == "==":
            return ["call built_in.eq 2"]
        elif op.content == "!=":
            return ["call built_in.neq 2"]
        elif op.content == ">=":
            return ["call built_in.geq 2"]
        elif op.content == "<=":
            return ["call built_in.leq 2"]
        elif op.content == ">":
            return ["call built_in.gt 2"]
        elif op.content == "<":
            return ["call built_in.lt 2"]
        else:
            self.error(f"unknown op {op.content}", op.location)
            return []

    def compileCall(self, call: Call) -> list[str]:
        code: list[str] = []
        # TODO
        var_info = self.GetVarInfo(call.var)
        if var_info.kind == "method":
            code.append("\n".join(var_info.code))
        elif var_info.kind != "function" and var_info.kind != "constructor":
            self.error("variable is not method, function or constructor", call.var.location)
        for i in call.expression_list:
            code.extend(self.compileExpression(i))
        code.append(f"call {var_info.type}.{call.var.attr} {len(call.expression_list)}")
        return code

    def compileGetVariable(self, var: GetVariable) -> list[str]:
        code: list[str] = []
        # TODO: get variable address
        return code

    def GetVarInfo(self, var: GetVariable) -> Info:
        # TODO: add code
        if isinstance(var.var, Identifier):
            var_info = Info()
            var_info.name = var.var.content
            if var.var.content == "self":
                var_info.type = self.argument["self"][0]
                var_info.kind = "argument"
            elif var.var.content in self.local:
                var_info.type = self.local[var.var.content][0]
                var_info.kind = "local"
            elif var.var.content in self.argument:
                var_info.type = self.argument[var.var.content][0]
                var_info.kind = "argument"
            elif var.var.content in self.global_:
                var_info.type = self.global_[var.var.content][0]
                var_info.kind = "global"
            elif self.now_class.name.content + "." + var.var.content in self.global_:
                var_info.type = self.global_[self.now_class.name.content + "." + var.var.content][0]
                var_info.kind = var_info.type.outside.content  # type: ignore
            else:
                self.error(f"variable {var} not found", var.location)
        else:
            var_info = self.GetVarInfo(var.var)
        if var.attr is not None:
            if var.attr.content in self.attribute[var_info.name]:
                var_info.type = self.attribute[var_info.name][var.attr.content][0]
                var_info.kind = "attribute"
            else:
                self.error(f"attribute {var.attr.content} not found in {var_info.type.outside.content}", var.attr.location)
        if var.index is not None:
            if var_info.type.inside is not None:
                var_info.type = var_info.type.inside
            else:
                self.error(f"variable {var} is not a container", var.index.location)
        return var_info
