"""Command specification for the educational virtual machine (UVM)."""

from dataclasses import dataclass
from typing import Dict, Tuple

OPCODE_BITS = 5
ADDR_BITS = 3
CONST_BITS = 8
OFFSET_BITS = 13
MEM_OFFSET_BITS = 3

MAX_OPCODE = (1 << OPCODE_BITS) - 1
MAX_ADDR = (1 << ADDR_BITS) - 1
MAX_CONST = (1 << CONST_BITS) - 1
MAX_OFFSET = (1 << OFFSET_BITS) - 1
MAX_MEM_OFFSET = (1 << MEM_OFFSET_BITS) - 1


@dataclass(frozen=True)
class CommandLayout:
    """Layout of a single UVM command in terms of bit fields.

    Attributes:
        opcode: Numeric opcode written into bits 0..4.
        fields: Mapping from field name to (shift, width) tuple.
    """

    opcode: int
    fields: Dict[str, Tuple[int, int]]


LOAD_CONST = CommandLayout(
    opcode=31,
    fields={
        "B": (5, ADDR_BITS),
        "C": (8, CONST_BITS),
    },
)

LOAD_MEM = CommandLayout(
    opcode=18,
    fields={
        "B": (5, MEM_OFFSET_BITS),
        "C": (19, ADDR_BITS),
        "D": (22, ADDR_BITS),
    },
)

STORE_MEM = CommandLayout(
    opcode=1,
    fields={
        "B": (5, ADDR_BITS),
        "C": (8, ADDR_BITS),
    },
)

BITREVERSE = CommandLayout(
    opcode=2,
    fields={
        "B": (5, ADDR_BITS),
        "C": (8, ADDR_BITS),
        "D": (11, OFFSET_BITS),
    },
)

OPCODES: Dict[str, CommandLayout] = {
    "LOAD_CONST": LOAD_CONST,
    "LOAD_MEM": LOAD_MEM,
    "STORE_MEM": STORE_MEM,
    "BITREVERSE": BITREVERSE,
}