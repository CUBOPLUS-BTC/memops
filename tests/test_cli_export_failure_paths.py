import json
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

import memops.cli as cli
from memops.backends import (
    BackendFeeRecommendations,
    BackendTransaction,
    BackendTransactionSummary,
)
from memops.cli import main

VALID_TXID = "ab" * 32

RECOMMENDATIONS = BackendFeeRecommendations(
    fastest_fee_sat_vb=25,
    half_hour_fee_sat_vb=20,
    hour_fee_sat_vb=15,
    economy_fee_sat_vb=10,
    minimum_fee_sat_vb=5,
)

NON_SEGWIT_RBF_HEX = "".join(
    [
        "01000000",
        "01",
        "00" * 32,
        "00000000",
        "00",
        "fdffffff",
        "01",
        "0000000000000000",
        "00",
        "00000000",
    ]
)


class StubDiagnosisBackend:
    def __init__(
        self,
        *,
        transaction: BackendTransaction,
        summary: BackendTransactionSummary,
        recommendations: BackendFeeRecommendations = RECOMMENDATIONS,
    ) -> None:
        self._transaction = transaction
        self._summary = summary
        self._recommendations = recommendations

    def get_transaction(self, txid: str) -> BackendTransaction:
        return self._transaction

    def get_transaction_summary(self, txid: str) -> BackendTransactionSummary:
        return self._summary

    def get_fee_recommendations(self) -> BackendFeeRecommendations:
        return self._recommendations


def build_backend() -> StubDiagnosisBackend:
    return StubDiagnosisBackend(
        transaction=BackendTransaction(
            txid=VALID_TXID,
            raw_hex=NON_SEGWIT_RBF_HEX,
        ),
        summary=BackendTransactionSummary(
            txid=VALID_TXID,
            confirmed=False,
            fee_sats=1200,
            weight_wu=400,
        ),
    )


def test_main_returns_one_when_export_writer_fails(monkeypatch) -> None:
    stdout = StringIO()
    stderr = StringIO()

    def fail_export(diagnosed, base_dir: Path) -> None:
        assert diagnosed.inspection.txid == VALID_TXID
        assert base_dir == Path("demo/output")
        raise OSError("simulated export failure")

    monkeypatch.setattr(cli, "export_diagnosis_artifacts", fail_export)

    exit_code = main(
        ["--why-stuck", "--export-dir", "demo/output", VALID_TXID],
        backend=build_backend(),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == "error: simulated export failure\n"


def test_main_returns_one_when_export_dir_override_is_a_file(tmp_path: Path) -> None:
    conflicting_base_dir = tmp_path / "exports-root"
    conflicting_base_dir.write_text("not-a-directory", encoding="utf-8")

    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["--why-stuck", "--export-dir", str(conflicting_base_dir), VALID_TXID],
        backend=build_backend(),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""

    error_output = stderr.getvalue()
    assert error_output.startswith("error: ")
    assert str(conflicting_base_dir) in error_output


def test_main_returns_one_when_configured_export_dir_is_a_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    conflicting_base_dir = tmp_path / "configured-exports"
    conflicting_base_dir.write_text("not-a-directory", encoding="utf-8")

    monkeypatch.setattr(
        cli,
        "get_settings",
        lambda: SimpleNamespace(export_dir=conflicting_base_dir),
    )

    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["--why-stuck", "--export", VALID_TXID],
        backend=build_backend(),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""

    error_output = stderr.getvalue()
    assert error_output.startswith("error: ")
    assert str(conflicting_base_dir) in error_output


def test_main_why_stuck_json_without_export_ignores_export_settings_and_writer(
    monkeypatch,
) -> None:
    def fail_get_settings() -> SimpleNamespace:
        raise AssertionError("settings should not be read without export")

    def fail_export(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("export should not run without export flags")

    monkeypatch.setattr(cli, "get_settings", fail_get_settings)
    monkeypatch.setattr(cli, "export_diagnosis_artifacts", fail_export)

    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["--why-stuck", "--json", VALID_TXID],
        backend=build_backend(),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""

    payload = json.loads(stdout.getvalue())
    assert payload["txid"] == VALID_TXID
    assert payload["diagnosis"]["recommended_action"] == "wait"
    assert "artifacts" not in payload


def test_main_inspection_json_without_export_ignores_export_settings_and_writer(
    monkeypatch,
) -> None:
    def fail_get_settings() -> SimpleNamespace:
        raise AssertionError("settings should not be read without export")

    def fail_export(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("export should not run outside why-stuck export mode")

    monkeypatch.setattr(cli, "get_settings", fail_get_settings)
    monkeypatch.setattr(cli, "export_diagnosis_artifacts", fail_export)

    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["--json", VALID_TXID],
        backend=build_backend(),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""

    payload = json.loads(stdout.getvalue())
    assert payload["txid"] == VALID_TXID
    assert "parsed" in payload
    assert "analysis" in payload
    assert "summary" not in payload
    assert "artifacts" not in payload
