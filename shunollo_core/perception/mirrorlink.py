"""
mirrorlink.py – sound-based internal communication bus for agent signaling
"""

from typing import Dict, List, Optional
import time
import threading
import uuid


class Signal:
    def __init__(self, sender: str, payload: Dict, timestamp: Optional[float] = None):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.payload = payload
        self.timestamp = timestamp or time.time()

    def __repr__(self):
        return f"<Signal from {self.sender} @ {self.timestamp:.3f}>"

# ------------------------------------------------------------------ #
class MirrorLinkBus:
    """Central in-memory broadcast system for agents."""

    def __init__(self):
        self._subscribers: Dict[str, List] = {}
        self._log: List[Signal] = []
        self._lock = threading.Lock()

    def subscribe(self, agent_name: str, callback):
        """Register a listener for agent_name."""
        with self._lock:
            if agent_name not in self._subscribers:
                self._subscribers[agent_name] = []
            self._subscribers[agent_name].append(callback)

    def unsubscribe(self, agent_name: str, callback):
        """Unregister a listener."""
        with self._lock:
            if agent_name in self._subscribers:
                if callback in self._subscribers[agent_name]:
                    self._subscribers[agent_name].remove(callback)

    def clear(self):
        """Reset the bus state (Tests only)."""
        with self._lock:
            self._subscribers.clear()
            self._log.clear()

    def emit(self, sender: str, payload: Dict):
        """Broadcast a signal from sender to all subscribers."""
        signal = Signal(sender=sender, payload=payload)
        with self._lock:
            self._log.append(signal)
            # Create a snapshot to safely iterate
            targets = list(self._subscribers.values())
        
        for listeners in targets:
            for cb in listeners:
                try:
                    cb(signal)
                except Exception as e:
                    print(f"[MirrorLink] Listener error: {e}")

    def get_log(self, limit=50) -> List[Signal]:
        """Return last N messages."""
        with self._lock:
            return self._log[-limit:]


# ------------------------------------------------------------------ #
# Singleton bus instance
MIRROR_LINK = MirrorLinkBus()

# Usage:
# - Agent A: MIRROR_LINK.emit("BlueHat", {"intent": "warn", "topic": "burst_dos"})
# - Agent B: MIRROR_LINK.subscribe("GrayHat", callback_fn)
