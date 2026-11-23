"""Virtual machine: memory model and interpretation loop."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from .decoder import DecodedCommand, load_program

MEMORY_SIZE = 256
WORD_BITS = 8
WORD_MASK = (1 << WORD_BITS) - 1
REGISTER_COUNT = 8


@dataclass
class MachineState:
    """State of the UVM: instruction memory and data memory.

    Attributes:
        program: Loaded decoded instructions.
        memory: Data memory of ``MEMORY_SIZE`` bytes.
        registers: Eight general-purpose registers.
        pc: Program counter.
    """

    program: List[DecodedCommand]
    memory: bytearray = field(
        default_factory=lambda: bytearray(MEMORY_SIZE)
    )
    registers: List[int] = field(
        default_factory=lambda: [0] * REGISTER_COUNT
    )
    pc: int = 0


def _resolve_address(state: MachineState, field_name: str,
                     command: DecodedCommand) -> int:
    """Resolve memory address for commands using registers.

    Address equals register value referenced by the field name.

    Args:
        state: Machine state.
        field_name: Name of field holding register index.
        command: Decoded command.

    Returns:
        Memory address.
    """
    return state.registers[command.fields[field_name]]


def _exec_load_const(state: MachineState,
                     command: DecodedCommand) -> None:
    """LOAD_CONST: write constant into register B."""
    state.registers[command.fields["B"]] = command.fields["C"] & WORD_MASK


def _exec_load_mem(state: MachineState,
                   command: DecodedCommand) -> None:
    """LOAD_MEM: read memory at reg[C] + offset into reg[D]."""
    base = _resolve_address(state, "C", command)
    address = (base + command.fields["B"]) & WORD_MASK
    state.registers[command.fields["D"]] = state.memory[address]


def _exec_store_mem(state: MachineState,
                    command: DecodedCommand) -> None:
    """STORE_MEM: store reg[B] into memory at address reg[C]."""
    address = _resolve_address(state, "C", command)
    state.memory[address] = state.registers[command.fields["B"]] & WORD_MASK


HANDLERS = {
    "LOAD_CONST": _exec_load_const,
    "LOAD_MEM": _exec_load_mem,
    "STORE_MEM": _exec_store_mem,
}


def step(state: MachineState) -> bool:
    """Execute one instruction.

    Args:
        state: Machine state to mutate.

    Returns:
        True if instruction was executed, False if program ended.
    """
    if state.pc >= len(state.program):
        return False
    command = state.program[state.pc]
    handler = HANDLERS.get(command.mnemonic)
    if handler is None:
        raise ValueError(f"Unsupported command: {command.mnemonic}")
    handler(state, command)
    state.pc += 1
    return True


def run(program_path: Path) -> MachineState:
    """Load binary program and execute it to completion.

    Args:
        program_path: Path to binary file with assembled program.

    Returns:
        Final machine state.
    """
    state = MachineState(program=load_program(program_path))
    while step(state):
        pass
    return state


def dump_memory(state: MachineState,
                start: int, end: int) -> Dict[str, List[int]]:
    """Produce JSON-ready dump of memory slice.

    Args:
        state: Machine state.
        start: First address (inclusive).
        end: Last address (exclusive).

    Returns:
        Dictionary with address range and byte values.
    """
    if not 0 <= start <= end <= MEMORY_SIZE:
        raise ValueError("Invalid dump range")
    return {
        "range": {"start": start, "end": end},
        "memory": list(state.memory[start:end]),
    }