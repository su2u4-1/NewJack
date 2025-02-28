from sys import argv
from typing import Dict, List
from os.path import isfile, abspath

import assembler


class VM:
    def __init__(self, size: int) -> None:
        self.size = size
        self.memory: Dict[int, int] = {}
        self.registers = [0] * 8
        self.pointer = 0
        self.rT = [0] * 8
        self.temp_value = ""

    def setr(self, key: int, value: int) -> None:
        while value >= 2147483648:
            value -= 4294967296
        while value < -2147483648:
            value += 4294967296
        if key == 4:
            self.memory[self.registers[0]] = value
        elif key == 6:
            self.rT[self.registers[6]] = value
        elif 0 <= key < 8:
            self.registers[key] = value
        else:
            raise Exception("Invalid register")

    def getr(self, key: int) -> int:
        if key == 4:
            if key not in self.memory:
                self.memory[key] = 0
            return self.memory[key]
        elif key == 6:
            return self.rT[self.registers[6]]
        elif 0 <= key < 8:
            return self.registers[key]
        else:
            raise Exception("Invalid register")

    def inpv(self, value: str, extended: bool = False) -> None:
        if extended:
            self.temp_value = value
        else:
            self.setr(7, int(value, 2))
        # print(value, int(value, 2), extended)

    def copy(self, r0: int, r1: int) -> None:
        self.setr(r1, self.getr(r0))

    def jump(self, r0: int, r1: int) -> None:
        if self.getr(r1) != 0:
            self.pointer = self.getr(r0)

    def comp(self, r0: int, ccode: int, r1: int) -> None:
        if ccode < 0 or ccode > 7:
            raise Exception("Invalid comparison code")
        if ccode == 1 and self.getr(r0) > self.getr(r1):
            self.setr(1, 1)
        elif ccode == 2 and self.getr(r0) == self.getr(r1):
            self.setr(1, 1)
        elif ccode == 3 and self.getr(r0) >= self.getr(r1):
            self.setr(1, 1)
        elif ccode == 4 and self.getr(r0) < self.getr(r1):
            self.setr(1, 1)
        elif ccode == 5 and self.getr(r0) != self.getr(r1):
            self.setr(1, 1)
        elif ccode == 6 and self.getr(r0) <= self.getr(r1):
            self.setr(1, 1)
        elif ccode == 7:
            self.setr(1, 1)
        else:
            self.setr(1, 0)

    def operation(self, ocode: int, r0: int, r1: int, r2: int) -> None:
        if ocode == 0:
            self.setr(r2, self.getr(r0) + self.getr(r1))
        elif ocode == 1:
            self.setr(r2, self.getr(r0) - self.getr(r1))
        elif ocode == 2:
            self.setr(r2, self.getr(r0) * self.getr(r1))
        elif ocode == 3:
            try:
                self.setr(r2, self.getr(r0) // self.getr(r1))
            except ZeroDivisionError as e:
                print(e, e.__traceback__)
                self.setr(r2, 0)
        elif ocode == 4:
            self.setr(r2, self.getr(r0) >> self.getr(r1))
        elif ocode == 5:
            self.setr(r2, self.getr(r0) << self.getr(r1))
        elif ocode == 6:
            self.setr(r2, self.getr(r0) & self.getr(r1))
        elif ocode == 7:
            self.setr(r2, self.getr(r0) | self.getr(r1))
        else:
            raise Exception(f"Invalid operation code: {ocode}")

    def exte(self, value: str, extended: bool) -> None:
        value = self.temp_value + value
        if extended:
            self.temp_value = value
        else:
            self.setr(7, int(value, 2))
        # print(value, int(value, 2), extended)

    def sett(self, value: int) -> None:
        if 0 <= value < 8:
            self.registers[6] = value
        else:
            raise Exception("Invalid register code")


class Args:
    def __init__(self, path: str = "") -> None:
        self.path = path


def parser_args(args: List[str]) -> Args:
    path = ""
    for i in args:
        if path == "" and isfile(i) and (i.endswith(".asm") or i.endswith(".vm")):
            path = abspath(i)
    if path == "":
        raise Exception("Need to pass in an .asm file")
    return Args(path)


def get_command(data: bytes, pointer: int) -> str:
    return bin(data[pointer])[2:].zfill(8) + bin(data[pointer + 1])[2:].zfill(8)


def main(args: Args) -> None:
    # s: dict[int, str] = {}  ##
    # i = 1  ##
    if args.path.endswith(".vm"):
        assembler.main(args.path, [False, False, False])
        args.path = args.path.split(".")[-2] + ".asm"
    with open(args.path, "rb") as f:
        data = f.read()
    vm = VM(4294967296)
    while vm.pointer < len(data):
        c = get_command(data, vm.pointer)
        if c[:3] == "000":
            vm.inpv(c[3:15], True if c[15] == "1" else False)
            vm.pointer += 2
        elif c[:3] == "001":
            vm.copy(int(c[3:6], 2), int(c[6:9], 2))
            vm.pointer += 2
        elif c[:3] == "010":
            vm.jump(int(c[3:6], 2), int(c[6:9], 2))
            vm.pointer += 2
        elif c[:3] == "011":
            vm.comp(int(c[3:6], 2), int(c[6:9], 2), int(c[9:12], 2))
            vm.pointer += 2
        elif c[:3] == "100":
            vm.operation(int(c[3:6], 2), int(c[6:9], 2), int(c[9:12], 2), int(c[12:15], 2))
            vm.pointer += 2
        elif c[:3] == "101":
            vm.exte(c[3:15], True if c[15] == "1" else False)
            # i -= 1  ##
            vm.pointer += 2
        elif c[:3] == "110":
            vm.sett(int(c[3:6], 2))
            vm.pointer += 2
        else:
            print(vm.registers)
            print(vm.rT)
            raise Exception(f"Invalid command {c} in {args.path} {vm.pointer}")
        # if vm.pointer in s:  ##
        #     break  ##
        # s[vm.pointer] = c  ##
        # print(i, vm.pointer, c, vm.registers)  ##
        # i += 1  ##
        # if vm.pointer == 6886:  ##
        #     break  ##
    print(vm.memory)
    # print(len(s))  ##
    # for j, i in enumerate(s):  ##
    #     print(j + 1, i, s[i])  ##
    print(vm.registers)
    print(vm.rT)
    print(vm.pointer)


if __name__ == "__main__":
    if len(argv) > 1:
        args = parser_args(argv[1:])
    else:
        args = parser_args(input("path & args: ").split())
    main(args)
