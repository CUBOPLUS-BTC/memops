"""Pure policy helpers for transaction replaceability reasoning."""

from collections.abc import Iterable

SEQUENCE_MAX = 0xFFFFFFFF
EXPLICIT_RBF_THRESHOLD = 0xFFFFFFFE


def _validate_sequence(sequence: int) -> int:
    """Validate that a sequence value fits in an unsigned 32-bit integer."""
    if sequence < 0 or sequence > SEQUENCE_MAX:
        msg = f"sequence must be between 0 and {SEQUENCE_MAX}, got {sequence}"
        raise ValueError(msg)
    return sequence


def signals_explicit_rbf(sequence: int) -> bool:
    """Return True if a sequence value explicitly signals BIP125 replaceability."""
    return _validate_sequence(sequence) < EXPLICIT_RBF_THRESHOLD


def any_input_signals_explicit_rbf(sequences: Iterable[int]) -> bool:
    """Return True if any input sequence explicitly signals BIP125 replaceability."""
    return any(signals_explicit_rbf(sequence) for sequence in sequences)
