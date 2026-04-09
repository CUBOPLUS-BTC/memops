"""Command-line interface for MemOps."""

import argparse
import sys
from collections.abc import Sequence
from typing import TextIO

from memops.backends import BackendError, MempoolSpaceBackend, TransactionBackend
from memops.services import InspectedTransaction, inspect_transaction


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the MemOps command-line parser."""
    parser = argparse.ArgumentParser(
        prog="memops",
        description="Inspect Bitcoin transactions and explicit RBF signaling.",
    )
    parser.add_argument("txid", help="Transaction id to inspect.")
    return parser


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
        resolved_backend = backend if backend is not None else MempoolSpaceBackend.from_settings()
        inspected = inspect_transaction(args.txid, resolved_backend)
    except (BackendError, ValueError) as exc:
        print(f"error: {exc}", file=resolved_stderr)
        return 1

    print(format_inspection_report(inspected), file=resolved_stdout)
    return 0
