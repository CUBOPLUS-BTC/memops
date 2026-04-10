"""Backend contracts and value objects for MemOps data retrieval."""

from dataclasses import dataclass, field
from enum import StrEnum
from math import isclose, isfinite
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


def _normalize_optional_non_negative_int(
    value: int | None,
    *,
    field_name: str,
) -> int | None:
    """Validate that an optional value is either None or a non-negative integer."""
    if value is None:
        return None
    return _normalize_non_negative_int(value, field_name=field_name)


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


def _normalize_fee_rate(value: float, *, field_name: str) -> float:
    """Validate that a fee rate is a finite non-negative real number."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        msg = f"{field_name} must be a real number"
        raise ValueError(msg)

    normalized = float(value)
    if not isfinite(normalized):
        msg = f"{field_name} must be finite"
        raise ValueError(msg)
    if normalized < 0:
        msg = f"{field_name} must be non-negative"
        raise ValueError(msg)
    return normalized


def _normalize_optional_fee_rate(value: float | None, *, field_name: str) -> float | None:
    """Validate that an optional value is either None or a valid fee rate."""
    if value is None:
        return None
    return _normalize_fee_rate(value, field_name=field_name)


def _weight_to_virtual_size(weight_wu: int) -> int:
    """Convert transaction weight units to virtual size."""
    return (weight_wu + 3) // 4


class FeeEvidenceSource(StrEnum):
    """Normalized source for transaction fee evidence."""

    BACKEND_SUMMARY = "backend_summary"


class FeeEvidenceCompleteness(StrEnum):
    """Completeness of normalized transaction fee evidence."""

    EXACT = "exact"
    INCOMPLETE = "incomplete"
    FALLBACK = "fallback"


@dataclass(frozen=True, slots=True)
class TransactionFeeEvidence:
    """Normalized fee evidence derived from backend-provided transaction fields."""

    source: FeeEvidenceSource
    completeness: FeeEvidenceCompleteness
    fee_sats: int | None = None
    weight_wu: int | None = None
    virtual_size_vbytes: int | None = None
    effective_fee_rate_sat_vb: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.source, FeeEvidenceSource):
            msg = "source must be a FeeEvidenceSource"
            raise ValueError(msg)
        if not isinstance(self.completeness, FeeEvidenceCompleteness):
            msg = "completeness must be a FeeEvidenceCompleteness"
            raise ValueError(msg)

        normalized_fee_sats = _normalize_optional_non_negative_int(
            self.fee_sats,
            field_name="fee_sats",
        )
        normalized_weight = _normalize_optional_positive_int(
            self.weight_wu,
            field_name="weight_wu",
        )
        normalized_vsize = _normalize_optional_positive_int(
            self.virtual_size_vbytes,
            field_name="virtual_size_vbytes",
        )
        normalized_effective_fee_rate = _normalize_optional_fee_rate(
            self.effective_fee_rate_sat_vb,
            field_name="effective_fee_rate_sat_vb",
        )

        if normalized_weight is not None and normalized_vsize is None:
            normalized_vsize = _weight_to_virtual_size(normalized_weight)

        if normalized_weight is not None and normalized_vsize is not None:
            expected_vsize = _weight_to_virtual_size(normalized_weight)
            if normalized_vsize != expected_vsize:
                msg = "virtual_size_vbytes must match weight_wu"
                raise ValueError(msg)

        if self.completeness is FeeEvidenceCompleteness.EXACT:
            if normalized_fee_sats is None:
                msg = "exact fee evidence requires fee_sats"
                raise ValueError(msg)
            if normalized_vsize is None:
                msg = "exact fee evidence requires virtual_size_vbytes"
                raise ValueError(msg)

            expected_effective_fee_rate = normalized_fee_sats / normalized_vsize
            if normalized_effective_fee_rate is None:
                normalized_effective_fee_rate = expected_effective_fee_rate
            elif not isclose(
                normalized_effective_fee_rate,
                expected_effective_fee_rate,
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                msg = "effective_fee_rate_sat_vb must match fee_sats and virtual_size_vbytes"
                raise ValueError(msg)

        if (
            self.completeness is FeeEvidenceCompleteness.INCOMPLETE
            and normalized_effective_fee_rate is not None
        ):
            msg = "incomplete fee evidence cannot define effective_fee_rate_sat_vb"
            raise ValueError(msg)

        if (
            self.completeness is FeeEvidenceCompleteness.FALLBACK
            and normalized_effective_fee_rate is None
        ):
            msg = "fallback fee evidence requires effective_fee_rate_sat_vb"
            raise ValueError(msg)

        object.__setattr__(self, "fee_sats", normalized_fee_sats)
        object.__setattr__(self, "weight_wu", normalized_weight)
        object.__setattr__(self, "virtual_size_vbytes", normalized_vsize)
        object.__setattr__(
            self,
            "effective_fee_rate_sat_vb",
            normalized_effective_fee_rate,
        )


def build_transaction_fee_evidence(
    *,
    source: FeeEvidenceSource = FeeEvidenceSource.BACKEND_SUMMARY,
    fee_sats: int | None = None,
    weight_wu: int | None = None,
    virtual_size_vbytes: int | None = None,
    fallback_fee_rate_sat_vb: float | None = None,
) -> TransactionFeeEvidence:
    """Build normalized fee evidence from backend-provided transaction fields."""
    normalized_fee_sats = _normalize_optional_non_negative_int(
        fee_sats,
        field_name="fee_sats",
    )
    normalized_weight = _normalize_optional_positive_int(
        weight_wu,
        field_name="weight_wu",
    )
    normalized_vsize = _normalize_optional_positive_int(
        virtual_size_vbytes,
        field_name="virtual_size_vbytes",
    )
    normalized_fallback_fee_rate = _normalize_optional_fee_rate(
        fallback_fee_rate_sat_vb,
        field_name="fallback_fee_rate_sat_vb",
    )

    if normalized_weight is not None and normalized_vsize is None:
        normalized_vsize = _weight_to_virtual_size(normalized_weight)

    if normalized_weight is not None and normalized_vsize is not None:
        expected_vsize = _weight_to_virtual_size(normalized_weight)
        if normalized_vsize != expected_vsize:
            msg = "virtual_size_vbytes must match weight_wu"
            raise ValueError(msg)

    if normalized_fee_sats is not None and normalized_vsize is not None:
        return TransactionFeeEvidence(
            source=source,
            completeness=FeeEvidenceCompleteness.EXACT,
            fee_sats=normalized_fee_sats,
            weight_wu=normalized_weight,
            virtual_size_vbytes=normalized_vsize,
            effective_fee_rate_sat_vb=normalized_fee_sats / normalized_vsize,
        )

    if normalized_fallback_fee_rate is not None:
        return TransactionFeeEvidence(
            source=source,
            completeness=FeeEvidenceCompleteness.FALLBACK,
            fee_sats=normalized_fee_sats,
            weight_wu=normalized_weight,
            virtual_size_vbytes=normalized_vsize,
            effective_fee_rate_sat_vb=normalized_fallback_fee_rate,
        )

    return TransactionFeeEvidence(
        source=source,
        completeness=FeeEvidenceCompleteness.INCOMPLETE,
        fee_sats=normalized_fee_sats,
        weight_wu=normalized_weight,
        virtual_size_vbytes=normalized_vsize,
        effective_fee_rate_sat_vb=None,
    )


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
    fee_sats: int | None = None
    weight_wu: int | None = None
    virtual_size_vbytes: int | None = None
    block_height: int | None = None
    block_time: int | None = None
    fee_evidence: TransactionFeeEvidence = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "txid", normalize_txid(self.txid))

        if not isinstance(self.confirmed, bool):
            msg = "confirmed must be a boolean"
            raise ValueError(msg)

        fee_evidence = build_transaction_fee_evidence(
            source=FeeEvidenceSource.BACKEND_SUMMARY,
            fee_sats=self.fee_sats,
            weight_wu=self.weight_wu,
            virtual_size_vbytes=self.virtual_size_vbytes,
        )
        object.__setattr__(self, "fee_sats", fee_evidence.fee_sats)
        object.__setattr__(self, "weight_wu", fee_evidence.weight_wu)
        object.__setattr__(
            self,
            "virtual_size_vbytes",
            fee_evidence.virtual_size_vbytes,
        )
        object.__setattr__(self, "fee_evidence", fee_evidence)

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
