"""
training_loop.py – now includes symbolic adaptation via meta_gene_layer
"""

from shunollo_core.perception.meta_gene_layer import TraitMemory

def apply_feedback(agent_name: str, feedback_score: int, *, traits, memory: TraitMemory):
    """Adapt explicit symbolic traits; this does not train a language model."""
    if type(feedback_score) not in (int, float) or feedback_score not in (-1, 0, 1):
        raise ValueError('Feedback must be -1, 0 or 1')
    if feedback_score > 0:
        memory.adapt(agent_name, traits)
    elif feedback_score < 0:
        memory.deprecate(agent_name, traits)
    return memory.summary(agent_name)
