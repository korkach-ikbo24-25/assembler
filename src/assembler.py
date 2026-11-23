"""Assembler that translates CSV assembly into an intermediate representation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from .command_spec import OPCODES
from .errors import FieldRangeError, ParseError

COMMENT_PREFIX = "#"
FIELD_SEPARATOR = ","


@dataclass(frozen=True)
class AssembledCommand:
    """Single assembled command in intermediate representation.

    Attributes:
        mnemonic: Source mnemonic, e.g. ``LOAD_CONST``.
        opcode: Numeric opcode of the command.
        fields: Mapping field name -> value in the order required by spec.
        encoded: 32-bit integer with all fields packed.
    """

    mnemonic: str
    opcode: int
    fields: Dict[str, int]
    encoded: int

    def as_test_line(self) -> str:
        """Return a human-readable line like ``A=31, B=3, C=62``."""
        parts = [f"A={self.opcode}"]
        for name, value in self.fields.items():
            parts.append(f"{name}={value}")
        return ", ".join(parts)


def _split_tokens(line: str) -> List[str]:
    """Split a raw source line into stripped tokens, ignoring comments.

    Args:
        line: Raw line from the source file.

    Returns:
        List of non-empty tokens.
    """
    code = line.split(COMMENT_PREFIX, maxsplit=1)[0]
    return [token.strip() for token in code.split(FIELD_SEPARATOR)
            if token.strip()]


def _build_command(mnemonic: str, operands: List[str]) -> AssembledCommand:
    """Build an assembled command from mnemonic and operand strings.

    Args:
        mnemonic: Command mnemonic.
        operands: Operand values as strings.

    Returns:
        Assembled command with packed encoding.

    Raises:
        ParseError: If the mnemonic is unknown or operand count is wrong.
        FieldRangeError: If an operand does not fit into its bit field.
    """
    layout = OPCODES.get(mnemonic)
    if layout is None:
        raise ParseError(f"Unknown mnemonic: {mnemonic}")
    names = list(layout.fields.keys())
    if len(operands) != len(names):
        raise ParseError(
            f"{mnemonic} expects {len(names)} operands, got {len(operands)}"
        )

    values: Dict[str, int] = {}
    encoded = layout.opcode
    for name, raw in zip(names, operands):
        try:
            value = int(raw, 0)
        except ValueError as exc:
            raise ParseError(f"Bad integer '{raw}' in {mnemonic}") from exc
        shift, width = layout.fields[name]
        if not 0 <= value < (1 << width):
            raise FieldRangeError(
                f"{mnemonic}.{name}={value} does not fit into {width} bits"
            )
        values[name] = value
        encoded |= value << shift

    return AssembledCommand(
        mnemonic=mnemonic,
        opcode=layout.opcode,
        fields=values,
        encoded=encoded,
    )


def assemble_source(text: str) -> List[AssembledCommand]:
    """Translate source text into a list of assembled commands.

    Args:
        text: Full text of an assembly file.

    Returns:
        List of assembled commands in source order.
    """
    commands: List[AssembledCommand] = []
    for line_no, raw in enumerate(text.splitlines(), start=1):
        tokens = _split_tokens(raw)
        if not tokens:
            continue
        try:
            commands.append(_build_command(tokens[0].upper(), tokens[1:]))
        except (ParseError, FieldRangeError) as exc:
            raise type(exc)(f"line {line_no}: {exc}") from exc
    return commands


def assemble_file(source_path: Path) -> List[AssembledCommand]:
    """Read assembly file from disk and assemble it.

    Args:
        source_path: Path to CSV assembly file.

    Returns:
        List of assembled commands.
    """
    text = source_path.read_text(encoding="utf-8")
    return assemble_source(text)


def commands_to_bytes(commands: List[AssembledCommand]) -> bytes:
    """Pack assembled commands into a little-endian byte stream.

    Args:
        commands: Assembled commands.

    Returns:
        Bytes ready to be written to the output file.
    """
    from .encoder import encode_program

    return encode_program(commands)