"""Symbolic trait adaptation with explicit, host-supplied reconstruction data.

No storage is opened implicitly. Hosts can keep independent TraitMemory instances;
module functions retain the historical single-process convenience interface.
"""
import random
from collections import defaultdict
from collections.abc import Mapping
from threading import RLock
from typing import Dict, List


class TraitMemory:
    """In-memory trait counts; persistence and snapshot selection belong to the host."""

    def __init__(self):
        self._traits = defaultdict(lambda: defaultdict(int))
        self._lock = RLock()

    def reconstruct_state(self, snapshot=None):
        """Atomically replace state from {agent: {codon: {'count': int}}}.

        Counts must be nonnegative integers; weights are never treated as counts.
        Legacy underscore tokenization is preserved. None explicitly resets state.
        The input is not mutated, and invalid input leaves previous state intact.
        """
        if snapshot is None:
            snapshot = {}
        if not isinstance(snapshot, Mapping):
            raise ValueError('Snapshot must be an agent-to-codon mapping')
        replacement = defaultdict(lambda: defaultdict(int))
        for agent, codons in snapshot.items():
            if not isinstance(agent, str) or not agent or not isinstance(codons, Mapping):
                raise ValueError('Each named agent requires a codon mapping')
            for codon, stats in codons.items():
                if not isinstance(codon, str) or not codon or not isinstance(stats, Mapping):
                    raise ValueError('Each codon requires count statistics')
                count = stats.get('count')
                if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                    raise ValueError('Codon count must be a nonnegative integer')
                for trait in codon.split('_'):
                    if trait:
                        replacement[agent][trait] += count
        with self._lock:
            self._traits = replacement

    def _update(self, agent, traits, delta):
        if not isinstance(agent, str) or not agent:
            raise ValueError('Agent must be a nonempty string')
        if isinstance(traits, str):
            raise ValueError('Traits must be a sequence, not a single string')
        traits = list(traits)
        if any(not isinstance(t, str) or not t for t in traits):
            raise ValueError('Traits must be nonempty strings')
        with self._lock:
            for trait in traits:
                self._traits[agent][trait] += delta

    def adapt(self, agent, codon):
        self._update(agent, codon, 1)

    def deprecate(self, agent, codon):
        self._update(agent, codon, -1)

    def trait_profile(self, agent):
        with self._lock:
            return dict(sorted(self._traits.get(agent, {}).items(), key=lambda item: -item[1]))

    def summary(self, agent):
        traits = self.trait_profile(agent)
        return {'agent': agent, 'trait_count': len(traits), 'top_traits': list(traits.items())[:5]}


_default_memory = TraitMemory()


def reconstruct_state(snapshot=None):
    """Replace default state explicitly; no argument resets it to empty."""
    _default_memory.reconstruct_state(snapshot)


def adapt(agent: str, codon: List[str]) -> None:
    _default_memory.adapt(agent, codon)


def deprecate(agent: str, codon: List[str]) -> None:
    _default_memory.deprecate(agent, codon)


def trait_profile(agent: str) -> Dict[str, int]:
    return _default_memory.trait_profile(agent)


def summary(agent: str) -> Dict:
    return _default_memory.summary(agent)


def mutate(agent: str, codon: List[str]) -> List[str]:
    """Preserve the existing symbolic mutation interface."""
    mutation_bank = {'high_pitch': 'low_pitch', 'low_pitch': 'high_pitch',
                     'bright': 'dim', 'dim': 'bright', 'loud': 'quiet', 'quiet': 'loud'}
    mutated = codon[:]
    idx = random.randint(0, len(codon) - 1)
    if codon[idx] in mutation_bank:
        mutated[idx] = mutation_bank[codon[idx]]
    return mutated
