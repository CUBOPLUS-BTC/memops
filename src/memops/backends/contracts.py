"""Backend contracts and value objects for MemOps data retrieval."""

from dataclasses import dataclass, field
from typing import Protocol

_HEX_DIGITS = frozenset("0123456789abcdef")


class BackendError(RuntimeError):
    """Base error for backend-related failures."""


class TransactionNotFoundError(BackendError):
    """Raised when a backend cannot find a transaction by txid."""


def normalize_txid(txid: str) -> str:
    """Normalize and validate a transaction identifier."""
    normalized = txid.strip().lower()

    if len(normalized) != 64:
        msg = "txid must be 64 hex characters"
        raise ValueError(msg)
    if any(character not in _HEX_DIGITS for character in normalized):
        msg = "txid must be 64 hex characters"
        raise ValueError(msg)
    return normalized


def normalize_raw_hex(raw_hex: str) -> str:
    """Normalize and validate raw transaction hex."""
    normalized = raw_hex.strip().lower()
    if normalized.startswith("0x"):
        normalized = normalized[2:]
    normalized = "".join(normalized.split())
    if not normalized:
        msg = "raw_hex must not be empty"
        raise ValueError(msg)
    try:
        bytes.fromhex(normalized)
    except ValueError as exc:
        msg = "raw_hex must be valid hexadecimal"
        raise ValueError(msg) from exc
    return normalized


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


def _normalize_optional_positive_int(value: int | None, *, field_name: str) -> int | None:
    """Validate that an optional value is either None or a positive integer."""
    if value is None:
        return None
    return _normalize_positive_int(value, field_name=field_name)


def _weight_to_virtual_size(weight_wu: int) -> int:
    """Convert transaction weight units to virtual size."""
    return (weight_wu + 3) // 4


@dataclass(frozen=True, slots=True)
class BackendTransaction:
    """Raw transaction data returned by a backend."""

    txid: str
    raw_hex: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "txid", normalize_txid(self.txid))
        object.__setattr__(self, "raw_hex", normalize_raw_hex(self.raw_hex))


@dataclass(frozen=True, slots=True)
class BackendTransactionSummary:
    """Minimal backend-provided transaction summary used for diagnosis."""

    txid: str
    confirmed: bool
    fee_sats: int
    weight_wu: int
    block_height: int | None = None
    block_time: int | None = None
    virtual_size_vbytes: int = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "txid", normalize_txid(self.txid))

        if not isinstance(self.confirmed, bool):
            msg = "confirmed must be a boolean"
            raise ValueError(msg)

        normalized_fee = _normalize_non_negative_int(self.fee_sats, field_name="fee_sats")
        object.__setattr__(self, "fee_sats", normalized_fee)

        normalized_weight = _normalize_positive_int(self.weight_wu, field_name="weight_wu")
        object.__setattr__(self, "weight_wu", normalized_weight)
        object.__setattr__(
            self,
            "virtual_size_vbytes",
            _weight_to_virtual_size(normalized_weight),
        )

        if self.confirmed:
            normalized_block_height = _normalize_optional_positive_int(
                self.block_height,
                field_name="block_height",
            )
            normalized_block_time = _normalize_optional_positive_int(
                self.block_time,
                field_name="block_time",
            )
        else:
            normalized_block_height = None
            normalized_block_time = None

        object.__setattr__(self, "block_height", normalized_block_height)
        object.__setattr__(self, "block_time", normalized_block_time)


@dataclass(frozen=True, slots=True)
class BackendFeeRecommendations:
    """Normalized fee recommendation bands returned by a backend."""

    fastest_fee_sat_vb: int
    half_hour_fee_sat_vb: int
    hour_fee_sat_vb: int
    economy_fee_sat_vb: int
    minimum_fee_sat_vb: int

    def __post_init__(self) -> None:
        normalized_fastest = _normalize_positive_int(
            self.fastest_fee_sat_vb,
            field_name="fastest_fee_sat_vb",
        )
        normalized_half_hour = _normalize_positive_int(
            self.half_hour_fee_sat_vb,
            field_name="half_hour_fee_sat_vb",
        )
        normalized_hour = _normalize_positive_int(
            self.hour_fee_sat_vb,
            field_name="hour_fee_sat_vb",
        )
        normalized_economy = _normalize_positive_int(
            self.economy_fee_sat_vb,
            field_name="economy_fee_sat_vb",
        )
        normalized_minimum = _normalize_positive_int(
            self.minimum_fee_sat_vb,
            field_name="minimum_fee_sat_vb",
        )

        object.__setattr__(self, "fastest_fee_sat_vb", normalized_fastest)
        object.__setattr__(self, "half_hour_fee_sat_vb", normalized_half_hour)
        object.__setattr__(self, "hour_fee_sat_vb", normalized_hour)
        object.__setattr__(self, "economy_fee_sat_vb", normalized_economy)
        object.__setattr__(self, "minimum_fee_sat_vb", normalized_minimum)

        if not (
            normalized_fastest
            >= normalized_half_hour
            >= normalized_hour
            >= normalized_economy
            >= normalized_minimum
        ):
            msg = "fee recommendations must be monotonic"
            raise ValueError(msg)


class TransactionBackend(Protocol):
    """Protocol for objects that can fetch backend transaction data."""

    def get_transaction(self, txid: str) -> BackendTransaction:
        """Fetch raw transaction data for the given txid."""

    def get_transaction_summary(self, txid: str) -> BackendTransactionSummary:
        """Fetch normalized transaction summary data for the given txid."""

    def get_fee_recommendations(self) -> BackendFeeRecommendations:
        """Fetch normalized fee recommendations."""
