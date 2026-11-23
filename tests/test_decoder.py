"""Tests for decoding machine code back to IR."""

import unittest

from src.assembler import assemble_source
from src.decoder import decode_bytes
from src.encoder import encode_program


class DecoderTest(unittest.TestCase):
    """Round-trip encoder <-> decoder checks."""

    def test_roundtrip_spec(self) -> None:
        """Encode then decode must preserve mnemonic and fields."""
        source = (
            "LOAD_CONST, 3, 62\n"
            "LOAD_MEM, 484, 4, 0\n"
            "STORE_MEM, 5, 6\n"
            "BITREVERSE, 3, 5, 222\n"
        )
        commands = assemble_source(source)
        decoded = decode_bytes(encode_program(commands))
        self.assertEqual(
            [cmd.mnemonic for cmd in decoded],
            [cmd.mnemonic for cmd in commands],
        )
        for original, restored in zip(commands, decoded):
            self.assertEqual(original.fields, restored.fields)

    def test_bad_length(self) -> None:
        """Non-multiple-of-4 input must raise ValueError."""
        with self.assertRaises(ValueError):
            decode_bytes(b"\x00\x01\x02")

    def test_unknown_opcode(self) -> None:
        """Unknown opcode must raise ValueError."""
        with self.assertRaises(ValueError):
            decode_bytes(b"\x1F\x00\x00\x00")


if __name__ == "__main__":
    unittest.main()