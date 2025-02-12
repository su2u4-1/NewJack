from traceback import format_stack
from typing import Literal, List, Tuple, Union

from compiler.AST import *
from compiler.lib import CompileError, CompileErrorGroup, Info, type_int, type_void, format_traceback, none
from built_in.built_in import built_in_function, built_in_class


class Compiler:
    def __init__(self, global_: List[DeclareVar], errout: List[str], debug_flag: bool = False) -> None:
        self.global_: dict[str, Tuple[Type, int]] = {}
        self.subroutine: dict[str, Tuple[Type, Literal["class", "constructor", "function", "method"]]] = {}
        self.subroutine.update(built_in_function)
        self.attribute: dict[str, dict[str, Tuple[Type, int]]] = {}
        for i in built_in_class:
            self.attribute[i] = {}
        self.argument: dict[str, dict[str, Tuple[Type, int]]] = {}
        self.local: dict[str, dict[str, Tuple[Type, int]]] = {}
        self.err_list: List[CompileError] = []
        self.count: dict[str, int] = {
            "subroutine": 0,
            "global": 0,
            "argument": 0,
            "attribute": 0,
            "local": 0,
            "loop": 0,
            "if": 0,
        }
        self.now_subroutine: Subroutine = Subroutine(none, "method", Type(none), [], [])
        self.loop: List[int] = []
        self.loop_n: List[int] = []
        self.debug_flag = debug_flag
        self.code: List[str] = ["debug-label start"]
        self.errout = errout
        self.now_class: Class = Class(none, [], [], "")
        self.declare(global_)
        if len(self.err_list) > 0:
            raise CompileErrorGroup(self.err_list)
        if self.debug_flag:
            self.showCompilerInfo()
            self.errout.append("code:-------------------------")
            self.errout.append("\n".join(self.code))
            self.errout.append("------------------------------")

    def error(self, text: str, location: Tuple[int, int]) -> None:
        i = CompileError(text, self.now_class.file_path, location, "compiler")
        i.traceback = "Traceback (most recent call last):\n" + "".join(format_stack())
        self.err_list.append(i)

    def addclass(self, c: Class) -> None:
        self.now_class = c
        code: List[str] = []
        self.err_list = []
        try:
            code.append(f"debug-label start {c.file_name}.{c.name}")
            code.extend(self.compileClass(c))
            code.append(f"debug-label end {c.file_name}.{c.name}")
        except Exception as e:
            self.errout.append("------------------------------")
            self.errout.append(format_traceback(e))
            self.errout.append(f"{type(e).__name__}: {e}")
        if len(self.err_list) > 0:
            raise CompileErrorGroup(self.err_list)
        if self.debug_flag:
            self.showCompilerInfo()
            self.errout.append("code:-------------------------")
            self.errout.append("\n".join(code))
            self.errout.append("------------------------------")
        else:
            self.code.extend(code)

    def showCompilerInfo(self) -> None:
        for k, v in self.__dict__.items():
            if k == "errout" or k == "code" or k == "err_list":
                continue
            self.errout.append(f"{k}:" + "-" * (29 - len(k)) + f"\n    {v}")

    def declare(self, vars: Union[List[DeclareVar], DeclareVar]) -> None:
        if isinstance(vars, DeclareVar):
            vars = [vars]
        for var in vars:
            if var.kind in ("class", "constructor", "function", "method"):
                if var.kind == "class":
                    if str(var.name) not in self.attribute:
                        self.count["attribute"] = 0
                        self.attribute[str(var.name)] = {}
                    self.now_class = Class(var.name, [], [], "")
                self.subroutine[str(var.name)] = (var.type, var.kind)
                self.count["subroutine"] += 1
                continue
            elif var.kind == "global":
                t = self.global_
            elif var.kind == "attribute":
                t = self.attribute[str(self.now_class.name)]
            elif var.kind == "argument":
                t = self.argument[str(self.now_subroutine.name)]
            else:
                t = self.local[str(self.now_subroutine.name)]
            t[str(var.name)] = (var.type, self.count[var.kind])
            self.count[var.kind] += 1

    def returncode(self) -> List[str]:
        if self.count["global"] != 0:
            self.code.insert(1, f"push {self.count['global']}")
            self.code.insert(2, f"call built_in.alloc 1")
            self.code.insert(3, "inpv 0")
            self.code.insert(4, "pop @V")
        self.code.append("debug-label end")
        return self.code

    def compileClass(self, class_: Class) -> List[str]:
        code: List[str] = []
        self.now_class = class_
        for i in class_.subroutine_list:
            code.extend(self.compileSubroutine(i))
        return code

    def compileSubroutine(self, subroutine: Subroutine) -> List[str]:
        code: List[str] = []
        self.loop_n.append(0)
        if str(subroutine.name).startswith(str(self.now_class.name) + "."):
            code.append(f"label {subroutine.name}")
        else:
            code.append(f"label {self.now_class.name}.{subroutine.name}")
        self.argument[str(subroutine.name)] = {}
        self.local[str(subroutine.name)] = {}
        self.count["argument"] = 0
        self.count["local"] = 0
        self.now_subroutine = subroutine
        if subroutine.kind != "function":
            self.argument[str(subroutine.name)]["self"] = (Type(self.now_class.name), 0)
            self.count["argument"] += 1
        if subroutine.kind == "constructor":
            code.append(f"push {len(self.attribute[str(self.now_class.name)])}")
            code.append(f"call built_in.alloc 1")
            code.append("pop @L 0")
        self.declare(subroutine.argument_list)
        for i in subroutine.statement_list:
            code.extend(self.compileStatement(i))
        del self.argument[str(subroutine.name)]
        del self.local[str(subroutine.name)]
        self.loop_n.pop()
        return code

    def compileStatement(self, statement: Statement) -> List[str]:
        if isinstance(statement, Var_S):
            return self.compileVar_S(statement)
        elif isinstance(statement, Do_S):
            return self.compileDo_S(statement)
        elif isinstance(statement, Let_S):
            return self.compileLet_S(statement)
        elif isinstance(statement, If_S):
            return self.compileIf_S(statement)
        elif isinstance(statement, While_S):
            return self.compileWhile_S(statement)
        elif isinstance(statement, For_S):
            return self.compileFor_S(statement)
        elif isinstance(statement, Return_S):
            return self.compileReturn_S(statement)
        elif isinstance(statement, Break_S):  # type: ignore
            return self.compileBreak_S(statement)
        else:
            self.error(f"unknown statement", statement.location)
            return []

    def compileVar_S(self, var: Var_S) -> List[str]:
        code: List[str] = []
        if len(var.var_list) < len(var.expression_list):
            self.error("'value' redundant 'variable'", var.location)
        for i, j in zip(var.var_list, var.expression_list):
            code.extend(self.compileExpression(j))
            if i.kind == "global":
                code.append("inpv 0")
                code.append(f"pop @V {self.global_[str(i.name)][1]}")
            elif i.kind == "attribute":
                code.append("push @L 0")
                code.append("pop $D")
                code.append(f"pop @D {self.attribute[str(self.now_class.name)][str(i.name)][1]}")
            else:
                self.declare(i)
                code.append(f"pop @L {self.count["local"] + self.count["argument"] - 1}")
        if len(var.var_list) > len(var.expression_list):
            for i in var.var_list[len(var.expression_list) :]:
                code.append("push 0")
                if i.kind == "global":
                    code.append("inpv 0")
                    code.append(f"pop @V {self.global_[str(i.name)][1]}")
                elif i.kind == "attribute":
                    code.append("push @L 0")
                    code.append("pop $D")
                    code.append(f"pop @D {self.attribute[str(self.now_class.name)][str(i.name)][1]}")
                else:
                    self.declare(i)
                    code.append(f"pop @L {self.count["local"] + self.count["argument"] - 1}")
        return code

    def compileDo_S(self, do: Do_S) -> List[str]:
        result = self.compileCall(do.call)
        result.append("pop $T")
        return result

    def compileLet_S(self, let: Let_S) -> List[str]:
        code: List[str] = []
        code.extend(self.GetVarInfo(let.var, True).code)
        code.extend(self.compileExpression(let.expression))
        code.append("pop $D")
        code.append("pop $T")
        code.append("stor @T $D")
        return code

    def compileIf_S(self, if_: If_S) -> List[str]:
        code: List[str] = []
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

    def compileWhile_S(self, while_: While_S) -> List[str]:
        code: List[str] = []
        n = self.count["loop"]
        self.count["loop"] += 1
        self.loop.append(n)
        self.loop_n[-1] += 1
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
            code.append(f"label while_end_{n}")
            for s in while_.else_statement_list:
                code.extend(self.compileStatement(s))
        code.append(f"label loop_end_{n}")
        self.loop_n[-1] -= 1
        if self.loop.pop() != n:
            self.error("loop level error", while_.location)
        return code

    def compileFor_S(self, for_: For_S) -> List[str]:
        code: List[str] = []
        n = self.count["loop"]
        self.count["loop"] += 1
        self.loop.append(n)
        self.loop_n[-1] += 1
        cn = self.count["local"]
        self.count["local"] += 1
        self.local[str(self.now_subroutine.name)][str(for_.for_count_integer)] = (type_int, cn)
        code.extend(self.compileExpression(for_.for_range[0]))
        code.append(f"pop @L {self.count['argument']+cn}")
        code.append(f"label for_start_{n}")
        for s in for_.statement_list:
            code.extend(self.compileStatement(s))
        code.extend(self.compileExpression(for_.for_range[2]))
        code.append(f"push @L {self.count['argument']+cn}")
        code.append("call built_in.add 2")
        code.append(f"pop @L {self.count['argument']+cn}")
        code.append(f"push @L {self.count['argument']+cn}")
        code.extend(self.compileExpression(for_.for_range[1]))
        code.append(f"call built_in.lt 2")
        code.append(f"goto for_start_{n} true")
        if for_.else_:
            for s in for_.else_statement_list:
                code.extend(self.compileStatement(s))
        code.append(f"label loop_end_{n}")
        self.loop_n[-1] -= 1
        if self.loop.pop() != n:
            self.error("loop level error", for_.location)
        return code

    def compileReturn_S(self, return_: Return_S) -> List[str]:
        code: List[str] = []
        if return_.expression is None:
            if self.now_subroutine.return_type == type_void:
                code.append("push 0")
            else:
                self.error(f"muse be return {self.now_subroutine.return_type}", return_.location)
        else:
            code.extend(self.compileExpression(return_.expression))
        code.append("return")
        return code

    def compileBreak_S(self, break_: Break_S) -> List[str]:
        if self.loop_n[-1] < int(break_.n):
            self.error("The break statement must be inside a loop", break_.location)
            return []
        else:
            return [f"goto loop_end_{self.loop[-int(break_.n)]} all"]

    def compileExpression(self, expression: Expression) -> List[str]:
        code: List[str] = []
        for i in expression.content:
            if isinstance(i, Term):
                code.extend(self.compileTerm(i))
            else:
                code.extend(self.compileOp(i))
        return code

    def compileTerm(self, term: Term) -> List[str]:
        code: List[str] = []
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
            code.extend(self.GetVarInfo(term.content).code)
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

    def compileOp(self, op: Op) -> List[str]:
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

    def compileCall(self, call: Call) -> List[str]:
        code: List[str] = []
        var_info = self.GetVarInfo(call.var)
        if var_info.name == "arr.new":
            for i in call.expression_list:
                code.extend(self.compileExpression(i))
            code.append("call built_in.alloc 1")
        else:
            if var_info.kind == "method":
                code.append("\n".join(var_info.code))
            elif var_info.kind == "constructor":
                code.append("push 0")
            elif var_info.kind != "function":
                self.error(f"variable {call.var} is not method, function or constructor", call.var.location)
            for i in call.expression_list:
                code.extend(self.compileExpression(i))
            if var_info.kind != "function":
                code.append(f"call {var_info.name} {len(call.expression_list) + 1}")
            else:
                code.append(f"call {var_info.name} {len(call.expression_list)}")
        return code

    def GetVarInfo(self, var: Variable, addr: bool = False) -> Info:
        t = ""
        if isinstance(var.var, Identifier):
            var_info = Info()
            var_info.name = str(var.var)
            if str(var.var) == "self" and self.now_subroutine.kind != "function":
                var_info.type = self.argument[str(self.now_subroutine.name)]["self"][0]
                var_info.kind = "argument"
                t = "L 0"
            elif str(var.var) in self.local[str(self.now_subroutine.name)]:
                var_info.type = self.local[str(self.now_subroutine.name)][str(var.var)][0]
                var_info.kind = "local"
                t = f"L {self.count['argument'] + self.local[str(self.now_subroutine.name)][str(var.var)][1]}"
            elif str(var.var) in self.argument[str(self.now_subroutine.name)]:
                var_info.type = self.argument[str(self.now_subroutine.name)][str(var.var)][0]
                var_info.kind = "argument"
                t = f"L {self.argument[str(self.now_subroutine.name)][str(var.var)][1]}"
            elif str(var.var) in self.global_:
                var_info.type = self.global_[str(var.var)][0]
                var_info.kind = "global"
                var_info.code.append("inpv 0")
                t = f"V {self.global_[str(var.var)][1]}"
            elif str(var.var) in self.subroutine:
                var_info.type = Type(Identifier(self.subroutine[str(var.var)][1]))
            else:
                self.error(f"variable {var} not found", var.location)
        else:
            var_info = self.GetVarInfo(var.var, addr)
        if var.attr is not None:
            assert var_info.type.outside.content not in ("constructor", "function", "method")
            if var_info.type.outside == "class":
                if f"{var_info.name}.{var.attr}" in self.subroutine:
                    var_info.type = self.subroutine[f"{var_info.name}.{var.attr}"][0]
                    var_info.kind = self.subroutine[f"{var_info.name}.{var.attr}"][1]
                    var_info.code = []
                else:
                    self.error(f"attribute '{var.attr}' not found in {var_info.name}", var.attr.location)
            elif str(var.attr) in self.attribute[str(var_info.type.outside)]:
                # $L ->       @L    ->    heap obj
                # 255  m[255] = 1023  m[1023] = attr0
                if t != "":
                    var_info.code.append("push @" + t)
                var_info.code.append("pop $D")
                if addr:
                    var_info.code.append(f"push $D {self.attribute[str(var_info.type.outside)][str(var.attr)][1]}")
                else:
                    var_info.code.append(f"push @D {self.attribute[str(var_info.type.outside)][str(var.attr)][1]}")
                var_info.kind = "attribute"
                var_info.type = self.attribute[str(var_info.type.outside)][str(var.attr)][0]
            elif str(var_info.type.outside) + "." + str(var.attr) in self.subroutine:
                var_info.kind = "method"
                var_info.name = str(var_info.type.outside)
                var_info.type = self.subroutine[str(var_info.type.outside) + "." + str(var.attr)][0]
                if t:
                    var_info.code.append("push @" + t)
            else:
                self.error(f"attribute '{var.attr}' not found in {var_info.type.outside}", var.attr.location)
            var_info.name += "." + str(var.attr)
        elif var.index is not None:
            if t != "":
                var_info.code.append("push $" + t)
            if var_info.type.inside is not None:
                var_info.type = var_info.type.inside
                var_info.code.extend(self.compileExpression(var.index))
                var_info.code.append("call built_in.add 2")
                if not addr:
                    var_info.code.append("pop $D")
                    var_info.code.append("push @D")
            else:
                self.error(f"variable {var} is not a container", var.index.location)
            var_info.name += f"[{var.index}]"
        else:
            if t != "":
                if addr:
                    var_info.code.append("push $" + t)
                else:
                    var_info.code.append("push @" + t)
        return var_info
