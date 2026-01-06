"""perception_bus – tiny pub/sub for sensory frames (in-memory)."""

from typing import Dict, Any, List, Callable

_subscribers: set[Callable[[Dict[str, Any]], None]] = set()


def publish(frame: Dict[str, Any]) -> None:
    """Broadcast a sensory frame (sound + light dict)."""
    for sub in list(_subscribers):
        try:
            sub(frame)
        except Exception as e:
            print(f"[PerceptionBus] Error in subscriber: {e}")


def subscribe(handler: Callable[[Dict[str, Any]], None]) -> None:
    """Register a callback to receive future frames."""
    _subscribers.add(handler)


def unsubscribe(handler: Callable[[Dict[str, Any]], None]) -> None:
    """Unregister a callback."""
    if handler in _subscribers:
        _subscribers.remove(handler)


def clear_subscribers() -> None:
    """Wipe all subscribers (Used for test isolation)."""
    _subscribers.clear()
