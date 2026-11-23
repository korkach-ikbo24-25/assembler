"""Generate example assembly programs for stage 5."""

from pathlib import Path
from typing import Iterable, List

VECTOR_LEN = 6
BASE_ADDR = 0
REG_SRC = 0
REG_VAL = 1
REG_DST = 2
EXAMPLES_DIR = Path("examples")


def _store_cell(addr: int, value: int) -> List[str]:
    """Emit commands writing ``value`` into ``mem[addr]``.

    Args:
        addr: Destination memory address.
        value: Byte value to store.

    Returns:
        Lines of assembly.
    """
    return [
        f"LOAD_CONST, 0, {addr}",
        f"LOAD_CONST, 1, {value}",
        "STORE_MEM, 1, 0",
    ]


def _bitreverse_inplace(addr: int) -> List[str]:
    """Emit commands reversing the byte at ``mem[addr]`` in place.

    Args:
        addr: Address of the byte to reverse.

    Returns:
        Lines of assembly.
    """
    return [
        f"LOAD_CONST, {REG_SRC}, {addr}",
        f"LOAD_MEM, 0, {REG_SRC}, {REG_VAL}",
        f"LOAD_CONST, {REG_DST}, {addr}",
        f"BITREVERSE, {REG_VAL}, {REG_DST}, 0",
    ]


def build_program(values: Iterable[int]) -> List[str]:
    """Build a program that reverses each vector element in place.

    Args:
        values: Six input bytes.

    Returns:
        Assembly lines (header comment included).
    """
    values = list(values)
    if len(values) != VECTOR_LEN:
        raise ValueError(f"Need exactly {VECTOR_LEN} values")
    lines = [f"# bitreverse in place over {VECTOR_LEN}-element vector"]
    for offset, value in enumerate(values):
        lines.extend(_store_cell(BASE_ADDR + offset, value))
    for offset in range(VECTOR_LEN):
        lines.extend(_bitreverse_inplace(BASE_ADDR + offset))
    return lines


EXAMPLES = {
    "vector_basic.csv": [176, 15, 129, 1, 2, 3],
    "vector_zeros.csv": [0, 0, 0, 0, 0, 0],
    "vector_ones.csv": [255, 255, 255, 255, 255, 255],
}


def main() -> int:
    """Write all example assembly files to disk.

    Returns:
        Process exit code.
    """
    EXAMPLES_DIR.mkdir(exist_ok=True)
    for name, values in EXAMPLES.items():
        path = EXAMPLES_DIR / name
        path.write_text("\n".join(build_program(values)) + "\n",
                        encoding="utf-8")
        print(f"wrote {path} ({len(values)} values)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())