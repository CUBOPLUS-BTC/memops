import pytest

from memops.backends import BackendTransaction, TransactionNotFoundError
from memops.services import ParsedTransaction, inspect_transaction

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


def test_inspect_transaction_returns_parsed_and_analyzed_non_segwit_transaction() -> None:
    backend = StubBackend(BackendTransaction(txid=VALID_TXID, raw_hex=NON_SEGWIT_RBF_HEX))

    inspected = inspect_transaction(VALID_TXID, backend)

    assert inspected.txid == VALID_TXID
    assert inspected.raw_hex == NON_SEGWIT_RBF_HEX
    assert inspected.parsed == ParsedTransaction(
        version=1,
        input_count=1,
        output_count=1,
        locktime=0,
        sequences=(0xFFFFFFFD,),
        is_segwit=False,
    )
    assert inspected.analysis.signals_explicit_rbf is True
    assert inspected.analysis.signaling_input_indexes == (0,)


def test_inspect_transaction_returns_parsed_and_analyzed_segwit_transaction() -> None:
    backend = StubBackend(BackendTransaction(txid=VALID_TXID, raw_hex=SEGWIT_FINAL_HEX))

    inspected = inspect_transaction(VALID_TXID, backend)

    assert inspected.txid == VALID_TXID
    assert inspected.parsed == ParsedTransaction(
        version=2,
        input_count=1,
        output_count=1,
        locktime=0,
        sequences=(0xFFFFFFFE,),
        is_segwit=True,
    )
    assert inspected.analysis.signals_explicit_rbf is False
    assert inspected.analysis.signaling_input_indexes == ()


def test_inspect_transaction_propagates_backend_errors() -> None:
    with pytest.raises(TransactionNotFoundError, match="transaction not found"):
        inspect_transaction(VALID_TXID, FailingBackend())


def test_inspect_transaction_propagates_parsing_errors() -> None:
    backend = StubBackend(
        BackendTransaction(
            txid=VALID_TXID,
            raw_hex="01000000",
        )
    )

    with pytest.raises(ValueError, match="too short"):
        inspect_transaction(VALID_TXID, backend)
