from io import StringIO

from memops.backends import BackendTransaction, TransactionNotFoundError
from memops.cli import format_inspection_report, main
from memops.services import inspect_transaction

VALID_TXID = "ab" * 32

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


class FailingBackend:
    def get_transaction(self, txid: str) -> BackendTransaction:
        raise TransactionNotFoundError(f"transaction not found: {txid}")


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
