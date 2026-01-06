def aggregate_scores(agent_results):
    """
    Combine agent results into a final decision.
    Currently averages scores and picks the dominant classification.
    """
    if not agent_results:
        return {"score": 0, "classification": "Unknown"}

    total_score = sum(r["score"] for r in agent_results)
    classifications = [r["classification"] for r in agent_results]

    avg_score = total_score / len(agent_results)
    dominant_class = max(set(classifications), key=classifications.count)

    return {
        "score": avg_score,
        "classification": dominant_class
    }
