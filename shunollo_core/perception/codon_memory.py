"""codon_memory.py
===================

Persistent JSON store capturing codon‑level stats + feedback per agent.

A *codon* is always a **string** produced by ``codon_builder.build_codons``.
"""  # noqa: E501

import json
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional
from shunollo_core.config import config
_PATH = Path(config.storage["codon_memory_path"])
_PATH.parent.mkdir(parents=True, exist_ok=True)

# --- I/O Shield State (P7.5) ---
_memory_lock = threading.RLock()
_memory: Dict = {}
_dirty = False

def _init_memory():
    global _memory
    with _memory_lock:
        if not _memory:
            if _PATH.exists():
                try:
                    _memory = json.loads(_PATH.read_text())
                except:
                    _memory = {}
            else:
                _memory = {}

# ------------------------------------------------------------------ #
# ------------------------------------------------------------------ #
# ------------------------------------------------------------------ #
# ------------------------------------------------------------------ #
from shunollo_core.memory.base import AbstractMemory

def sync_to_disk() -> None:
    """Flush memory to disk if changes were made."""
    # NO-OP: Database is immediate (ACID)
    pass

# ------------------------------------------------------------------ #
# --- Cache for Weights (Prevent DB spam per packet) ---
_weight_cache = {}
_cache_lock = threading.RLock()

def get_codon_weight(agent: str, codon: str, memory: AbstractMemory) -> float:
    """Calculates weight dynamically from DB feedback (with caching)."""
    with _cache_lock:
        # Lazy load weights for this agent if not in cache
        if agent not in _weight_cache:
            print(f"[Memory] Cold start: Fetching weights for {agent} from DB...")
            _weight_cache[agent] = memory.get_codon_weights(agent)
            
        return _weight_cache[agent].get(codon, 1.0)

def record_codon_feedback(
    agent: str,
    codons: List[str],
    score: float,
    memory: AbstractMemory,
    feedback: Optional[str] = None,
) -> None:
    """Updates memory in Database (Persistent) and invalidates cache."""
    for codon in codons:
        # 1. Log the feedback event (History)
        if feedback:
             memory.record_codon_feedback(agent, codon, feedback, score)
    
    # 2. Invalidate cache for this agent so next fetch re-calculates
    if feedback:
        with _cache_lock:
            if agent in _weight_cache:
                del _weight_cache[agent]

