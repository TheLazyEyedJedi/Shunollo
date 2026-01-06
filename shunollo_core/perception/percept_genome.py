"""percept_genome.py
=====================

In‑memory adaptive weight table mapping ``(agent, codon) -> weight``.

* Weights default to **1.0**.
* ``update_weights()`` applies exponential moving‑average learning.
* ``decay_all()`` globally decays every stored weight.
* Optional ``flush_to_disk() / load_from_disk()`` helpers write a small JSON
  snapshot so that learned weights survive restarts.
"""  # noqa: E501

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from shunollo_core.perception.codon_memory import (
    record_codon_feedback,
    get_codon_weight,
)

_weights: Dict[str, Dict[str, float]] = defaultdict(dict)

_LR = 0.1          # learning‑rate for new reward
_DECAY = 0.99      # weight decay per tick
_MIN_W, _MAX_W = 0.0, 5.0

# ------------------------------------------------------------------ #
def update_weights(agent: str, codons: List[str], reward: float) -> None:
    """
    Blend ``reward`` into each codon’s weight for *agent*.

    Positive reward pushes weight up, negative pushes down.
    """  # noqa: E501
    mem = _weights[agent]
    for codon in codons:
        old = mem.get(codon, 1.0)
        new = max(_MIN_W, min(_MAX_W, old * (1 - _LR) + reward * _LR))
        mem[codon] = new

    # Store simple ± feedback in codon_memory
    feedback_tag = "positive" if reward > 0 else "negative" if reward < 0 else None
    if feedback_tag:
        record_codon_feedback(agent, codons, score=reward, feedback=feedback_tag)

def get_weight(agent: str, codon: str) -> float:
    """Return in‑memory weight or fall back to codon_memory disk value."""
    if codon in _weights.get(agent, {}):
        return _weights[agent][codon]
    return get_codon_weight(agent, codon)

def decay_all() -> None:
    for mem in _weights.values():
        for codon, w in mem.items():
            mem[codon] = max(_MIN_W, w * _DECAY)

# ---- optional lightweight persistence -------------------------------- #
_SNAPSHOT = Path(__file__).with_suffix(".weights.json")

def flush_to_disk() -> None:
    _SNAPSHOT.write_text(json.dumps(_weights, indent=2))

def load_from_disk() -> None:
    if _SNAPSHOT.exists():
        _weights.clear()
        _weights.update(json.loads(_SNAPSHOT.read_text()))
