from os.path import isfile, abspath
from sys import argv
from typing import List, Optional

from compiler.lib import CompileError

label: dict[str, int] = {}


def error(text: str, file: str, line: int) -> None:
    raise CompileError(text, file, (line, 0), "compiler")


from typing import Optional


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
    rtob = {"A": "000", "C": "001", "D": "010", "L": "011", "M": "100", "P": "101", "T": "110", "V": "111"}
    code = ""
    for line, i in enumerate(source):
        i = i.strip()
        if i.startswith("inpv"):
            i = i.split()
            if len(i) == 2:
                if -2048 <= int(i[1]) < 2047:
                    code += f"000{my_bin(int(i[1]), 12)}0"
                else:
                    n = abs(int(i[1])).bit_length() + 1
                    n += 12 - (n % 12)
                    binary = my_bin(int(i[1]), n)
                    code += f"000{binary[:12]}"
                    for j in range(1, len(binary) // 12):
                        code += f"1101{binary[j*12:j*12+12]}"
                    code += "0"
        elif i.startswith("copy"):
            i = i.split()
            if len(i) == 3:
                code += f"001{rtob[i[1][1]]}{rtob[i[2][1]]}" + "0" * 7
        elif i.startswith("jump"):
            i = i.split()
            if len(i) == 3:
                code += f"010{rtob[i[1][1]]}{rtob[i[2][1]]}" + "0" * 7
    return code


def assembler1(source: List[str], file: str) -> List[str]:
    code: List[str] = []
    for line, i in enumerate(source):
        i = i.strip()
        if i.startswith("setv"):
            i = i.split()
            if len(i) == 3 and i[1][0] == "$":
                code.append(f"inpv {i[2]}\ncopy $V ${i[1]}")
            else:
                error("Unknown format", file, line)
        elif i.startswith("j-if"):
            i = i.split()
            if len(i) == 5 and i[1][0] == "$" and i[2][0] == "$" and i[4][0] == "$":
                code.append(f"comp ${i[2][1]} {i[3]} ${i[4][1]}\njump ${i[1][1]} $C")
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
        elif i[:3] in ("add", "sub", "mul", "div", "rmv", "lmv", "and", "or_") and i[3] == "v":
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
    return code


def assembler0(source: List[str], file: str) -> List[str]:
    code: List[str] = []
    for line, i in enumerate(source):
        i = i.strip()
        if i.startswith("//") or i.startswith("debug") or i == "\n" or i == "":
            continue
        elif i.startswith("label"):
            code.append(f"setl {i.split()[1]}")
        elif i == "inpv [global abbress]":
            code.append("inpv 0")
        elif i.startswith("push"):
            i = i.split()
            if len(i) == 2:
                if i[1][0] == "@":
                    code.append(f"load @{i[1][1]} $D\nstor @P $D\naddv $P 1 $P")
                elif i[1][0] == "$":
                    code.append(f"stor @P ${i[1][1]}\naddv $P 1 $P")
                else:
                    code.append(f"intv {i[1]}\npush $V")
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
                    code.append(f"subv $P 1 $P\nload @P $D\ncopy @{i[1][1]} $D")
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
                    code.append(f"getl $T {i[1]}\npop $C\njump $T $C")
                elif i[2] == "false":
                    code.append(f"getl $T {i[1]}\npop $C\ninpv 0\ncomp $C == $V\njump $T $C")
                elif i[2] == "all":
                    code.append(f"getl $T {i[1]}\nsetv $C 1\njump $T $C")
                else:
                    error("flag must be 'true', 'false' or 'all'", file, line)
            else:
                error("Unknown format", file, line)
        elif i.startswith("call"):
            i = i.split()
            if len(i) == 3:
                code.append(" ".join(i))
            else:
                error("Unknown format", file, line)
        elif i.startswith("alloc"):
            i = i.split()
            if len(i) == 2:
                code.append(" ".join(i))
            else:
                error("Unknown format", file, line)
        elif i.startswith("return"):
            code.append("return")
        else:
            code.append(i)
    return code


def main(path: str) -> None:
    code: List[str] = []
    if isfile(path):
        path = abspath(path)
    else:
        print(f"path error: {path}")
    with open(path, "r") as f:
        code = f.readlines()
    code = assembler0(code, path)
    with open("o0.vm", "w") as f:
        f.write("\n".join(code))
    code = assembler1(code, abspath("o0.vm"))
    with open("o1.vm", "w") as f:
        f.write("\n".join(code))
    asm = assembler2(code, abspath("o1.vm"))
    with open("o2.vm", "wb") as f:
        f.write(bytes(int(asm[i : i + 8], 2) for i in range(0, len(asm), 8)))


if len(argv) > 1:
    if len(argv) == 2:
        path = argv[1]
        main(path)
    elif len(argv) > 2:
        print(f"path error (only one path): {" ".join(argv[1:])}")
    else:
        print(f"path error: no path")
else:
    main(input("file path: "))
