import json

from memops.backends import (
    BackendFeeRecommendations,
    BackendTransaction,
    BackendTransactionSummary,
)
from memops.services import diagnose_why_stuck
from memops.services.exports import (
    diagnosis_to_export_payload,
    format_export_payload_json,
    render_diagnosis_markdown,
)

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


def build_diagnosed_transaction():
    return diagnose_why_stuck(
        VALID_TXID,
        StubDiagnosisBackend(
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
        ),
    )


def test_diagnosis_to_export_payload_returns_expected_structure() -> None:
    diagnosed = build_diagnosed_transaction()

    payload = diagnosis_to_export_payload(diagnosed)

    assert payload["txid"] == VALID_TXID
    assert payload["raw_hex"] == NON_SEGWIT_RBF_HEX
    assert payload["parsed"]["version"] == 1
    assert payload["parsed"]["input_count"] == 1
    assert payload["parsed"]["output_count"] == 1
    assert payload["parsed"]["locktime"] == 0
    assert payload["parsed"]["sequences"] == [0xFFFFFFFD]
    assert payload["parsed"]["is_segwit"] is False
    assert payload["analysis"]["signals_explicit_rbf"] is True
    assert payload["analysis"]["signaling_input_indexes"] == [0]
    assert payload["summary"]["confirmed"] is False
    assert payload["summary"]["fee_sats"] == 1200
    assert payload["summary"]["weight_wu"] == 400
    assert payload["summary"]["virtual_size_vbytes"] == 100
    assert payload["fee_context"]["fee_rate_sat_vb"] == 12.0
    assert payload["fee_context"]["market_position"] == "below_hour"
    assert payload["fee_context"]["target_fee_rate_sat_vb"] == 15
    assert payload["fee_context"]["fee_rate_shortfall_sat_vb"] == 3.0
    assert payload["fee_context"]["recommended_fees"]["minimum_fee_sat_vb"] == 5
    assert payload["diagnosis"]["recommended_action"] == "wait"
    assert payload["diagnosis"]["severity"] == "warning"
    assert payload["diagnosis"]["reason"] == "fee_below_priority_band"
    assert payload["diagnosis"]["explicitly_signals_rbf"] is True


def test_format_export_payload_json_returns_valid_json() -> None:
    diagnosed = build_diagnosed_transaction()

    payload = json.loads(format_export_payload_json(diagnosed))

    assert payload["txid"] == VALID_TXID
    assert payload["analysis"]["signals_explicit_rbf"] is True
    assert payload["fee_context"]["market_position"] == "below_hour"
    assert payload["diagnosis"]["recommended_action"] == "wait"


def test_render_diagnosis_markdown_includes_expected_sections() -> None:
    diagnosed = build_diagnosed_transaction()

    report = render_diagnosis_markdown(diagnosed)

    assert "# MemOps Why-Stuck Diagnosis" in report
    assert "## Transaction" in report
    assert f"- txid: {VALID_TXID}" in report
    assert "- confirmed: no" in report
    assert "- fee_sats: 1200" in report
    assert "- weight_wu: 400" in report
    assert "- virtual_size_vbytes: 100" in report
    assert "- fee_rate_sat_vb: 12.00" in report
    assert "- market_position: below_hour" in report
    assert "- target_fee_rate_sat_vb: 15" in report
    assert "- fee_rate_shortfall_sat_vb: 3.00" in report
    assert "## Fee Recommendations" in report
    assert "- minimum_fee_sat_vb: 5" in report
    assert "## Parsed Transaction" in report
    assert "- segwit: no" in report
    assert "- explicit_rbf: yes" in report
    assert "- signaling_inputs: 0" in report
    assert "## Diagnosis" in report
    assert "- recommended_action: wait" in report
    assert "- severity: warning" in report
    assert "- reason: fee_below_priority_band" in report
    assert "### Summary" in report
    assert "The transaction is paying below the faster confirmation bands." in report
    assert "### Explanation" in report
