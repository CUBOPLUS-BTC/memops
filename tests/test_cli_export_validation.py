from io import StringIO

import pytest

from memops.cli import build_argument_parser, main, validate_cli_args

VALID_TXID = "ab" * 32


def test_build_argument_parser_accepts_export_flags() -> None:
    args = build_argument_parser().parse_args(
        ["--why-stuck", "--export", "--export-dir", "demo/output", VALID_TXID]
    )

    assert args.why_stuck is True
    assert args.export is True
    assert args.export_dir == "demo/output"
    assert args.output_json is False
    assert args.txid == VALID_TXID


def test_build_argument_parser_accepts_export_dir_without_export_flag() -> None:
    args = build_argument_parser().parse_args(
        ["--why-stuck", "--export-dir", "demo/output", VALID_TXID]
    )

    assert args.why_stuck is True
    assert args.export is False
    assert args.export_dir == "demo/output"
    assert args.txid == VALID_TXID


def test_validate_cli_args_rejects_export_without_why_stuck() -> None:
    args = build_argument_parser().parse_args(["--export", VALID_TXID])

    with pytest.raises(ValueError, match=r"--export requires --why-stuck\."):
        validate_cli_args(args)


def test_validate_cli_args_rejects_export_dir_without_why_stuck() -> None:
    args = build_argument_parser().parse_args(["--export-dir", "demo/output", VALID_TXID])

    with pytest.raises(ValueError, match=r"--export-dir requires --why-stuck\."):
        validate_cli_args(args)


def test_main_reports_export_usage_error_and_returns_two() -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["--export", VALID_TXID],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == "error: --export requires --why-stuck.\n"


def test_main_reports_export_dir_usage_error_and_returns_two() -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["--export-dir", "demo/output", VALID_TXID],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == "error: --export-dir requires --why-stuck.\n"
