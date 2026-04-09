import pytest

from memops.services import ParsedTransaction, analyze_parsed_transaction


def test_analyze_parsed_transaction_flags_explicit_rbf_inputs() -> None:
    parsed = ParsedTransaction(
        version=2,
        input_count=3,
        output_count=2,
        locktime=0,
        sequences=(0xFFFFFFFF, 0xFFFFFFFD, 0xFFFFFFFE),
        is_segwit=True,
    )

    analysis = analyze_parsed_transaction(parsed)

    assert analysis.version == 2
    assert analysis.input_count == 3
    assert analysis.output_count == 2
    assert analysis.locktime == 0
    assert analysis.is_segwit is True
    assert analysis.sequences == (0xFFFFFFFF, 0xFFFFFFFD, 0xFFFFFFFE)
    assert analysis.signals_explicit_rbf is True
    assert analysis.signaling_input_indexes == (1,)


def test_analyze_parsed_transaction_reports_non_replaceable_when_no_input_signals() -> None:
    parsed = ParsedTransaction(
        version=1,
        input_count=2,
        output_count=1,
        locktime=0,
        sequences=(0xFFFFFFFF, 0xFFFFFFFE),
        is_segwit=False,
    )

    analysis = analyze_parsed_transaction(parsed)

    assert analysis.signals_explicit_rbf is False
    assert analysis.signaling_input_indexes == ()


def test_analyze_parsed_transaction_rejects_mismatched_sequence_count() -> None:
    parsed = ParsedTransaction(
        version=1,
        input_count=2,
        output_count=1,
        locktime=0,
        sequences=(0xFFFFFFFF,),
        is_segwit=False,
    )

    with pytest.raises(ValueError, match="sequence count"):
        analyze_parsed_transaction(parsed)
