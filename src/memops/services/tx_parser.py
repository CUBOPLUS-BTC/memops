"""Raw Bitcoin transaction parsing helpers."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParsedTransaction:
    """Minimal metadata extracted from a raw Bitcoin transaction."""

    version: int
    input_count: int
    output_count: int
    locktime: int
    sequences: tuple[int, ...]
    is_segwit: bool


def _read_bytes(payload: bytes, offset: int, size: int, *, context: str) -> tuple[bytes, int]:
    end = offset + size
    if end > len(payload):
        msg = f"unexpected end of transaction while reading {context}"
        raise ValueError(msg)
    return payload[offset:end], end


def _read_uint32(payload: bytes, offset: int, *, context: str) -> tuple[int, int]:
    raw_value, offset = _read_bytes(payload, offset, 4, context=context)
    return int.from_bytes(raw_value, "little"), offset


def _read_compact_size(payload: bytes, offset: int) -> tuple[int, int]:
    prefix_bytes, offset = _read_bytes(payload, offset, 1, context="compact size")
    prefix = prefix_bytes[0]

    if prefix < 0xFD:
        return prefix, offset

    if prefix == 0xFD:
        width = 2
    elif prefix == 0xFE:
        width = 4
    else:
        width = 8

    raw_value, offset = _read_bytes(payload, offset, width, context="compact size payload")
    return int.from_bytes(raw_value, "little"), offset


def parse_raw_transaction(raw_hex: str) -> ParsedTransaction:
    """Parse a raw transaction hex string into minimal metadata."""

    normalized = raw_hex.strip()
    if normalized.startswith(("0x", "0X")):
        normalized = normalized[2:]

    if not normalized:
        msg = "raw transaction hex must not be empty"
        raise ValueError(msg)

    try:
        payload = bytes.fromhex(normalized)
    except ValueError as exc:
        msg = "raw transaction must be valid hexadecimal"
        raise ValueError(msg) from exc

    return parse_raw_transaction_bytes(payload)


def parse_raw_transaction_bytes(payload: bytes) -> ParsedTransaction:
    """Parse raw transaction bytes into minimal metadata."""

    if len(payload) < 10:
        msg = "raw transaction is too short"
        raise ValueError(msg)

    offset = 0
    version, offset = _read_uint32(payload, offset, context="version")

    is_segwit = False
    if len(payload) >= offset + 2 and payload[offset] == 0 and payload[offset + 1] != 0:
        is_segwit = True
        offset += 2

    input_count, offset = _read_compact_size(payload, offset)

    sequences: list[int] = []
    for _ in range(input_count):
        _, offset = _read_bytes(payload, offset, 32, context="input prevout txid")
        _, offset = _read_bytes(payload, offset, 4, context="input prevout index")

        script_length, offset = _read_compact_size(payload, offset)
        _, offset = _read_bytes(payload, offset, script_length, context="input script")

        sequence, offset = _read_uint32(payload, offset, context="input sequence")
        sequences.append(sequence)

    output_count, offset = _read_compact_size(payload, offset)

    for _ in range(output_count):
        _, offset = _read_bytes(payload, offset, 8, context="output value")

        script_length, offset = _read_compact_size(payload, offset)
        _, offset = _read_bytes(payload, offset, script_length, context="output script")

    if is_segwit:
        for _ in range(input_count):
            item_count, offset = _read_compact_size(payload, offset)
            for _ in range(item_count):
                item_length, offset = _read_compact_size(payload, offset)
                _, offset = _read_bytes(payload, offset, item_length, context="witness item")

    locktime, offset = _read_uint32(payload, offset, context="locktime")

    if offset != len(payload):
        msg = "raw transaction has trailing bytes"
        raise ValueError(msg)

    return ParsedTransaction(
        version=version,
        input_count=input_count,
        output_count=output_count,
        locktime=locktime,
        sequences=tuple(sequences),
        is_segwit=is_segwit,
    )
