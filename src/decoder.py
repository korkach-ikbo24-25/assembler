"""Decoder: machine code -> intermediate representation."""

from dataclasses import dataclass
from pathlib import Path

from .command_spec import CommandLayout, opcodes

command_size = 4
byte_order = "little"
opcode_mask = 0x1F
by_name = {layout.opcode: name for name, layout in opcodes.items()}


@dataclass(frozen=True)
class DecodedCommand:
    """Decoded command with mnemonic, opcode and field values.

    Attributes:
        mnemonic: Human-readable mnemonic.
        opcode: Numeric opcode.
        fields: Mapping field name -> value.
    """

    mnemonic: str
    opcode: int
    fields: dict[str, int]


def _extract(word: int, layout: CommandLayout) -> dict[str, int]:
    """Extract field values from a 32-bit word."""
    values: dict[str, int] = {}
    for name, (shift, width) in layout.fields.items():
        mask = (1 << width) - 1
        values[name] = (word >> shift) & mask
    return values


def decode_word(word: int) -> DecodedCommand:
    """Decode one 32-bit word into a decoded command."""
    opcode = word & opcode_mask
    mnemonic = by_name.get(opcode)
    if mnemonic is None:
        raise ValueError(f"Unknown opcode: {opcode}")
    layout = opcodes[mnemonic]
    return DecodedCommand(mnemonic, opcode, _extract(word, layout))


def decode_bytes(data: bytes) -> list[DecodedCommand]:
    """Decode a binary program into decoded commands."""
    if len(data) % command_size != 0:
        raise ValueError("Program size must be a multiple of 4 bytes")
    words = [
        int.from_bytes(data[i:i + command_size], byte_order)
        for i in range(0, len(data), command_size)
    ]
    return [decode_word(word) for word in words]


def load_program(path: Path) -> list[DecodedCommand]:
    """Read a binary file and decode it into commands."""
    return decode_bytes(path.read_bytes())
