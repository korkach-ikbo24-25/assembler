"""Tests for the UVM interpreter and memory model."""

import unittest

from src.assembler import assemble_source
from src.decoder import decode_bytes
from src.encoder import encode_program
from src.vm import MachineState, run, step


def _state_from_source(text: str) -> MachineState:
    """Assemble text and build initial machine state."""
    program = decode_bytes(encode_program(assemble_source(text)))
    return MachineState(program=program)


class VmTest(unittest.TestCase):
    """Validate load/store operations and the interpretation loop."""

    def test_load_const(self) -> None:
        """LOAD_CONST writes constant into register B."""
        state = _state_from_source("LOAD_CONST, 2, 123")
        step(state)
        self.assertEqual(state.registers[2], 123)

    def test_store_then_load(self) -> None:
        """Store to mem[0] and load back through offset."""
        text = (
            "LOAD_CONST, 0, 0\n"
            "LOAD_CONST, 1, 99\n"
            "STORE_MEM, 1, 0\n"
            "LOAD_CONST, 2, 0\n"
            "LOAD_MEM, 0, 0, 3\n"
        )
        state = _state_from_source(text)
        while step(state):
            pass
        self.assertEqual(state.memory[0], 99)
        self.assertEqual(state.registers[3], 99)

    def test_run_copies_array(self) -> None:
        """Array copy program must duplicate values 0..3 to 8..11."""
        program = [
            # init memory[0..3]
            "LOAD_CONST, 0, 0", "LOAD_CONST, 1, 11", "STORE_MEM, 1, 0",
            "LOAD_CONST, 0, 1", "LOAD_CONST, 1, 22", "STORE_MEM, 1, 0",
            "LOAD_CONST, 0, 2", "LOAD_CONST, 1, 33", "STORE_MEM, 1, 0",
            "LOAD_CONST, 0, 3", "LOAD_CONST, 1, 44", "STORE_MEM, 1, 0",
            # copy 0..3 -> 8..11
            "LOAD_CONST, 0, 0", "LOAD_CONST, 2, 8",
            "LOAD_MEM, 0, 0, 1", "STORE_MEM, 1, 2",
            "LOAD_CONST, 0, 1", "LOAD_CONST, 2, 9",
            "LOAD_MEM, 0, 0, 1", "STORE_MEM, 1, 2",
            "LOAD_CONST, 0, 2", "LOAD_CONST, 2, 10",
            "LOAD_MEM, 0, 0, 1", "STORE_MEM, 1, 2",
            "LOAD_CONST, 0, 3", "LOAD_CONST, 2, 11",
            "LOAD_MEM, 0, 0, 1", "STORE_MEM, 1, 2",
        ]
        state = _state_from_source("\n".join(program))
        while step(state):
            pass
        self.assertEqual(list(state.memory[0:4]), [11, 22, 33, 44])
        self.assertEqual(list(state.memory[8:12]), [11, 22, 33, 44])


if __name__ == "__main__":
    unittest.main()