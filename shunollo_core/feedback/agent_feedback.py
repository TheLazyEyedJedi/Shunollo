def apply_feedback(agent, event, feedback_score):
    # Placeholder logic: adjust internal weights or logs
    if hasattr(agent, "adjust_weights"):
        agent.adjust_weights(event, feedback_score)
    else:
        print(f"No feedback handler on {agent.__class__.__name__}")
