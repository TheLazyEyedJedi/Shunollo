# score_utils.py
def compute_consensus_score(agent_scores: dict) -> float:
    """
    Compute a weighted average from agent scores.
    """
    if not agent_scores:
        return 0.0
    total_weight = len(agent_scores)
    weighted_sum = sum(agent_scores.values())
    return round(weighted_sum / total_weight, 2)
