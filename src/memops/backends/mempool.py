"""mempool.space backend adapter."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Final, cast
from urllib import error, request

from memops.config import Network, Settings, get_settings

from .contracts import (
    BackendError,
    BackendTransaction,
    TransactionNotFoundError,
    normalize_txid,
)

_SUPPORTED_NETWORKS: Final[frozenset[str]] = frozenset({"mainnet", "testnet", "signet", "regtest"})
_DEFAULT_TIMEOUT: Final[float] = 10.0

Urlopen = Callable[..., Any]


def _normalize_base_url(base_url: str) -> str:
    normalized = base_url.strip().rstrip("/")
    if not normalized:
        msg = "base_url must not be empty"
        raise ValueError(msg)
    return normalized


def _normalize_network(network: str) -> Network:
    normalized = network.strip().lower()
    if normalized not in _SUPPORTED_NETWORKS:
        msg = f"unsupported network: {network}"
        raise ValueError(msg)
    return cast(Network, normalized)


def build_mempool_api_base_url(base_url: str, network: str) -> str:
    """Build the mempool.space API base URL for the configured network."""
    normalized_base_url = _normalize_base_url(base_url)
    normalized_network = _normalize_network(network)

    if normalized_network == "mainnet":
        return f"{normalized_base_url}/api"

    return f"{normalized_base_url}/{normalized_network}/api"


@dataclass(frozen=True, slots=True)
class MempoolSpaceBackend:
    """HTTP backend for retrieving transactions from mempool.space."""

    base_url: str
    network: Network = "mainnet"
    timeout: float = _DEFAULT_TIMEOUT
    urlopen: Urlopen = field(default=request.urlopen, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "base_url", _normalize_base_url(self.base_url))
        object.__setattr__(self, "network", _normalize_network(self.network))

        if self.timeout <= 0:
            msg = "timeout must be positive"
            raise ValueError(msg)

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "MempoolSpaceBackend":
        """Create a backend instance from application settings."""
        resolved_settings = settings if settings is not None else get_settings()
        return cls(
            base_url=resolved_settings.backend_url,
            network=resolved_settings.network,
        )

    @property
    def api_base_url(self) -> str:
        """Return the network-specific mempool.space API base URL."""
        return build_mempool_api_base_url(self.base_url, self.network)

    def get_transaction(self, txid: str) -> BackendTransaction:
        """Fetch a transaction from the backend by txid."""
        normalized_txid = normalize_txid(txid)
        url = f"{self.api_base_url}/tx/{normalized_txid}/hex"

        try:
            with self.urlopen(url, timeout=self.timeout) as response:
                status = getattr(response, "status", 200)
                if status != 200:
                    msg = f"backend returned unexpected status: {status}"
                    raise BackendError(msg)

                raw_hex = response.read().decode("utf-8")
        except error.HTTPError as exc:
            if exc.code == 404:
                msg = f"transaction not found: {normalized_txid}"
                raise TransactionNotFoundError(msg) from exc

            msg = f"backend returned unexpected status: {exc.code}"
            raise BackendError(msg) from exc
        except error.URLError as exc:
            msg = f"backend request failed: {exc.reason}"
            raise BackendError(msg) from exc

        return BackendTransaction(txid=normalized_txid, raw_hex=raw_hex)
