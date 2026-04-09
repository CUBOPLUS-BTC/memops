"""Backend contracts and value objects for transaction retrieval."""

from dataclasses import dataclass
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


@dataclass(frozen=True, slots=True)
class BackendTransaction:
    """Raw transaction data returned by a backend."""

    txid: str
    raw_hex: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "txid", normalize_txid(self.txid))
        object.__setattr__(self, "raw_hex", normalize_raw_hex(self.raw_hex))


class TransactionBackend(Protocol):
    """Protocol for objects that can fetch raw transaction data."""

    def get_transaction(self, txid: str) -> BackendTransaction:
        """Fetch raw transaction data for the given txid."""
