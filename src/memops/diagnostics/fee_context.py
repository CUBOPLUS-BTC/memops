"""Pure fee context analysis for why-stuck diagnosis."""

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

from memops.backends import BackendFeeRecommendations, BackendTransactionSummary


class FeeMarketPosition(StrEnum):
    """Relative position of a fee rate against backend recommendation bands."""

    CONFIRMED = "confirmed"
    BELOW_MINIMUM = "below_minimum"
    BELOW_ECONOMY = "below_economy"
    BELOW_HOUR = "below_hour"
    BELOW_HALF_HOUR = "below_half_hour"
    BELOW_FASTEST = "below_fastest"
    AT_OR_ABOVE_FASTEST = "at_or_above_fastest"


@dataclass(frozen=True, slots=True)
class TransactionFeeContext:
    """Normalized fee context used by the diagnosis workflow."""

    txid: str
    confirmed: bool
    fee_sats: int
    weight_wu: int
    virtual_size_vbytes: int
    fee_rate_sat_vb: float
    market_position: FeeMarketPosition
    target_fee_rate_sat_vb: int | None
    fee_rate_shortfall_sat_vb: float | None
    recommended_fees: BackendFeeRecommendations


def _normalize_non_negative_int(value: int, *, field_name: str) -> int:
    """Validate that a value is a non-negative integer."""
    if isinstance(value, bool) or not isinstance(value, int):
        msg = f"{field_name} must be an integer"
        raise ValueError(msg)
    if value < 0:
        msg = f"{field_name} must be non-negative"
        raise ValueError(msg)
    return value


def _normalize_positive_int(value: int, *, field_name: str) -> int:
    """Validate that a value is a positive integer."""
    normalized = _normalize_non_negative_int(value, field_name=field_name)
    if normalized == 0:
        msg = f"{field_name} must be positive"
        raise ValueError(msg)
    return normalized


def _normalize_fee_rate(value: float) -> float:
    """Validate that a fee rate is a finite non-negative real number."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        msg = "fee_rate_sat_vb must be a real number"
        raise ValueError(msg)

    normalized = float(value)
    if not isfinite(normalized):
        msg = "fee_rate_sat_vb must be finite"
        raise ValueError(msg)
    if normalized < 0:
        msg = "fee_rate_sat_vb must be non-negative"
        raise ValueError(msg)
    return normalized


def calculate_fee_rate_sat_vb(fee_sats: int, virtual_size_vbytes: int) -> float:
    """Calculate fee rate in sat/vB from fee and virtual size."""
    normalized_fee = _normalize_non_negative_int(fee_sats, field_name="fee_sats")
    normalized_vsize = _normalize_positive_int(
        virtual_size_vbytes,
        field_name="virtual_size_vbytes",
    )
    return normalized_fee / normalized_vsize


def classify_fee_market_position(
    fee_rate_sat_vb: float,
    recommendations: BackendFeeRecommendations,
    *,
    confirmed: bool = False,
) -> FeeMarketPosition:
    """Classify a fee rate relative to current backend recommendation bands."""
    if not isinstance(confirmed, bool):
        msg = "confirmed must be a boolean"
        raise ValueError(msg)

    if confirmed:
        return FeeMarketPosition.CONFIRMED

    normalized_fee_rate = _normalize_fee_rate(fee_rate_sat_vb)

    if normalized_fee_rate < recommendations.minimum_fee_sat_vb:
        return FeeMarketPosition.BELOW_MINIMUM
    if normalized_fee_rate < recommendations.economy_fee_sat_vb:
        return FeeMarketPosition.BELOW_ECONOMY
    if normalized_fee_rate < recommendations.hour_fee_sat_vb:
        return FeeMarketPosition.BELOW_HOUR
    if normalized_fee_rate < recommendations.half_hour_fee_sat_vb:
        return FeeMarketPosition.BELOW_HALF_HOUR
    if normalized_fee_rate < recommendations.fastest_fee_sat_vb:
        return FeeMarketPosition.BELOW_FASTEST
    return FeeMarketPosition.AT_OR_ABOVE_FASTEST


def determine_target_fee_rate_sat_vb(
    position: FeeMarketPosition,
    recommendations: BackendFeeRecommendations,
) -> int | None:
    """Return the next recommended fee-rate target for a classified position."""
    if position in {
        FeeMarketPosition.CONFIRMED,
        FeeMarketPosition.AT_OR_ABOVE_FASTEST,
    }:
        return None
    if position is FeeMarketPosition.BELOW_FASTEST:
        return recommendations.fastest_fee_sat_vb
    if position is FeeMarketPosition.BELOW_HALF_HOUR:
        return recommendations.half_hour_fee_sat_vb
    if position is FeeMarketPosition.BELOW_HOUR:
        return recommendations.hour_fee_sat_vb
    if position is FeeMarketPosition.BELOW_ECONOMY:
        return recommendations.economy_fee_sat_vb
    if position is FeeMarketPosition.BELOW_MINIMUM:
        return recommendations.minimum_fee_sat_vb

    msg = f"unsupported fee market position: {position}"
    raise ValueError(msg)


def build_transaction_fee_context(
    summary: BackendTransactionSummary,
    recommendations: BackendFeeRecommendations,
) -> TransactionFeeContext:
    """Build normalized fee context from transaction summary and fee bands."""
    fee_rate_sat_vb = calculate_fee_rate_sat_vb(
        summary.fee_sats,
        summary.virtual_size_vbytes,
    )
    market_position = classify_fee_market_position(
        fee_rate_sat_vb,
        recommendations,
        confirmed=summary.confirmed,
    )
    target_fee_rate_sat_vb = determine_target_fee_rate_sat_vb(
        market_position,
        recommendations,
    )
    fee_rate_shortfall_sat_vb = (
        None
        if target_fee_rate_sat_vb is None
        else max(target_fee_rate_sat_vb - fee_rate_sat_vb, 0.0)
    )

    return TransactionFeeContext(
        txid=summary.txid,
        confirmed=summary.confirmed,
        fee_sats=summary.fee_sats,
        weight_wu=summary.weight_wu,
        virtual_size_vbytes=summary.virtual_size_vbytes,
        fee_rate_sat_vb=fee_rate_sat_vb,
        market_position=market_position,
        target_fee_rate_sat_vb=target_fee_rate_sat_vb,
        fee_rate_shortfall_sat_vb=fee_rate_shortfall_sat_vb,
        recommended_fees=recommendations,
    )
