import json

import pytest

from memops.backends import (
    BackendFeeRecommendations,
    BackendTransaction,
    BackendTransactionSummary,
)
from memops.cli import format_inspection_json, format_why_stuck_json
from memops.diagnostics import build_transaction_fee_context
from memops.services import diagnose_why_stuck, inspect_transaction
from memops.services.exports import format_export_payload_json

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


class StubInspectionBackend:
    def __init__(self, transaction: BackendTransaction) -> None:
        self._transaction = transaction

    def get_transaction(self, txid: str) -> BackendTransaction:
        return self._transaction


def test_backend_transaction_summary_normalizes_exact_fee_evidence_from_fee_and_weight() -> None:
    summary = BackendTransactionSummary(
        txid=VALID_TXID,
        confirmed=False,
        fee_sats=400,
        weight_wu=561,
    )

    fee_evidence = summary.fee_evidence

    assert summary.virtual_size_vbytes == 141
    assert fee_evidence.source.value == "backend_summary"
    assert fee_evidence.completeness.value == "exact"
    assert fee_evidence.fee_sats == 400
    assert fee_evidence.weight_wu == 561
    assert fee_evidence.virtual_size_vbytes == 141
    assert fee_evidence.effective_fee_rate_sat_vb == pytest.approx(400 / 141)


def test_backend_transaction_summary_normalizes_exact_fee_evidence_from_fee_and_vsize() -> None:
    summary = BackendTransactionSummary(
        txid=VALID_TXID,
        confirmed=False,
        fee_sats=282,
        virtual_size_vbytes=141,
    )

    fee_evidence = summary.fee_evidence

    assert summary.weight_wu is None
    assert summary.virtual_size_vbytes == 141
    assert fee_evidence.source.value == "backend_summary"
    assert fee_evidence.completeness.value == "exact"
    assert fee_evidence.fee_sats == 282
    assert fee_evidence.weight_wu is None
    assert fee_evidence.virtual_size_vbytes == 141
    assert fee_evidence.effective_fee_rate_sat_vb == pytest.approx(2.0)


def test_backend_transaction_summary_marks_fee_evidence_incomplete_when_fields_missing() -> None:
    summary = BackendTransactionSummary(
        txid=VALID_TXID,
        confirmed=False,
        weight_wu=400,
    )

    fee_evidence = summary.fee_evidence

    assert summary.fee_sats is None
    assert summary.virtual_size_vbytes == 100
    assert fee_evidence.source.value == "backend_summary"
    assert fee_evidence.completeness.value == "incomplete"
    assert fee_evidence.fee_sats is None
    assert fee_evidence.weight_wu == 400
    assert fee_evidence.virtual_size_vbytes == 100
    assert fee_evidence.effective_fee_rate_sat_vb is None


def test_fee_context_requires_exact_fee_evidence_for_why_stuck_analysis() -> None:
    summary = BackendTransactionSummary(
        txid=VALID_TXID,
        confirmed=False,
        weight_wu=400,
    )

    with pytest.raises(ValueError, match="requires exact fee evidence"):
        build_transaction_fee_context(summary, RECOMMENDATIONS)


def test_why_stuck_json_and_export_json_include_summary_fee_evidence() -> None:
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

    why_stuck_payload = json.loads(format_why_stuck_json(diagnosed))
    export_payload = json.loads(format_export_payload_json(diagnosed))

    for payload in (why_stuck_payload, export_payload):
        assert payload["summary"]["fee_evidence"]["source"] == "backend_summary"
        assert payload["summary"]["fee_evidence"]["completeness"] == "exact"
        assert payload["summary"]["fee_evidence"]["fee_sats"] == 282
        assert payload["summary"]["fee_evidence"]["weight_wu"] is None
        assert payload["summary"]["fee_evidence"]["virtual_size_vbytes"] == 141
        assert payload["summary"]["fee_evidence"]["effective_fee_rate_sat_vb"] == pytest.approx(2.0)
        assert "fee_evidence" not in payload["fee_context"]


def test_inspection_json_regression_does_not_include_fee_evidence_or_diagnosis_fields() -> None:
    backend = StubInspectionBackend(
        BackendTransaction(
            txid=VALID_TXID,
            raw_hex=NON_SEGWIT_RBF_HEX,
        )
    )

    inspected = inspect_transaction(VALID_TXID, backend)
    payload = json.loads(format_inspection_json(inspected))

    assert payload["txid"] == VALID_TXID
    assert payload["analysis"]["signals_explicit_rbf"] is True
    assert set(payload) == {"txid", "raw_hex", "parsed", "analysis"}
    assert "summary" not in payload
    assert "fee_context" not in payload
    assert "diagnosis" not in payload
    assert "fee_evidence" not in payload
