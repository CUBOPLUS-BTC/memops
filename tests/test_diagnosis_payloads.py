from pathlib import Path

import pytest

from memops.backends import (
    BackendFeeRecommendations,
    BackendTransaction,
    BackendTransactionSummary,
)
from memops.cli import diagnosis_to_dict
from memops.services import diagnose_why_stuck
from memops.services.diagnosis_payloads import (
    build_backend_transaction_summary_payload,
    build_diagnosed_transaction_payload,
)
from memops.services.exports import DiagnosisArtifactPaths, diagnosis_to_export_payload

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


def test_build_backend_transaction_summary_payload_exposes_incomplete_fee_evidence() -> None:
    summary = BackendTransactionSummary(
        txid=VALID_TXID,
        confirmed=False,
        weight_wu=400,
    )

    payload = build_backend_transaction_summary_payload(summary)

    assert payload["txid"] == VALID_TXID
    assert payload["confirmed"] is False
    assert payload["fee_sats"] is None
    assert payload["weight_wu"] == 400
    assert payload["virtual_size_vbytes"] == 100
    assert payload["block_height"] is None
    assert payload["block_time"] is None
    assert payload["fee_evidence"]["source"] == "backend_summary"
    assert payload["fee_evidence"]["completeness"] == "incomplete"
    assert payload["fee_evidence"]["fee_sats"] is None
    assert payload["fee_evidence"]["weight_wu"] == 400
    assert payload["fee_evidence"]["virtual_size_vbytes"] == 100
    assert payload["fee_evidence"]["effective_fee_rate_sat_vb"] is None


def test_build_diagnosed_transaction_payload_exposes_fee_evidence_without_duplication() -> None:
    backend = StubDiagnosisBackend(
        transaction=BackendTransaction(
            txid=VALID_TXID,
            raw_hex=NON_SEGWIT_RBF_HEX,
        ),
        summary=BackendTransactionSummary(
            txid=VALID_TXID,
            confirmed=False,
            fee_sats=282,
            virtual_size_vbytes=141,
        ),
    )

    diagnosed = diagnose_why_stuck(VALID_TXID, backend)
    payload = build_diagnosed_transaction_payload(diagnosed)

    assert payload["txid"] == VALID_TXID
    assert payload["summary"]["fee_evidence"]["source"] == "backend_summary"
    assert payload["summary"]["fee_evidence"]["completeness"] == "exact"
    assert payload["summary"]["fee_evidence"]["fee_sats"] == 282
    assert payload["summary"]["fee_evidence"]["weight_wu"] is None
    assert payload["summary"]["fee_evidence"]["virtual_size_vbytes"] == 141
    assert payload["summary"]["fee_evidence"]["effective_fee_rate_sat_vb"] == pytest.approx(2.0)

    assert "fee_evidence" not in payload["fee_context"]
    assert payload["fee_context"]["fee_rate_sat_vb"] == pytest.approx(2.0)
    assert payload["fee_context"]["market_position"] == "below_minimum"
    assert payload["fee_context"]["recommended_fees"]["minimum_fee_sat_vb"] == 5

    assert payload["diagnosis"]["reason"] == "low_fee"
    assert payload["diagnosis"]["recommended_action"] == "bump_fee_rbf"


def test_cli_and_export_payloads_share_same_base_payload() -> None:
    backend = StubDiagnosisBackend(
        transaction=BackendTransaction(
            txid=VALID_TXID,
            raw_hex=NON_SEGWIT_RBF_HEX,
        ),
        summary=BackendTransactionSummary(
            txid=VALID_TXID,
            confirmed=False,
            fee_sats=400,
            weight_wu=400,
        ),
    )

    diagnosed = diagnose_why_stuck(VALID_TXID, backend)

    artifact_dir = Path("artifacts") / VALID_TXID
    artifact_paths = DiagnosisArtifactPaths(
        txid=VALID_TXID,
        artifact_dir=artifact_dir,
        analysis_json_path=artifact_dir / "analysis.json",
        report_markdown_path=artifact_dir / "report.md",
    )

    shared_payload = build_diagnosed_transaction_payload(diagnosed)
    export_payload = diagnosis_to_export_payload(diagnosed)
    cli_payload = diagnosis_to_dict(diagnosed, artifact_paths=artifact_paths)

    cli_payload_without_artifacts = dict(cli_payload)
    artifacts_payload = cli_payload_without_artifacts.pop("artifacts")

    assert export_payload == shared_payload
    assert cli_payload_without_artifacts == shared_payload
    assert artifacts_payload == {
        "artifact_dir": str(artifact_dir),
        "analysis_json_path": str(artifact_dir / "analysis.json"),
        "report_markdown_path": str(artifact_dir / "report.md"),
    }
    assert export_payload["summary"]["fee_evidence"]["completeness"] == "exact"
