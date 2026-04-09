import pytest

from memops.services import parse_raw_transaction

LEGACY_TX_HEX = (
    "01000000"
    "01"
    "1111111111111111111111111111111111111111111111111111111111111111"
    "00000000"
    "00"
    "ffffffff"
    "01"
    "e803000000000000"
    "00"
    "00000000"
)

SEGWIT_TX_HEX = (
    "02000000"
    "0001"
    "01"
    "2222222222222222222222222222222222222222222222222222222222222222"
    "01000000"
    "00"
    "fdffffff"
    "02"
    "e803000000000000"
    "00"
    "d007000000000000"
    "00"
    "02"
    "01aa"
    "02bbbb"
    "00000000"
)


def test_parse_raw_transaction_parses_legacy_transaction_metadata() -> None:
    parsed = parse_raw_transaction(LEGACY_TX_HEX)

    assert parsed.version == 1
    assert parsed.input_count == 1
    assert parsed.output_count == 1
    assert parsed.locktime == 0
    assert parsed.sequences == (0xFFFFFFFF,)
    assert parsed.is_segwit is False


def test_parse_raw_transaction_parses_segwit_transaction_metadata() -> None:
    parsed = parse_raw_transaction(SEGWIT_TX_HEX)

    assert parsed.version == 2
    assert parsed.input_count == 1
    assert parsed.output_count == 2
    assert parsed.locktime == 0
    assert parsed.sequences == (0xFFFFFFFD,)
    assert parsed.is_segwit is True


def test_parse_raw_transaction_accepts_prefixed_hex() -> None:
    parsed = parse_raw_transaction(f"  0x{LEGACY_TX_HEX}  ")

    assert parsed.version == 1


def test_parse_raw_transaction_rejects_invalid_hex() -> None:
    with pytest.raises(ValueError, match="valid hexadecimal"):
        parse_raw_transaction("zz")


def test_parse_raw_transaction_rejects_truncated_transaction() -> None:
    with pytest.raises(ValueError, match="too short"):
        parse_raw_transaction("01000000")


def test_parse_raw_transaction_rejects_trailing_bytes() -> None:
    with pytest.raises(ValueError, match="trailing bytes"):
        parse_raw_transaction(f"{LEGACY_TX_HEX}00")
