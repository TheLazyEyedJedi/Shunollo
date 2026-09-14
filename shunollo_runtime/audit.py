"""SQLite persistence for runtime signal envelopes; no domain decisions or math."""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Union

from .interfaces import ThalamusMiddleware


class SQLiteAuditMiddleware(ThalamusMiddleware):
    """Record middleware observations without altering their physical payload.

    Construction explicitly opens the supplied database; importing this module
    does not. The parent directory must already exist. Each hook commits before
    returning. A record proves that the hook ran, not that delivery succeeded.
    Serialization/storage errors propagate to the transport's error policy.
    Only JSON-compatible payloads with finite numbers are supported.
    """

    def __init__(self, path: Union[str, Path]) -> None:
        self._lock = threading.RLock()
        self._closed = False
        self._connection = sqlite3.connect(str(path), check_same_thread=False)
        try:
            with self._connection:
                self._connection.execute(
                    "CREATE TABLE IF NOT EXISTS runtime_signal_audit ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "observed_at REAL NOT NULL, direction TEXT NOT NULL, "
                    "channel TEXT NOT NULL, payload_json TEXT NOT NULL)"
                )
        except BaseException:
            self._connection.close()
            raise

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeError("Audit middleware is closed")

    def _record(self, direction: str, channel: str, payload: Dict[str, Any]) -> None:
        if not isinstance(channel, str) or not channel:
            raise ValueError("channel must be a nonempty string")
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dictionary")
        encoded = json.dumps(payload, allow_nan=False)
        with self._lock:
            self._require_open()
            with self._connection:
                self._connection.execute(
                    "INSERT INTO runtime_signal_audit "
                    "(observed_at, direction, channel, payload_json) VALUES (?, ?, ?, ?)",
                    (time.time(), direction, channel, encoded),
                )

    def on_publish(self, channel: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Persist an outgoing signal observation, preserving its payload."""
        self._record("publish", channel, payload)
        return payload

    def on_receive(self, channel: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Persist an incoming signal observation, preserving its payload."""
        self._record("receive", channel, payload)
        return payload

    def records(self, after_id: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Read observed signals in insertion order using a stable cursor."""
        if type(after_id) is not int or after_id < 0:
            raise ValueError("after_id must be a nonnegative integer")
        if type(limit) is not int or not 1 <= limit <= 10000:
            raise ValueError("limit must be an integer between 1 and 10000")
        with self._lock:
            self._require_open()
            rows = self._connection.execute(
                "SELECT id, observed_at, direction, channel, payload_json "
                "FROM runtime_signal_audit WHERE id > ? ORDER BY id LIMIT ?",
                (after_id, limit),
            ).fetchall()
        return [
            {"id": row[0], "observed_at": row[1], "direction": row[2],
             "channel": row[3], "payload": json.loads(row[4])}
            for row in rows
        ]

    def close(self) -> None:
        """Release the runtime persistence handle; repeated closes are safe."""
        with self._lock:
            if not self._closed:
                self._connection.close()
                self._closed = True

    def __enter__(self) -> SQLiteAuditMiddleware:
        self._require_open()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
