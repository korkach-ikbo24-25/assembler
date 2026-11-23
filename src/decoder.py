"""Decoder: machine code -> intermediate representation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .command_spec import OPCODES, CommandLayout

COMMAND_SIZE = 4
BYTE_ORDER = "little"
OPCODE_MASK = 0x1F
BY_NAME: Dict[int, str] = {layout.opcode: name for name, layout in OPCODES.items()}


@dataclass(frozen=True)
class DecodedCommand:
    """Decoded command with mnemonic, opcode and field values.

    Attributes:
        mnemonic: Human-readable command mnemonic.
        opcode: Numeric opcode.
        fields: Mapping field name -> integer value.
    """

    mnemonic: str
    opcode: int
    fields: Dict[str, int]


def _extract(word: int, layout: CommandLayout) -> Dict[str, int]:
    """Extract field values from a 32-bit word using layout.

    Args:
        word: 32-bit command word.
        layout: Layout describing fields.

    Returns:
        Mapping field name -> extracted integer.
    """
    values: Dict[str, int] = {}
    for name, (shift, width) in layout.fields.items():
        mask = (1 << width) - 1
        values[name] = (word >> shift) & mask
    return values


def decode_word(word: int) -> DecodedCommand:
    """Decode one 32-bit word into a decoded command.

    Args:
        word: 32-bit command word.

    Returns:
        Decoded command.

    Raises:
        ValueError: If opcode is unknown.
    """
    opcode = word & OPCODE_MASK
    mnemonic = BY_NAME.get(opcode)
    if mnemonic is None:
        raise ValueError(f"Unknown opcode: {opcode}")
    layout = OPCODES[mnemonic]
    return DecodedCommand(mnemonic, opcode, _extract(word, layout))


def decode_bytes(data: bytes) -> List[DecodedCommand]:
    """Decode a binary program into a list of decoded commands.

    Args:
        data: Raw binary program.

    Returns:
        List of decoded commands in program order.

    Raises:
        ValueError: If data length is not a multiple of 4.
    """
    if len(data) % COMMAND_SIZE != 0:
        raise ValueError("Program size must be a multiple of 4 bytes")
    words = [
        int.from_bytes(data[i:i + COMMAND_SIZE], BYTE_ORDER)
        for i in range(0, len(data), COMMAND_SIZE)
    ]
    return [decode_word(word) for word in words]


def load_program(path: Path) -> List[DecodedCommand]:
    """Read binary file and decode it into commands.

    Args:
        path: Path to binary program.

    Returns:
        List of decoded commands.
    """
    return decode_bytes(path.read_bytes())