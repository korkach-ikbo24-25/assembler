"""Command-line interpreter for the UVM."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .vm import run, dump_memory


def _build_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="uvm-run",
        description="Interpreter for the educational virtual machine.",
    )
    parser.add_argument("binary", type=Path,
                        help="Path to assembled binary program")
    parser.add_argument("dump", type=Path,
                        help="Path to JSON memory dump output")
    parser.add_argument("--start", type=int, default=0,
                        help="Dump start address (inclusive)")
    parser.add_argument("--end", type=int, default=256,
                        help="Dump end address (exclusive)")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point of the interpreter CLI.

    Args:
        argv: Optional list of command-line arguments.

    Returns:
        Process exit code.
    """
    args = _build_parser().parse_args(argv)
    try:
        state = run(args.binary)
        payload = dump_memory(state, args.start, args.end)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    args.dump.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"executed {state.pc} command(s) -> {args.dump}")
    return 0


if __name__ == "__main__":
    sys.exit(main())