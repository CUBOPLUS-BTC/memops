import pytest

from memops.services import any_input_signals_explicit_rbf, signals_explicit_rbf


@pytest.mark.parametrize(
    ("sequence", "expected"),
    [
        (0xFFFFFFFF, False),
        (0xFFFFFFFE, False),
        (0xFFFFFFFD, True),
        (1, True),
        (0, True),
    ],
)
def test_signals_explicit_rbf_matches_bip125_threshold(sequence: int, expected: bool) -> None:
    assert signals_explicit_rbf(sequence) is expected


@pytest.mark.parametrize("sequence", [-1, 0x100000000])
def test_signals_explicit_rbf_rejects_invalid_uint32_values(sequence: int) -> None:
    with pytest.raises(ValueError):
        signals_explicit_rbf(sequence)


def test_any_input_signals_explicit_rbf_returns_true_when_any_input_signals() -> None:
    assert any_input_signals_explicit_rbf([0xFFFFFFFF, 0xFFFFFFFD, 0xFFFFFFFF]) is True


def test_any_input_signals_explicit_rbf_returns_false_when_no_inputs_signal() -> None:
    assert any_input_signals_explicit_rbf([0xFFFFFFFF, 0xFFFFFFFE]) is False


def test_any_input_signals_explicit_rbf_returns_false_for_empty_iterable() -> None:
    assert any_input_signals_explicit_rbf([]) is False
