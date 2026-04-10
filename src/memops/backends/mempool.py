"""mempool.space backend adapter."""

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Final, cast
from urllib import error, request

from memops.config import Network, Settings, get_settings

from .contracts import (
    BackendError,
    BackendFeeRecommendations,
    BackendTransaction,
    BackendTransactionSummary,
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


def _parse_transaction_summary_payload(
    requested_txid: str,
    payload: Any,
) -> BackendTransactionSummary:
    if not isinstance(payload, dict):
        msg = "backend returned invalid transaction summary payload"
        raise BackendError(msg)

    payload_txid = payload.get("txid")
    status = payload.get("status")

    if not isinstance(payload_txid, str) or not isinstance(status, dict):
        msg = "backend returned invalid transaction summary payload"
        raise BackendError(msg)

    try:
        normalized_payload_txid = normalize_txid(payload_txid)
    except ValueError as exc:
        msg = "backend returned invalid transaction summary payload"
        raise BackendError(msg) from exc

    if normalized_payload_txid != requested_txid:
        msg = "backend returned mismatched transaction summary"
        raise BackendError(msg)

    try:
        return BackendTransactionSummary(
            txid=normalized_payload_txid,
            confirmed=status.get("confirmed"),
            fee_sats=payload.get("fee"),
            weight_wu=payload.get("weight"),
            virtual_size_vbytes=payload.get("vsize"),
            block_height=status.get("block_height"),
            block_time=status.get("block_time"),
        )
    except ValueError as exc:
        msg = "backend returned invalid transaction summary payload"
        raise BackendError(msg) from exc


def _parse_fee_recommendations_payload(payload: Any) -> BackendFeeRecommendations:
    if not isinstance(payload, dict):
        msg = "backend returned invalid fee recommendations payload"
        raise BackendError(msg)

    try:
        return BackendFeeRecommendations(
            fastest_fee_sat_vb=payload.get("fastestFee"),
            half_hour_fee_sat_vb=payload.get("halfHourFee"),
            hour_fee_sat_vb=payload.get("hourFee"),
            economy_fee_sat_vb=payload.get("economyFee"),
            minimum_fee_sat_vb=payload.get("minimumFee"),
        )
    except ValueError as exc:
        msg = "backend returned invalid fee recommendations payload"
        raise BackendError(msg) from exc


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

    def _read_response_body(
        self,
        url: str,
        *,
        not_found_message: str | None = None,
    ) -> bytes:
        try:
            with self.urlopen(url, timeout=self.timeout) as response:
                status = getattr(response, "status", 200)
                if status != 200:
                    msg = f"backend returned unexpected status: {status}"
                    raise BackendError(msg)
                return response.read()
        except error.HTTPError as exc:
            if exc.code == 404 and not_found_message is not None:
                raise TransactionNotFoundError(not_found_message) from exc

            msg = f"backend returned unexpected status: {exc.code}"
            raise BackendError(msg) from exc
        except error.URLError as exc:
            msg = f"backend request failed: {exc.reason}"
            raise BackendError(msg) from exc

    def _read_text_response(
        self,
        url: str,
        *,
        not_found_message: str | None = None,
    ) -> str:
        payload = self._read_response_body(url, not_found_message=not_found_message)
        try:
            return payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            msg = "backend returned invalid text payload"
            raise BackendError(msg) from exc

    def _read_json_response(
        self,
        url: str,
        *,
        not_found_message: str | None = None,
    ) -> Any:
        payload = self._read_response_body(url, not_found_message=not_found_message)
        try:
            return json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            msg = "backend returned invalid JSON"
            raise BackendError(msg) from exc

    def get_transaction(self, txid: str) -> BackendTransaction:
        """Fetch a transaction from the backend by txid."""
        normalized_txid = normalize_txid(txid)
        url = f"{self.api_base_url}/tx/{normalized_txid}/hex"
        raw_hex = self._read_text_response(
            url,
            not_found_message=f"transaction not found: {normalized_txid}",
        )
        return BackendTransaction(txid=normalized_txid, raw_hex=raw_hex)

    def get_transaction_summary(self, txid: str) -> BackendTransactionSummary:
        """Fetch normalized transaction summary data for the given txid."""
        normalized_txid = normalize_txid(txid)
        url = f"{self.api_base_url}/tx/{normalized_txid}"
        payload = self._read_json_response(
            url,
            not_found_message=f"transaction not found: {normalized_txid}",
        )
        return _parse_transaction_summary_payload(normalized_txid, payload)

    def get_fee_recommendations(self) -> BackendFeeRecommendations:
        """Fetch normalized fee recommendations."""
        url = f"{self.api_base_url}/v1/fees/recommended"
        payload = self._read_json_response(url)
        return _parse_fee_recommendations_payload(payload)
