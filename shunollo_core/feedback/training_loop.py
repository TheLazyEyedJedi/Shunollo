"""
training_loop.py – now includes symbolic adaptation via meta_gene_layer
"""

from shunollo_core.perception.meta_gene_layer import adapt, deprecate
from shunollo_core.perception.percept_genome import get_recent

def apply_feedback(agent_name: str, feedback_score: int):
    """Train based on recent feedback."""
    codons = get_recent(agent_name, limit=1)
    if not codons:
        return

    latest = codons[0]
    if feedback_score > 0:
        adapt(agent_name, latest)
    else:
        deprecate(agent_name, latest)
