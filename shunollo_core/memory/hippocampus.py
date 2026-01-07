"""
Hippocampus (Episodic Memory)
-----------------------------
Biological Role: Consolidation of Short-term to Long-term memory. Spatial navigation.
Cybernetic Role: Stores raw Sensory Events (Episodes) for offline replay ('Dreaming').

Features:
- Append-only Log (JSONL) of ShunolloSignals.
- 'Dreaming' interface to recall past events.
- Physics-RAG: Vector similarity search for episodic recall (Déjà Vu).
"""
import json
import random
import os
from pathlib import Path
from datetime import datetime
from typing import List, Generator, Tuple, Optional
from shunollo_core.models import ShunolloSignal
from shunollo_core.config import config

# Cross-platform file locking
if os.name == 'nt':  # Windows
    import msvcrt
    def _lock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
    def _unlock_file(f):
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass  # Already unlocked
else:  # Unix/Linux/Mac
    import fcntl
    def _lock_file(f):
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    def _unlock_file(f):
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


class Hippocampus:
    """
    Episodic Memory with Physics-RAG capabilities.
    
    Uses lazy-loaded in-memory cache to avoid O(n) file reads on every recall.
    Thread-safe file operations via file locking.
    """
    
    # Default threshold for "similar" signals (Euclidean distance in normalized 18-dim space)
    # Rule of thumb: 0.5 = very similar, 1.0 = somewhat similar, 2.0 = loosely related
    DEFAULT_THRESHOLD = 1.0
    
    def __init__(self, max_cache_size: int = 10000):
        self.storage_path = Path(config.storage["cache_dir"]) / "episodic_memory.jsonl"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for O(1) access (fixes Issue 1: O(n) scan)
        self._cache: Optional[List[ShunolloSignal]] = None
        self._cache_dirty = True
        self._max_cache_size = max_cache_size

    def _load_cache(self) -> List[ShunolloSignal]:
        """Lazy-load cache from disk. Only reads file once until invalidated."""
        if self._cache is not None and not self._cache_dirty:
            return self._cache
        
        self._cache = []
        if not self.storage_path.exists():
            self._cache_dirty = False
            return self._cache
        
        lines = self.storage_path.read_text(encoding="utf-8").splitlines()
        
        # Limit to most recent entries if cache is too large
        if len(lines) > self._max_cache_size:
            lines = lines[-self._max_cache_size:]
        
        for line in lines:
            try:
                data = json.loads(line)
                self._cache.append(ShunolloSignal(**data))
            except Exception:
                continue
        
        self._cache_dirty = False
        return self._cache

    def remember(self, signal: ShunolloSignal) -> None:
        """
        Encodes a conscious experience (Signal) into Long-Term Memory.
        Thread-safe with file locking.
        """
        record = signal.model_dump()
        # Ensure timestamp is string
        if isinstance(record.get("timestamp"), datetime):
            record["timestamp"] = record["timestamp"].isoformat()
        
        # File locking for thread safety (fixes Issue 4)
        with open(self.storage_path, "a", encoding="utf-8") as f:
            try:
                _lock_file(f)
                f.write(json.dumps(record) + "\n")
            finally:
                _unlock_file(f)
        
        # Invalidate cache so next recall picks up new data
        self._cache_dirty = True
        
        # Also append to in-memory cache for immediate access
        if self._cache is not None:
            self._cache.append(signal)
            # Trim cache if too large
            if len(self._cache) > self._max_cache_size:
                self._cache = self._cache[-self._max_cache_size:]

    def dream(self, batch_size: int = 10, random_sample: bool = True) -> Generator[ShunolloSignal, None, None]:
        """
        Recalls past experiences.
        If random_sample=True, picks random moments (Remixing).
        If False, picks most recent (Reflection).
        """
        cache = self._load_cache()
        if not cache:
            return

        if random_sample:
            selection = random.sample(cache, min(len(cache), batch_size))
        else:
            selection = cache[-batch_size:]

        for signal in selection:
            yield signal

    def recall_similar(
        self, 
        query_vector: List[float], 
        k: int = 3, 
        threshold: Optional[float] = None
    ) -> List[Tuple[ShunolloSignal, float]]:
        """
        Find episodes with similar physics vectors (Déjà Vu / Physics-RAG).
        
        Uses in-memory cache for O(n) where n = cache size (not file size).
        
        Args:
            query_vector: 18-dimensional normalized physics fingerprint
            k: Maximum number of matches to return
            threshold: Maximum Euclidean distance to consider a match.
                      Default is 1.0 (somewhat similar in normalized space).
                      Use 0.5 for strict matching, 2.0 for loose matching.
        
        Returns:
            List of (ShunolloSignal, distance) tuples, sorted by similarity (closest first).
        """
        if threshold is None:
            threshold = self.DEFAULT_THRESHOLD
            
        cache = self._load_cache()
        if not cache:
            return []
        
        matches = []
        for signal in cache:
            stored_vector = signal.to_vector(normalize=True)
            
            # Euclidean distance (18 floats = trivial compute)
            distance = sum((a - b) ** 2 for a, b in zip(query_vector, stored_vector)) ** 0.5
            
            if distance <= threshold:
                matches.append((signal, distance))
        
        # Sort by distance (closest = most similar)
        matches.sort(key=lambda x: x[1])
        return matches[:k]
    
    def get_novelty_score(self, query_vector: List[float]) -> float:
        """
        Calculate how novel this signal is compared to memory.
        
        Returns:
            Distance to nearest neighbor (0.0 = exact match, higher = more novel).
            Returns infinity if memory is empty.
        """
        matches = self.recall_similar(query_vector, k=1, threshold=float('inf'))
        if not matches:
            return float('inf')
        return matches[0][1]

    def clear_memory(self):
        """Amnesia."""
        if self.storage_path.exists():
            self.storage_path.unlink()
        self._cache = None
        self._cache_dirty = True
