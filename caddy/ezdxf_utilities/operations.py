import enum
from typing import Iterable, Iterator, NamedTuple, Tuple

__all__ = ["OpCode", "Operation", "convert_opcodes", "CONVERT"]


class OpCode(enum.Enum):
    replace = enum.auto()
    delete = enum.auto()
    insert = enum.auto()
    equal = enum.auto()


class Operation(NamedTuple):
    opcode: OpCode
    i1: int
    i2: int
    j1: int
    j2: int


def convert_opcodes(
    opcodes: Iterable[Tuple[str, int, int, int, int]]
) -> Iterator[Operation]:
    for tag, i1, i2, j1, j2 in opcodes:
        yield Operation(CONVERT[tag], i1, i2, j1, j2)


CONVERT = {
    "replace": OpCode.replace,
    "delete": OpCode.delete,
    "insert": OpCode.insert,
    "equal": OpCode.equal,
}
