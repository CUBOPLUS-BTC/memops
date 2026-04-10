import math

import pytest

from memops.backends import BackendFeeRecommendations, BackendTransactionSummary
from memops.diagnostics import (
    FeeMarketPosition,
    TransactionFeeContext,
    build_transaction_fee_context,
    calculate_fee_rate_sat_vb,
    classify_fee_market_position,
    determine_target_fee_rate_sat_vb,
)

VALID_TXID = "ab" * 32
RECOMMENDATIONS = BackendFeeRecommendations(
    fastest_fee_sat_vb=25,
    half_hour_fee_sat_vb=20,
    hour_fee_sat_vb=15,
    economy_fee_sat_vb=10,
    minimum_fee_sat_vb=5,
)


def make_summary(
    *,
    fee_sats: int,
    weight_wu: int,
    confirmed: bool = False,
) -> BackendTransactionSummary:
    return BackendTransactionSummary(
        txid=VALID_TXID,
        confirmed=confirmed,
        fee_sats=fee_sats,
        weight_wu=weight_wu,
    )


def test_calculate_fee_rate_sat_vb_returns_expected_value() -> None:
    assert calculate_fee_rate_sat_vb(280, 141) == pytest.approx(280 / 141)


@pytest.mark.parametrize(
    ("fee_sats", "virtual_size_vbytes", "message"),
    [
        (-1, 100, "fee_sats must be non-negative"),
        (100, 0, "virtual_size_vbytes must be positive"),
        (True, 100, "fee_sats must be an integer"),
        (100, True, "virtual_size_vbytes must be an integer"),
    ],
)
def test_calculate_fee_rate_sat_vb_rejects_invalid_values(
    fee_sats: int,
    virtual_size_vbytes: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        calculate_fee_rate_sat_vb(fee_sats, virtual_size_vbytes)


@pytest.mark.parametrize(
    ("fee_rate_sat_vb", "expected_position"),
    [
        (0.0, FeeMarketPosition.BELOW_MINIMUM),
        (4.99, FeeMarketPosition.BELOW_MINIMUM),
        (5.0, FeeMarketPosition.BELOW_ECONOMY),
        (9.99, FeeMarketPosition.BELOW_ECONOMY),
        (10.0, FeeMarketPosition.BELOW_HOUR),
        (14.99, FeeMarketPosition.BELOW_HOUR),
        (15.0, FeeMarketPosition.BELOW_HALF_HOUR),
        (19.99, FeeMarketPosition.BELOW_HALF_HOUR),
        (20.0, FeeMarketPosition.BELOW_FASTEST),
        (24.99, FeeMarketPosition.BELOW_FASTEST),
        (25.0, FeeMarketPosition.AT_OR_ABOVE_FASTEST),
        (50.0, FeeMarketPosition.AT_OR_ABOVE_FASTEST),
    ],
)
def test_classify_fee_market_position_returns_expected_band(
    fee_rate_sat_vb: float,
    expected_position: FeeMarketPosition,
) -> None:
    assert classify_fee_market_position(fee_rate_sat_vb, RECOMMENDATIONS) is expected_position


def test_classify_fee_market_position_returns_confirmed_for_confirmed_tx() -> None:
    assert (
        classify_fee_market_position(
            1.0,
            RECOMMENDATIONS,
            confirmed=True,
        )
        is FeeMarketPosition.CONFIRMED
    )


@pytest.mark.parametrize(
    ("fee_rate_sat_vb", "message"),
    [
        (-1.0, "fee_rate_sat_vb must be non-negative"),
        (math.inf, "fee_rate_sat_vb must be finite"),
        (math.nan, "fee_rate_sat_vb must be finite"),
        ("1.0", "fee_rate_sat_vb must be a real number"),
        (True, "fee_rate_sat_vb must be a real number"),
    ],
)
def test_classify_fee_market_position_rejects_invalid_fee_rates(
    fee_rate_sat_vb: object,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        classify_fee_market_position(fee_rate_sat_vb, RECOMMENDATIONS)  # type: ignore[arg-type]


def test_classify_fee_market_position_rejects_non_boolean_confirmed() -> None:
    with pytest.raises(ValueError, match="confirmed must be a boolean"):
        classify_fee_market_position(
            1.0,
            RECOMMENDATIONS,
            confirmed="yes",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("position", "expected_target"),
    [
        (FeeMarketPosition.CONFIRMED, None),
        (FeeMarketPosition.BELOW_MINIMUM, 5),
        (FeeMarketPosition.BELOW_ECONOMY, 10),
        (FeeMarketPosition.BELOW_HOUR, 15),
        (FeeMarketPosition.BELOW_HALF_HOUR, 20),
        (FeeMarketPosition.BELOW_FASTEST, 25),
        (FeeMarketPosition.AT_OR_ABOVE_FASTEST, None),
    ],
)
def test_determine_target_fee_rate_sat_vb_returns_expected_target(
    position: FeeMarketPosition,
    expected_target: int | None,
) -> None:
    assert determine_target_fee_rate_sat_vb(position, RECOMMENDATIONS) == expected_target


def test_build_transaction_fee_context_for_low_fee_unconfirmed_transaction() -> None:
    summary = make_summary(
        fee_sats=280,
        weight_wu=561,
        confirmed=False,
    )

    context = build_transaction_fee_context(summary, RECOMMENDATIONS)

    assert isinstance(context, TransactionFeeContext)
    assert context.txid == VALID_TXID
    assert context.confirmed is False
    assert context.fee_sats == 280
    assert context.weight_wu == 561
    assert context.virtual_size_vbytes == 141
    assert context.fee_rate_sat_vb == pytest.approx(280 / 141)
    assert context.market_position is FeeMarketPosition.BELOW_MINIMUM
    assert context.target_fee_rate_sat_vb == 5
    assert context.fee_rate_shortfall_sat_vb == pytest.approx(5 - (280 / 141))
    assert context.fee_evidence == summary.fee_evidence
    assert context.recommended_fees == RECOMMENDATIONS


def test_build_transaction_fee_context_for_confirmed_transaction() -> None:
    summary = make_summary(
        fee_sats=1200,
        weight_wu=400,
        confirmed=True,
    )

    context = build_transaction_fee_context(summary, RECOMMENDATIONS)

    assert context.confirmed is True
    assert context.fee_rate_sat_vb == pytest.approx(12.0)
    assert context.market_position is FeeMarketPosition.CONFIRMED
    assert context.target_fee_rate_sat_vb is None
    assert context.fee_rate_shortfall_sat_vb is None
    assert context.fee_evidence == summary.fee_evidence


def test_build_transaction_fee_context_for_transaction_at_or_above_fastest_band() -> None:
    summary = make_summary(
        fee_sats=2600,
        weight_wu=400,
        confirmed=False,
    )

    context = build_transaction_fee_context(summary, RECOMMENDATIONS)

    assert context.weight_wu == 400
    assert context.virtual_size_vbytes == 100
    assert context.fee_rate_sat_vb == pytest.approx(26.0)
    assert context.market_position is FeeMarketPosition.AT_OR_ABOVE_FASTEST
    assert context.target_fee_rate_sat_vb is None
    assert context.fee_rate_shortfall_sat_vb is None
    assert context.fee_evidence == summary.fee_evidence


def test_build_transaction_fee_context_supports_exact_evidence_without_weight() -> None:
    summary = BackendTransactionSummary(
        txid=VALID_TXID,
        confirmed=False,
        fee_sats=282,
        virtual_size_vbytes=141,
    )

    context = build_transaction_fee_context(summary, RECOMMENDATIONS)

    assert context.fee_sats == 282
    assert context.weight_wu is None
    assert context.virtual_size_vbytes == 141
    assert context.fee_rate_sat_vb == pytest.approx(2.0)
    assert context.market_position is FeeMarketPosition.BELOW_MINIMUM
    assert context.target_fee_rate_sat_vb == 5
    assert context.fee_rate_shortfall_sat_vb == pytest.approx(3.0)
    assert context.fee_evidence == summary.fee_evidence


def test_build_transaction_fee_context_rejects_incomplete_fee_evidence() -> None:
    summary = BackendTransactionSummary(
        txid=VALID_TXID,
        confirmed=False,
        weight_wu=400,
    )

    with pytest.raises(ValueError, match="requires exact fee evidence"):
        build_transaction_fee_context(summary, RECOMMENDATIONS)
