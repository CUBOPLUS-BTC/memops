import pytest

from memops.backends import BackendFeeRecommendations, BackendTransactionSummary
from memops.diagnostics import (
    WhyStuckAction,
    WhyStuckDiagnosis,
    WhyStuckReason,
    WhyStuckSeverity,
    apply_why_stuck_policy,
    build_transaction_fee_context,
)

VALID_TXID = "ab" * 32
RECOMMENDATIONS = BackendFeeRecommendations(
    fastest_fee_sat_vb=25,
    half_hour_fee_sat_vb=20,
    hour_fee_sat_vb=15,
    economy_fee_sat_vb=10,
    minimum_fee_sat_vb=5,
)


def make_context(
    *,
    fee_sats: int,
    confirmed: bool = False,
) -> object:
    summary = BackendTransactionSummary(
        txid=VALID_TXID,
        confirmed=confirmed,
        fee_sats=fee_sats,
        weight_wu=400,
    )
    return build_transaction_fee_context(summary, RECOMMENDATIONS)


def test_apply_why_stuck_policy_rejects_non_boolean_rbf_flag() -> None:
    context = make_context(fee_sats=400)

    with pytest.raises(ValueError, match="explicitly_signals_rbf must be a boolean"):
        apply_why_stuck_policy(
            context,  # type: ignore[arg-type]
            explicitly_signals_rbf="yes",  # type: ignore[arg-type]
        )


def test_apply_why_stuck_policy_returns_confirmed_diagnosis() -> None:
    context = make_context(
        fee_sats=1200,
        confirmed=True,
    )

    diagnosis = apply_why_stuck_policy(
        context,  # type: ignore[arg-type]
        explicitly_signals_rbf=True,
    )

    assert isinstance(diagnosis, WhyStuckDiagnosis)
    assert diagnosis.txid == VALID_TXID
    assert diagnosis.confirmed is True
    assert diagnosis.reason is WhyStuckReason.CONFIRMED
    assert diagnosis.severity is WhyStuckSeverity.INFO
    assert diagnosis.recommended_action is WhyStuckAction.NONE
    assert diagnosis.explicitly_signals_rbf is True
    assert diagnosis.can_bump_fee is False
    assert diagnosis.target_fee_rate_sat_vb is None
    assert diagnosis.fee_rate_shortfall_sat_vb is None
    assert diagnosis.summary == "Transaction is already confirmed."
    assert "already included in a block" in diagnosis.explanation


def test_apply_why_stuck_policy_returns_low_fee_replaceable_diagnosis() -> None:
    context = make_context(fee_sats=400)

    diagnosis = apply_why_stuck_policy(
        context,  # type: ignore[arg-type]
        explicitly_signals_rbf=True,
    )

    assert diagnosis.reason is WhyStuckReason.LOW_FEE
    assert diagnosis.severity is WhyStuckSeverity.HIGH
    assert diagnosis.recommended_action is WhyStuckAction.BUMP_FEE_RBF
    assert diagnosis.explicitly_signals_rbf is True
    assert diagnosis.can_bump_fee is True
    assert diagnosis.target_fee_rate_sat_vb == 5
    assert diagnosis.fee_rate_shortfall_sat_vb == pytest.approx(1.0)
    assert diagnosis.summary == "Current fee rate is too low for the present fee market."
    assert "explicitly signals RBF" in diagnosis.explanation


def test_apply_why_stuck_policy_returns_low_fee_final_diagnosis() -> None:
    context = make_context(fee_sats=900)

    diagnosis = apply_why_stuck_policy(
        context,  # type: ignore[arg-type]
        explicitly_signals_rbf=False,
    )

    assert diagnosis.reason is WhyStuckReason.LOW_FEE
    assert diagnosis.severity is WhyStuckSeverity.HIGH
    assert diagnosis.recommended_action is WhyStuckAction.CONSIDER_MANUAL_CPFP
    assert diagnosis.explicitly_signals_rbf is False
    assert diagnosis.can_bump_fee is False
    assert diagnosis.target_fee_rate_sat_vb == 10
    assert diagnosis.fee_rate_shortfall_sat_vb == pytest.approx(1.0)
    assert "does not explicitly signal RBF" in diagnosis.summary
    assert "manual CPFP" in diagnosis.explanation


def test_apply_why_stuck_policy_returns_wait_diagnosis_for_priority_gap() -> None:
    context = make_context(fee_sats=1200)

    diagnosis = apply_why_stuck_policy(
        context,  # type: ignore[arg-type]
        explicitly_signals_rbf=True,
    )

    assert diagnosis.reason is WhyStuckReason.FEE_BELOW_PRIORITY_BAND
    assert diagnosis.severity is WhyStuckSeverity.WARNING
    assert diagnosis.recommended_action is WhyStuckAction.WAIT
    assert diagnosis.explicitly_signals_rbf is True
    assert diagnosis.can_bump_fee is True
    assert diagnosis.target_fee_rate_sat_vb == 15
    assert diagnosis.fee_rate_shortfall_sat_vb == pytest.approx(3.0)
    assert diagnosis.summary == "The transaction is paying below the faster confirmation bands."
    assert "not deeply underpriced" in diagnosis.explanation


def test_apply_why_stuck_policy_returns_wait_diagnosis_for_competitive_fee() -> None:
    context = make_context(fee_sats=2600)

    diagnosis = apply_why_stuck_policy(
        context,  # type: ignore[arg-type]
        explicitly_signals_rbf=False,
    )

    assert diagnosis.reason is WhyStuckReason.COMPETITIVE_FEE
    assert diagnosis.severity is WhyStuckSeverity.INFO
    assert diagnosis.recommended_action is WhyStuckAction.WAIT
    assert diagnosis.explicitly_signals_rbf is False
    assert diagnosis.can_bump_fee is False
    assert diagnosis.target_fee_rate_sat_vb is None
    assert diagnosis.fee_rate_shortfall_sat_vb is None
    assert diagnosis.summary == "The transaction fee is competitive with the current market."
    assert "not obviously stuck because of low fees" in diagnosis.explanation
