from memops.backends import (
    BackendFeeRecommendations,
    BackendTransaction,
    BackendTransactionSummary,
)
from memops.cli import format_why_stuck_report
from memops.services import diagnose_why_stuck
from memops.services.exports import render_diagnosis_markdown

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


def test_format_why_stuck_report_includes_fee_evidence_metadata() -> None:
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
    report = format_why_stuck_report(diagnosed)

    assert "fee_evidence_source: backend_summary" in report
    assert "fee_evidence_completeness: exact" in report


def test_render_diagnosis_markdown_includes_fee_evidence_metadata() -> None:
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
    markdown = render_diagnosis_markdown(diagnosed)

    assert "- fee_evidence_source: backend_summary" in markdown
    assert "- fee_evidence_completeness: exact" in markdown
