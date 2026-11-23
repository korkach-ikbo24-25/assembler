"""End-to-end tests for stage-5 vector examples."""

import unittest

from src.assembler import assemble_source
from src.alu import bitreverse
from src.decoder import decode_bytes
from src.encoder import encode_program
from src.vm import MachineState, step

from tools.make_examples import EXAMPLES, build_program


def _run_source(text: str) -> MachineState:
    """Assemble, decode and execute a text program."""
    program = decode_bytes(encode_program(assemble_source(text)))
    state = MachineState(program=program)
    while step(state):
        pass
    return state


class VectorExamplesTest(unittest.TestCase):
    """Verify each example reverses its vector in place."""

    def _check(self, values: list[int]) -> None:
        """Run example and compare against expected bitreverse output."""
        state = _run_source("\n".join(build_program(values)))
        expected = [bitreverse(v) for v in values]
        self.assertEqual(list(state.memory[0:6]), expected)

    def test_basic(self) -> None:
        """Mixed values example."""
        self._check(EXAMPLES["vector_basic.csv"])

    def test_zeros(self) -> None:
        """All zeros stay zeros."""
        self._check(EXAMPLES["vector_zeros.csv"])

    def test_ones(self) -> None:
        """All 0xFF stay 0xFF."""
        self._check(EXAMPLES["vector_ones.csv"])


if __name__ == "__main__":
    unittest.main()