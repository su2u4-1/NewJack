from os.path import isfile, abspath
from sys import argv
from typing import Iterator, List, Optional, Tuple

from compiler.lib import CompileError

label: dict[str, int] = {}
# register to binary
rtob = {"A": "000", "C": "001", "D": "010", "L": "011", "M": "100", "P": "101", "T": "110", "V": "111"}
btor = {"000": "A", "001": "C", "010": "D", "011": "L", "100": "M", "101": "P", "110": "T", "111": "V"}
# C-code to binary
ctob = {"nv": "000", ">": "001", "==": "010", ">=": "011", "<": "100", "!=": "101", "<=": "110", "aw": "111"}
btoc = {"000": "nv", "001": "> ", "010": "==", "011": ">=", "100": "< ", "101": "!=", "110": "<=", "111": "aw"}
# operator to binary
otob = {"add": "000", "sub": "001", "mul": "010", "div": "011", "rmv": "100", "lmv": "101", "and": "110", "or_": "111"}
btoo = {"000": "add", "001": "sub", "010": "mul", "011": "div", "100": "rmv", "101": "lmv", "110": "and", "111": "or_"}


def asmtovm(asm: str, file: str) -> List[str]:
    def getvalue(iterator: Iterator[str], length: int) -> str:
        value = ""
        for _ in range(length):
            value += next(iterator)
        return value

    code: List[str] = []
    a = iter(asm)
    value = ""
    try:
        while True:
            code_type = next(a) + next(a) + next(a)
            if code_type == "000":
                # inpv
                value = getvalue(a, 12)
                if next(a) == "0":
                    code.append(f"inpv {int(value, 2)}")
                else:
                    code.append(f"inpv {value} 1")
            elif code_type == "001":
                # copy
                code.append(f"copy ${btor[getvalue(a, 3)]} ${btor[getvalue(a, 3)]}")
                assert "0000000" == getvalue(a, 7)
            elif code_type == "010":
                # jump
                code.append(f"jump ${btor[getvalue(a, 3)]} ${btor[getvalue(a, 3)]}")
                assert "0000000" == getvalue(a, 7)
            elif code_type == "011":
                # comp
                code.append(f"comp ${btor[getvalue(a, 3)]} {btoc[getvalue(a, 3)]} ${btor[getvalue(a, 3)]}")
                assert "0000" == getvalue(a, 4)
            elif code_type == "100":
                # operator
                code.append(f"{btoo[getvalue(a, 3)]}r ${btor[getvalue(a, 3)]} ${btor[getvalue(a, 3)]} ${btor[getvalue(a, 3)]}")
                assert "0" == next(a)
            elif code_type == "101":
                # exte
                value += getvalue(a, 12)
                code.append(f"exte {value} {next(a)}")
            elif code_type == "110":
                # sett
                code.append(f"sett {str(int(getvalue(a, 3), 2))}")
                assert "0000000000" == getvalue(a, 10)
            else:
                error(f"error: unknown code type '{code_type}'", file, -1)
    except StopIteration:
        return code


def split_newlines(source: List[str]) -> List[str]:
    result: List[str] = []
    for line in source:
        result.extend(line.split("\n"))
    return result


def error(text: str, file: str, line: int) -> None:
    raise CompileError(text, file, (line, 0), "assembler")


def my_bin(n: int, l: Optional[int] = None) -> str:
    neg = n < 0
    n = abs(n)
    result = ""
    while n > 1:
        result = str(n % 2) + result
        n = n // 2
    if n == 1:
        result = "1" + result
    if l is None:
        result = "0" + result
    else:
        if len(result) < l:
            result = "0" * (l - len(result)) + result
        elif len(result) != l:
            raise ValueError("l is too small")
    if neg:
        result = "".join("1" if i == "0" else "0" for i in result)
        result = bin(int(result, 2) + 1)[2:]
    return result


def assembler2(source: List[str], file: str) -> str:
    code = ""
    code_len = 0
    for line, i in enumerate(source):
        i = i.strip()
        if i.startswith("inpv"):
            i = i.split()
            if len(i) == 2:
                if -2048 <= int(i[1]) < 2047:
                    code += f"000{my_bin(int(i[1]), 12)}0"
                    code_len += 2
                else:
                    n = abs(int(i[1])).bit_length() + 1
                    n += 12 - (n % 12)
                    binary = my_bin(int(i[1]), n)
                    code += f"000{binary[:12]}"
                    code_len += 2
                    for j in range(1, len(binary) // 12):
                        code += f"1101{binary[j*12:j*12+12]}"
                        code_len += 2
                    code += "0"
            else:
                error("Unknown format", file, line)
        elif i.startswith("copy"):
            i = i.split()
            if len(i) == 3 and i[1][0] == "$" and i[2][0] == "$":
                code += f"001{rtob[i[1][1]]}{rtob[i[2][1]]}" + "0" * 7
                code_len += 2
            else:
                error("Unknown format", file, line)
        elif i.startswith("jump"):
            i = i.split()
            if len(i) == 3 and i[1][0] == "$" and i[2][0] == "$":
                code += f"010{rtob[i[1][1]]}{rtob[i[2][1]]}" + "0" * 7
                code_len += 2
            else:
                error("Unknown format", file, line)
        elif i.startswith("comp"):
            i = i.split()
            if len(i) == 4 and i[1][0] == "$" and i[3][0] == "$":
                if i[2] in ("nv", ">", "==", ">=", "<", "!=", "<=", "aw"):
                    code += f"011{rtob[i[1][1]]}{ctob[i[2]]}{rtob[i[3][1]]}0000"
                    code_len += 2
                else:
                    error("Unknown C-code", file, line)
            else:
                error("Unknown format", file, line)
        elif i[:3] in ("add", "sub", "mul", "div", "rmv", "lmv", "and", "or_"):
            i = i.split()
            if len(i) == 4 and i[0][3] == "r" and i[1][0] == "$" and i[2][0] == "$" and i[3][0] == "$":
                code += f"100{otob[i[0][:3]]}{rtob[i[1][1]]}{rtob[i[2][1]]}{rtob[i[3][1]]}0"
                code_len += 2
            else:
                error("Unknown format", file, line)
        elif i.startswith("sett"):
            i = i.split()
            if len(i) == 2:
                if 0 <= int(i[1]) <= 7:
                    code += f"110{my_bin(int(i[1]), 3)}0000000000"
                    code_len += 2
                else:
                    error("$T can only be switched in the range of 0~7", file, line)
            else:
                error("Unknown format", file, line)
        elif i.startswith("//setl"):
            i = i.split()
            if len(i) == 2:
                label[i[1]] = code_len
            else:
                error("Unknown format", file, line)
        elif i.startswith("//getl"):
            i = i.split()
            if len(i) == 2:
                code += f"/{i[1]}/"
                code_len += 2
            else:
                error("Unknown format", file, line)
        else:
            error("Unknown command", file, line)
    while "/" in code:
        t = code.split("/", maxsplit=2)
        i = label[t[1]]
        r = ""
        if -2048 <= i < 2047:
            r += f"000{my_bin(i, 12)}0"
        else:
            n = abs(i).bit_length() + 1
            n += 12 - (n % 12)
            binary = my_bin(i, n)
            r += f"000{binary[:12]}"
            for j in range(1, len(binary) // 12):
                r += f"1101{binary[j*12:j*12+12]}"
            r += "0"
        code = t[0] + r + t[2]
    return code


def assembler1(source: List[str], file: str) -> List[str]:
    code: List[str] = []
    for line, i in enumerate(source):
        i = i.strip()
        if i.startswith("setv"):
            i = i.split()
            if len(i) == 3 and i[1][0] == "$":
                code.append(f"inpv {i[2]}\ncopy $V ${i[1][1]}")
            else:
                error("Unknown format", file, line)
        elif i.startswith("load"):
            i = i.split()
            if len(i) == 3 and i[1][0] == "@" and i[2][0] == "$":
                code.append(f"copy ${i[1][1]} $A\ncopy $M ${i[2][1]}")
            else:
                error("Unknown format", file, line)
        elif i.startswith("stor"):
            i = i.split()
            if len(i) == 3 and i[1][0] == "@" and i[2][0] == "$":
                code.append(f"copy ${i[1][1]} $A\ncopy ${i[2][1]} $M")
            else:
                error("Unknown format", file, line)
        elif i[:3] in ("add", "sub", "mul", "div", "rmv", "lmv", "and", "or") and i[3] == "v":
            i = i.split()
            if len(i) == 4 and i[1][0] == "$" and i[3][0] == "$":
                code.append(f"inpv {i[2]}\n{i[0][:3]}r ${i[1][1]} $V ${i[3][1]}")
            else:
                error("Unknown format", file, line)
        elif i.startswith("setl"):
            i = i.split()
            if len(i) == 2:
                code.append(f"//setl {i[1]}")
            else:
                error("Unknown format", file, line)
        elif i.startswith("getl"):
            i = i.split()
            if len(i) == 3 and i[1][0] == "$":
                code.append(f"//getl {i[2]}\ncopy $V ${i[1][1]}")
            else:
                error("Unknown format", file, line)
        else:
            code.append(i)
    return split_newlines(code)


def assembler0(source: List[str], file: str) -> List[str]:
    code: List[str] = []
    for line, i in enumerate(source):
        i = i.strip()
        if i.startswith("//") or i.startswith("debug") or i == "\n" or i == "":
            continue
        elif i.startswith("label"):
            code.append(f"setl {i.split()[1]}")
        elif i.startswith("push"):
            i = i.split()
            if len(i) == 2:
                if i[1][0] == "@":
                    code.append(f"load @{i[1][1]} $D\nstor @P $D\naddv $P 1 $P")
                elif i[1][0] == "$":
                    code.append(f"stor @P ${i[1][1]}\naddv $P 1 $P")
                else:
                    code.append(f"inpv {i[1]}\nstor @P $V\naddv $P 1 $P")
            elif len(i) == 3:
                if i[1][0] == "@":
                    code.append(f"sett 7\naddv ${i[1][1]} {i[2]} $T\nload @T $D\nsett 0\nstor @P $D\naddv $P 1 $P")
                elif i[1][0] == "$":
                    code.append(f"addv ${i[1][1]} {i[2]} $D\nstor @P $D\naddv $P 1 $P")
                else:
                    error("Unknown format", file, line)
            else:
                error("Unknown format", file, line)
        elif i.startswith("pop"):
            i = i.split()
            if len(i) == 2:
                if i[1][0] == "@":
                    code.append(f"subv $P 1 $P\nload @P $D\nstor @{i[1][1]} $D")
                elif i[1][0] == "$":
                    code.append(f"subv $P 1 $P\nload @P $D\ncopy ${i[1][1]} $D")
                else:
                    error("Unknown format", file, line)
            elif len(i) == 3:
                if i[1][0] == "@":
                    code.append(f"subv $P 1 $P\nload @P $D\nsett 7\naddv ${i[1][1]} {i[2]} $T\nstor @T $D\nsett 0")
                else:
                    error("Unknown format", file, line)
        elif i.startswith("goto"):
            i = i.split()
            if len(i) == 3:
                if i[2] == "true":
                    code.append(f"getl $T {i[1]}\nsubv $P 1 $P\nload @P $D\ncopy $C $D\njump $T $C")
                elif i[2] == "false":
                    code.append(f"getl $T {i[1]}\nsubv $P 1 $P\nload @P $D\ncopy $C $D\ninpv 0\ncomp $C == $V\njump $T $C")
                elif i[2] == "all":
                    code.append(f"getl $T {i[1]}\nsetv $C 1\njump $T $C")
                else:
                    error("flag must be 'true', 'false' or 'all'", file, line)
            else:
                error("Unknown format", file, line)
        elif i.startswith("call"):
            i = i.split()
            if len(i) == 3:
                code.append(f"copy $P $T\nsubv $T {i[2]} $T\ngetl $D {i[1]}\nstor @P $D\naddv $P 1 $P\nsubv $L 4 $D\nload @D $D")
                code.append("stor @P $D\naddv $P 1 $P\nsubv $P 2 $D\nstor @P $D\naddv $P 1 $P\nstor @P $L\naddv $P 1 $P\nsett 1")
                code.append("copy $P $T\nsett 0")
                for j in range(int(i[2])):
                    code.append(f"addv $T {j} $D\nload @D $D\nstor @P $D\naddv $P 1 $P")
                code.append(f"sett 1\ncopy $T $L\nsett 0\ngetl $D {i[1]}\ninpv 1\njump $D $V")
            else:
                error("Unknown format", file, line)
        elif i.startswith("return"):
            code.append("subv $P 1 $P")
            code.append("load @P $D")
            code.append("copy $T $D")
            code.append("subv $L 3 $L")
            code.append("load @L $D")
            code.append("addv $L 1 $L")
            code.append("load @L $P")
            code.append("addv $L 1 $L")
            code.append("load @L $L")
            code.append("inpv 1")
            code.append("jump $D $V")
            code.append("stor @P $T")
            code.append("addv $P 1 $P")
        else:
            code.append(i)
    return split_newlines(code)


def preprocess(source: List[str]) -> List[str]:
    code: List[str] = []
    for i in source:
        i = i.strip()
        if i.startswith("call built_in."):
            if i == "call built_in.neg 1":  # -
                code.append("pop $D\ninpv 0\nsubr $V $D $D\npush $D")
            elif i == "call built_in.invert 1":  # !
                code.append("pop $D\ninpv 0\ncomp $V == $D\npush $C")
            elif i == "call built_in.add 2":  # +
                code.append("pop $D\npop $T\naddr $D $T $D\npush $D")
            elif i == "call built_in.sub 2":  # -
                code.append("pop $D\npop $T\nsubr $D $T $D\npush $D")
            elif i == "call built_in.mul 2":  # *
                code.append("pop $D\npop $T\nmulr $D $T $D\npush $D")
            elif i == "call built_in.div 2":  # /
                code.append("pop $D\npop $T\ndivr $D $T $D\npush $D")
            elif i == "call built_in.or 2":  # |
                code.append("pop $D\npop $T\nor_r $D $T $D\npush $D")
            elif i == "call built_in.and 2":  # &
                code.append("pop $D\npop $T\nandr $D $T $D\npush $D")
            elif i == "call built_in.lm 2":  # <<
                code.append("pop $D\npop $T\nlmvr $D $T $D\npush $D")
            elif i == "call built_in.rm 2":  # >>
                code.append("pop $D\npop $T\nrmvr $D $T $D\npush $D")
            elif i == "call built_in.eq 2":  # ==
                code.append("pop $D\npop $T\ncomp $D == $T\npush $C")
            elif i == "call built_in.neq 2":  # !=
                code.append("pop $D\npop $T\ncomp $D != $T\npush $C")
            elif i == "call built_in.geq 2":  # >=
                code.append("pop $D\npop $T\ncomp $D >= $T\npush $C")
            elif i == "call built_in.leq 2":  # <=
                code.append("pop $D\npop $T\ncomp $D <= $T\npush $C")
            elif i == "call built_in.gt 2":  # >
                code.append("pop $D\npop $T\ncomp $D > $T\npush $C")
            elif i == "call built_in.lt 2":  # <
                code.append("pop $D\npop $T\ncomp $D < $T\npush $C")
            elif i == "call built_in.bool 1":  # bool
                code.append("pop $D\ninpv 0\ncomp $D == $V\ncomp $C == $V\npush $C")
        else:
            code.append(i)
    return split_newlines(code)


def main(path: str, flags: List[bool]) -> None:
    code: List[str] = []
    if isfile(path):
        path = abspath(path)
    else:
        print(f"path error: {path}")
        return
    with open(path, "r", encoding="utf-8") as f:
        code = f.readlines()
    file_name = ".".join(path.split(".")[:-1])
    code = preprocess(code)
    try:
        code = assembler0(code, path)
    except CompileError as e:
        print("in assembler0:")
        print(e.show(code[e.line])[0])
        return
    if flags[0]:
        with open(file_name + "_o0.vm", "w", encoding="utf-8") as f:
            f.write("\n".join(code))
    try:
        code = assembler1(code, abspath(file_name + "_o0.vm"))
    except CompileError as e:
        print("in assembler1:")
        print(e.show(code[e.line])[0])
        return
    if flags[1]:
        with open(file_name + "_o1.vm", "w", encoding="utf-8") as f:
            f.write("\n".join(code))
    try:
        asm = assembler2(code, abspath(file_name + "_o1.vm"))
    except CompileError as e:
        print("in assembler2:")
        print(e.show(code[e.line])[0])
        return
    if flags[2]:
        with open(file_name + "_o2.vm", "w", encoding="utf-8") as f:
            f.write("\n".join(asmtovm(asm, file_name + ".asm")))
    with open(file_name + ".asm", "wb") as f:
        f.write(bytes(int(asm[i : i + 8], 2) for i in range(0, len(asm), 8)))


def parser_args(args: List[str]) -> Tuple[str, List[bool]]:
    path = ""
    if len(args) >= 1:
        for i in args:
            if isfile(i):
                path = i
                break
    flags = [False, False, False]
    if "-o0" in args:
        flags[0] = True
    if "-o1" in args:
        flags[1] = True
    if "-o2" in args:
        flags[2] = True
    return path, flags


if __name__ == "__main__":
    if len(argv) <= 1:
        path, flags = parser_args(input("path and flags (only one path):").split())
    else:
        path, flags = parser_args(argv[1:])
    main(path, flags)
