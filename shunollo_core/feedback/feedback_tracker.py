"""
feedback_tracker.py – manages symbolic feedback logic for perceptual codons
"""

from shunollo_core.perception.meta_gene_layer import adapt, deprecate
from shunollo_core.perception.percept_genome import get_recent

def handle_manual_feedback(agent: str, score: int) -> None:
    """Responds to manual feedback by adapting/deprecating codons."""
    recent = get_recent(agent, limit=1)
    if recent:
        codon = recent[0]
        if score > 0:
            adapt(agent, codon)
        else:
            deprecate(agent, codon)
