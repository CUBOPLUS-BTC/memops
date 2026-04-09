"""Why-stuck diagnosis workflow services."""

from dataclasses import dataclass

from memops.backends.contracts import BackendTransactionSummary, TransactionBackend
from memops.diagnostics import (
    TransactionFeeContext,
    WhyStuckDiagnosis,
    apply_why_stuck_policy,
    build_transaction_fee_context,
)

from .inspection import InspectedTransaction, inspect_transaction


@dataclass(frozen=True, slots=True)
class DiagnosedTransaction:
    """Full why-stuck diagnosis result for a transaction."""

    inspection: InspectedTransaction
    summary: BackendTransactionSummary
    fee_context: TransactionFeeContext
    diagnosis: WhyStuckDiagnosis


def diagnose_why_stuck(txid: str, backend: TransactionBackend) -> DiagnosedTransaction:
    """Fetch, inspect, contextualize, and diagnose a transaction."""

    inspection = inspect_transaction(txid, backend)
    summary = backend.get_transaction_summary(inspection.txid)

    if summary.txid != inspection.txid:
        msg = "backend transaction summary txid does not match inspected transaction"
        raise ValueError(msg)

    fee_context = build_transaction_fee_context(
        summary,
        backend.get_fee_recommendations(),
    )
    diagnosis = apply_why_stuck_policy(
        fee_context,
        explicitly_signals_rbf=inspection.analysis.signals_explicit_rbf,
    )

    return DiagnosedTransaction(
        inspection=inspection,
        summary=summary,
        fee_context=fee_context,
        diagnosis=diagnosis,
    )
