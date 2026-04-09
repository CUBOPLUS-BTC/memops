import pytest

from memops.backends import BackendTransaction, normalize_raw_hex, normalize_txid

VALID_TXID = "ab" * 32


def test_normalize_txid_strips_whitespace_and_lowercases() -> None:
    assert normalize_txid(f"  {VALID_TXID.upper()}  ") == VALID_TXID


@pytest.mark.parametrize("candidate", ["", "abc", "g0" * 32])
def test_normalize_txid_rejects_invalid_values(candidate: str) -> None:
    with pytest.raises(ValueError, match="64 hex characters"):
        normalize_txid(candidate)


def test_normalize_raw_hex_strips_prefix_whitespace_and_lowercases() -> None:
    assert normalize_raw_hex("  0xAA bb  ") == "aabb"


def test_normalize_raw_hex_rejects_empty_value() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        normalize_raw_hex("   ")


def test_normalize_raw_hex_rejects_invalid_hex() -> None:
    with pytest.raises(ValueError, match="valid hexadecimal"):
        normalize_raw_hex("zz")


def test_backend_transaction_normalizes_fields() -> None:
    transaction = BackendTransaction(
        txid=f"  {VALID_TXID.upper()}  ",
        raw_hex="  0xAA bb  ",
    )

    assert transaction.txid == VALID_TXID
    assert transaction.raw_hex == "aabb"
