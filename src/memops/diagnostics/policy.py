"""Pure diagnosis policy for why-stuck decisions."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from .fee_context import FeeMarketPosition, TransactionFeeContext

_SEVERE_LOW_FEE_POSITIONS: Final[frozenset[FeeMarketPosition]] = frozenset(
    {
        FeeMarketPosition.BELOW_MINIMUM,
        FeeMarketPosition.BELOW_ECONOMY,
    }
)
_SLOW_CONFIRMATION_POSITIONS: Final[frozenset[FeeMarketPosition]] = frozenset(
    {
        FeeMarketPosition.BELOW_HOUR,
        FeeMarketPosition.BELOW_HALF_HOUR,
        FeeMarketPosition.BELOW_FASTEST,
    }
)


class WhyStuckReason(StrEnum):
    """Normalized reason categories for why-stuck diagnosis."""

    CONFIRMED = "confirmed"
    LOW_FEE = "low_fee"
    FEE_BELOW_PRIORITY_BAND = "fee_below_priority_band"
    COMPETITIVE_FEE = "competitive_fee"


class WhyStuckAction(StrEnum):
    """Recommended next action for the user."""

    NONE = "none"
    WAIT = "wait"
    BUMP_FEE_RBF = "bump_fee_rbf"
    CONSIDER_MANUAL_CPFP = "consider_manual_cpfp"


class WhyStuckSeverity(StrEnum):
    """Severity of the current diagnosis."""

    INFO = "info"
    WARNING = "warning"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class WhyStuckDiagnosis:
    """Pure diagnosis result derived from fee context and local policy."""

    txid: str
    confirmed: bool
    reason: WhyStuckReason
    severity: WhyStuckSeverity
    recommended_action: WhyStuckAction
    explicitly_signals_rbf: bool
    can_bump_fee: bool
    market_position: FeeMarketPosition
    fee_rate_sat_vb: float
    target_fee_rate_sat_vb: int | None
    fee_rate_shortfall_sat_vb: float | None
    summary: str
    explanation: str


def _validate_boolean(value: bool, *, field_name: str) -> bool:
    """Validate that a value is a real boolean."""
    if not isinstance(value, bool):
        msg = f"{field_name} must be a boolean"
        raise ValueError(msg)
    return value


def _require_target_fee_rate_sat_vb(context: TransactionFeeContext) -> int:
    """Return a required target fee rate for underpriced transactions."""
    target_fee_rate_sat_vb = context.target_fee_rate_sat_vb
    if target_fee_rate_sat_vb is None:
        msg = "underpriced transaction context must define target fee rate"
        raise ValueError(msg)
    return target_fee_rate_sat_vb


def apply_why_stuck_policy(
    context: TransactionFeeContext,
    *,
    explicitly_signals_rbf: bool,
) -> WhyStuckDiagnosis:
    """Apply pure why-stuck policy to a normalized transaction fee context."""
    normalized_explicitly_signals_rbf = _validate_boolean(
        explicitly_signals_rbf,
        field_name="explicitly_signals_rbf",
    )

    if context.confirmed:
        if context.market_position is not FeeMarketPosition.CONFIRMED:
            msg = "confirmed transaction context must use confirmed market position"
            raise ValueError(msg)

        return WhyStuckDiagnosis(
            txid=context.txid,
            confirmed=True,
            reason=WhyStuckReason.CONFIRMED,
            severity=WhyStuckSeverity.INFO,
            recommended_action=WhyStuckAction.NONE,
            explicitly_signals_rbf=normalized_explicitly_signals_rbf,
            can_bump_fee=False,
            market_position=context.market_position,
            fee_rate_sat_vb=context.fee_rate_sat_vb,
            target_fee_rate_sat_vb=context.target_fee_rate_sat_vb,
            fee_rate_shortfall_sat_vb=context.fee_rate_shortfall_sat_vb,
            summary="Transaction is already confirmed.",
            explanation=(
                "The backend reports that the transaction is already included "
                "in a block, so it is not stuck in the mempool."
            ),
        )

    if context.market_position is FeeMarketPosition.CONFIRMED:
        msg = "unconfirmed transaction context cannot use confirmed market position"
        raise ValueError(msg)

    if context.market_position in _SEVERE_LOW_FEE_POSITIONS:
        target_fee_rate_sat_vb = _require_target_fee_rate_sat_vb(context)

        if normalized_explicitly_signals_rbf:
            return WhyStuckDiagnosis(
                txid=context.txid,
                confirmed=False,
                reason=WhyStuckReason.LOW_FEE,
                severity=WhyStuckSeverity.HIGH,
                recommended_action=WhyStuckAction.BUMP_FEE_RBF,
                explicitly_signals_rbf=True,
                can_bump_fee=True,
                market_position=context.market_position,
                fee_rate_sat_vb=context.fee_rate_sat_vb,
                target_fee_rate_sat_vb=context.target_fee_rate_sat_vb,
                fee_rate_shortfall_sat_vb=context.fee_rate_shortfall_sat_vb,
                summary="Current fee rate is too low for the present fee market.",
                explanation=(
                    f"The transaction pays {context.fee_rate_sat_vb:.2f} sat/vB "
                    f"and is currently in the '{context.market_position.value}' "
                    f"band. The next target band is {target_fee_rate_sat_vb} "
                    "sat/vB, and the transaction explicitly signals RBF, so a "
                    "fee bump is the clearest next step."
                ),
            )

        return WhyStuckDiagnosis(
            txid=context.txid,
            confirmed=False,
            reason=WhyStuckReason.LOW_FEE,
            severity=WhyStuckSeverity.HIGH,
            recommended_action=WhyStuckAction.CONSIDER_MANUAL_CPFP,
            explicitly_signals_rbf=False,
            can_bump_fee=False,
            market_position=context.market_position,
            fee_rate_sat_vb=context.fee_rate_sat_vb,
            target_fee_rate_sat_vb=context.target_fee_rate_sat_vb,
            fee_rate_shortfall_sat_vb=context.fee_rate_shortfall_sat_vb,
            summary=(
                "Current fee rate is too low and the transaction does not explicitly signal RBF."
            ),
            explanation=(
                f"The transaction pays {context.fee_rate_sat_vb:.2f} sat/vB "
                f"and is currently in the '{context.market_position.value}' "
                f"band. The next target band is {target_fee_rate_sat_vb} "
                "sat/vB, but without explicit RBF the safest advice is to wait "
                "or consider a manual CPFP if you control a spendable output."
            ),
        )

    if context.market_position in _SLOW_CONFIRMATION_POSITIONS:
        target_fee_rate_sat_vb = _require_target_fee_rate_sat_vb(context)

        return WhyStuckDiagnosis(
            txid=context.txid,
            confirmed=False,
            reason=WhyStuckReason.FEE_BELOW_PRIORITY_BAND,
            severity=WhyStuckSeverity.WARNING,
            recommended_action=WhyStuckAction.WAIT,
            explicitly_signals_rbf=normalized_explicitly_signals_rbf,
            can_bump_fee=normalized_explicitly_signals_rbf,
            market_position=context.market_position,
            fee_rate_sat_vb=context.fee_rate_sat_vb,
            target_fee_rate_sat_vb=context.target_fee_rate_sat_vb,
            fee_rate_shortfall_sat_vb=context.fee_rate_shortfall_sat_vb,
            summary="The transaction is paying below the faster confirmation bands.",
            explanation=(
                f"The transaction pays {context.fee_rate_sat_vb:.2f} sat/vB, "
                f"below the current {target_fee_rate_sat_vb} sat/vB target "
                "band, but it is not deeply underpriced. Waiting is a "
                "reasonable default under current fee pressure."
            ),
        )

    if context.market_position is FeeMarketPosition.AT_OR_ABOVE_FASTEST:
        return WhyStuckDiagnosis(
            txid=context.txid,
            confirmed=False,
            reason=WhyStuckReason.COMPETITIVE_FEE,
            severity=WhyStuckSeverity.INFO,
            recommended_action=WhyStuckAction.WAIT,
            explicitly_signals_rbf=normalized_explicitly_signals_rbf,
            can_bump_fee=normalized_explicitly_signals_rbf,
            market_position=context.market_position,
            fee_rate_sat_vb=context.fee_rate_sat_vb,
            target_fee_rate_sat_vb=context.target_fee_rate_sat_vb,
            fee_rate_shortfall_sat_vb=context.fee_rate_shortfall_sat_vb,
            summary="The transaction fee is competitive with the current market.",
            explanation=(
                f"The transaction pays {context.fee_rate_sat_vb:.2f} sat/vB, "
                "which is at or above the current fastest band of "
                f"{context.recommended_fees.fastest_fee_sat_vb} sat/vB. It is "
                "not obviously stuck because of low fees, so waiting is the "
                "right default."
            ),
        )

    msg = f"unsupported fee market position: {context.market_position}"
    raise ValueError(msg)
