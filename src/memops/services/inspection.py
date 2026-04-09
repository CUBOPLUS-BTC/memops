"""Transaction inspection workflow services."""

from dataclasses import dataclass

from memops.backends.contracts import TransactionBackend

from .analysis import TransactionAnalysis, analyze_parsed_transaction
from .tx_parser import ParsedTransaction, parse_raw_transaction


@dataclass(frozen=True, slots=True)
class InspectedTransaction:
    """Full inspection result for a transaction."""

    txid: str
    raw_hex: str
    parsed: ParsedTransaction
    analysis: TransactionAnalysis


def inspect_transaction(txid: str, backend: TransactionBackend) -> InspectedTransaction:
    """Fetch, parse, and analyze a transaction by txid."""
    backend_transaction = backend.get_transaction(txid)
    parsed = parse_raw_transaction(backend_transaction.raw_hex)
    analysis = analyze_parsed_transaction(parsed)

    return InspectedTransaction(
        txid=backend_transaction.txid,
        raw_hex=backend_transaction.raw_hex,
        parsed=parsed,
        analysis=analysis,
    )
