"""
AbstractThalamus (The Nervous System Contract)
----------------------------------------------
The interface for the Synaptic Bus.
The Runtime (or App) must implement this using Redis, Kafka, or Memory.

This interface supports a MIDDLEWARE chain to allow Commercial Apps to
inject proprietary logic (Audit, Security) without modifying the Open Source code.
"""
from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, List


class ThalamusMiddleware(ABC):
    """
    Hook for intercepting messages on the bus.
    E.g., AuditLogging, Encryption, RBAC.
    """
    @abstractmethod
    def on_publish(self, channel: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Called before a message is published. Can modify payload."""
        pass

    @abstractmethod
    def on_receive(self, channel: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Called after a message is received. Can modify payload."""
        pass


class AbstractThalamus(ABC):
    """
    The Biomimetic Bus.
    Decouples the 'Brain' (Analyzers) from the 'Body' (Sensors).
    """

    def __init__(self, middleware: List[ThalamusMiddleware] = None):
        self._middleware = middleware or []

    def _apply_publish_middleware(self, channel: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all publish hooks."""
        for mw in self._middleware:
            payload = mw.on_publish(channel, payload)
        return payload

    def _apply_receive_middleware(self, channel: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all receive hooks."""
        for mw in self._middleware:
            payload = mw.on_receive(channel, payload)
        return payload

    @abstractmethod
    def publish_stimulus(self, channel: str, stimulus: Dict[str, Any]) -> bool:
        """Send a nerve impulse (Stimulus) to the system."""
        pass

    @abstractmethod
    def consume_stimulus(self, channel: str, timeout: int = 1) -> Dict[str, Any] | None:
        """Await a nerve impulse from a synaptic pathway (Queue)."""
        pass

    @abstractmethod
    def broadcast_stimulus(self, channel: str, stimulus: Dict[str, Any]) -> bool:
        """Broadcast a signal to all listeners on a synaptic pathway (Pub/Sub)."""
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if Thalamus is reachable."""
        pass
