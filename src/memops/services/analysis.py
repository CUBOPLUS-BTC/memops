"""Transaction analysis helpers built on parsed transaction metadata."""

from dataclasses import dataclass

from .policy import signals_explicit_rbf
from .tx_parser import ParsedTransaction


@dataclass(frozen=True, slots=True)
class TransactionAnalysis:
    """High-level analysis derived from a parsed transaction."""

    version: int
    input_count: int
    output_count: int
    locktime: int
    is_segwit: bool
    sequences: tuple[int, ...]
    signals_explicit_rbf: bool
    signaling_input_indexes: tuple[int, ...]


def analyze_parsed_transaction(parsed: ParsedTransaction) -> TransactionAnalysis:
    """Analyze replaceability-relevant properties of a parsed transaction."""
    if len(parsed.sequences) != parsed.input_count:
        msg = "parsed transaction sequence count does not match input count"
        raise ValueError(msg)

    signaling_input_indexes = tuple(
        index for index, sequence in enumerate(parsed.sequences) if signals_explicit_rbf(sequence)
    )

    return TransactionAnalysis(
        version=parsed.version,
        input_count=parsed.input_count,
        output_count=parsed.output_count,
        locktime=parsed.locktime,
        is_segwit=parsed.is_segwit,
        sequences=parsed.sequences,
        signals_explicit_rbf=bool(signaling_input_indexes),
        signaling_input_indexes=signaling_input_indexes,
    )
