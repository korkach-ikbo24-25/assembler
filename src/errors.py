"""Custom exceptions for the UVM assembler."""


class AssemblerError(Exception):
    """Base error raised by the assembler."""


class ParseError(AssemblerError):
    """Raised when a source line cannot be parsed."""


class FieldRangeError(AssemblerError):
    """Raised when a field value does not fit into its bit width."""