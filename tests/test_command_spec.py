"""Tests for command layouts and encodings from the UVM specification."""

import unittest

from src.assembler import assemble_source


class SpecEncodingTest(unittest.TestCase):
    """Check that assembler reproduces spec test byte sequences."""

    def test_load_const(self) -> None:
        """LOAD_CONST(31, B=3, C=62) must produce 7F 3E 00 00."""
        command = assemble_source("LOAD_CONST, 3, 62")[0]
        self.assertEqual(command.opcode, 31)
        self.assertEqual(command.encoded, 0x00003E7F)

    def test_load_mem(self) -> None:
        """LOAD_MEM(18, B=484, C=4, D=0) must produce 92 3C 20 00."""
        command = assemble_source("LOAD_MEM, 484, 4, 0")[0]
        self.assertEqual(command.opcode, 18)
        self.assertEqual(command.encoded, 0x00203C92)

    def test_store_mem(self) -> None:
        """STORE_MEM(1, B=5, C=6) must produce A1 06 00 00."""
        command = assemble_source("STORE_MEM, 5, 6")[0]
        self.assertEqual(command.opcode, 1)
        self.assertEqual(command.encoded, 0x000006A1)

    def test_bitreverse(self) -> None:
        """BITREVERSE(2, B=3, C=5, D=222) must produce 62 F5 06 00."""
        command = assemble_source("BITREVERSE, 3, 5, 222")[0]
        self.assertEqual(command.opcode, 2)
        self.assertEqual(command.encoded, 0x0006F562)


if __name__ == "__main__":
    unittest.main()