"""Arithmetic-logic unit operations for the UVM."""

word_bits = 8
word_mask = (1 << word_bits) - 1


def bitreverse(value: int) -> int:
    """Reverse bits of an 8-bit word.

    Args:
        value: Integer value; only low 8 bits are used.

    Returns:
        Value with bit order reversed within 8 bits.
    """
    value &= word_mask
    result = 0
    for _ in range(word_bits):
        result = (result << 1) | (value & 1)
        value >>= 1
    return result
