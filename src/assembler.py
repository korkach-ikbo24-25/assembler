"""Assembler translating CSV into intermediate representation."""

from dataclasses import dataclass
from pathlib import Path

from .command_spec import opcodes
from .errors import FieldRangeError, ParseError

comment_prefix = "#"
field_separator = ","


@dataclass(frozen=True)
class AssembledCommand:
    """Assembled command in intermediate representation.

    Attributes:
        mnemonic: Source mnemonic.
        opcode: Numeric opcode.
        fields: Mapping field name -> value.
        encoded: 32-bit packed word.
    """

    mnemonic: str
    opcode: int
    fields: dict[str, int]
    encoded: int

    def as_test_line(self) -> str:
        """Return a line like ``A=31, B=3, C=62``."""
        parts = [f"A={self.opcode}"]
        parts.extend(f"{name}={value}"
                     for name, value in self.fields.items())
        return ", ".join(parts)


def _split_tokens(line: str) -> list[str]:
    """Split a raw line into tokens, ignoring comments."""
    code = line.split(comment_prefix, maxsplit=1)[0]
    return [token.strip() for token in code.split(field_separator)
            if token.strip()]


def _parse_field(name: str, raw: str, width: int) -> int:
    """Parse one operand and check its bit width."""
    try:
        value = int(raw, 0)
    except ValueError as exc:
        raise ParseError(f"Bad integer '{raw}'") from exc
    if not 0 <= value < (1 << width):
        raise FieldRangeError(
            f"{name}={value} does not fit into {width} bits"
        )
    return value


def _build_command(mnemonic: str,
                   operands: list[str]) -> AssembledCommand:
    """Build one assembled command from mnemonic and operands."""
    layout = opcodes.get(mnemonic)
    if layout is None:
        raise ParseError(f"Unknown mnemonic: {mnemonic}")
    names = list(layout.fields.keys())
    if len(operands) != len(names):
        raise ParseError(
            f"{mnemonic} expects {len(names)} operands, "
            f"got {len(operands)}"
        )

    values: dict[str, int] = {}
    encoded = layout.opcode
    for name, raw in zip(names, operands):
        shift, width = layout.fields[name]
        value = _parse_field(f"{mnemonic}.{name}", raw, width)
        values[name] = value
        encoded |= value << shift

    return AssembledCommand(
        mnemonic=mnemonic,
        opcode=layout.opcode,
        fields=values,
        encoded=encoded,
    )


def assemble_source(text: str) -> list[AssembledCommand]:
    """Translate source text into a list of assembled commands."""
    commands: list[AssembledCommand] = []
    for line_no, raw in enumerate(text.splitlines(), start=1):
        tokens = _split_tokens(raw)
        if not tokens:
            continue
        try:
            commands.append(_build_command(tokens[0].upper(), tokens[1:]))
        except (ParseError, FieldRangeError) as exc:
            raise type(exc)(f"line {line_no}: {exc}") from exc
    return commands


def assemble_file(source_path: Path) -> list[AssembledCommand]:
    """Read assembly file from disk and assemble it."""
    return assemble_source(source_path.read_text(encoding="utf-8"))


def commands_to_bytes(commands: list[AssembledCommand]) -> bytes:
    """Pack commands into a little-endian byte stream."""
    from .encoder import encode_program

    return encode_program(commands)
