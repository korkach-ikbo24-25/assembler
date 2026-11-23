"""Tests for parsing, comments and validation in the assembler."""

import unittest

from src.assembler import assemble_source, commands_to_bytes
from src.errors import FieldRangeError, ParseError


class ParserTest(unittest.TestCase):
    """Validate parser behaviour on edge cases."""

    def test_comments_and_blank_lines(self) -> None:
        """Comments and empty lines must be ignored."""
        text = "\n# comment\nLOAD_CONST, 1, 2\n"
        self.assertEqual(len(assemble_source(text)), 1)

    def test_unknown_mnemonic(self) -> None:
        """Unknown mnemonic must raise ParseError."""
        with self.assertRaises(ParseError):
            assemble_source("FOO, 1")

    def test_wrong_operand_count(self) -> None:
        """Wrong number of operands must raise ParseError."""
        with self.assertRaises(ParseError):
            assemble_source("LOAD_CONST, 1")

    def test_field_range(self) -> None:
        """Too large field value must raise FieldRangeError."""
        with self.assertRaises(FieldRangeError):
            assemble_source("LOAD_CONST, 8, 62")

    def test_byte_stream(self) -> None:
        """commands_to_bytes must pack commands little-endian."""
        commands = assemble_source("LOAD_CONST, 3, 62")
        self.assertEqual(commands_to_bytes(commands), b"\x7F\x3E\x00\x00")


if __name__ == "__main__":
    unittest.main()