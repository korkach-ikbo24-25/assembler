"""Machine code encoder: intermediate representation -> bytes."""

from typing import Iterable, List

from .assembler import AssembledCommand

COMMAND_SIZE = 4
BYTE_ORDER = "little"


def encode_command(command: AssembledCommand) -> bytes:
    """Encode a single assembled command into 4 machine bytes.

    Args:
        command: Assembled command with packed ``encoded`` field.

    Returns:
        Four bytes in little-endian order.
    """
    return command.encoded.to_bytes(COMMAND_SIZE, byteorder=BYTE_ORDER)


def encode_program(commands: Iterable[AssembledCommand]) -> bytes:
    """Encode a sequence of commands into a contiguous byte stream.

    Args:
        commands: Iterable of assembled commands.

    Returns:
        Bytes of length ``COMMAND_SIZE * number_of_commands``.
    """
    buffer = bytearray()
    for command in commands:
        buffer.extend(encode_command(command))
    return bytes(buffer)


def format_byte_dump(commands: Iterable[AssembledCommand]) -> List[str]:
    """Produce per-command byte dump lines like ``7F 3E 00 00``.

    Args:
        commands: Iterable of assembled commands.

    Returns:
        List of uppercase hex strings, one per command.
    """
    return [
        " ".join(f"{byte:02X}" for byte in encode_command(command))
        for command in commands
    ]