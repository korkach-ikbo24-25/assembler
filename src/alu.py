"""Arithmetic-logic unit operations for the UVM."""

WORD_BITS = 8
WORD_MASK = (1 << WORD_BITS) - 1


def bitreverse(value: int) -> int:
    """Reverse bits of an 8-bit word.

    Args:
        value: Integer value (only low 8 bits are used).

    Returns:
        Value with bit order reversed within 8 bits.
    """
    value &= WORD_MASK
    result = 0
    for _ in range(WORD_BITS):
        result = (result << 1) | (value & 1)
        value >>= 1
    return result