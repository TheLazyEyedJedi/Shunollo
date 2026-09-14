"""Persistence and transport-contract tests, with no external services."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from shunollo_runtime.audit import SQLiteAuditMiddleware
from shunollo_runtime.interfaces import AbstractThalamus


class LocalThalamus(AbstractThalamus):
    """Minimal test transport exercising the existing middleware chain."""

    def publish_stimulus(self, channel, stimulus):
        self.payload = self._apply_publish_middleware(channel, stimulus)
        return True

    def consume_stimulus(self, channel, timeout=1):
        return self._apply_receive_middleware(channel, self.payload)

    def broadcast_stimulus(self, channel, stimulus):
        return self.publish_stimulus(channel, stimulus)

    def is_healthy(self):
        return True


def test_transport_preserves_payload_and_persists_snapshot(tmp_path):
    path = tmp_path / "audit.sqlite"
    payload = {"energy": 0.3, "metadata": {"label": "sample"}}
    with SQLiteAuditMiddleware(path) as audit:
        transport = LocalThalamus(middleware=[audit])
        assert transport.publish_stimulus("sensor", payload)
        assert transport.consume_stimulus("sensor") is payload
        payload["metadata"]["label"] = "changed"
    with SQLiteAuditMiddleware(path) as audit:
        records = audit.records()
        assert [r["direction"] for r in records] == ["publish", "receive"]
        assert all(r["payload"]["metadata"]["label"] == "sample" for r in records)


def test_unrelated_domains_and_cursor(tmp_path):
    with SQLiteAuditMiddleware(tmp_path / "audit.sqlite") as audit:
        audit.on_publish("motor", {"vibration": [0.2, 0.3]})
        audit.on_publish("support", {"ticket_id": "T-1", "priority": "low"})
        first = audit.records(limit=1)
        second = audit.records(after_id=first[0]["id"], limit=1)
        assert second[0]["channel"] == "support"
        assert second[0]["payload"] == {"ticket_id": "T-1", "priority": "low"}
        assert audit.records(after_id=second[0]["id"]) == []


@pytest.mark.parametrize("value", [float("nan"), float("inf"), object()])
def test_rejects_unserializable_values_without_partial_write(tmp_path, value):
    with SQLiteAuditMiddleware(tmp_path / "audit.sqlite") as audit:
        with pytest.raises((ValueError, TypeError)):
            audit.on_publish("sensor", {"value": value})
        assert audit.records() == []
        audit.on_publish("sensor", {"value": 1})
        assert len(audit.records()) == 1


def test_concurrent_observations_are_committed(tmp_path):
    with SQLiteAuditMiddleware(tmp_path / "audit.sqlite") as audit:
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda i: audit.on_publish("sensor", {"i": i}), range(40)))
        rows = audit.records()
        assert len({r["id"] for r in rows}) == 40
        assert {r["payload"]["i"] for r in rows} == set(range(40))


def test_parameterized_storage_and_explicit_lifecycle(tmp_path):
    audit = SQLiteAuditMiddleware(tmp_path / "audit.sqlite")
    channel = "'); DROP TABLE runtime_signal_audit; --"
    audit.on_publish(channel, {"text": "quoted ' text"})
    assert audit.records()[0]["channel"] == channel
    audit.close()
    audit.close()
    with pytest.raises(RuntimeError, match="closed"):
        audit.records()
    with pytest.raises(RuntimeError, match="closed"):
        audit.on_publish("sensor", {})


@pytest.mark.parametrize("kwargs", [{"limit": 0}, {"limit": True}, {"after_id": -1}])
def test_invalid_cursor_arguments(tmp_path, kwargs):
    with SQLiteAuditMiddleware(tmp_path / "audit.sqlite") as audit:
        with pytest.raises(ValueError):
            audit.records(**kwargs)
