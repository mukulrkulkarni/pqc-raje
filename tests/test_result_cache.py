"""Security and boundary tests for the single-worker result download cache."""
from concurrent.futures import ThreadPoolExecutor

import pytest

from app.services.result_cache import (
    DOWNLOADS_PER_MINUTE, TOTAL_CACHE_BYTES, TTL_SECONDS, LatestResultCache,
)


class Clock:
    def __init__(self):
        self.value = 1000.0

    def __call__(self):
        return self.value


def test_split_manifest_reassembles_exact_bytes_and_enforces_limits():
    cache = LatestResultCache()
    payload = b"x" * (16 * 1024 * 1024 + 7)
    token = cache.store("session-a", "result.json", payload)
    assert cache.download("session-a", token) == ("result.json", payload)
    with pytest.raises(ValueError, match="32 MiB"):
        cache.store("session-a", "too-large.json", b"x" * (TOTAL_CACHE_BYTES + 1))


def test_tokens_are_opaque_bound_latest_only_and_restart_invalid():
    cache = LatestResultCache()
    first = cache.store("session-a", "result.json", b"first")
    second = cache.store("session-b", "result.json", b"second")
    assert first != second and len(first) >= 32
    assert cache.download("session-a", first) is None
    assert cache.download("session-a", second) is None
    assert cache.download("session-b", second) == ("result.json", b"second")
    assert LatestResultCache().download("session-b", second) is None


def test_expiry_and_successful_only_per_session_rate_limit():
    clock = Clock()
    cache = LatestResultCache(clock)
    token = cache.store("session-a", "result.json", b"bytes")
    assert cache.download("other", token) is None
    for _ in range(DOWNLOADS_PER_MINUTE):
        assert cache.download("session-a", token) == ("result.json", b"bytes")
    with pytest.raises(PermissionError, match="rate limit"):
        cache.download("session-a", token)
    clock.value += 60.1
    assert cache.download("session-a", token) == ("result.json", b"bytes")
    clock.value += TTL_SECONDS
    assert cache.download("session-a", token) is None


def test_concurrent_downloads_never_exceed_success_limit():
    cache = LatestResultCache()
    token = cache.store("session-a", "result.json", b"bytes")

    def attempt():
        try:
            return cache.download("session-a", token) is not None
        except PermissionError:
            return False

    with ThreadPoolExecutor(max_workers=40) as executor:
        outcomes = list(executor.map(lambda _: attempt(), range(40)))
    assert sum(outcomes) == DOWNLOADS_PER_MINUTE


def test_invalid_inputs_and_integrity_failure_do_not_serve_bytes():
    cache = LatestResultCache()
    with pytest.raises(ValueError, match="session_id"):
        cache.store("", "result.json", b"x")
    with pytest.raises(ValueError, match="payload"):
        cache.store("session-a", "result.json", "x")  # type: ignore[arg-type]
    token = cache.store("session-a", "result.json", b"bytes")
    entry = cache._entry
    assert entry is not None
    object.__setattr__(entry.artifact, "parts", (b"tampered",))
    with pytest.raises(ValueError, match="checksum"):
        cache.download("session-a", token)
    assert cache.download("session-a", token) is None
