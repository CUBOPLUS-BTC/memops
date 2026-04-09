"""Rendering helpers and artifact export workflow for why-stuck diagnosis."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from memops.services.diagnosis import DiagnosedTransaction


@dataclass(frozen=True, slots=True)
class DiagnosisArtifactPaths:
    """Paths written for an exported why-stuck diagnosis."""

    txid: str
    artifact_dir: Path
    analysis_json_path: Path
    report_markdown_path: Path


def _format_optional_int(value: int | None) -> str:
    """Render an optional integer value for human-readable output."""
    return "none" if value is None else str(value)


def _format_optional_float(value: float | None) -> str:
    """Render an optional float value for human-readable output."""
    return "none" if value is None else f"{value:.2f}"


def diagnosis_to_export_payload(diagnosed: DiagnosedTransaction) -> dict[str, Any]:
    """Convert a diagnosed transaction into a JSON-serializable export payload."""
    inspection = diagnosed.inspection
    summary = diagnosed.summary
    fee_context = diagnosed.fee_context
    diagnosis = diagnosed.diagnosis
    recommended_fees = fee_context.recommended_fees

    return {
        "txid": inspection.txid,
        "raw_hex": inspection.raw_hex,
        "parsed": {
            "version": inspection.parsed.version,
            "input_count": inspection.parsed.input_count,
            "output_count": inspection.parsed.output_count,
            "locktime": inspection.parsed.locktime,
            "sequences": list(inspection.parsed.sequences),
            "is_segwit": inspection.parsed.is_segwit,
        },
        "analysis": {
            "signals_explicit_rbf": inspection.analysis.signals_explicit_rbf,
            "signaling_input_indexes": list(inspection.analysis.signaling_input_indexes),
        },
        "summary": {
            "txid": summary.txid,
            "confirmed": summary.confirmed,
            "fee_sats": summary.fee_sats,
            "weight_wu": summary.weight_wu,
            "virtual_size_vbytes": summary.virtual_size_vbytes,
            "block_height": summary.block_height,
            "block_time": summary.block_time,
        },
        "fee_context": {
            "txid": fee_context.txid,
            "confirmed": fee_context.confirmed,
            "fee_sats": fee_context.fee_sats,
            "weight_wu": fee_context.weight_wu,
            "virtual_size_vbytes": fee_context.virtual_size_vbytes,
            "fee_rate_sat_vb": fee_context.fee_rate_sat_vb,
            "market_position": fee_context.market_position.value,
            "target_fee_rate_sat_vb": fee_context.target_fee_rate_sat_vb,
            "fee_rate_shortfall_sat_vb": fee_context.fee_rate_shortfall_sat_vb,
            "recommended_fees": {
                "fastest_fee_sat_vb": recommended_fees.fastest_fee_sat_vb,
                "half_hour_fee_sat_vb": recommended_fees.half_hour_fee_sat_vb,
                "hour_fee_sat_vb": recommended_fees.hour_fee_sat_vb,
                "economy_fee_sat_vb": recommended_fees.economy_fee_sat_vb,
                "minimum_fee_sat_vb": recommended_fees.minimum_fee_sat_vb,
            },
        },
        "diagnosis": {
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
        },
    }


def format_export_payload_json(diagnosed: DiagnosedTransaction) -> str:
    """Render a diagnosed transaction export payload as formatted JSON."""
    return json.dumps(
        diagnosis_to_export_payload(diagnosed),
        indent=2,
        sort_keys=True,
    )


def render_diagnosis_markdown(diagnosed: DiagnosedTransaction) -> str:
    """Render a diagnosed transaction as a human-readable markdown report."""
    inspection = diagnosed.inspection
    summary = diagnosed.summary
    fee_context = diagnosed.fee_context
    diagnosis = diagnosed.diagnosis
    recommended_fees = fee_context.recommended_fees

    signaling_inputs = (
        ", ".join(str(index) for index in inspection.analysis.signaling_input_indexes)
        if inspection.analysis.signaling_input_indexes
        else "none"
    )

    lines = [
        "# MemOps Why-Stuck Diagnosis",
        "",
        "## Transaction",
        f"- txid: {inspection.txid}",
        f"- confirmed: {'yes' if summary.confirmed else 'no'}",
        f"- fee_sats: {summary.fee_sats}",
        f"- weight_wu: {summary.weight_wu}",
        f"- virtual_size_vbytes: {summary.virtual_size_vbytes}",
        f"- block_height: {_format_optional_int(summary.block_height)}",
        f"- block_time: {_format_optional_int(summary.block_time)}",
        f"- fee_rate_sat_vb: {fee_context.fee_rate_sat_vb:.2f}",
        f"- market_position: {fee_context.market_position.value}",
        (f"- target_fee_rate_sat_vb: {_format_optional_int(fee_context.target_fee_rate_sat_vb)}"),
        (
            "- fee_rate_shortfall_sat_vb: "
            f"{_format_optional_float(fee_context.fee_rate_shortfall_sat_vb)}"
        ),
        "",
        "## Fee Recommendations",
        f"- fastest_fee_sat_vb: {recommended_fees.fastest_fee_sat_vb}",
        f"- half_hour_fee_sat_vb: {recommended_fees.half_hour_fee_sat_vb}",
        f"- hour_fee_sat_vb: {recommended_fees.hour_fee_sat_vb}",
        f"- economy_fee_sat_vb: {recommended_fees.economy_fee_sat_vb}",
        f"- minimum_fee_sat_vb: {recommended_fees.minimum_fee_sat_vb}",
        "",
        "## Parsed Transaction",
        f"- version: {inspection.parsed.version}",
        f"- input_count: {inspection.parsed.input_count}",
        f"- output_count: {inspection.parsed.output_count}",
        f"- locktime: {inspection.parsed.locktime}",
        f"- segwit: {'yes' if inspection.parsed.is_segwit else 'no'}",
        (
            "- explicit_rbf: yes"
            if inspection.analysis.signals_explicit_rbf
            else "- explicit_rbf: no"
        ),
        f"- signaling_inputs: {signaling_inputs}",
        "",
        "## Diagnosis",
        f"- recommended_action: {diagnosis.recommended_action.value}",
        f"- severity: {diagnosis.severity.value}",
        f"- reason: {diagnosis.reason.value}",
        "",
        "### Summary",
        diagnosis.summary,
        "",
        "### Explanation",
        diagnosis.explanation,
        "",
    ]
    return "\n".join(lines)


def export_diagnosis_artifacts(
    diagnosed: DiagnosedTransaction,
    base_dir: Path | str,
) -> DiagnosisArtifactPaths:
    """Write why-stuck diagnosis artifacts to disk."""
    txid = diagnosed.inspection.txid
    artifact_dir = Path(base_dir) / txid
    artifact_dir.mkdir(parents=True, exist_ok=True)

    analysis_json_path = artifact_dir / "analysis.json"
    report_markdown_path = artifact_dir / "report.md"

    analysis_json_path.write_text(
        f"{format_export_payload_json(diagnosed)}\n",
        encoding="utf-8",
    )
    report_markdown_path.write_text(
        render_diagnosis_markdown(diagnosed),
        encoding="utf-8",
    )

    return DiagnosisArtifactPaths(
        txid=txid,
        artifact_dir=artifact_dir,
        analysis_json_path=analysis_json_path,
        report_markdown_path=report_markdown_path,
    )
