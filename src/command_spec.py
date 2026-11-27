"""Command specification for the educational virtual machine."""

from dataclasses import dataclass

opcode_bits = 5
addr_bits = 3
const_bits = 8
load_mem_offset_bits = 13
bitreverse_offset_bits = 14


@dataclass(frozen=True)
class CommandLayout:
    """Bit layout of a single command.

    Attributes:
        opcode: Numeric opcode.
        fields: Mapping field name -> (shift, width).
    """

    opcode: int
    fields: dict[str, tuple[int, int]]


load_const = CommandLayout(
    opcode=31,
    fields={
        "B": (5, addr_bits),
        "C": (8, const_bits),
    },
)

load_mem = CommandLayout(
    opcode=18,
    fields={
        "B": (5, load_mem_offset_bits),
        "C": (19, addr_bits),
        "D": (22, addr_bits),
    },
)

store_mem = CommandLayout(
    opcode=1,
    fields={
        "B": (5, addr_bits),
        "C": (8, addr_bits),
    },
)

bitreverse = CommandLayout(
    opcode=2,
    fields={
        "B": (5, addr_bits),
        "C": (8, addr_bits),
        "D": (11, bitreverse_offset_bits),
    },
)

opcodes: dict[str, CommandLayout] = {
    "LOAD_CONST": load_const,
    "LOAD_MEM": load_mem,
    "STORE_MEM": store_mem,
    "BITREVERSE": bitreverse,
}
