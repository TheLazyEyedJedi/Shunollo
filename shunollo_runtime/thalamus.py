"""
RedisThalamus - Reference Implementation
----------------------------------------
The default, Open Source implementation of the Thalamus using Redis.
"""
import os
import json
import time
from typing import Dict, Any, List, Optional

from .interfaces import AbstractThalamus, ThalamusMiddleware


class RedisThalamus(AbstractThalamus):
    """Redis-backed implementation of the Thalamus."""

    def __init__(self, host: str = None, port: int = None, db: int = 0, middleware: List[ThalamusMiddleware] = None):
        super().__init__(middleware=middleware)
        # Defer import to prevent hard dependency if not using Redis
        import redis

        self.host = host or os.getenv("SHUNOLLO_REDIS_HOST") or os.getenv("REDIS_HOST", "localhost")
        self.port = int(port or os.getenv("SHUNOLLO_REDIS_PORT") or os.getenv("REDIS_PORT", 6379))
        self.db = db
        self._pool = None
        self._client: Optional[redis.Redis] = None
        self._connect()

    def _connect(self):
        """Establish connection pool."""
        import redis
        try:
            self._pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                socket_connect_timeout=2
            )
            self._client = redis.Redis(connection_pool=self._pool)
        except Exception as e:
            print(f"[RedisThalamus] [WARN] Init Failed: {e}")
            self._client = None

    @property
    def client(self):
        """Lazy resilient client accessor."""
        if not self._client:
            self._connect()
        return self._client

    def is_healthy(self) -> bool:
        """Check if Thalamus is reachable."""
        try:
            return self.client.ping()
        except Exception:
            return False

    def publish_stimulus(self, channel: str, stimulus: Dict[str, Any]) -> bool:
        """Relay a stimulus to a specific synaptic pathway (Queue)."""
        if not self.client:
            return False

        try:
            payload = self._apply_publish_middleware(channel, stimulus)
            if "timestamp" not in payload:
                payload["timestamp"] = time.time()

            self.client.lpush(channel, json.dumps(payload))
            return True
        except Exception as e:
            print(f"[RedisThalamus] [X] Signal Lost: {e}")
            return False

    def consume_stimulus(self, channel: str, timeout: int = 1) -> Dict[str, Any] | None:
        """Await a stimulus from a synaptic pathway."""
        if not self.client:
            time.sleep(timeout)
            return None

        try:
            item = self.client.brpop(channel, timeout=timeout)
            if item:
                _, data = item
                payload = json.loads(data)
                return self._apply_receive_middleware(channel, payload)
        except Exception:
            pass
        return None

    def broadcast_stimulus(self, channel: str, stimulus: Dict[str, Any]) -> bool:
        """Broadcast a signal to all listeners on a synaptic pathway (Pub/Sub)."""
        if not self.client:
            return False

        try:
            payload = self._apply_publish_middleware(channel, stimulus)
            if "timestamp" not in payload:
                payload["timestamp"] = time.time()

            self.client.publish(channel, json.dumps(payload))
            return True
        except Exception as e:
            print(f"[RedisThalamus] [X] Broadcast Failed: {e}")
            return False


# Singleton Instance (The Global Thalamus)
_thalamus_instance: Optional[RedisThalamus] = None


def get_thalamus(middleware: List[ThalamusMiddleware] = None) -> RedisThalamus:
    global _thalamus_instance
    if not _thalamus_instance:
        _thalamus_instance = RedisThalamus(middleware=middleware)
    return _thalamus_instance
