import json
from pathlib import Path

import pytest

from memops.backends import (
    BackendFeeRecommendations,
    BackendTransaction,
    BackendTransactionSummary,
)
from memops.services import DiagnosedTransaction, diagnose_why_stuck
from memops.services.exports import export_diagnosis_artifacts

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


def build_diagnosed_transaction() -> DiagnosedTransaction:
    backend = StubDiagnosisBackend(
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
    return diagnose_why_stuck(VALID_TXID, backend)


def test_export_diagnosis_artifacts_writes_expected_files_from_real_diagnosis(
    tmp_path: Path,
) -> None:
    diagnosed = build_diagnosed_transaction()

    artifact_paths = export_diagnosis_artifacts(diagnosed, tmp_path)

    assert artifact_paths.artifact_dir == tmp_path / VALID_TXID
    assert artifact_paths.analysis_json_path == (artifact_paths.artifact_dir / "analysis.json")
    assert artifact_paths.report_markdown_path == (artifact_paths.artifact_dir / "report.md")
    assert artifact_paths.artifact_dir.is_dir()
    assert artifact_paths.analysis_json_path.is_file()
    assert artifact_paths.report_markdown_path.is_file()

    payload = json.loads(artifact_paths.analysis_json_path.read_text(encoding="utf-8"))
    report = artifact_paths.report_markdown_path.read_text(encoding="utf-8")

    assert payload["txid"] == VALID_TXID
    assert payload["diagnosis"]["recommended_action"] == "wait"
    assert "# MemOps Why-Stuck Diagnosis" in report


def test_export_diagnosis_artifacts_rejects_base_dir_that_is_a_file(
    tmp_path: Path,
) -> None:
    diagnosed = build_diagnosed_transaction()
    invalid_base_dir = tmp_path / "exports-root"
    invalid_base_dir.write_text("not-a-directory", encoding="utf-8")

    with pytest.raises(OSError):
        export_diagnosis_artifacts(diagnosed, invalid_base_dir)


def test_export_diagnosis_artifacts_rejects_existing_file_at_txid_artifact_path(
    tmp_path: Path,
) -> None:
    diagnosed = build_diagnosed_transaction()
    conflicting_artifact_path = tmp_path / VALID_TXID
    conflicting_artifact_path.write_text("conflict", encoding="utf-8")

    with pytest.raises(FileExistsError):
        export_diagnosis_artifacts(diagnosed, tmp_path)


def test_export_diagnosis_artifacts_rejects_directory_at_analysis_json_path(
    tmp_path: Path,
) -> None:
    diagnosed = build_diagnosed_transaction()
    artifact_dir = tmp_path / VALID_TXID
    artifact_dir.mkdir()
    (artifact_dir / "analysis.json").mkdir()

    with pytest.raises(IsADirectoryError):
        export_diagnosis_artifacts(diagnosed, tmp_path)
