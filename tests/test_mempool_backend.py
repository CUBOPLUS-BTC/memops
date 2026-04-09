import json
from urllib import error

import pytest

from memops.backends import (
    BackendError,
    BackendTransaction,
    BackendTransactionSummary,
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


def make_transaction_summary_body(
    *,
    txid: str = VALID_TXID,
    fee: int = 280,
    weight: int = 561,
    confirmed: bool = False,
    block_height: int | None = None,
    block_time: int | None = None,
) -> str:
    status: dict[str, object] = {"confirmed": confirmed}
    if block_height is not None:
        status["block_height"] = block_height
    if block_time is not None:
        status["block_time"] = block_time

    return json.dumps(
        {
            "txid": txid,
            "fee": fee,
            "weight": weight,
            "status": status,
        }
    )


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


def test_mempool_space_backend_fetches_transaction_summary_for_unconfirmed_transaction() -> None:
    calls: list[tuple[str, float]] = []

    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        calls.append((url, timeout))
        return FakeResponse(
            make_transaction_summary_body(
                fee=280,
                weight=561,
                confirmed=False,
            )
        )

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space/",
        timeout=2.5,
        urlopen=fake_urlopen,
    )

    summary = backend.get_transaction_summary(VALID_TXID.upper())

    assert calls == [
        (f"https://mempool.space/api/tx/{VALID_TXID}", 2.5),
    ]
    assert summary == BackendTransactionSummary(
        txid=VALID_TXID,
        confirmed=False,
        fee_sats=280,
        weight_wu=561,
    )


def test_mempool_space_backend_fetches_transaction_summary_for_confirmed_transaction() -> None:
    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        return FakeResponse(
            make_transaction_summary_body(
                fee=1200,
                weight=800,
                confirmed=True,
                block_height=840000,
                block_time=1_700_000_000,
            )
        )

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space",
        urlopen=fake_urlopen,
    )

    summary = backend.get_transaction_summary(VALID_TXID)

    assert summary == BackendTransactionSummary(
        txid=VALID_TXID,
        confirmed=True,
        fee_sats=1200,
        weight_wu=800,
        block_height=840000,
        block_time=1_700_000_000,
    )


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


def test_mempool_space_backend_maps_not_found_errors_for_transaction_summary() -> None:
    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        raise error.HTTPError(url, 404, "not found", hdrs=None, fp=None)

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space",
        urlopen=fake_urlopen,
    )

    with pytest.raises(TransactionNotFoundError, match="transaction not found"):
        backend.get_transaction_summary(VALID_TXID)


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


def test_mempool_space_backend_rejects_invalid_transaction_summary_json() -> None:
    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        return FakeResponse("not-json")

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space",
        urlopen=fake_urlopen,
    )

    with pytest.raises(BackendError, match="invalid JSON"):
        backend.get_transaction_summary(VALID_TXID)


def test_mempool_space_backend_rejects_invalid_transaction_summary_payload() -> None:
    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        return FakeResponse(
            json.dumps(
                {
                    "txid": VALID_TXID,
                    "weight": 400,
                    "status": {"confirmed": False},
                }
            )
        )

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space",
        urlopen=fake_urlopen,
    )

    with pytest.raises(BackendError, match="invalid transaction summary payload"):
        backend.get_transaction_summary(VALID_TXID)


def test_mempool_space_backend_rejects_mismatched_transaction_summary_txid() -> None:
    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        return FakeResponse(
            make_transaction_summary_body(
                txid="cd" * 32,
                fee=300,
                weight=500,
                confirmed=False,
            )
        )

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space",
        urlopen=fake_urlopen,
    )

    with pytest.raises(BackendError, match="mismatched transaction summary"):
        backend.get_transaction_summary(VALID_TXID)
