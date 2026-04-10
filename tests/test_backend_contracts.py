import pytest

from memops.backends import (
    BackendFeeRecommendations,
    BackendTransaction,
    BackendTransactionSummary,
    FeeEvidenceCompleteness,
    FeeEvidenceSource,
    TransactionFeeEvidence,
    build_transaction_fee_evidence,
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


def test_transaction_fee_evidence_derives_exact_fee_rate_from_fee_and_weight() -> None:
    evidence = TransactionFeeEvidence(
        source=FeeEvidenceSource.BACKEND_SUMMARY,
        completeness=FeeEvidenceCompleteness.EXACT,
        fee_sats=280,
        weight_wu=561,
    )
    assert evidence.fee_sats == 280
    assert evidence.weight_wu == 561
    assert evidence.virtual_size_vbytes == 141
    assert evidence.effective_fee_rate_sat_vb == pytest.approx(280 / 141)


def test_build_transaction_fee_evidence_returns_exact_evidence_from_fee_and_vsize() -> None:
    evidence = build_transaction_fee_evidence(
        fee_sats=400,
        virtual_size_vbytes=100,
    )
    assert evidence.source is FeeEvidenceSource.BACKEND_SUMMARY
    assert evidence.completeness is FeeEvidenceCompleteness.EXACT
    assert evidence.fee_sats == 400
    assert evidence.weight_wu is None
    assert evidence.virtual_size_vbytes == 100
    assert evidence.effective_fee_rate_sat_vb == pytest.approx(4.0)


def test_build_transaction_fee_evidence_returns_incomplete_evidence_without_size_data() -> None:
    evidence = build_transaction_fee_evidence(fee_sats=400)
    assert evidence.completeness is FeeEvidenceCompleteness.INCOMPLETE
    assert evidence.fee_sats == 400
    assert evidence.weight_wu is None
    assert evidence.virtual_size_vbytes is None
    assert evidence.effective_fee_rate_sat_vb is None


def test_build_transaction_fee_evidence_returns_fallback_evidence_when_rate_is_provided() -> None:
    evidence = build_transaction_fee_evidence(
        weight_wu=561,
        fallback_fee_rate_sat_vb=12.5,
    )
    assert evidence.completeness is FeeEvidenceCompleteness.FALLBACK
    assert evidence.weight_wu == 561
    assert evidence.virtual_size_vbytes == 141
    assert evidence.effective_fee_rate_sat_vb == pytest.approx(12.5)


def test_build_transaction_fee_evidence_rejects_inconsistent_weight_and_vsize() -> None:
    with pytest.raises(ValueError, match="virtual_size_vbytes must match weight_wu"):
        build_transaction_fee_evidence(
            fee_sats=280,
            weight_wu=561,
            virtual_size_vbytes=140,
        )


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


def test_backend_fee_recommendations_accepts_monotonic_values() -> None:
    recommendations = BackendFeeRecommendations(
        fastest_fee_sat_vb=25,
        half_hour_fee_sat_vb=20,
        hour_fee_sat_vb=15,
        economy_fee_sat_vb=10,
        minimum_fee_sat_vb=5,
    )

    assert recommendations.fastest_fee_sat_vb == 25
    assert recommendations.half_hour_fee_sat_vb == 20
    assert recommendations.hour_fee_sat_vb == 15
    assert recommendations.economy_fee_sat_vb == 10
    assert recommendations.minimum_fee_sat_vb == 5


def test_backend_fee_recommendations_rejects_non_positive_values() -> None:
    with pytest.raises(ValueError, match="minimum_fee_sat_vb must be positive"):
        BackendFeeRecommendations(
            fastest_fee_sat_vb=10,
            half_hour_fee_sat_vb=8,
            hour_fee_sat_vb=6,
            economy_fee_sat_vb=4,
            minimum_fee_sat_vb=0,
        )


def test_backend_fee_recommendations_rejects_non_monotonic_values() -> None:
    with pytest.raises(ValueError, match="must be monotonic"):
        BackendFeeRecommendations(
            fastest_fee_sat_vb=10,
            half_hour_fee_sat_vb=12,
            hour_fee_sat_vb=9,
            economy_fee_sat_vb=4,
            minimum_fee_sat_vb=1,
        )
