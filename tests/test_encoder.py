"""Tests for machine code encoding and byte dump formatting."""

import unittest

from src.assembler import assemble_source
from src.encoder import (
    encode_command,
    encode_program,
    format_byte_dump,
)


class EncoderTest(unittest.TestCase):
    """Validate encoder against UVM specification test vectors."""

    def test_encode_load_const(self) -> None:
        """LOAD_CONST(A=31,B=3,C=62) must encode as 7F 3E 00 00."""
        command = assemble_source("LOAD_CONST, 3, 62")[0]
        self.assertEqual(encode_command(command), b"\x7F\x3E\x00\x00")

    def test_encode_load_mem(self) -> None:
        """LOAD_MEM(A=18,B=484,C=4,D=0) must encode as 92 3C 20 00."""
        command = assemble_source("LOAD_MEM, 484, 4, 0")[0]
        self.assertEqual(encode_command(command), b"\x92\x3C\x20\x00")

    def test_encode_store_mem(self) -> None:
        """STORE_MEM(A=1,B=5,C=6) must encode as A1 06 00 00."""
        command = assemble_source("STORE_MEM, 5, 6")[0]
        self.assertEqual(encode_command(command), b"\xA1\x06\x00\x00")

    def test_encode_bitreverse(self) -> None:
        """BITREVERSE(A=2,B=3,C=5,D=222) must encode as 62 F5 06 00."""
        command = assemble_source("BITREVERSE, 3, 5, 222")[0]
        self.assertEqual(encode_command(command), b"\x62\xF5\x06\x00")

    def test_encode_program_length(self) -> None:
        """Program of N commands must produce 4*N bytes."""
        commands = assemble_source(
            "LOAD_CONST, 1, 1\nSTORE_MEM, 2, 3\n"
        )
        self.assertEqual(len(encode_program(commands)), 8)

    def test_byte_dump_lines(self) -> None:
        """Byte dump must match spec vectors line by line."""
        commands = assemble_source(
            "LOAD_CONST, 3, 62\n"
            "LOAD_MEM, 484, 4, 0\n"
            "STORE_MEM, 5, 6\n"
            "BITREVERSE, 3, 5, 222\n"
        )
        self.assertEqual(
            format_byte_dump(commands),
            [
                "7F 3E 00 00",
                "92 3C 20 00",
                "A1 06 00 00",
                "62 F5 06 00",
            ],
        )


if __name__ == "__main__":
    unittest.main()