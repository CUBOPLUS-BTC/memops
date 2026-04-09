from urllib import error

import pytest

from memops.backends import (
    BackendError,
    BackendTransaction,
    MempoolSpaceBackend,
    TransactionNotFoundError,
    build_mempool_api_base_url,
)
from memops.config import Settings

VALID_TXID = "ab" * 32


class FakeResponse:
    def __init__(self, body: str, *, status: int = 200) -> None:
        self._body = body.encode("utf-8")
        self.status = status

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None


@pytest.mark.parametrize(
    ("network", "expected"),
    [
        ("mainnet", "https://mempool.space/api"),
        ("testnet", "https://mempool.space/testnet/api"),
        ("signet", "https://mempool.space/signet/api"),
        ("regtest", "https://mempool.space/regtest/api"),
    ],
)
def test_build_mempool_api_base_url_selects_expected_network_path(
    network: str, expected: str
) -> None:
    assert build_mempool_api_base_url(" https://mempool.space/ ", network) == expected


def test_build_mempool_api_base_url_rejects_unknown_network() -> None:
    with pytest.raises(ValueError, match="unsupported network"):
        build_mempool_api_base_url("https://mempool.space", "liquid")


def test_mempool_space_backend_fetches_and_normalizes_transaction() -> None:
    calls: list[tuple[str, float]] = []

    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        calls.append((url, timeout))
        return FakeResponse("  0xAA bb  ")

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space/",
        network="signet",
        timeout=3.5,
        urlopen=fake_urlopen,
    )

    transaction = backend.get_transaction(VALID_TXID.upper())

    assert calls == [
        (f"https://mempool.space/signet/api/tx/{VALID_TXID}/hex", 3.5),
    ]
    assert transaction == BackendTransaction(txid=VALID_TXID, raw_hex="aabb")


def test_mempool_space_backend_from_settings_uses_application_config() -> None:
    settings = Settings(
        backend_url="https://example.com/",
        network="testnet",
    )

    backend = MempoolSpaceBackend.from_settings(settings)

    assert backend.api_base_url == "https://example.com/testnet/api"


def test_mempool_space_backend_rejects_non_positive_timeout() -> None:
    with pytest.raises(ValueError, match="timeout must be positive"):
        MempoolSpaceBackend(base_url="https://mempool.space", timeout=0)


def test_mempool_space_backend_maps_not_found_errors() -> None:
    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        raise error.HTTPError(url, 404, "not found", hdrs=None, fp=None)

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space",
        urlopen=fake_urlopen,
    )

    with pytest.raises(TransactionNotFoundError, match="transaction not found"):
        backend.get_transaction(VALID_TXID)


def test_mempool_space_backend_maps_unexpected_http_errors() -> None:
    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        raise error.HTTPError(url, 500, "server error", hdrs=None, fp=None)

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space",
        urlopen=fake_urlopen,
    )

    with pytest.raises(BackendError, match="unexpected status: 500"):
        backend.get_transaction(VALID_TXID)


def test_mempool_space_backend_maps_transport_errors() -> None:
    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        raise error.URLError("connection reset")

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space",
        urlopen=fake_urlopen,
    )

    with pytest.raises(BackendError, match="request failed"):
        backend.get_transaction(VALID_TXID)
