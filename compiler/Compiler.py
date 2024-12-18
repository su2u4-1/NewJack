from traceback import format_stack

from AST import *
from lib import CompileError, CompileErrorGroup, Info, type_class, type_int, type_void, type_argument, format_traceback, none


class Compiler:
    def __init__(self, global_: Global, errout: list[str], debug_flag: bool = False) -> None:
        # [global, local......]
        self.scope: list[dict[str, tuple[Type, int]]] = [{}]
        self.attribute: dict[str, dict[str, tuple[Type, int]]] = {}
        self.global_ = global_
        self.err_list: list[CompileError] = []
        self.count: dict[str, int] = {
            "global": 0,
            "argument": 0,
            "attribute": 0,
            "local": 0,
            "loop": 0,
            "if": 0,
        }
        self.now_class: Class = Class(none, [], [], "")
        self.now_subroutine: Subroutine = Subroutine(none, "method", Type(none), [], [])
        self.loop: list[int] = []
        self.debug_flag = debug_flag
        self.code: list[str] = ["debug-label start"]
        self.errout = errout
        self.declare(global_.global_variable)

    def error(self, text: str, location: tuple[int, int]) -> None:
        i = CompileError(text, self.now_class.file_path, location, "compiler")
        i.traceback = "Traceback (most recent call last):\n" + "".join(format_stack())
        self.err_list.append(i)

    def addclass(self, c: Class) -> None:
        self.now_class = c
        code: list[str] = []
        try:
            # compile class
            code.append(f"debug-label start {self.now_class.name}.{c.name}")
            code.extend(self.compileClass(c))
            code.append(f"debug-label end {self.now_class.name}.{c.name}")
        # show error info
        except Exception as e:
            self.errout.append("\n------------------------------\n")
            self.errout.append(format_traceback(e))
            self.errout.append(f"{type(e).__name__}: {e}")
        self.errout.append("\n------------------------------\n")
        if len(self.err_list) > 0:
            raise CompileErrorGroup(self.err_list)
        if self.debug_flag:
            self.printinfo(code)
        else:
            self.code.extend(code)

    def declare(self, vars: list[DeclareVar] | DeclareVar) -> None:
        if isinstance(vars, DeclareVar):
            vars = [vars]
        for var in vars:
            if var.kind == "global":
                if var.type == type_class:
                    self.count["attribute"] = 0
                t = self.scope[0]
            elif var.kind == "attribute":
                t = self.attribute[str(self.now_class.name)]
            elif var.kind == "argument":
                t = self.scope[-2]
            else:
                t = self.scope[-1]
            t[str(var.name)] = (var.type, self.count[var.kind])
            self.count[var.kind] += 1

    def returncode(self) -> list[str]:
        self.code.insert(1, f"alloc heap {self.count["global"]}")
        self.code.insert(2, f"pop pointer global")
        self.code.append("debug-label end")
        return self.code

    def printinfo(self, code: list[str]) -> None:
        for k, v in self.__dict__.items():
            self.errout.append(f"{k}:" + "-" * (29 - len(k)) + f"\n    {v}")
        self.errout.append("\ncode:-------------------------\n")
        self.errout.append("\n".join(code))
        self.errout.append("\n------------------------------\n")

    def compileClass(self, class_: Class) -> list[str]:
        code: list[str] = []
        self.now_class = class_
        for i in class_.subroutine_list:
            code.extend(self.compileSubroutine(i))
        return code

    def compileSubroutine(self, subroutine: Subroutine) -> list[str]:
        code: list[str] = [f"label {self.now_class.name}.{subroutine.name}"]
        self.scope.append(dict())
        self.scope.append(dict())
        self.count["argument"] = 0
        self.count["local"] = 0
        self.now_subroutine = subroutine
        if subroutine.kind == "method":
            self.scope[-2]["self"] = (type_argument, 0)
            self.count["argument"] += 1
        elif subroutine.kind == "constructor":
            code.append(f"alloc stack {len(self.attribute[str(self.now_class.name)])}")
            code.append("pop term 1")
        for i in subroutine.argument_list:
            self.declare(i)
        for i in subroutine.statement_list:
            code.extend(self.compileStatement(i))
        self.scope.pop()
        self.scope.pop()
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
        for i in var.var_list:
            assert i.kind == "local"
        if len(var.var_list) < len(var.expression_list):
            self.error("'value' redundant 'variable'", var.location)
        for i, j in zip(var.var_list, var.expression_list):
            self.declare(i)
            t = self.count["local"] + self.count["argument"] - 1
            code.extend(self.compileExpression(j))
            code.append(f"pop @L {t}")
        if len(var.var_list) > len(var.expression_list):
            for i in var.var_list[len(var.expression_list) :]:
                self.declare(i)
                t = self.count["local"] + self.count["argument"] - 1
                code.append("push 0")
                code.append(f"pop @L {t}")
        return code

    def compileDo_S(self, do: Do_S) -> list[str]:
        result = self.compileCall(do.call)
        result.append("pop @T 0")
        return result

    def compileLet_S(self, let: Let_S) -> list[str]:
        code: list[str] = []
        code.extend(self.GetVarAddress(let.var))
        code.extend(self.compileExpression(let.expression))
        code.append("pop $D")
        code.append("pop $T")
        code.append("stor @T $D")
        return code

    def compileIf_S(self, if_: If_S) -> list[str]:
        # TODO: add code
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
        # TODO: add code
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
        # TODO: add code
        code: list[str] = []
        n = self.count["loop"]
        self.count["loop"] += 1
        self.loop.append(n)
        cn = self.count["local"]
        self.count["local"] += 1
        self.scope[-1][str(for_.for_count_integer)] = (type_int, cn)
        code.extend(self.compileExpression(for_.for_range[0]))
        code.append(f"label for_start_{n}")
        for s in for_.statement_list:
            code.extend(self.compileStatement(s))
        code.extend(self.compileExpression(for_.for_range[2]))
        code.append("")
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
                code.append("push 0")
            else:
                self.error(f"muse be return {self.now_subroutine.return_type}", return_.location)
        else:
            code.extend(self.compileExpression(return_.expression))
        code.append("return")
        return code

    def compileBreak_S(self, break_: Break_S) -> list[str]:
        if len(self.loop) < int(break_.n):
            self.error("The break statement must be inside a loop", break_.location)
            return []
        else:
            self.loop = self.loop[: -int(break_.n)]
            return [f"goto loop_end_{self.loop[-int(break_.n)]} all"]

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
            code.append(f"push {term.content}")
        elif isinstance(term.content, Float):
            code.append(f"push {term.content.a}")
            code.append(f"push {term.content.b}")
            code.append("call built_in.float 2")
        elif isinstance(term.content, Char):
            code.append(f"push {ord(term.content.content)}")
            code.append("call built_in.char 1")
        elif isinstance(term.content, String):
            for i in str(term.content):
                code.append(f"push {ord(i)}")
            code.append(f"call built_in.string {len(term.content.content)}")
        elif isinstance(term.content, Call):
            code.extend(self.compileCall(term.content))
        elif isinstance(term.content, Variable):
            code.extend(self.GetVarAddress(term.content))
        elif isinstance(term.content, Expression):
            code.extend(self.compileExpression(term.content))
        elif isinstance(term.content, Term):
            code.extend(self.compileTerm(term.content))
        else:
            if term.content == "false":
                code.append("push 0")
            elif term.content == "true":
                code.append("push 1")
            elif term.content == "self":
                if self.now_subroutine.kind != "function":
                    code.append("push @L 0")
                else:
                    self.error("self must be in method or constructor", term.location)
            else:
                self.error(f"unknown keyword {term}", term.location)
        if term.neg is not None:
            if term.neg == "-":
                code.append("call built_in.neg 1")
            elif term.neg == "!":
                code.append("call built_in.invert 1")
        return code

    def compileOp(self, op: Op) -> list[str]:
        if op == "+":
            return ["call built_in.add 2"]
        elif op == "-":
            return ["call built_in.sub 2"]
        elif op == "*":
            return ["call built_in.mul 2"]
        elif op == "/":
            return ["call built_in.div 2"]
        elif op == "|":
            return ["call built_in.or 2"]
        elif op == "&":
            return ["call built_in.and 2"]
        elif op == "<<":
            return ["call built_in.lm 2"]
        elif op == ">>":
            return ["call built_in.rm 2"]
        elif op == "==":
            return ["call built_in.eq 2"]
        elif op == "!=":
            return ["call built_in.neq 2"]
        elif op == ">=":
            return ["call built_in.geq 2"]
        elif op == "<=":
            return ["call built_in.leq 2"]
        elif op == ">":
            return ["call built_in.gt 2"]
        elif op == "<":
            return ["call built_in.lt 2"]
        else:
            self.error(f"unknown op {op}", op.location)
            return []

    def compileCall(self, call: Call) -> list[str]:
        code: list[str] = []
        var_info = self.GetVarInfo(call.var)
        if var_info.kind == "method":
            code.append("\n".join(var_info.code))
        elif var_info.kind != "function" and var_info.kind != "constructor":
            self.error(f"variable {call.var} is not method, function or constructor", call.var.location)
        for i in call.expression_list:
            code.extend(self.compileExpression(i))
        code.append(f"call {var_info.type}.{call.var.attr} {len(call.expression_list)}")
        return code

    def GetVarAddress(self, var: Variable) -> list[str]:
        # TODO: get variable address
        code: list[str] = ["<compileGetVariable>"]
        return code

    def GetVarInfo(self, var: Variable) -> Info:
        # TODO: add code
        if isinstance(var.var, Identifier):
            var_info = Info()
            var_info.code.append("<GetVarInfo>")
            var_info.name = var.var.content
            if var.var.content == "self":
                var_info.type = self.scope[-2]["self"][0]
                var_info.kind = "argument"
            elif var.var.content in self.scope[-1]:
                var_info.type = self.scope[-1][var.var.content][0]
                var_info.kind = "local"
            elif var.var.content in self.scope[-2]:
                var_info.type = self.scope[-2][var.var.content][0]
                var_info.kind = "argument"
            elif var.var.content in self.scope[0]:
                var_info.type = self.scope[0][var.var.content][0]
                var_info.kind = "global"
            elif self.now_class.name.content + "." + var.var.content in self.scope[0]:
                var_info.type = self.scope[0][self.now_class.name.content + "." + var.var.content][0]
                var_info.kind = var_info.type.outside.content  # type: ignore
            else:
                self.error(f"variable {var} not found", var.location)
        else:
            var_info = self.GetVarInfo(var.var)
        if var.attr is not None:
            if var_info.type.outside == "class":
                if f"{var_info.name}.{var.attr}" in self.scope[0]:
                    var_info.type = Type(Identifier(var_info.name))
                    var_info.kind = self.scope[0][f"{var_info.name}.{var.attr}"][0].outside.content  # type: ignore
                else:
                    self.error(f"attribute {var.attr} not found in {var_info.name}", var.attr.location)
            elif var.attr.content in self.attribute[var_info.type.outside.content]:
                var_info.kind = self.attribute[var_info.type.outside.content][var.attr.content][0].outside.content  # type: ignore
                if var_info.kind != "method":
                    var_info.type = self.attribute[var_info.type.outside.content][var.attr.content][0]
            else:
                self.error(f"attribute {var.attr} not found in {var_info.type.outside}", var.attr.location)
            var_info.name += "." + var.attr.content
        if var.index is not None:
            if var_info.type.inside is not None:
                var_info.type = var_info.type.inside
            else:
                self.error(f"variable {var} is not a container", var.index.location)
            var_info.name += f"[{var.index}]"
        return var_info
