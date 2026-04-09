from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import ValidationError

from memops.config import Settings, get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_settings_defaults_use_expected_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MEMOPS_BACKEND_URL", raising=False)
    monkeypatch.delenv("MEMOPS_NETWORK", raising=False)
    monkeypatch.delenv("MEMOPS_EXPORT_DIR", raising=False)

    settings = Settings()

    assert settings.backend_url == "https://mempool.space"
    assert settings.network == "mainnet"
    assert settings.export_dir == Path("demo/output")


def test_settings_read_environment_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MEMOPS_BACKEND_URL", "https://mempool.space/")
    monkeypatch.setenv("MEMOPS_NETWORK", "signet")
    monkeypatch.setenv("MEMOPS_EXPORT_DIR", "/tmp/memops-exports")

    settings = Settings()

    assert settings.backend_url == "https://mempool.space"
    assert settings.network == "signet"
    assert settings.export_dir == Path("/tmp/memops-exports")


def test_settings_reject_empty_backend_url() -> None:
    with pytest.raises(ValidationError):
        Settings(backend_url="   ")


def test_settings_reject_invalid_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MEMOPS_NETWORK", "liquid")

    with pytest.raises(ValidationError):
        Settings()


def test_get_settings_returns_cached_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MEMOPS_BACKEND_URL", "https://example.com")

    first = get_settings()
    second = get_settings()

    assert first is second
    assert first.backend_url == "https://example.com"
