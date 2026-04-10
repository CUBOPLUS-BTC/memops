import pytest

from memops.backends import (
    BackendError,
    BackendFeeRecommendations,
    BackendTransaction,
    BackendTransactionSummary,
    TransactionNotFoundError,
)
from memops.diagnostics import FeeMarketPosition, WhyStuckAction, WhyStuckReason
from memops.services import DiagnosedTransaction, diagnose_why_stuck

VALID_TXID = "ab" * 32
OTHER_TXID = "cd" * 32
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


class SummaryFailingBackend:
    def __init__(self, transaction: BackendTransaction) -> None:
        self._transaction = transaction

    def get_transaction(self, txid: str) -> BackendTransaction:
        return self._transaction

    def get_transaction_summary(self, txid: str) -> BackendTransactionSummary:
        raise TransactionNotFoundError(f"transaction not found: {txid}")

    def get_fee_recommendations(self) -> BackendFeeRecommendations:
        raise AssertionError("fee recommendations should not be requested")


class RecommendationsFailingBackend:
    def __init__(
        self,
        *,
        transaction: BackendTransaction,
        summary: BackendTransactionSummary,
    ) -> None:
        self._transaction = transaction
        self._summary = summary

    def get_transaction(self, txid: str) -> BackendTransaction:
        return self._transaction

    def get_transaction_summary(self, txid: str) -> BackendTransactionSummary:
        return self._summary

    def get_fee_recommendations(self) -> BackendFeeRecommendations:
        raise BackendError("fee recommendations unavailable")


def test_diagnose_why_stuck_returns_replaceable_low_fee_diagnosis() -> None:
    backend = StubDiagnosisBackend(
        transaction=BackendTransaction(txid=VALID_TXID, raw_hex=NON_SEGWIT_RBF_HEX),
        summary=BackendTransactionSummary(
            txid=VALID_TXID,
            confirmed=False,
            fee_sats=400,
            weight_wu=400,
        ),
    )

    diagnosed = diagnose_why_stuck(VALID_TXID, backend)

    assert isinstance(diagnosed, DiagnosedTransaction)
    assert diagnosed.inspection.txid == VALID_TXID
    assert diagnosed.inspection.analysis.signals_explicit_rbf is True
    assert diagnosed.summary.txid == VALID_TXID
    assert diagnosed.fee_context.market_position is FeeMarketPosition.BELOW_MINIMUM
    assert diagnosed.fee_context.fee_rate_sat_vb == pytest.approx(4.0)
    assert diagnosed.diagnosis.reason is WhyStuckReason.LOW_FEE
    assert diagnosed.diagnosis.recommended_action is WhyStuckAction.BUMP_FEE_RBF
    assert diagnosed.diagnosis.explicitly_signals_rbf is True
    assert diagnosed.diagnosis.can_bump_fee is True


def test_diagnose_why_stuck_uses_local_rbf_analysis_for_final_transaction() -> None:
    backend = StubDiagnosisBackend(
        transaction=BackendTransaction(txid=VALID_TXID, raw_hex=SEGWIT_FINAL_HEX),
        summary=BackendTransactionSummary(
            txid=VALID_TXID,
            confirmed=False,
            fee_sats=400,
            weight_wu=400,
        ),
    )

    diagnosed = diagnose_why_stuck(VALID_TXID, backend)

    assert diagnosed.inspection.analysis.signals_explicit_rbf is False
    assert diagnosed.diagnosis.reason is WhyStuckReason.LOW_FEE
    assert diagnosed.diagnosis.recommended_action is WhyStuckAction.CONSIDER_MANUAL_CPFP
    assert diagnosed.diagnosis.explicitly_signals_rbf is False
    assert diagnosed.diagnosis.can_bump_fee is False


def test_diagnose_why_stuck_supports_exact_fee_evidence_without_weight() -> None:
    backend = StubDiagnosisBackend(
        transaction=BackendTransaction(txid=VALID_TXID, raw_hex=NON_SEGWIT_RBF_HEX),
        summary=BackendTransactionSummary(
            txid=VALID_TXID,
            confirmed=False,
            fee_sats=282,
            virtual_size_vbytes=141,
        ),
    )

    diagnosed = diagnose_why_stuck(VALID_TXID, backend)

    assert diagnosed.inspection.analysis.signals_explicit_rbf is True
    assert diagnosed.fee_context.weight_wu is None
    assert diagnosed.fee_context.virtual_size_vbytes == 141
    assert diagnosed.fee_context.fee_rate_sat_vb == pytest.approx(2.0)
    assert diagnosed.diagnosis.reason is WhyStuckReason.LOW_FEE
    assert diagnosed.diagnosis.recommended_action is WhyStuckAction.BUMP_FEE_RBF


def test_diagnose_why_stuck_returns_confirmed_diagnosis_for_confirmed_transaction() -> None:
    backend = StubDiagnosisBackend(
        transaction=BackendTransaction(txid=VALID_TXID, raw_hex=NON_SEGWIT_RBF_HEX),
        summary=BackendTransactionSummary(
            txid=VALID_TXID,
            confirmed=True,
            fee_sats=1200,
            weight_wu=400,
            block_height=840000,
            block_time=1_700_000_000,
        ),
    )

    diagnosed = diagnose_why_stuck(VALID_TXID, backend)

    assert diagnosed.fee_context.market_position is FeeMarketPosition.CONFIRMED
    assert diagnosed.diagnosis.reason is WhyStuckReason.CONFIRMED
    assert diagnosed.diagnosis.recommended_action is WhyStuckAction.NONE
    assert diagnosed.diagnosis.confirmed is True
    assert diagnosed.diagnosis.explicitly_signals_rbf is True
    assert diagnosed.diagnosis.can_bump_fee is False


def test_diagnose_why_stuck_rejects_mismatched_summary_txid() -> None:
    backend = StubDiagnosisBackend(
        transaction=BackendTransaction(txid=VALID_TXID, raw_hex=NON_SEGWIT_RBF_HEX),
        summary=BackendTransactionSummary(
            txid=OTHER_TXID,
            confirmed=False,
            fee_sats=400,
            weight_wu=400,
        ),
    )

    with pytest.raises(
        ValueError,
        match="backend transaction summary txid does not match inspected transaction",
    ):
        diagnose_why_stuck(VALID_TXID, backend)


def test_diagnose_why_stuck_rejects_incomplete_fee_evidence() -> None:
    backend = StubDiagnosisBackend(
        transaction=BackendTransaction(txid=VALID_TXID, raw_hex=NON_SEGWIT_RBF_HEX),
        summary=BackendTransactionSummary(
            txid=VALID_TXID,
            confirmed=False,
            weight_wu=400,
        ),
    )

    with pytest.raises(ValueError, match="requires exact fee evidence"):
        diagnose_why_stuck(VALID_TXID, backend)


def test_diagnose_why_stuck_propagates_transaction_summary_errors() -> None:
    backend = SummaryFailingBackend(
        BackendTransaction(txid=VALID_TXID, raw_hex=NON_SEGWIT_RBF_HEX),
    )

    with pytest.raises(TransactionNotFoundError, match="transaction not found"):
        diagnose_why_stuck(VALID_TXID, backend)


def test_diagnose_why_stuck_propagates_fee_recommendation_errors() -> None:
    backend = RecommendationsFailingBackend(
        transaction=BackendTransaction(txid=VALID_TXID, raw_hex=NON_SEGWIT_RBF_HEX),
        summary=BackendTransactionSummary(
            txid=VALID_TXID,
            confirmed=False,
            fee_sats=400,
            weight_wu=400,
        ),
    )

    with pytest.raises(BackendError, match="fee recommendations unavailable"):
        diagnose_why_stuck(VALID_TXID, backend)
