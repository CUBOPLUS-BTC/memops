"""Shared structured payload builders for why-stuck diagnosis outputs."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from memops.backends import (
    BackendFeeRecommendations,
    BackendTransactionSummary,
    TransactionFeeEvidence,
)
from memops.diagnostics import TransactionFeeContext

if TYPE_CHECKING:
    from memops.diagnostics import WhyStuckDiagnosis
    from memops.services.diagnosis import DiagnosedTransaction
    from memops.services.inspection import InspectedTransaction


def build_inspection_payload(inspected: InspectedTransaction) -> dict[str, Any]:
    """Build a stable structured payload for transaction inspection results."""
    return {
        "txid": inspected.txid,
        "raw_hex": inspected.raw_hex,
        "parsed": {
            "version": inspected.parsed.version,
            "input_count": inspected.parsed.input_count,
            "output_count": inspected.parsed.output_count,
            "locktime": inspected.parsed.locktime,
            "sequences": list(inspected.parsed.sequences),
            "is_segwit": inspected.parsed.is_segwit,
        },
        "analysis": {
            "signals_explicit_rbf": inspected.analysis.signals_explicit_rbf,
            "signaling_input_indexes": list(inspected.analysis.signaling_input_indexes),
        },
    }


def build_fee_evidence_payload(
    fee_evidence: TransactionFeeEvidence,
) -> dict[str, Any]:
    """Build a stable structured payload for normalized fee evidence."""
    return {
        "source": fee_evidence.source.value,
        "completeness": fee_evidence.completeness.value,
        "fee_sats": fee_evidence.fee_sats,
        "weight_wu": fee_evidence.weight_wu,
        "virtual_size_vbytes": fee_evidence.virtual_size_vbytes,
        "effective_fee_rate_sat_vb": fee_evidence.effective_fee_rate_sat_vb,
    }


def build_backend_transaction_summary_payload(
    summary: BackendTransactionSummary,
) -> dict[str, Any]:
    """Build a stable structured payload for backend transaction summaries."""
    return {
        "txid": summary.txid,
        "confirmed": summary.confirmed,
        "fee_sats": summary.fee_sats,
        "weight_wu": summary.weight_wu,
        "virtual_size_vbytes": summary.virtual_size_vbytes,
        "block_height": summary.block_height,
        "block_time": summary.block_time,
        "fee_evidence": build_fee_evidence_payload(summary.fee_evidence),
    }


def build_fee_recommendations_payload(
    recommendations: BackendFeeRecommendations,
) -> dict[str, int]:
    """Build a structured payload for backend fee recommendations."""
    return {
        "fastest_fee_sat_vb": recommendations.fastest_fee_sat_vb,
        "half_hour_fee_sat_vb": recommendations.half_hour_fee_sat_vb,
        "hour_fee_sat_vb": recommendations.hour_fee_sat_vb,
        "economy_fee_sat_vb": recommendations.economy_fee_sat_vb,
        "minimum_fee_sat_vb": recommendations.minimum_fee_sat_vb,
    }


def build_transaction_fee_context_payload(
    context: TransactionFeeContext,
) -> dict[str, Any]:
    """Build a stable structured payload for transaction fee context."""
    return {
        "txid": context.txid,
        "confirmed": context.confirmed,
        "fee_sats": context.fee_sats,
        "weight_wu": context.weight_wu,
        "virtual_size_vbytes": context.virtual_size_vbytes,
        "fee_rate_sat_vb": context.fee_rate_sat_vb,
        "market_position": context.market_position.value,
        "target_fee_rate_sat_vb": context.target_fee_rate_sat_vb,
        "fee_rate_shortfall_sat_vb": context.fee_rate_shortfall_sat_vb,
        "recommended_fees": build_fee_recommendations_payload(context.recommended_fees),
    }


def build_why_stuck_diagnosis_payload(
    diagnosis: WhyStuckDiagnosis,
) -> dict[str, Any]:
    """Build a stable structured payload for why-stuck diagnosis results."""
    return {
        "txid": diagnosis.txid,
        "confirmed": diagnosis.confirmed,
        "reason": diagnosis.reason.value,
        "severity": diagnosis.severity.value,
        "recommended_action": diagnosis.recommended_action.value,
        "explicitly_signals_rbf": diagnosis.explicitly_signals_rbf,
        "can_bump_fee": diagnosis.can_bump_fee,
        "market_position": diagnosis.market_position.value,
        "fee_rate_sat_vb": diagnosis.fee_rate_sat_vb,
        "target_fee_rate_sat_vb": diagnosis.target_fee_rate_sat_vb,
        "fee_rate_shortfall_sat_vb": diagnosis.fee_rate_shortfall_sat_vb,
        "summary": diagnosis.summary,
        "explanation": diagnosis.explanation,
    }


def build_diagnosed_transaction_payload(
    diagnosed: DiagnosedTransaction,
) -> dict[str, Any]:
    """Build the shared structured payload for why-stuck JSON outputs."""
    inspection_payload = build_inspection_payload(diagnosed.inspection)

    return {
        "txid": inspection_payload["txid"],
        "raw_hex": inspection_payload["raw_hex"],
        "parsed": inspection_payload["parsed"],
        "analysis": inspection_payload["analysis"],
        "summary": build_backend_transaction_summary_payload(diagnosed.summary),
        "fee_context": build_transaction_fee_context_payload(diagnosed.fee_context),
        "diagnosis": build_why_stuck_diagnosis_payload(diagnosed.diagnosis),
    }
