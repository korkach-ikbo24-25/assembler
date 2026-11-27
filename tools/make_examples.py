"""Generate example assembly programs for stage 5."""

from pathlib import Path
from typing import Iterable

vector_len = 6
base_addr = 0
reg_src = 0
reg_val = 1
reg_dst = 2
examples_dir = Path("examples")


def _store_cell(addr: int, value: int) -> list[str]:
    """Emit commands writing ``value`` into ``mem[addr]``."""
    return [
        f"LOAD_CONST, 0, {addr}",
        f"LOAD_CONST, 1, {value}",
        "STORE_MEM, 1, 0",
    ]


def _bitreverse_inplace(addr: int) -> list[str]:
    """Emit commands reversing ``mem[addr]`` in place."""
    return [
        f"LOAD_CONST, {reg_src}, {addr}",
        f"LOAD_MEM, 0, {reg_src}, {reg_val}",
        f"LOAD_CONST, {reg_dst}, {addr}",
        f"BITREVERSE, {reg_val}, {reg_dst}, 0",
    ]


def build_program(values: Iterable[int]) -> list[str]:
    """Build a program reversing each vector element in place."""
    values = list(values)
    if len(values) != vector_len:
        raise ValueError(f"Need exactly {vector_len} values")
    lines = [f"# bitreverse in place over {vector_len}-element vector"]
    for offset, value in enumerate(values):
        lines.extend(_store_cell(base_addr + offset, value))
    for offset in range(vector_len):
        lines.extend(_bitreverse_inplace(base_addr + offset))
    return lines


examples = {
    "vector_basic.csv": [176, 15, 129, 1, 2, 3],
    "vector_zeros.csv": [0, 0, 0, 0, 0, 0],
    "vector_ones.csv": [255, 255, 255, 255, 255, 255],
}


def main() -> int:
    """Write all example assembly files to disk."""
    examples_dir.mkdir(exist_ok=True)
    for name, values in examples.items():
        path = examples_dir / name
        text = "\n".join(build_program(values)) + "\n"
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path} ({len(values)} values)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
