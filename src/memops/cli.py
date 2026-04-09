"""Command-line interface for MemOps."""

import argparse
import json
import sys
from collections.abc import Sequence
from typing import Any, TextIO

from memops.backends import BackendError, MempoolSpaceBackend, TransactionBackend
from memops.services import (
    DiagnosedTransaction,
    InspectedTransaction,
    diagnose_why_stuck,
    inspect_transaction,
)


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the MemOps command-line parser."""
    parser = argparse.ArgumentParser(
        prog="memops",
        description="Inspect Bitcoin transactions and explain likely why-stuck conditions.",
    )
    parser.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        help="Render the result as JSON.",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Write why-stuck diagnosis artifacts to disk.",
    )
    parser.add_argument(
        "--export-dir",
        help="Override the export artifact directory (requires --why-stuck).",
    )
    parser.add_argument(
        "--why-stuck",
        dest="why_stuck",
        action="store_true",
        help="Run the why-stuck diagnosis workflow instead of basic inspection.",
    )
    parser.add_argument("txid", help="Transaction id to inspect.")
    return parser


def validate_cli_args(args: argparse.Namespace) -> None:
    """Validate CLI argument combinations before running application logic."""
    if args.export and not args.why_stuck:
        msg = "--export requires --why-stuck."
        raise ValueError(msg)
    if args.export_dir and not args.why_stuck:
        msg = "--export-dir requires --why-stuck."
        raise ValueError(msg)


def _format_optional_int(value: int | None) -> str:
    """Render an optional integer field for text output."""
    return "none" if value is None else str(value)


def _format_optional_float(value: float | None) -> str:
    """Render an optional float field for text output."""
    return "none" if value is None else f"{value:.2f}"


def inspection_to_dict(inspected: InspectedTransaction) -> dict[str, Any]:
    """Convert an inspected transaction into a JSON-serializable payload."""
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


def diagnosis_to_dict(diagnosed: DiagnosedTransaction) -> dict[str, Any]:
    """Convert a diagnosed transaction into a JSON-serializable payload."""
    inspection_payload = inspection_to_dict(diagnosed.inspection)
    recommended_fees = diagnosed.fee_context.recommended_fees

    return {
        "txid": diagnosed.inspection.txid,
        "raw_hex": diagnosed.inspection.raw_hex,
        "parsed": inspection_payload["parsed"],
        "analysis": inspection_payload["analysis"],
        "summary": {
            "txid": diagnosed.summary.txid,
            "confirmed": diagnosed.summary.confirmed,
            "fee_sats": diagnosed.summary.fee_sats,
            "weight_wu": diagnosed.summary.weight_wu,
            "virtual_size_vbytes": diagnosed.summary.virtual_size_vbytes,
            "block_height": diagnosed.summary.block_height,
            "block_time": diagnosed.summary.block_time,
        },
        "fee_context": {
            "txid": diagnosed.fee_context.txid,
            "confirmed": diagnosed.fee_context.confirmed,
            "fee_sats": diagnosed.fee_context.fee_sats,
            "weight_wu": diagnosed.fee_context.weight_wu,
            "virtual_size_vbytes": diagnosed.fee_context.virtual_size_vbytes,
            "fee_rate_sat_vb": diagnosed.fee_context.fee_rate_sat_vb,
            "market_position": diagnosed.fee_context.market_position.value,
            "target_fee_rate_sat_vb": diagnosed.fee_context.target_fee_rate_sat_vb,
            "fee_rate_shortfall_sat_vb": diagnosed.fee_context.fee_rate_shortfall_sat_vb,
            "recommended_fees": {
                "fastest_fee_sat_vb": recommended_fees.fastest_fee_sat_vb,
                "half_hour_fee_sat_vb": recommended_fees.half_hour_fee_sat_vb,
                "hour_fee_sat_vb": recommended_fees.hour_fee_sat_vb,
                "economy_fee_sat_vb": recommended_fees.economy_fee_sat_vb,
                "minimum_fee_sat_vb": recommended_fees.minimum_fee_sat_vb,
            },
        },
        "diagnosis": {
            "txid": diagnosed.diagnosis.txid,
            "confirmed": diagnosed.diagnosis.confirmed,
            "reason": diagnosed.diagnosis.reason.value,
            "severity": diagnosed.diagnosis.severity.value,
            "recommended_action": diagnosed.diagnosis.recommended_action.value,
            "explicitly_signals_rbf": diagnosed.diagnosis.explicitly_signals_rbf,
            "can_bump_fee": diagnosed.diagnosis.can_bump_fee,
            "market_position": diagnosed.diagnosis.market_position.value,
            "fee_rate_sat_vb": diagnosed.diagnosis.fee_rate_sat_vb,
            "target_fee_rate_sat_vb": diagnosed.diagnosis.target_fee_rate_sat_vb,
            "fee_rate_shortfall_sat_vb": diagnosed.diagnosis.fee_rate_shortfall_sat_vb,
            "summary": diagnosed.diagnosis.summary,
            "explanation": diagnosed.diagnosis.explanation,
        },
    }


def format_inspection_json(inspected: InspectedTransaction) -> str:
    """Render an inspected transaction as formatted JSON."""
    return json.dumps(inspection_to_dict(inspected), indent=2, sort_keys=True)


def format_why_stuck_json(diagnosed: DiagnosedTransaction) -> str:
    """Render a diagnosed transaction as formatted JSON."""
    return json.dumps(diagnosis_to_dict(diagnosed), indent=2, sort_keys=True)


def format_inspection_report(inspected: InspectedTransaction) -> str:
    """Render an inspected transaction as a human-readable report."""
    signaling_inputs = (
        ", ".join(str(index) for index in inspected.analysis.signaling_input_indexes)
        if inspected.analysis.signaling_input_indexes
        else "none"
    )

    return "\n".join(
        [
            f"txid: {inspected.txid}",
            f"version: {inspected.parsed.version}",
            f"inputs: {inspected.parsed.input_count}",
            f"outputs: {inspected.parsed.output_count}",
            f"locktime: {inspected.parsed.locktime}",
            f"segwit: {'yes' if inspected.parsed.is_segwit else 'no'}",
            (
                "explicit_rbf: yes"
                if inspected.analysis.signals_explicit_rbf
                else "explicit_rbf: no"
            ),
            f"signaling_inputs: {signaling_inputs}",
        ]
    )


def format_why_stuck_report(diagnosed: DiagnosedTransaction) -> str:
    """Render a diagnosed transaction as a human-readable report."""
    summary = diagnosed.summary
    fee_context = diagnosed.fee_context
    diagnosis = diagnosed.diagnosis

    return "\n".join(
        [
            f"txid: {diagnosed.inspection.txid}",
            f"confirmed: {'yes' if summary.confirmed else 'no'}",
            f"fee_sats: {summary.fee_sats}",
            f"weight_wu: {summary.weight_wu}",
            f"virtual_size_vbytes: {summary.virtual_size_vbytes}",
            f"fee_rate_sat_vb: {fee_context.fee_rate_sat_vb:.2f}",
            f"market_position: {fee_context.market_position.value}",
            f"target_fee_rate_sat_vb: {_format_optional_int(fee_context.target_fee_rate_sat_vb)}",
            (
                "fee_rate_shortfall_sat_vb: "
                f"{_format_optional_float(fee_context.fee_rate_shortfall_sat_vb)}"
            ),
            ("explicit_rbf: yes" if diagnosis.explicitly_signals_rbf else "explicit_rbf: no"),
            f"recommended_action: {diagnosis.recommended_action.value}",
            f"severity: {diagnosis.severity.value}",
            f"reason: {diagnosis.reason.value}",
            f"summary: {diagnosis.summary}",
            f"explanation: {diagnosis.explanation}",
        ]
    )


def main(
    argv: Sequence[str] | None = None,
    *,
    backend: TransactionBackend | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the MemOps CLI."""
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    resolved_stdout = sys.stdout if stdout is None else stdout
    resolved_stderr = sys.stderr if stderr is None else stderr

    try:
        validate_cli_args(args)
    except ValueError as exc:
        print(f"error: {exc}", file=resolved_stderr)
        return 2

    try:
        resolved_backend = backend if backend is not None else MempoolSpaceBackend.from_settings()

        if args.why_stuck:
            diagnosed = diagnose_why_stuck(args.txid, resolved_backend)
            output = (
                format_why_stuck_json(diagnosed)
                if args.output_json
                else format_why_stuck_report(diagnosed)
            )
        else:
            inspected = inspect_transaction(args.txid, resolved_backend)
            output = (
                format_inspection_json(inspected)
                if args.output_json
                else format_inspection_report(inspected)
            )
    except (BackendError, ValueError) as exc:
        print(f"error: {exc}", file=resolved_stderr)
        return 1

    print(output, file=resolved_stdout)
    return 0
