"""Machine code encoder: IR -> bytes."""

from typing import Iterable

from .assembler import AssembledCommand

command_size = 4
byte_order = "little"


def encode_command(command: AssembledCommand) -> bytes:
    """Encode a single assembled command into 4 bytes."""
    return command.encoded.to_bytes(command_size, byteorder=byte_order)


def encode_program(commands: Iterable[AssembledCommand]) -> bytes:
    """Encode a sequence of commands into a byte stream."""
    buffer = bytearray()
    for command in commands:
        buffer.extend(encode_command(command))
    return bytes(buffer)


def format_byte_dump(commands: Iterable[AssembledCommand]) -> list[str]:
    """Produce per-command hex strings like ``7F 3E 00 00``."""
    return [
        " ".join(f"{byte:02X}" for byte in encode_command(command))
        for command in commands
    ]
