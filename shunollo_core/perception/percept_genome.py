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
import math
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
def update_weights(agent: str, codons: List[str], reward: float, *, memory=None) -> None:
    """
    Blend ``reward`` into each codon’s weight for *agent*.

    Positive reward pushes weight up, negative pushes down.
    """  # noqa: E501
    if memory is None:
        raise ValueError('An explicit host memory adapter is required')
    if not isinstance(agent, str) or not agent or not codons or any(not isinstance(c, str) or not c for c in codons):
        raise ValueError('Named agent and nonempty codon strings required')
    if isinstance(reward, bool) or not isinstance(reward, (int, float)) or not math.isfinite(reward):
        raise ValueError('Finite reward required')
    feedback_tag = 'positive' if reward > 0 else 'negative' if reward < 0 else None
    if feedback_tag:
        record_codon_feedback(agent, codons, score=reward, memory=memory, feedback=feedback_tag)
    mem = _weights[agent]
    for codon in codons:
        old = mem.get(codon, 1.0)
        new = max(_MIN_W, min(_MAX_W, old * (1 - _LR) + reward * _LR))
        mem[codon] = new


def get_weight(agent: str, codon: str, *, memory=None) -> float:
    """Return in‑memory weight or fall back to codon_memory disk value."""
    if memory is not None:
        return memory.get_codon_weights(agent).get(codon, 1.0)
    if codon in _weights.get(agent, {}):
        return _weights[agent][codon]
    return 1.0

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
