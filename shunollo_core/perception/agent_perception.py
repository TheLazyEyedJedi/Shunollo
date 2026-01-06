"""agent_perception – central hub for Shunollo perception.

• **Mixin class `AgentPerception`** – gives every agent `.hear()` / `.see()` that
  push frames into the ring buffers **and** broadcast on the perception bus.
• **Module‑level helpers** – `hear()`, `see()`, `last_heard()`, `last_seen()` so
  external scripts can inject or query frames without subclassing an agent.
"""
from __future__ import annotations
from typing import Any, Dict, Optional
import numpy as np

from shunollo_core.perception.perception_bus import publish, subscribe
from shunollo_core.perception.perception_buffer import AUDIO_BUFFER, VISUAL_BUFFER

# ------------------------------------------------------------------ #
# Mixin for agents
# ------------------------------------------------------------------ #
class AgentPerception:
    """Mixin that wires an agent into global perception buffers + bus."""

    last_heard: Optional[Any] = None
    last_seen:  Optional[Any] = None

    def __init__(self, *args, **kwargs):
        subscribe(self._on_frame)   # listen for frames from others
        super().__init__(*args, **kwargs)

    # ----------------- instance methods --------------------------- #
    def hear(self, sound: Any) -> None:
        """Store & broadcast an audio frame (dict or ndarray)."""
        self.last_heard = sound
        if isinstance(sound, np.ndarray):
            AUDIO_BUFFER.push(sound)
        publish({"sound": sound})

    def see(self, light: Any) -> None:
        """Store & broadcast a visual frame (dict or ndarray)."""
        self.last_seen = light
        if isinstance(light, np.ndarray):
            VISUAL_BUFFER.push(light)
        publish({"light": light})

    def _on_frame(self, frame: Dict[str, Any]) -> None:
        """Override in subclasses to react to bus frames."""
        pass

# ------------------------------------------------------------------ #
# Module‑level helpers for external scripts
# ------------------------------------------------------------------ #

def hear(frame: Any) -> None:          # noqa: D401
    """Emit an audio frame without needing an agent instance."""
    if isinstance(frame, np.ndarray):
        AUDIO_BUFFER.push(frame)
    publish({"sound": frame})

def see(frame: Any) -> None:           # noqa: D401
    """Emit a visual frame without needing an agent instance."""
    if isinstance(frame, np.ndarray):
        VISUAL_BUFFER.push(frame)
    publish({"light": frame})

def last_heard():
    """Return the most recent audio numpy frame (or None)."""
    return AUDIO_BUFFER.last()

def last_seen():
    """Return the most recent visual numpy frame (or None)."""
    return VISUAL_BUFFER.last()

__all__ = [
    "AgentPerception",
    "hear",
    "see",
    "last_heard",
    "last_seen",
]
