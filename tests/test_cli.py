import json
from io import StringIO

from memops.backends import (
    BackendFeeRecommendations,
    BackendTransaction,
    BackendTransactionSummary,
    TransactionNotFoundError,
)
from memops.cli import (
    diagnosis_to_dict,
    format_inspection_json,
    format_inspection_report,
    format_why_stuck_json,
    format_why_stuck_report,
    inspection_to_dict,
    main,
)
from memops.services import diagnose_why_stuck, inspect_transaction

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

SEGWIT_FINAL_HEX = "".join(
    [
        "02000000",
        "0001",
        "01",
        "11" * 32,
        "01000000",
        "00",
        "feffffff",
        "01",
        "0100000000000000",
        "00",
        "00",
        "00000000",
    ]
)


class StubBackend:
    def __init__(self, transaction: BackendTransaction) -> None:
        self._transaction = transaction

    def get_transaction(self, txid: str) -> BackendTransaction:
        return self._transaction


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


class FailingBackend:
    def get_transaction(self, txid: str) -> BackendTransaction:
        raise TransactionNotFoundError(f"transaction not found: {txid}")


def test_inspection_to_dict_returns_expected_structure() -> None:
    inspected = inspect_transaction(
        VALID_TXID,
        StubBackend(BackendTransaction(txid=VALID_TXID, raw_hex=NON_SEGWIT_RBF_HEX)),
    )

    assert inspection_to_dict(inspected) == {
        "txid": VALID_TXID,
        "raw_hex": NON_SEGWIT_RBF_HEX,
        "parsed": {
            "version": 1,
            "input_count": 1,
            "output_count": 1,
            "locktime": 0,
            "sequences": [0xFFFFFFFD],
            "is_segwit": False,
        },
        "analysis": {
            "signals_explicit_rbf": True,
            "signaling_input_indexes": [0],
        },
    }


def test_diagnosis_to_dict_returns_expected_structure() -> None:
    diagnosed = diagnose_why_stuck(
        VALID_TXID,
        StubDiagnosisBackend(
            transaction=BackendTransaction(txid=VALID_TXID, raw_hex=NON_SEGWIT_RBF_HEX),
            summary=BackendTransactionSummary(
                txid=VALID_TXID,
                confirmed=False,
                fee_sats=400,
                weight_wu=400,
            ),
        ),
    )

    payload = diagnosis_to_dict(diagnosed)

    assert payload["txid"] == VALID_TXID
    assert payload["parsed"]["version"] == 1
    assert payload["analysis"]["signals_explicit_rbf"] is True
    assert payload["summary"]["confirmed"] is False
    assert payload["summary"]["virtual_size_vbytes"] == 100
    assert payload["fee_context"]["market_position"] == "below_minimum"
    assert payload["fee_context"]["target_fee_rate_sat_vb"] == 5
    assert payload["fee_context"]["recommended_fees"]["minimum_fee_sat_vb"] == 5
    assert payload["diagnosis"]["reason"] == "low_fee"
    assert payload["diagnosis"]["recommended_action"] == "bump_fee_rbf"
    assert payload["diagnosis"]["explicitly_signals_rbf"] is True


def test_format_inspection_json_returns_valid_json() -> None:
    inspected = inspect_transaction(
        VALID_TXID,
        StubBackend(BackendTransaction(txid=VALID_TXID, raw_hex=SEGWIT_FINAL_HEX)),
    )

    payload = json.loads(format_inspection_json(inspected))

    assert payload["txid"] == VALID_TXID
    assert payload["parsed"]["version"] == 2
    assert payload["parsed"]["is_segwit"] is True
    assert payload["analysis"]["signals_explicit_rbf"] is False
    assert payload["analysis"]["signaling_input_indexes"] == []


def test_format_why_stuck_json_returns_valid_json() -> None:
    diagnosed = diagnose_why_stuck(
        VALID_TXID,
        StubDiagnosisBackend(
            transaction=BackendTransaction(txid=VALID_TXID, raw_hex=SEGWIT_FINAL_HEX),
            summary=BackendTransactionSummary(
                txid=VALID_TXID,
                confirmed=False,
                fee_sats=400,
                weight_wu=400,
            ),
        ),
    )

    payload = json.loads(format_why_stuck_json(diagnosed))

    assert payload["txid"] == VALID_TXID
    assert payload["analysis"]["signals_explicit_rbf"] is False
    assert payload["summary"]["fee_sats"] == 400
    assert payload["fee_context"]["market_position"] == "below_minimum"
    assert payload["diagnosis"]["recommended_action"] == "consider_manual_cpfp"
    assert payload["diagnosis"]["explicitly_signals_rbf"] is False


def test_format_inspection_report_includes_expected_fields() -> None:
    inspected = inspect_transaction(
        VALID_TXID,
        StubBackend(BackendTransaction(txid=VALID_TXID, raw_hex=NON_SEGWIT_RBF_HEX)),
    )

    report = format_inspection_report(inspected)

    assert f"txid: {VALID_TXID}" in report
    assert "version: 1" in report
    assert "inputs: 1" in report
    assert "outputs: 1" in report
    assert "locktime: 0" in report
    assert "segwit: no" in report
    assert "explicit_rbf: yes" in report
    assert "signaling_inputs: 0" in report


def test_format_why_stuck_report_includes_expected_fields() -> None:
    diagnosed = diagnose_why_stuck(
        VALID_TXID,
        StubDiagnosisBackend(
            transaction=BackendTransaction(txid=VALID_TXID, raw_hex=NON_SEGWIT_RBF_HEX),
            summary=BackendTransactionSummary(
                txid=VALID_TXID,
                confirmed=False,
                fee_sats=1200,
                weight_wu=400,
            ),
        ),
    )

    report = format_why_stuck_report(diagnosed)

    assert f"txid: {VALID_TXID}" in report
    assert "confirmed: no" in report
    assert "fee_sats: 1200" in report
    assert "weight_wu: 400" in report
    assert "virtual_size_vbytes: 100" in report
    assert "fee_rate_sat_vb: 12.00" in report
    assert "market_position: below_hour" in report
    assert "target_fee_rate_sat_vb: 15" in report
    assert "fee_rate_shortfall_sat_vb: 3.00" in report
    assert "explicit_rbf: yes" in report
    assert "recommended_action: wait" in report
    assert "severity: warning" in report
    assert "reason: fee_below_priority_band" in report
    assert "summary: The transaction is paying below the faster confirmation bands." in report
    assert "explanation:" in report


def test_main_prints_report_and_returns_zero() -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [VALID_TXID],
        backend=StubBackend(BackendTransaction(txid=VALID_TXID, raw_hex=SEGWIT_FINAL_HEX)),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""

    output = stdout.getvalue()
    assert f"txid: {VALID_TXID}" in output
    assert "segwit: yes" in output
    assert "explicit_rbf: no" in output
    assert "signaling_inputs: none" in output


def test_main_prints_json_report_when_requested() -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["--json", VALID_TXID],
        backend=StubBackend(BackendTransaction(txid=VALID_TXID, raw_hex=NON_SEGWIT_RBF_HEX)),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""

    payload = json.loads(stdout.getvalue())
    assert payload["txid"] == VALID_TXID
    assert payload["parsed"]["version"] == 1
    assert payload["parsed"]["is_segwit"] is False
    assert payload["analysis"]["signals_explicit_rbf"] is True
    assert payload["analysis"]["signaling_input_indexes"] == [0]


def test_main_prints_why_stuck_report_when_requested() -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["--why-stuck", VALID_TXID],
        backend=StubDiagnosisBackend(
            transaction=BackendTransaction(txid=VALID_TXID, raw_hex=NON_SEGWIT_RBF_HEX),
            summary=BackendTransactionSummary(
                txid=VALID_TXID,
                confirmed=False,
                fee_sats=1200,
                weight_wu=400,
            ),
        ),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""

    output = stdout.getvalue()
    assert f"txid: {VALID_TXID}" in output
    assert "fee_rate_sat_vb: 12.00" in output
    assert "explicit_rbf: yes" in output
    assert "recommended_action: wait" in output
    assert "severity: warning" in output
    assert "reason: fee_below_priority_band" in output


def test_main_prints_why_stuck_json_when_requested() -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["--why-stuck", "--json", VALID_TXID],
        backend=StubDiagnosisBackend(
            transaction=BackendTransaction(txid=VALID_TXID, raw_hex=SEGWIT_FINAL_HEX),
            summary=BackendTransactionSummary(
                txid=VALID_TXID,
                confirmed=False,
                fee_sats=400,
                weight_wu=400,
            ),
        ),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""

    payload = json.loads(stdout.getvalue())
    assert payload["txid"] == VALID_TXID
    assert payload["analysis"]["signals_explicit_rbf"] is False
    assert payload["fee_context"]["market_position"] == "below_minimum"
    assert payload["diagnosis"]["recommended_action"] == "consider_manual_cpfp"
    assert payload["diagnosis"]["severity"] == "high"


def test_main_reports_backend_errors_and_returns_one() -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [VALID_TXID],
        backend=FailingBackend(),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert "error: transaction not found" in stderr.getvalue()


def test_main_reports_why_stuck_backend_errors_and_returns_one() -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["--why-stuck", VALID_TXID],
        backend=FailingBackend(),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert "error: transaction not found" in stderr.getvalue()


def test_main_reports_parsing_errors_and_returns_one() -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [VALID_TXID],
        backend=StubBackend(BackendTransaction(txid=VALID_TXID, raw_hex="01000000")),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert "error:" in stderr.getvalue()
    assert "too short" in stderr.getvalue()
