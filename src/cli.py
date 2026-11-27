"""Command-line interface for the UVM assembler."""

import argparse
import sys
from pathlib import Path

from .assembler import AssembledCommand, assemble_file
from .encoder import encode_program, format_byte_dump
from .errors import AssemblerError


def _build_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="uvm-asm",
        description="Assembler for the educational virtual machine.",
    )
    parser.add_argument("source", type=Path,
                        help="Path to CSV assembly file")
    parser.add_argument("output", type=Path,
                        help="Path to binary output file")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Print IR and byte dump to stdout",
    )
    return parser


def _print_ir(commands: list[AssembledCommand]) -> None:
    """Print intermediate representation."""
    for index, command in enumerate(commands, start=1):
        print(f"{index:02d}: {command.mnemonic}: {command.as_test_line()}")


def _print_dump(commands: list[AssembledCommand]) -> None:
    """Print machine code as hex byte lines."""
    for index, line in enumerate(format_byte_dump(commands), start=1):
        print(f"{index:02d}: {line}")


def main(argv: list[str] | None = None) -> int:
    """Entry point of the assembler CLI."""
    args = _build_parser().parse_args(argv)
    try:
        commands = assemble_file(args.source)
    except (AssemblerError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.test:
        _print_ir(commands)
        _print_dump(commands)

    args.output.write_bytes(encode_program(commands))
    print(f"assembled {len(commands)} command(s) -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
