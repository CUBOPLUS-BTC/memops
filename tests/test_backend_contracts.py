import pytest

from memops.backends import (
    BackendTransaction,
    BackendTransactionSummary,
    normalize_raw_hex,
    normalize_txid,
)

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


def test_backend_transaction_summary_normalizes_and_derives_virtual_size() -> None:
    summary = BackendTransactionSummary(
        txid=f"  {VALID_TXID.upper()}  ",
        confirmed=True,
        fee_sats=141,
        weight_wu=561,
        block_height=900000,
        block_time=1_700_000_000,
    )

    assert summary.txid == VALID_TXID
    assert summary.confirmed is True
    assert summary.fee_sats == 141
    assert summary.weight_wu == 561
    assert summary.virtual_size_vbytes == 141
    assert summary.block_height == 900000
    assert summary.block_time == 1_700_000_000


def test_backend_transaction_summary_clears_block_metadata_for_unconfirmed_transactions() -> None:
    summary = BackendTransactionSummary(
        txid=VALID_TXID,
        confirmed=False,
        fee_sats=250,
        weight_wu=400,
        block_height=123,
        block_time=456,
    )

    assert summary.block_height is None
    assert summary.block_time is None
    assert summary.virtual_size_vbytes == 100


def test_backend_transaction_summary_rejects_negative_fee() -> None:
    with pytest.raises(ValueError, match="fee_sats must be non-negative"):
        BackendTransactionSummary(
            txid=VALID_TXID,
            confirmed=False,
            fee_sats=-1,
            weight_wu=400,
        )


def test_backend_transaction_summary_rejects_non_positive_weight() -> None:
    with pytest.raises(ValueError, match="weight_wu must be positive"):
        BackendTransactionSummary(
            txid=VALID_TXID,
            confirmed=False,
            fee_sats=1,
            weight_wu=0,
        )


def test_backend_transaction_summary_rejects_non_boolean_confirmed() -> None:
    with pytest.raises(ValueError, match="confirmed must be a boolean"):
        BackendTransactionSummary(
            txid=VALID_TXID,
            confirmed="yes",  # type: ignore[arg-type]
            fee_sats=1,
            weight_wu=4,
        )


def test_backend_transaction_summary_rejects_invalid_block_metadata_for_confirmed_tx() -> None:
    with pytest.raises(ValueError, match="block_height must be positive"):
        BackendTransactionSummary(
            txid=VALID_TXID,
            confirmed=True,
            fee_sats=1,
            weight_wu=4,
            block_height=0,
        )
