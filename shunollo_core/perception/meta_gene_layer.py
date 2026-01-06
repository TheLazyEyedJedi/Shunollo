"""
meta_gene_layer.py – governs symbolic mutation and adaptation in agent perceptual genomes
"""

import random
from typing import List, Dict
from collections import defaultdict, Counter

# Internal symbolic trait tracking
_trait_memory: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
_bootstrapped = False

def _bootstrap_if_needed():
    global _bootstrapped
    if not _bootstrapped:
        reconstruct_state()
        _bootstrapped = True

def reconstruct_state():
    """Manually rebuild the trait memory from persistent CodonMemory."""
    global _trait_memory
    from shunollo_core.perception.codon_memory import get_all_memory
    
    # Clear existing memory if any (Idempotency)
    _trait_memory.clear()
    
    mem = get_all_memory()
    for agent, agent_codons in mem.items():
        for codon, stats in agent_codons.items():
            count = stats.get('count', 0)
            # Split codon into traits and add to memory
            traits = codon.split('_')
            for t in traits:
                _trait_memory[agent][t] += count

def adapt(agent: str, codon: List[str]) -> None:
    """Reinforce codon parts as adaptive traits."""
    _bootstrap_if_needed()
    for trait in codon:
        _trait_memory[agent][trait] += 1


def deprecate(agent: str, codon: List[str]) -> None:
    """Suppress codon parts that proved unhelpful."""
    _bootstrap_if_needed()
    for trait in codon:
        _trait_memory[agent][trait] -= 1


def mutate(agent: str, codon: List[str]) -> List[str]:
    """Apply symbolic mutation to one part of the codon."""
    mutation_bank = {
        "high_pitch": "low_pitch",
        "low_pitch": "high_pitch",
        "bright": "dim",
        "dim": "bright",
        "loud": "quiet",
        "quiet": "loud"
    }

    mutated = codon[:]
    idx = random.randint(0, len(codon) - 1)
    if codon[idx] in mutation_bank:
        mutated[idx] = mutation_bank[codon[idx]]
    return mutated


def trait_profile(agent: str) -> Dict[str, int]:
    """Return the trait frequency profile for an agent."""
    _bootstrap_if_needed()
    return dict(sorted(_trait_memory[agent].items(), key=lambda x: -x[1]))


def summary(agent: str) -> Dict:
    """Summarize adaptation state."""
    traits = trait_profile(agent)
    return {
        "agent": agent,
        "trait_count": len(traits),
        "top_traits": list(traits.items())[:5]
    }
