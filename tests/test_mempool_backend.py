import json
from urllib import error

import pytest

from memops.backends import (
    BackendError,
    BackendFeeRecommendations,
    BackendTransaction,
    BackendTransactionSummary,
    FeeEvidenceCompleteness,
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
    fee: int | None = 280,
    weight: int | None = 561,
    vsize: int | None = None,
    confirmed: bool = False,
    block_height: int | None = None,
    block_time: int | None = None,
) -> str:
    status: dict[str, object] = {"confirmed": confirmed}
    if block_height is not None:
        status["block_height"] = block_height
    if block_time is not None:
        status["block_time"] = block_time

    payload: dict[str, object] = {
        "txid": txid,
        "status": status,
    }
    if fee is not None:
        payload["fee"] = fee
    if weight is not None:
        payload["weight"] = weight
    if vsize is not None:
        payload["vsize"] = vsize

    return json.dumps(payload)


def make_fee_recommendations_body(
    *,
    fastest_fee: int = 25,
    half_hour_fee: int = 20,
    hour_fee: int = 15,
    economy_fee: int = 10,
    minimum_fee: int = 5,
) -> str:
    return json.dumps(
        {
            "fastestFee": fastest_fee,
            "halfHourFee": half_hour_fee,
            "hourFee": hour_fee,
            "economyFee": economy_fee,
            "minimumFee": minimum_fee,
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
    assert summary.fee_evidence.completeness is FeeEvidenceCompleteness.EXACT


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
    assert summary.fee_evidence.completeness is FeeEvidenceCompleteness.EXACT


def test_mempool_space_backend_fetches_transaction_summary_with_vsize_when_weight_is_missing() -> (
    None
):
    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        return FakeResponse(
            make_transaction_summary_body(
                fee=282,
                weight=None,
                vsize=141,
                confirmed=False,
            )
        )

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space",
        urlopen=fake_urlopen,
    )

    summary = backend.get_transaction_summary(VALID_TXID)

    assert summary == BackendTransactionSummary(
        txid=VALID_TXID,
        confirmed=False,
        fee_sats=282,
        virtual_size_vbytes=141,
    )
    assert summary.fee_evidence.completeness is FeeEvidenceCompleteness.EXACT
    assert summary.fee_evidence.effective_fee_rate_sat_vb == pytest.approx(2.0)


def test_mempool_space_backend_returns_incomplete_fee_evidence_when_fee_is_missing() -> None:
    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        return FakeResponse(
            make_transaction_summary_body(
                fee=None,
                weight=400,
                confirmed=False,
            )
        )

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space",
        urlopen=fake_urlopen,
    )

    summary = backend.get_transaction_summary(VALID_TXID)

    assert summary == BackendTransactionSummary(
        txid=VALID_TXID,
        confirmed=False,
        weight_wu=400,
    )
    assert summary.virtual_size_vbytes == 100
    assert summary.fee_evidence.completeness is FeeEvidenceCompleteness.INCOMPLETE
    assert summary.fee_evidence.effective_fee_rate_sat_vb is None


def test_mempool_space_backend_fetches_fee_recommendations() -> None:
    calls: list[tuple[str, float]] = []

    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        calls.append((url, timeout))
        return FakeResponse(
            make_fee_recommendations_body(
                fastest_fee=30,
                half_hour_fee=24,
                hour_fee=18,
                economy_fee=12,
                minimum_fee=6,
            )
        )

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space/",
        network="testnet",
        timeout=4.0,
        urlopen=fake_urlopen,
    )

    recommendations = backend.get_fee_recommendations()

    assert calls == [
        ("https://mempool.space/testnet/api/v1/fees/recommended", 4.0),
    ]
    assert recommendations == BackendFeeRecommendations(
        fastest_fee_sat_vb=30,
        half_hour_fee_sat_vb=24,
        hour_fee_sat_vb=18,
        economy_fee_sat_vb=12,
        minimum_fee_sat_vb=6,
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


def test_mempool_space_backend_maps_fee_recommendations_404_to_backend_error() -> None:
    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        raise error.HTTPError(url, 404, "not found", hdrs=None, fp=None)

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space",
        urlopen=fake_urlopen,
    )

    with pytest.raises(BackendError, match="unexpected status: 404"):
        backend.get_fee_recommendations()


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


def test_mempool_space_backend_rejects_invalid_fee_recommendations_json() -> None:
    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        return FakeResponse("not-json")

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space",
        urlopen=fake_urlopen,
    )

    with pytest.raises(BackendError, match="invalid JSON"):
        backend.get_fee_recommendations()


def test_mempool_space_backend_rejects_invalid_transaction_summary_payload() -> None:
    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        return FakeResponse(
            json.dumps(
                {
                    "txid": VALID_TXID,
                    "fee": "280",
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


def test_mempool_space_backend_rejects_invalid_fee_recommendations_payload() -> None:
    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        return FakeResponse(
            json.dumps(
                {
                    "fastestFee": 30,
                    "halfHourFee": 24,
                    "hourFee": 18,
                    "economyFee": 12,
                }
            )
        )

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space",
        urlopen=fake_urlopen,
    )

    with pytest.raises(BackendError, match="invalid fee recommendations payload"):
        backend.get_fee_recommendations()


def test_mempool_space_backend_rejects_non_monotonic_fee_recommendations_payload() -> None:
    def fake_urlopen(url: str, *, timeout: float) -> FakeResponse:
        return FakeResponse(
            make_fee_recommendations_body(
                fastest_fee=20,
                half_hour_fee=22,
                hour_fee=18,
                economy_fee=12,
                minimum_fee=6,
            )
        )

    backend = MempoolSpaceBackend(
        base_url="https://mempool.space",
        urlopen=fake_urlopen,
    )

    with pytest.raises(BackendError, match="invalid fee recommendations payload"):
        backend.get_fee_recommendations()


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
