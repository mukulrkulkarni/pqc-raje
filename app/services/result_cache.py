"""Bounded, single-worker, process-memory result cache for /app downloads."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import secrets
import threading
import time
from typing import Callable

from electre3.serialization import MAX_ARTIFACT_BYTES, reassemble_artifact, split_artifact

TOTAL_CACHE_BYTES = 32 * 1024 * 1024
TTL_SECONDS = 30 * 60
DOWNLOADS_PER_MINUTE = 30


@dataclass(frozen=True)
class CachedArtifact:
    """One immutable result artifact and its validated split representation."""

    name: str
    manifest: dict[str, object]
    parts: tuple[bytes, ...]
    byte_length: int


@dataclass(frozen=True)
class CacheEntry:
    """A token-bound cache entry, valid only within one process."""

    token: str
    session_id: str
    artifact: CachedArtifact
    expires_at: float


class LatestResultCache:
    """Keep one latest result with bounded bytes and successful-download rate state.

    An application restart creates a new instance, intentionally invalidating all
    tokens and rate state.  The lock serializes replacement, expiry, and download
    accounting for the single-worker deployment contract.
    """

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._lock = threading.RLock()
        self._entry: CacheEntry | None = None
        self._successful_downloads: dict[str, list[float]] = {}

    def store(self, session_id: str, name: str, payload: bytes) -> str:
        """Replace the cached result and return an opaque session-bound token."""
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("session_id is required")
        if not isinstance(payload, bytes):
            raise ValueError("payload must be bytes")
        if len(payload) > TOTAL_CACHE_BYTES:
            raise ValueError("result exceeds the 32 MiB cache limit")
        manifest, parts = split_artifact(name, payload, MAX_ARTIFACT_BYTES)
        # Validate before publication. This also protects exact-byte serving.
        if reassemble_artifact(manifest, parts) != payload:
            raise ValueError("split artifact failed exact-byte validation")
        artifact = CachedArtifact(name, manifest, parts, len(payload))
        token = secrets.token_urlsafe(32)
        with self._lock:
            now = self._clock()
            self._purge_locked(now)
            self._entry = CacheEntry(token, session_id, artifact, now + TTL_SECONDS)
            return token

    def download(self, session_id: str, token: str) -> tuple[str, bytes] | None:
        """Return exact bytes after token, session, expiry, and rate validation.

        A rate rejection does not consume a download. Invalid requests never alter
        rate state. The counter increments only after checksum-verified bytes exist.
        """
        if not isinstance(session_id, str) or not isinstance(token, str):
            return None
        with self._lock:
            now = self._clock()
            self._purge_locked(now)
            entry = self._entry
            if entry is None or not secrets.compare_digest(entry.token, token):
                return None
            if not secrets.compare_digest(entry.session_id, session_id):
                return None
            events = [point for point in self._successful_downloads.get(session_id, []) if point > now - 60]
            if len(events) >= DOWNLOADS_PER_MINUTE:
                self._successful_downloads[session_id] = events
                raise PermissionError("download rate limit exceeded")
            try:
                payload = reassemble_artifact(entry.artifact.manifest, entry.artifact.parts)
            except ValueError:
                self._entry = None
                raise
            if len(payload) != entry.artifact.byte_length or sha256(payload).hexdigest() != entry.artifact.manifest["sha256"]:
                self._entry = None
                raise ValueError("cached artifact integrity validation failed")
            events.append(now)
            self._successful_downloads[session_id] = events
            return entry.artifact.name, payload

    def _purge_locked(self, now: float) -> None:
        if self._entry is not None and self._entry.expires_at <= now:
            self._entry = None
        self._successful_downloads = {
            session_id: [point for point in events if point > now - 60]
            for session_id, events in self._successful_downloads.items()
            if any(point > now - 60 for point in events)
        }


result_cache = LatestResultCache()
