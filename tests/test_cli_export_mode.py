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


def test_main_writes_artifacts_in_text_mode_when_export_dir_is_provided(
    tmp_path: Path,
) -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["--why-stuck", "--export-dir", str(tmp_path), VALID_TXID],
        backend=build_backend(),
        stdout=stdout,
        stderr=stderr,
    )

    artifact_dir = tmp_path / VALID_TXID
    analysis_json_path = artifact_dir / "analysis.json"
    report_markdown_path = artifact_dir / "report.md"

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert artifact_dir.is_dir()
    assert analysis_json_path.is_file()
    assert report_markdown_path.is_file()

    output = stdout.getvalue()
    assert f"txid: {VALID_TXID}" in output
    assert "recommended_action: wait" in output
    assert "Artifacts written:" in output
    assert f"- directory: {artifact_dir}" in output
    assert f"- analysis_json: {analysis_json_path}" in output
    assert f"- report_markdown: {report_markdown_path}" in output

    payload = json.loads(analysis_json_path.read_text(encoding="utf-8"))
    report = report_markdown_path.read_text(encoding="utf-8")

    assert payload["txid"] == VALID_TXID
    assert payload["diagnosis"]["recommended_action"] == "wait"
    assert "# MemOps Why-Stuck Diagnosis" in report


def test_main_includes_artifact_paths_in_json_output_when_exporting(
    tmp_path: Path,
) -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["--why-stuck", "--json", "--export-dir", str(tmp_path), VALID_TXID],
        backend=build_backend(),
        stdout=stdout,
        stderr=stderr,
    )

    artifact_dir = tmp_path / VALID_TXID
    analysis_json_path = artifact_dir / "analysis.json"
    report_markdown_path = artifact_dir / "report.md"

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert artifact_dir.is_dir()
    assert analysis_json_path.is_file()
    assert report_markdown_path.is_file()

    payload = json.loads(stdout.getvalue())

    assert payload["txid"] == VALID_TXID
    assert payload["diagnosis"]["recommended_action"] == "wait"
    assert payload["artifacts"] == {
        "artifact_dir": str(artifact_dir),
        "analysis_json_path": str(analysis_json_path),
        "report_markdown_path": str(report_markdown_path),
    }


def test_main_uses_settings_export_dir_when_export_flag_is_enabled(
    tmp_path: Path,
    monkeypatch,
) -> None:
    configured_export_dir = tmp_path / "configured-exports"
    monkeypatch.setattr(
        cli,
        "get_settings",
        lambda: SimpleNamespace(export_dir=configured_export_dir),
    )

    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["--why-stuck", "--export", VALID_TXID],
        backend=build_backend(),
        stdout=stdout,
        stderr=stderr,
    )

    artifact_dir = configured_export_dir / VALID_TXID
    analysis_json_path = artifact_dir / "analysis.json"
    report_markdown_path = artifact_dir / "report.md"

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert artifact_dir.is_dir()
    assert analysis_json_path.is_file()
    assert report_markdown_path.is_file()

    output = stdout.getvalue()
    assert "Artifacts written:" in output
    assert f"- directory: {artifact_dir}" in output
    assert f"- analysis_json: {analysis_json_path}" in output
    assert f"- report_markdown: {report_markdown_path}" in output
