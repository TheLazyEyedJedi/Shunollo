# shunollo_core/perception/perception_buffer.py  ─────────────────────────────
"""Ring buffers for silent audio + visual playback.

Agents can push perceptual frames (numpy arrays) into these buffers; another
thread could later drive PyAudio/Pygame for true playback.  For Phase‑1 we only
retain the most recent *N* frames so agents can reference `last_heard` /
`last_seen` in their scoring.
"""
from __future__ import annotations
import numpy as np
from collections import deque
from threading import Lock
from typing import Deque, Tuple

class RingBuffer:
    def __init__(self, size: int, frame_shape: Tuple[int, ...]):
        self.size = size
        self.frame_shape = frame_shape
        self.buf: Deque[np.ndarray] = deque(maxlen=size)
        self._lock = Lock()

    def push(self, frame: np.ndarray) -> None:
        if frame.shape != self.frame_shape:
            raise ValueError(f"expected shape {self.frame_shape}, got {frame.shape}")
        with self._lock:
            self.buf.append(frame.astype(np.float32))

    def last(self) -> np.ndarray | None:
        with self._lock:
            return self.buf[-1].copy() if self.buf else None

# global buffers (configurable)
AUDIO_BUFFER = RingBuffer(size=32, frame_shape=(128,))     # e.g. 128‑bin FFT
VISUAL_BUFFER = RingBuffer(size=32, frame_shape=(64, 64))  # e.g. 64×64 greyscale

# -----------------------------------------------------------------------------
