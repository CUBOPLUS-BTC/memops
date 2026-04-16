"""End-to-end why-stuck diagnosis services."""

from dataclasses import dataclass

from memops.backends import BackendFeeRecommendations, BackendTransactionSummary
from memops.backends.contracts import FeeEvidenceCompleteness
from memops.diagnostics import (
    TransactionFeeContext,
    WhyStuckDiagnosis,
    apply_why_stuck_policy,
    build_confirmed_why_stuck_diagnosis,
    build_insufficient_fee_evidence_diagnosis,
    build_transaction_fee_context,
)

from .inspection import InspectedTransaction, inspect_transaction


@dataclass(frozen=True, slots=True)
class DiagnosedTransaction:
    """Complete why-stuck diagnosis result returned by the application service."""

    inspection: InspectedTransaction
    summary: BackendTransactionSummary
    fee_recommendations: BackendFeeRecommendations
    fee_context: TransactionFeeContext | None
    diagnosis: WhyStuckDiagnosis


def _validate_summary_matches_inspection(
    *,
    summary: BackendTransactionSummary,
    inspection: InspectedTransaction,
) -> None:
    """Ensure backend summary data matches the inspected transaction."""
    if summary.txid != inspection.txid:
        msg = "backend transaction summary txid does not match inspected transaction"
        raise ValueError(msg)


def _summary_has_exact_fee_evidence(summary: BackendTransactionSummary) -> bool:
    """Return whether the backend summary carries exact fee evidence."""
    return summary.fee_evidence.completeness is FeeEvidenceCompleteness.EXACT


def diagnose_why_stuck(txid: str, backend: object) -> DiagnosedTransaction:
    """Diagnose why a transaction appears stuck using local and backend evidence."""
    inspection = inspect_transaction(txid, backend)
    summary = backend.get_transaction_summary(txid)
    _validate_summary_matches_inspection(summary=summary, inspection=inspection)

    fee_recommendations = backend.get_fee_recommendations()
    explicitly_signals_rbf = inspection.analysis.signals_explicit_rbf

    if _summary_has_exact_fee_evidence(summary):
        fee_context = build_transaction_fee_context(summary, fee_recommendations)
        diagnosis = apply_why_stuck_policy(
            fee_context,
            explicitly_signals_rbf=explicitly_signals_rbf,
        )
    elif summary.confirmed:
        fee_context = None
        diagnosis = build_confirmed_why_stuck_diagnosis(
            txid=summary.txid,
            explicitly_signals_rbf=explicitly_signals_rbf,
        )
    else:
        fee_context = None
        diagnosis = build_insufficient_fee_evidence_diagnosis(
            txid=summary.txid,
            explicitly_signals_rbf=explicitly_signals_rbf,
        )

    return DiagnosedTransaction(
        inspection=inspection,
        summary=summary,
        fee_recommendations=fee_recommendations,
        fee_context=fee_context,
        diagnosis=diagnosis,
    )
