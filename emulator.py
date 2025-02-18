from sys import argv
from typing import List
from os.path import isfile, abspath

import assembler


class VM:
    def __init__(self, size: int) -> None:
        self.size = size
        self.memory = [0] * size
        self.registers = [0] * 8
        # self.registers.__setitem__ = self.setr
        # self.registers.__getitem__ = self.getr
        self.pointer = 0
        self.rT = [0] * 8
        self.temp_value

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
            return self.memory[key]
        elif 0 <= key < 8:
            return self.registers[key]
        else:
            raise Exception("Invalid register")

    def inpv(self, value: int, extended: bool = False) -> None:
        if extended:
            self.temp_value = value
        else:
            self.setr(7, value)

    def copy(self, r0: int, r1: int) -> None:
        self.setr(r1, self.getr(r0))

    def jump(self, r0: int, r1: int) -> None:
        if self.getr(r1) == 0:
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
        if self.getr(ocode) == 0:
            self.setr(r2, self.getr(r0) + self.getr(r1))
        elif self.getr(ocode) == 1:
            self.setr(r2, self.getr(r0) - self.getr(r1))
        elif self.getr(ocode) == 2:
            self.setr(r2, self.getr(r0) * self.getr(r1))
        elif self.getr(ocode) == 3:
            self.setr(r2, self.getr(r0) // self.getr(r1))
        elif self.getr(ocode) == 4:
            self.setr(r2, self.getr(r0) >> self.getr(r1))
        elif self.getr(ocode) == 5:
            self.setr(r2, self.getr(r0) << self.getr(r1))
        elif self.getr(ocode) == 6:
            self.setr(r2, self.getr(r0) & self.getr(r1))
        elif self.getr(ocode) == 7:
            self.setr(r2, self.getr(r0) | self.getr(r1))
        else:
            raise Exception("Invalid operation code")

    def exte(self, value: int, extended: bool) -> None:
        value = int(str(self.temp_value) + str(value))
        if extended:
            self.temp_value = value
        else:
            self.setr(7, value)

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


def main(args: Args) -> None:
    if args.path.endswith(".vm"):
        assembler.main(args.path, [False, False, False])
        args.path = args.path.split(".")[-2] + ".asm"
    with open(args.path, "rb") as f:
        data = f.read()
    print(type(data))
    for i in data:
        print(bin(i)[2:].zfill(8), end=" ")


if __name__ == "__main__":
    if len(argv) > 1:
        args = parser_args(argv[1:])
    else:
        args = parser_args(input("path & args: ").split())
    main(args)
