"""Virtual machine: memory model and interpretation loop."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .alu import bitreverse
from .decoder import DecodedCommand, load_program

memory_size = 256
word_bits = 8
word_mask = (1 << word_bits) - 1
register_count = 8

Handler = Callable[["MachineState", DecodedCommand], None]


@dataclass
class MachineState:
    """State of the UVM: instruction memory and data memory.

    Attributes:
        program: Decoded instructions.
        memory: Data memory of ``memory_size`` bytes.
        registers: Eight general-purpose registers.
        pc: Program counter.
    """

    program: list[DecodedCommand]
    memory: bytearray = field(
        default_factory=lambda: bytearray(memory_size)
    )
    registers: list[int] = field(
        default_factory=lambda: [0] * register_count
    )
    pc: int = 0


def _reg(state: MachineState, command: DecodedCommand,
         name: str) -> int:
    """Return value of register referenced by field ``name``."""
    return state.registers[command.fields[name]]


def _exec_load_const(state: MachineState,
                     command: DecodedCommand) -> None:
    """LOAD_CONST: write constant into register B."""
    state.registers[command.fields["B"]] = (
        command.fields["C"] & word_mask
    )


def _exec_load_mem(state: MachineState,
                   command: DecodedCommand) -> None:
    """LOAD_MEM: reg[D] = mem[reg[C] + B]."""
    address = (_reg(state, command, "C") + command.fields["B"])
    state.registers[command.fields["D"]] = state.memory[address]


def _exec_store_mem(state: MachineState,
                    command: DecodedCommand) -> None:
    """STORE_MEM: mem[reg[C]] = reg[B]."""
    address = _reg(state, command, "C")
    state.memory[address] = (
        state.registers[command.fields["B"]] & word_mask
    )


def _exec_bitreverse(state: MachineState,
                     command: DecodedCommand) -> None:
    """BITREVERSE: mem[reg[C] + D] = bitreverse(reg[B])."""
    source = state.registers[command.fields["B"]] & word_mask
    address = _reg(state, command, "C") + command.fields["D"]
    state.memory[address] = bitreverse(source)


handlers: dict[str, Handler] = {
    "LOAD_CONST": _exec_load_const,
    "LOAD_MEM": _exec_load_mem,
    "STORE_MEM": _exec_store_mem,
    "BITREVERSE": _exec_bitreverse,
}


def step(state: MachineState) -> bool:
    """Execute one instruction; return False when program ends."""
    if state.pc >= len(state.program):
        return False
    command = state.program[state.pc]
    handler = handlers.get(command.mnemonic)
    if handler is None:
        raise ValueError(f"Unsupported command: {command.mnemonic}")
    handler(state, command)
    state.pc += 1
    return True


def run(program_path: Path) -> MachineState:
    """Load binary program and execute it to completion."""
    state = MachineState(program=load_program(program_path))
    while step(state):
        pass
    return state


def dump_memory(state: MachineState,
                start: int, end: int) -> dict[str, object]:
    """Produce a JSON-ready dump of a memory slice."""
    if not 0 <= start <= end <= memory_size:
        raise ValueError("Invalid dump range")
    return {
        "range": {"start": start, "end": end},
        "memory": list(state.memory[start:end]),
    }
